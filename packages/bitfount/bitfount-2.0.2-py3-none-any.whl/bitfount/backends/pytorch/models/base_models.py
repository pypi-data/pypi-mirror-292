"""Base models and helper classes using PyTorch as the backend."""

from __future__ import annotations

from abc import abstractmethod
import contextlib
from functools import partial
import inspect
from io import BytesIO
from itertools import chain
import logging
import os
import re
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    MutableMapping,
    Optional,
    OrderedDict,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import desert
from marshmallow import fields
import numpy as np
import pandas as pd
import pytorch_lightning as pl
from pytorch_lightning.callbacks import (
    Callback,
    ModelCheckpoint,
    StochasticWeightAveraging,
)
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.callbacks.progress import TQDMProgressBar
from pytorch_lightning.loggers import TensorBoardLogger
from sklearn.base import BaseEstimator
import torch
from torch import Tensor, nn as nn

# Convention is to import functional as F
# noinspection PyPep8Naming
from torch.nn import functional as F
import torch.optim as optimizers
from torch.optim.lr_scheduler import _LRScheduler
import torch.optim.lr_scheduler as schedulers
from torch.utils.data import DataLoader
import torch_optimizer as torch_optimizers

from bitfount.backends.pytorch._torch_shims import LightningLoggerBase
from bitfount.backends.pytorch.data.dataloaders import (
    PyTorchBitfountDataLoader,
    PyTorchIterableBitfountDataLoader,
    _BasePyTorchBitfountDataLoader,
)
from bitfount.backends.pytorch.epoch_callbacks import EpochCallbacks
from bitfount.backends.pytorch.federated.mixins import _PyTorchDistributedModelMixIn
from bitfount.backends.pytorch.types import (
    ImgAndTabBatch,
    ImgAndTabDataSplit,
    ImgDataReturnType,
    ImgFwdTypes,
    ImgXorTabBatch,
    ImgXorTabDataSplit,
    TabDataReturnType,
    TabFwdTypes,
    _AdaptorForPyTorchTensor,
)
from bitfount.backends.pytorch.utils import (
    _TORCH_DTYPES,
    LoggerType,
    autodetect_gpu,
    enhanced_torch_load,
    has_mps,
)
from bitfount.backends.pytorch.weight_clipper import _PytorchParamConstraint
from bitfount.config import BITFOUNT_LOGS_DIR, BITFOUNT_OUTPUT_DIR, DP_AVAILABLE
from bitfount.data.databunch import BitfountDataBunch
from bitfount.data.dataloaders import BitfountDataLoader
from bitfount.data.datasets import _BitfountDataset
from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.exceptions import IterableDataSourceError
from bitfount.data.types import DataSplit, _SingleOrMulti
from bitfount.federated.helper import TaskContext
from bitfount.federated.privacy.differential import (
    DPModellerConfig,
    _DifferentiallyPrivate,
)
from bitfount.metrics import Metric, MetricCollection
from bitfount.models.base_models import (
    ClassifierMixIn,
    LoggerConfig,
    NeuralNetworkMixIn,
    NeuralNetworkPredefinedModel,
    Optimizer,
    Scheduler,
    _BaseModel,
)
from bitfount.types import (
    T_DTYPE,
    T_FIELDS_DICT,
    EvaluateReturnType,
    PredictReturnType,
    _StrAnyDict,
    _TensorLike,
)
from bitfount.utils import _merge_list_of_dicts, delegates, seed_all
from bitfount.utils.logging_utils import filter_stderr

logger = logging.getLogger(__name__)


if DP_AVAILABLE:
    from opacus import GradSampleModule, PrivacyEngine
    from opacus.accountants import RDPAccountant
    from opacus.validators import ModuleValidator, register_module_fixer
    from opacus.validators.errors import UnsupportedModuleError


_OptimizerType = Union[torch_optimizers.Optimizer, optimizers.Optimizer]

_OPTIMIZERS: Dict[str, Type[_OptimizerType]] = {
    name: class_
    # If there are name clashes, preference is given to the original torch version
    for name, class_ in dict(
        cast(
            Iterator[Tuple[str, Any]],
            chain.from_iterable(
                d.items() for d in (vars(torch_optimizers), vars(optimizers))
            ),
        )
    ).items()
    if inspect.isclass(class_)
    and issubclass(class_, (optimizers.Optimizer, torch_optimizers.Optimizer))
    and not inspect.isabstract(class_)
    and name != "Optimizer"
}

_SCHEDULERS: Dict[str, Type[_LRScheduler]] = {
    name: class_
    for name, class_ in vars(schedulers).items()
    if inspect.isclass(class_)
    and issubclass(class_, _LRScheduler)
    and not inspect.isabstract(class_)
    and name != "_LRScheduler"
}


_STEP_OUTPUT = Union[torch.Tensor, _StrAnyDict]  # From pl.LightningModule


def _calculate_embedding_sizes(
    categorical_feature_sizes: Iterable[int],
) -> List[Tuple[int, int]]:
    """Calculate embedding sizes.

    The formula for determining the size of the embeddings is determined by
    empirical evidence alone and borrowed from the fast.ai library.

    Args:
        categorical_feature_sizes: An iterable of the number of categories in each
            categorical feature.

    Returns:
        A list of (number of categories, embedding vector length) pairs for each
        categorical feature.
    """
    embedding_sizes = [
        (n_categories, min(600, round(1.6 * n_categories**0.56)))
        for n_categories in categorical_feature_sizes
    ]
    return embedding_sizes


if DP_AVAILABLE:
    # Module fixer implementation that is more friendly with our expected layer sizes,
    # etc. We register this as the preferred module replacer for BatchNorm layers in
    # Opacus.
    @register_module_fixer(  # type: ignore[misc] # Reason: untyped decorator (not ours)
        [nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d, nn.SyncBatchNorm]
    )
    def _fix_batch_norm(
        module: Union[nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d, nn.SyncBatchNorm]
    ) -> nn.GroupNorm:
        # A default value of 32 is chosen for the number of groups based on the paper
        # *Group Normalization* https://arxiv.org/abs/1803.08494.
        # If this is not appropriate for the num_features in the layer we then try to
        # find an alternative.
        num_groups = min(32, module.num_features)
        while num_groups > 1:
            # If num_features is divisible by num_groups we can use it
            if module.num_features % num_groups == 0:
                break
            # Otherwise, try the next number down
            num_groups -= 1
        else:
            # If we reach the end of the while-loop we couldn't find a compatible
            # number of groups.
            raise UnsupportedModuleError(
                "Unable to find compatible number of groups for GroupNorm replacement "
                "of BatchNorm. Tried [2,32]."
            )

        return nn.GroupNorm(num_groups, module.num_features, affine=module.affine)


@delegates()
class PyTorchClassifierMixIn(ClassifierMixIn):
    """MixIn for PyTorch classification problems.

    PyTorch classification models must have this class in their inheritance hierarchy.
    """

    def _do_output_activation(self, output: torch.Tensor) -> torch.Tensor:
        """Perform final activation function on output."""
        if self.multilabel:
            return torch.sigmoid(output)
        else:
            return F.softmax(output, dim=1)


@delegates()
class _PyTorchNeuralNetworkMixIn(NeuralNetworkMixIn):
    """All Pytorch Neural Networks must inherit from this abstract class.

    Specifies model structure and hyperparameters.
    """

    @staticmethod
    def _get_optimizer(optimizer: Optimizer) -> Callable[..., _OptimizerType]:
        """Returns appropriate optimizer class."""
        if optimizer.name in _OPTIMIZERS:
            return partial(_OPTIMIZERS[optimizer.name], **optimizer.params)

        raise ValueError(
            "Optimizer not supported.",
            "Please provide one supported by 'torch' or 'torch_optimizer'.",
        )

    @staticmethod
    def _get_scheduler(scheduler: Scheduler) -> Callable[..., _LRScheduler]:
        """Returns appropriate scheduler class."""
        if scheduler.name in _SCHEDULERS:
            return partial(_SCHEDULERS[scheduler.name], **scheduler.params)

        raise ValueError(
            "Scheduler not supported.",
            "Please provide one supported by 'torch'.",
        )

    @staticmethod
    def _get_early_stopping_callback(
        early_stopping_params: Optional[_StrAnyDict] = None,
    ) -> EarlyStopping:
        """Returns EarlyStopping Callback."""
        if early_stopping_params is None:
            early_stopping_params = dict(
                monitor="validation_loss",
                min_delta=0.00,
                patience=2,
                verbose=True,
                mode="min",
            )

        return EarlyStopping(**early_stopping_params)


T_PYTORCH = TypeVar("T_PYTORCH", bound="BasePyTorchModel")


@delegates()
class BasePyTorchModel(
    _PyTorchDistributedModelMixIn[T_DTYPE],
    _PyTorchNeuralNetworkMixIn,
    _DifferentiallyPrivate,
    _BaseModel,
    Generic[T_DTYPE, T_PYTORCH],
    pl.LightningModule,
):
    """Implements a Neural Network in PyTorch Lightning.

    Args:
        model_name: Used for tensorboard logging. Model name will be left blank and
            default to "default" if none provided. Optional.
        model_version: Used for tensorboard logging.If version is not specified the
            logger inspects the save directory for existing versions, then automatically
            assigns the next available version. If it is a string then it is used as the
            run-specific subdirectory name, otherwise `version_${version}` is used.
            Optional.
        stochastic_weight_avg: Whether to use [Stochastic Weight Averaging (SWA)](
            https://pytorch.org/blog/pytorch-1.6-now-includes-stochastic-\
weight-averaging).
        logger_config: Logger configuration. Optional. Will default to Tensorboard if
            not provided.

    Attributes:
        epochs: Number of epochs to train for when calling fit.
        model_name: Name of the model.
        model_version: Version of the model.
        steps: Number of steps to train for when calling fit.
        stochastic_weight_avg: Whether to use Stochastic Weight Averaging (SWA).
    """

    # Validate attributes
    _validation_results: List[Dict[str, str]]

    # Test attributes
    _test_preds: Optional[Union[List[np.ndarray], pd.DataFrame]]
    _test_targets: Optional[List[np.ndarray]]
    _test_keys: Optional[List[str]]

    train_dl: _BasePyTorchBitfountDataLoader
    # The below fields are left as nested due the
    # `load_only`/`dump_only` methods they have
    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "_dp_config": fields.Nested(
            desert.schema(DPModellerConfig),
            allow_none=True,
            data_key="dp_config",
            dump_only=True,
        ),
        "dp_config": fields.Nested(
            desert.schema(DPModellerConfig),
            allow_none=True,
            data_key="dp_config",
            load_only=True,
        ),
    }

    def __init__(
        self,
        model_name: Optional[str] = None,
        model_version: Optional[Union[int, str]] = None,
        stochastic_weight_avg: bool = False,
        logger_config: Optional[LoggerConfig] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        self.model_name = model_name
        self.model_version = model_version
        self.stochastic_weight_avg = stochastic_weight_avg
        # Set training attributes
        self._model: Optional[nn.Module] = None  # actual underlying model
        self._pl_logger = self._get_logger_from_config(logger_config)
        self._pl_trainer: pl.Trainer = self.trainer_init()  # cannot be "self.trainer"
        self._trained_on_previous_batch: bool = False
        self._total_num_batches_trained: int = 0
        self._model_weights_rolled_back: bool = False
        self._datasource: Optional[BaseSource] = None

        # Store initial values for steps/epochs as these may get overwritten in
        # a set_model_training_iterations() call.
        self._total_epochs = self.epochs
        self._total_steps = self.steps

        self._test_preds = None
        self._test_targets = None
        self._test_keys = None

    @abstractmethod
    def _create_model(self) -> nn.Module:
        """Creates and returns model."""
        raise NotImplementedError

    @abstractmethod
    def _split_dataloader_output(
        self,
        data: Union[
            ImgAndTabDataSplit,
            ImgXorTabDataSplit,
        ],
    ) -> Union[ImgDataReturnType, TabDataReturnType]:
        """Splits the data from the dataloader into X, y."""
        raise NotImplementedError

    @abstractmethod
    def _do_output_activation(self, output: torch.Tensor) -> torch.Tensor:
        """Perform final activation function on output.

        Should be provided by MixIn class.
        """
        raise NotImplementedError

    def tensor_precision(self) -> T_DTYPE:
        """Returns tensor dtype used by Pytorch Lightning Trainer.

        :::note

        Currently only 32-bit training is supported.

        :::

        Returns:
            Pytorch tensor dtype.
        """
        # TODO: [BIT-727] support non-32 bit training
        return cast(T_DTYPE, _TORCH_DTYPES[self._pl_trainer.precision])

    def initialise_model(
        self,
        data: Optional[BaseSource] = None,
        context: Optional[TaskContext] = None,
    ) -> None:
        """Any initialisation of models/dataloaders to be done here.

        Initialises the dataloaders and sets `self._model` to be the output from
        `self.create_model`. Any initialisation ahead of federated or local training,
        serialization or deserialization should be done here.

        Args:
            data: The datasource for model training. Defaults to None.
            context: Indicates if the model is running as a modeller or worker.
                If None, there is no difference between modeller and worker.
        """
        self._initialised = True
        seed_all(self.seed)
        # Set initialisation context
        self._context = context
        if self._context == TaskContext.MODELLER:
            # In a distributed setting, the Modeller needs to first initialise its
            # own model before it can be used. The pod identifier needs to be set
            # before the model is initialised so the  relevant details can be
            # retrieved from the schema. For this we just use the first pod
            # identifier specified in the datastructure as it is assumed the
            # schemas for all the Pods are the same.
            pod_identifiers = self.datastructure.get_pod_identifiers()
            if pod_identifiers:
                self.set_datastructure_identifier(pod_identifiers[0])

        if data is not None:
            if self.datastructure.query:
                table_schema = self.datastructure._override_schema(
                    data_identifier=self._datastructure_identifier
                )
                self.databunch = BitfountDataBunch(
                    data_structure=self.datastructure,
                    schema=table_schema,
                    datasource=data,
                )
            elif self.datastructure.table:
                if context:
                    table_schema = self.schema.get_table_schema(
                        self.datastructure.get_table_name(
                            self._datastructure_identifier
                        )
                    )
                    self.databunch = BitfountDataBunch(
                        data_structure=self.datastructure,
                        schema=table_schema,
                        datasource=data,
                    )
                else:
                    # For local training, we can add the datasource to the schema.
                    try:
                        data.load_data(table_name=self.datastructure.table)
                    except IterableDataSourceError as e:
                        logger.warning(e)
                    self._add_datasource_to_schema(data)

            # Initialise model details
            if self._context != TaskContext.MODELLER:
                self._set_dataloaders(self.batch_size)
        self._opt_func: Callable[..., _OptimizerType] = self._get_optimizer(
            self.optimizer
        )
        self._scheduler_func: Optional[Callable[..., _LRScheduler]] = None
        if isinstance(self.scheduler, Scheduler):
            self._scheduler_func = self._get_scheduler(self.scheduler)

        self._model = self._create_model()

        # Initialise DP if requested
        self._initialise_differential_privacy()

    def _get_logger_from_config(
        self, logger_config: Optional[LoggerConfig]
    ) -> LightningLoggerBase:
        """Initialises the logger for the model."""
        if logger_config is None:
            ml_logger = TensorBoardLogger(
                name=self.model_name,
                version=self.model_version,
                save_dir=str(BITFOUNT_LOGS_DIR),
            )
        elif logger_config.name == "Neptune":
            # Neptune logger doesn't have the concept of a save_dir so no need to set
            ml_logger = LoggerType[logger_config.name].value(**logger_config.params)
        else:
            ml_logger = LoggerType[logger_config.name].value(
                save_dir=str(logger_config.save_dir or BITFOUNT_LOGS_DIR),
                **logger_config.params,
            )
        return ml_logger

    def _initialise_differential_privacy(self) -> None:
        """Initialises the Differential Privacy Engine if requested."""
        if self._dp_config:
            conf = self._dp_config
            # Check DP can be used with model
            if not self._model:
                raise ValueError("Model uninitialized")
            validation_errors = ModuleValidator.validate(self._model)
            if validation_errors:
                # If autofix, try to do so
                if conf.auto_fix:
                    errors_str = "\n\t".join(repr(err) for err in validation_errors)
                    # Logging the opacus errors for debugging purposes in our logs.
                    logger.debug(
                        f"Incompatible modules detected in model: \n\t{errors_str}"
                    )
                    # Still raise a warning.
                    logger.warning(
                        "Some of the modules used in the model are incompatible "
                        "with `opacus`, attempting to autofix."
                    )
                    self._model = ModuleValidator.fix_and_validate(self._model)
                else:
                    raise UnsupportedModuleError(validation_errors)

            # If not on modeller:
            # - Create Engine
            # - Change Dataloaders
            # - Create Noise Multiplier
            if self._context != TaskContext.MODELLER:
                self._dp_engine = PrivacyEngine(secure_mode=True)

                # Recreate train dataloader with shuffled data, which is required for
                # privacy guarantees. It will be replaced with a CSPRNG shuffler later
                # by Opacus itself.
                # We use the private method to do this to ensure the created dataloader
                # uses the expected dataset and batch size.
                logger.info("Creating shuffled training dataloader")
                self.train_dl.shuffle = True
                if isinstance(self.train_dl, PyTorchIterableBitfountDataLoader):
                    self.train_dl.secure_rng = True
                elif isinstance(self.train_dl, PyTorchBitfountDataLoader):
                    self.train_dl.dataloader = self.train_dl.get_pytorch_dataloader()

                self._noise_multiplier = conf.noise_multiplier

            # In order for the model to be compatible on both modeller and worker
            # we need to manually make it privacy compatible by wrapping it in a
            # GradSampleModule.
            # This is the same approach taken in PrivacyEngine.make_private() and
            # doing it now, ahead of time, is not incompatible with that call as it's
            # able to detect that the model is already wrapped.
            # We use batch_first=True as that's the default value in
            # PrivacyEngine.make_private() and we don't expose the ability to
            # specify a different value. make_private() will also raise an error
            # if the values of batch_first or loss_reduction differ which makes
            # this forward-compatible with any changes to the default values in
            # make_private().
            if not self._model:
                raise ValueError("Model uninitialized")
            self._model = GradSampleModule(
                self._model,
                batch_first=True,
                loss_reduction=conf.loss_reduction,
            )

    def trainer_init(self) -> pl.Trainer:
        """Initialises the Lightning Trainer for this model.

        Documentation for pytorch-lightning trainer can be found here:
        https://pytorch-lightning.readthedocs.io/en/stable/common/trainer.html

        Returns:
            The pytorch lightning trainer.
        """
        callbacks: List[Callback] = [TQDMProgressBar(refresh_rate=1), EpochCallbacks()]

        if self.stochastic_weight_avg:
            # If SWA is requested, add it with a default value
            # https://pytorch-lightning.readthedocs.io/en/stable/advanced/training_tricks.html#stochastic-weight-averaging  # noqa: B950
            callbacks.append(StochasticWeightAveraging(swa_lrs=1e-2))

        if self.early_stopping:
            callbacks.append(
                self._get_early_stopping_callback(self.early_stopping.params)
            )

        if self._dp_config:
            # This combination of arguments saves just the most recent copy of the
            # weights in the checkpoint each batch and makes a copy of it called
            # 'last.ckpt' so the name is always known
            logger.debug("Model checkpointing callback initialised")
            checkpoint_callback = ModelCheckpoint(
                save_last=True,
                save_weights_only=True,
                save_top_k=1,
                every_n_train_steps=1,
            )
            callbacks.append(checkpoint_callback)

        # torch emits warnings to stderr that are not relevant for us, so we need
        # to filter them out
        with filter_stderr(
            re.escape(
                "[W Context.cpp:70] Warning:"
                " torch.use_deterministic_algorithms is in beta"
            )
        ):
            # TODO: [BIT-1412] allow the user to provide these arguments in the
            # constructor
            gpu_kwargs = autodetect_gpu()
            trainer = pl.Trainer(
                enable_checkpointing=True if self._dp_config else False,
                max_epochs=self.epochs or -1,
                max_steps=self.steps or -1,
                # Setting deterministic to True ensures that the results are
                # reproducible but this comes at the cost of performance. Also, some
                # operations require setting the CUBLAS_WORKSPACE_CONFIG env var to
                # `:4096:8` or `:16:8` when using CUDA.
                deterministic=True,
                auto_lr_find=True,
                logger=self._pl_logger,
                callbacks=callbacks,
                check_val_every_n_epoch=1,
                default_root_dir=str(BITFOUNT_OUTPUT_DIR),
                **gpu_kwargs,
            )
            return trainer

    def train_dataloader(self) -> Optional[BitfountDataLoader]:  # type: ignore[override] # Reason: see below  # noqa: B950
        """Returns training dataloader."""
        # We override the dataloader return annotation as the LightningModule
        # expects a pytorch DataLoader, and we return PyTorchBitfountDataLoader
        return self.train_dl

    def val_dataloader(self) -> Optional[BitfountDataLoader]:  # type: ignore[override] # Reason: see below  # noqa: B950
        """Returns validation dataloader."""
        # We override the dataloader return annotation as the LightningModule
        # expects a pytorch DataLoader, and we returnPyTorchBitfountDataLoader
        return self.validation_dl

    def test_dataloader(self) -> Optional[BitfountDataLoader]:  # type: ignore[override] # Reason: see below  # noqa: B950
        """Returns test dataloader."""
        # We override the dataloader return annotation as the LightningModule
        # expects a pytorch DataLoader, and we return PyTorchBitfountDataLoader
        return self.test_dl

    def _expect_keys(
        self, dataloaders: Optional[Union[List[BitfountDataLoader], List[DataLoader]]]
    ) -> bool:
        """Should data keys be expected in entries from target dataloader.

        Args:
            dataloaders: A list of Pytorch/Bitfount dataloaders. This should be a
                single-element list, `Optional` and longer lists are provided only
                to enable compatibility with the PyTorch Lightning return types.

        Returns:
            bool: True if data keys are expected in entries, False otherwise.

        Raises:
            TypeError: If no dataloader is provided.
            TypeError: If the number of dataloaders provided is not 1.
        """
        if dataloaders is None:
            raise TypeError(
                "Expected list of PyTorch or Bitfount dataloaders; got `None`"
            )
        if len(dataloaders) != 1:
            raise TypeError(
                f"Expected exactly one PyTorch or Bitfount dataloader;"
                f" got {len(dataloaders)}"
            )

        dataloader = dataloaders[0]

        return (
            isinstance(dataloader, _BasePyTorchBitfountDataLoader)
            and dataloader.expect_key_in_iter()
        )

    def serialize(self, filename: Union[str, os.PathLike]) -> None:
        """Serialize model to file with provided `filename`.

        Args:
            filename: Path to file to save serialized model.
        """
        if not self._initialised:
            logger.info("Model not yet initialised. Auto-initialising model.")
            self.initialise_model()
        # Model has been initialised, assuring mypy of this
        assert self._model is not None  # nosec assert_used
        torch.save(self._model.state_dict(), filename)

    def deserialize(
        self,
        content: Union[str, os.PathLike, bytes],
        weights_only: bool = True,
        **kwargs: Any,
    ) -> None:
        """Deserialize model.

        :::danger

        If `weights_only` is set to False, this should not be used on a model file that
        has been received across a trust boundary due to underlying use of `pickle` by
        `torch`.

        :::

        Args:
            content: Path to file containing serialized model.
            weights_only: Whether to load only the weights or the entire model.
            **kwargs: Additional keyword arguments to pass to `torch.load`.
        """
        kwargs.update({"weights_only": weights_only})
        if not self._initialised:
            logger.info("Model not yet initialised. Auto-initialising model.")
            self.initialise_model()
        # Model has been initialised, assuring mypy of this
        assert self._model is not None  # nosec assert_used
        load_contents = BytesIO(content) if isinstance(content, bytes) else content
        self._model.load_state_dict(enhanced_torch_load(load_contents, **kwargs))

    @staticmethod
    def _get_layer_sizes(
        layers: List[int], input_size: int
    ) -> Tuple[Tuple[int, int], ...]:
        """Converts layer sizes to in a tuple of # in and out parameters."""
        layer_sizes = []
        for idx, size in enumerate(layers):
            if idx == 0:
                layer_sizes.append((input_size, size))
            else:
                layer_sizes.append((layers[idx - 1], size))

        return tuple(layer_sizes)

    def _get_loss(
        self,
        output: torch.Tensor,
        target: torch.Tensor,
        loss_modifiers: Tuple[torch.Tensor, ...],
    ) -> Tensor:
        """Computes the appropriate (weighted) loss.

        Args:
            output: The model output.
            target: The expected output.
            loss_modifiers: A tuple of tensors representing additional loss modifiers:
                - 0: weightings for each sample in this batch
                - 1: categories

        Returns:
            A scalar tensor representing the loss.
        """
        sample_weight: torch.Tensor = loss_modifiers[0]
        categories: torch.Tensor = loss_modifiers[1]
        criterion = cast(Callable, self.loss_func)(reduction="none")
        # Handle categorical classification
        output = self._handle_categories_or_tuple(output, categories)

        if self.loss_func == nn.CrossEntropyLoss:
            loss: torch.Tensor = criterion(output, target.long())
        elif self.loss_func == nn.BCEWithLogitsLoss:
            loss = criterion(output, target.type_as(output))
            loss = loss.mean(dim=1)
        else:
            raise ValueError(
                f"Loss function {type(self.loss_func).__name__} is unsupported."
            )

        # Calculate weighted mean loss
        loss = loss * sample_weight.squeeze() / sample_weight.squeeze().sum()
        loss = loss.sum()

        return loss

    @staticmethod
    def _handle_categories_or_tuple(
        output: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
        categories: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Handles conversion of output if categorical or tensor."""
        if categories is not None:
            # get output corresponding to right head depending on label
            categories = categories.unsqueeze(dim=1)
            output_to_stack: Tuple[Tensor, ...]
            if not isinstance(output, tuple):
                output_to_stack = (output,)
            else:
                output_to_stack = output
            stacked_output = torch.stack(output_to_stack, 1)
            categories = categories.expand_as(stacked_output)
            output = stacked_output.gather(1, categories)[:, 1]
        # Handle tuple output
        elif isinstance(output, tuple):
            output = output[0]
        return output

    def _compute_training_metrics(
        self,
        outputs: np.ndarray,
        targets: np.ndarray,
        training_metrics: Optional[MutableMapping[str, Metric]] = None,
    ) -> Dict[str, str]:
        """Computes metrics to be printed whilst training."""
        m = MetricCollection.create_from_model(self, training_metrics)
        results = m.compute(targets, outputs, threshold=0.5)
        # If using MPS, we need to cast the results to
        # float32 to be compatible with MPS
        # https://github.com/facebookresearch/segment-anything/issues/94
        if has_mps():
            for k, v in results.items():
                results[k] = np.float32(v)  # type: ignore[assignment] # Reason: see above # noqa: B950
        self.log_dict(results, on_epoch=True, logger=True)
        results_with_str_values: Dict[str, str] = {}
        for k, v in results.items():
            results_with_str_values[k] = str(v)
        return results_with_str_values

    def configure_optimizers(
        self,
    ) -> Union[_OptimizerType, Tuple[List[_OptimizerType], List[_LRScheduler]]]:
        """Configures the optimizer(s) and scheduler(s) for backpropagation.

        Returns:
            Either the optimizer of your choice or a tuple of optimizers and learning
            rate schedulers.
        """
        parameters = filter(lambda p: p.requires_grad, self.parameters())
        optimizer: _OptimizerType = self._opt_func(parameters)

        # Attach PrivacyEngine if present
        if self._dp_engine:
            if not self._dp_config:
                raise ValueError(
                    "DP Engine created but no configuration could be found."
                )

            if isinstance(self.train_dl, PyTorchBitfountDataLoader):
                dataloader = self.train_dl.dataloader
            elif isinstance(self.train_dl, PyTorchIterableBitfountDataLoader):
                # TODO: [BIT-1685] We are using a custom dataloader which is not what
                # opacus expects so we need to have a workaround for this `make_private`
                # method call. We likely do not even need to replace the dataloader
                # anyway so if possible we should make the model and optimizer private
                # individually.
                dataloader = self.train_dl  # type: ignore[assignment] # Reason: See above # noqa: B950

            # Create DP-sensitive (model, optimizer, dataloader)
            if not self._model:
                raise ValueError("Model uninitialized")
            dp_model, dp_optimizer, dp_dataloader = self._dp_engine.make_private(
                module=self._model,
                optimizer=optimizer,
                data_loader=dataloader,
                # If self._dp_engine exists then self._noise_multiplier will
                # also have been set, and this method is only used on the worker.
                noise_multiplier=cast(float, self._noise_multiplier),
                max_grad_norm=self._dp_config.max_grad_norm,
                loss_reduction=self._dp_config.loss_reduction,
                # TODO: [BIT-1474] Identify what changes are needed to enable
                #       poisson_sampling=True.
                poisson_sampling=False,
            )

            logger.info("Replacing model with DP-sensitive version.")
            self._model = dp_model

            # TODO: [BIT-1685] Confirm that we don't need to replace the dataloader if
            # it is iterable
            if isinstance(self.train_dl, PyTorchBitfountDataLoader):
                logger.info("Replacing dataloader with DP-sensitive version.")
                self.train_dl.dataloader = dp_dataloader

            optimizer = dp_optimizer
        if self._scheduler_func:
            scheduler = self._scheduler_func(optimizer)
            return [optimizer], [scheduler]

        return optimizer

    def forward(self, x: Union[ImgFwdTypes, TabFwdTypes]) -> Any:
        """Performs a forward pass of the underlying model.

        Args:
            x: Input to the model.

        Returns:
            Output of the model.

        """
        return self._model(x)  # type: ignore[misc] # reason: the model is set by this stage # noqa: B950

    def _skip_training_batch(self, batch_idx: int) -> bool:
        """Checks if the current batch from the training set should be skipped.

        This is a workaround for the fact that PyTorch Lightning starts the Dataloader
        iteration from the beginning every time `fit` is called. This means that if we
        are training in steps, we are always training on the same batches. So this
        method needs to be called at the beginning of every `training_step` to skip
        to the right batch index.

        Args:
            batch_idx: the index of the batch from `training_step`.

        Returns:
            True if the batch should be skipped, otherwise False.
        """
        # TODO: [BIT-1237] remove this code block and find a better way to do this that
        # doesn't involve loading every batch into memory until we get to the right one
        if self.steps:
            # If we have trained on the previous batch, we can avoid the checks because
            # it means we have already reached the target start batch.
            if not self._trained_on_previous_batch:
                if (self.steps != self._pl_trainer.max_steps) and (
                    batch_idx < (self._total_num_batches_trained % len(self.train_dl))
                ):
                    return True
                else:
                    self._trained_on_previous_batch = True

            # `_total_num_batches_trained` hasn't been incremented yet so we need to add
            # 1 here to get the correct batch number.
            if self._total_num_batches_trained + 1 == self._pl_trainer.max_steps:
                self._trained_on_previous_batch = False

        if not self._pl_trainer.sanity_checking:
            self._total_num_batches_trained += 1

        return False

    def training_step(  # type: ignore[override] # Reason: see below
        self,
        batch: Union[
            Tuple[Union[ImgXorTabBatch, ImgAndTabBatch], torch.Tensor],
            Tuple[Union[ImgXorTabBatch, ImgAndTabBatch], torch.Tensor, Sequence[str]],
        ],
        batch_idx: int,
    ) -> Optional[torch.Tensor]:
        """Training step.

        Args:
            batch: The batch to be trained on.
            batch_idx: The index of the batch to be trained on from the train
                dataloader.

        Returns:
            The loss from this batch as a `torch.Tensor`.
        """
        # Override the pl.lightning method, as it requires *args
        # and **kwargs as arguments whereas we will always have
        # the batch and the batch_idx as args.
        # `data` contains the X batch and often some additional information.
        # This can be split into relevant chunks by the `split_dataloader_output()`
        # method, which details how to perform that split.
        if self.param_clipping:
            # Make sure that the parameters stay within required bounds
            # for SecureAggregation
            clipper = _PytorchParamConstraint(**cast(dict, self.param_clipping))
            # If we are in this check, self.param_clipping is
            # a dictionary so it is safe to cast

            # Check for BatchNorm modules
            modules_to_clip = [
                mod_name
                for mod_name, modules in self._model._modules.items()  # type: ignore[union-attr] # Reason: _model is initialized before training  # noqa: B950
                if "BatchNorm" in str(modules)
            ]
            # Apply the parameter contraint to all batch norm modules
            for mod in modules_to_clip:
                self._model._modules[mod].apply(clipper)  # type: ignore[union-attr] # Reason: _model is initialized before training  # noqa: B950

        if self._skip_training_batch(batch_idx):
            # Returning `None` to skip this batch
            return None

        data, y = batch[:2]

        x, *loss_modifiers = self._split_dataloader_output(data)
        # Perform forward pass and get loss
        y_hat = self(x)
        loss = self._get_loss(
            output=y_hat,
            target=y,
            loss_modifiers=cast(Tuple[torch.Tensor, ...], loss_modifiers),
        )
        self.log(
            "train_loss", loss, on_step=True, on_epoch=True, prog_bar=True, logger=True
        )
        if self._dp_engine and self._dp_config:
            # Calculate current epsilon level
            epsilon = self._dp_engine.get_epsilon(self._dp_config.delta)

            # Log current epsilon level
            self.log("epsilon", epsilon, prog_bar=True, logger=True)

        return loss

    def training_epoch_end(self, kwargs: Any) -> None:
        """Extract gradient from weights after training."""
        if self.param_clipping:
            # Make sure that the parameters stay within required bounds
            # for SecureAggregation
            clipper = _PytorchParamConstraint(**cast(dict, self.param_clipping))
            # If we are in this check, self.param_clipping
            # is a dictionary so it is safe to cast

            # Check for BatchNorm modules
            modules_to_clip = [
                mod_name
                for mod_name, modules in self._model._modules.items()  # type: ignore[union-attr] # Reason: _model is initialized before training  # noqa: B950
                if "BatchNorm" in str(modules)
            ]
            # Apply the parameter contraint to all batch norm modules
            for mod in modules_to_clip:
                self._model._modules[mod].apply(  # type: ignore[union-attr] # Reason: _model is initialized before training  # noqa: B950
                    clipper
                )

        try:
            # For now, this will fail for the resnet model since it is defined with
            # no layers, so wrapping in a try...except.
            self._training_epoch_end_gradients = [
                layer.weight.grad.detach().clone()
                for layer in self._model.layers  # type: ignore[union-attr] # Reason: _model is initialized before training  # noqa: B950
            ]
        except AttributeError:
            pass

    def _roll_back_model_weights(self, state_dict: OrderedDict[str, Tensor]) -> None:
        """Rolls back model weights to the most recent weights available."""
        if not self._model_weights_rolled_back and self._model is not None:
            logger.warning(
                "Rolling back model weights to before privacy guarantee was exceeded."
            )
            # We don't use the `load_from_checkpoint` method because we want to only
            # load the state dictionary from the checkpoint
            self.load_state_dict(state_dict)
            self._model_weights_rolled_back = True
        elif self._model_weights_rolled_back:
            logger.debug("Ignoring state dictionary. Model weights already rolled back")
        else:
            logger.warning("Uninitialised model. Unable to roll back weights.")

    def on_save_checkpoint(self, checkpoint: _StrAnyDict) -> None:
        """Hook that runs prior to saving a model checkpoint.

        This is used to roll back the model weights in the event the privacy guarantee
        has been exceeded prior to overwriting the checkpoint.
        """
        if self._is_privacy_guarantee_exceeded():
            try:
                # `log_dir` attribute is present on the pytorch lightning logger and
                # documented but mypy is unaware for some reason.
                previous_state_dict = enhanced_torch_load(
                    f"{self._pl_trainer.logger.log_dir}/checkpoints/last.ckpt"  # type: ignore[union-attr] # Reason: see above # noqa: B950
                )["state_dict"]
            except FileNotFoundError:
                # This will likely be the case when the limit is exceeded on
                # the first batch
                logger.debug(
                    f"Could not find file {self._pl_trainer.logger.log_dir}/checkpoints/last.ckpt"  # type: ignore[union-attr] # Reason: see above # noqa: B950
                )
                logger.warning(
                    "No checkpoint available to roll back model weights. "
                    "Re-initialising model."
                )
                self._pl_trainer.should_stop = True
                self.initialise_model(data=self._datasource, context=TaskContext.WORKER)
                checkpoint["state_dict"] = self.state_dict()
                self._model_weights_rolled_back = True
            else:
                checkpoint["state_dict"] = previous_state_dict
                self._roll_back_model_weights(previous_state_dict)
                self._pl_trainer.should_stop = True

    def on_train_batch_start(
        self,
        batch: _SingleOrMulti[_SingleOrMulti[np.ndarray]],
        batch_idx: int,
    ) -> Optional[Literal[-1]]:
        """Checks if any privacy guarantees have been exceeded and stops training if so.

        Args:
            batch: The batch to be trained on.
            batch_idx: The index of the batch to be trained on from the train
                dataloader.

        Returns:
            -1 if the entire epoch should be skipped, otherwise None.
        """
        # Check privacy constraints and set stopping criterion as needed
        if self._is_privacy_guarantee_exceeded():
            # This skips training for the rest of the current epoch
            # and only works in the `on_train_batch_start` hook
            return -1

        return None

    def validation_step(
        self,
        batch: Union[
            Tuple[Union[ImgXorTabBatch, ImgAndTabBatch], torch.Tensor],
            Tuple[Union[ImgXorTabBatch, ImgAndTabBatch], torch.Tensor, Sequence[str]],
        ],
        batch_idx: int,
    ) -> Dict[str, Tensor]:
        """Validation step.

        Args:
            batch: The batch to be evaluated.
            batch_idx: The index of the batch to be evaluated from the validation
                dataloader.

        Returns:
            A dictionary of strings and values that should be averaged at the end of
            every epoch and logged e.g. `{"validation_loss": loss}`. These will be
            passed to the `validation_epoch_end` method.
        """
        # Extract X, y and other data from batch
        data, y = batch[:2]

        x, *loss_modifiers = self._split_dataloader_output(data)

        # Get validation output and loss
        y_hat = self(x)
        loss = self._get_loss(
            output=y_hat,
            target=y,
            loss_modifiers=cast(Tuple[torch.Tensor, ...], loss_modifiers),
        )
        # Handle categorical data
        categories = loss_modifiers[-1]
        y_hat = self._handle_categories_or_tuple(y_hat, categories)

        y_hat = self._do_output_activation(y_hat)

        # Log and return desired outputs
        self.log("validation_loss", loss, on_epoch=True, prog_bar=True, logger=True)
        return {"validation_loss": loss, "outputs": y_hat, "targets": y}

    def validation_epoch_end(  # type: ignore[override] # Reason: see below
        self, outputs: List[Dict[str, Tensor]]
    ) -> None:
        """Called at the end of the validation epoch with all validation step outputs.

        Ensures that the average metrics from a validation epoch is stored. Logs results
        and also appends to `self.val_stats`.

        Args:
            outputs: List of outputs from each validation step.
        """
        # Override the pl.lightning method, as it requires a different type for outputs.

        # Merge outputs into singular lists rather than a list of dicts.
        # NOTE: This also _flattens_ the non-scalar outputs (such as `outputs` and
        # `targets`) such that a list (of len Z) MxN tensors becomes a list
        # (of len ZxM) (N,) tensors
        merged_outputs: Dict[str, List[torch.Tensor]] = _merge_list_of_dicts(outputs)

        # Check that `outputs` and `targets` of the merged outputs have the same
        # length (`validation_loss` will likely not have the same length as that is a
        # single entry per batch rather than per row)
        if (outputs_len := len(merged_outputs["outputs"])) != (
            targets_len := len(merged_outputs["targets"])
        ):
            raise ValueError(
                f"Mismatch in number of validation outputs vs validation targets;"
                f" got {outputs_len} outputs and {targets_len} targets."
            )

        # Calculate metrics from outputs. This will also log them out to self.log().
        if not self._pl_trainer.sanity_checking:
            validation_metrics = self._compute_training_metrics(
                outputs=np.asarray(
                    [i.cpu().numpy() for i in merged_outputs["outputs"]]
                ),
                targets=np.asarray(
                    [i.cpu().numpy() for i in merged_outputs["targets"]]
                ),
                training_metrics=self.metrics,
            )
            # Calculate average validation loss and add to validation metrics dictionary
            avg_val_loss = torch.mean(torch.stack(merged_outputs["validation_loss"]))
            validation_metrics["validation_loss"] = f"{avg_val_loss.item():.4f}"
            self._validation_results.append(validation_metrics)

    def test_step(
        self,
        batch: Union[
            Tuple[Union[ImgXorTabBatch, ImgAndTabBatch], torch.Tensor],
            Tuple[Union[ImgXorTabBatch, ImgAndTabBatch], torch.Tensor, Sequence[str]],
        ],
        batch_idx: int,
    ) -> _StrAnyDict:
        """Make sure to set self.preds and self.target before returning in this method.

        They will be returned by the `evaluate` method.

        Args:
            batch: The batch to be evaluated.
            batch_idx: The index of the batch to be evaluated from the test
                dataloader.

        Returns:
            A dictionary of predictions and targets. These will be passed to the
            `test_epoch_end` method.
        """
        # Extract X, y and other data from batch
        data, y = batch[:2]

        # If the data provides data keys, extract those as well
        keys: Optional[List[str]] = None
        if self._expect_keys(self.trainer.test_dataloaders):
            batch = cast(
                Tuple[
                    Union[ImgXorTabBatch, ImgAndTabBatch], torch.Tensor, Sequence[str]
                ],
                batch,
            )
            keys = list(batch[2])

        x, *loss_modifiers = self._split_dataloader_output(data)

        # Get validation output and loss
        y_hat = self(x)

        # Handle categorical or tuple output
        categories = loss_modifiers[-1]
        y_hat = self._handle_categories_or_tuple(y_hat, categories)

        y_hat = self._do_output_activation(y_hat)

        # Output targets and prediction for later
        if keys is not None:
            return {"predictions": y_hat, "targets": y, "keys": keys}
        else:
            return {"predictions": y_hat, "targets": y}

    def test_epoch_end(self, outputs: List[Dict[str, Union[torch.Tensor, List[str]]]]) -> None:  # type: ignore[override] # Reason: see below # noqa: B950
        """Aggregates the predictions and targets from the test set.

        Args:
            outputs: List of outputs from each test step.
        """
        # Override the pl.lightning method, as it requires a different type for outputs.

        # Merge outputs into singular lists rather than a list of dicts.
        # NOTE: This also _flattens_ the non-scalar outputs (such as `outputs` and
        # `targets`) such that a list (of len Z) MxN tensors becomes a list
        # (of len ZxM) (N,) tensors
        merged_outputs: Dict[str, List[Union[torch.Tensor, str]]] = (
            _merge_list_of_dicts(outputs)
        )

        self._test_preds = [
            i.cpu().numpy()
            for i in cast(List[torch.Tensor], merged_outputs["predictions"])
        ]
        self._test_targets = [
            i.cpu().numpy() for i in cast(List[torch.Tensor], merged_outputs["targets"])
        ]

        if self._expect_keys(self.trainer.test_dataloaders):
            self._test_keys = cast(List[str], merged_outputs["keys"])

            # If keys are expected, there should be the same number as the number of
            # predictions
            if (predictions_len := len(merged_outputs["predictions"])) != (
                keys_len := len(merged_outputs["keys"])
            ):
                raise ValueError(
                    f"Mismatch in number of predictions vs data keys;"
                    f" got {predictions_len} predictions and {keys_len} keys."
                )

    def _fit_local(
        self,
        data: BaseSource,
        metrics: Optional[MutableMapping[str, Metric]] = None,
        **kwargs: Any,
    ) -> Dict[str, str]:
        """Fits the model.

        Args:
            data: The data source to be used for training the model.
            metrics: Validation metrics to print during training. Defaults to None and
                will instead use metrics appropriate to the task. Optional.

        Returns:
            Validation metrics for the final epoch
        """
        # Check model initialisation
        if self._initialised:
            logger.debug("Model already initialised, will not reinitialise.")
        else:
            logger.info("Model not yet initialised. Auto-initialising model.")
            self.initialise_model(data)

        # TODO: [BIT-499] Check DP privacy guarantees before we even start; return NULL
        #       state if exceeded.
        self._validation_results = []
        with self._use_metrics(metrics), self._use_datasource(data):
            # will perform self.epochs or self.steps of local training
            self._pl_trainer.fit(self)

            # If training has been specified in terms of epochs, we are guaranteed to
            # have run validation after training. However if training is specified in
            # terms of steps, we only would have run validation after training if the
            # the number of steps is the same as that in an epoch. Therefore we must
            # manually run validation to ensure we have the latest validation metrics
            # that reflect the state of the model at the end of training.
            if self.steps and self.steps % len(self.train_dl) != 0:
                self._pl_trainer.validate(self)

        try:
            # Getting the most recent set of validation metrics
            validation_results = self._validation_results[-1]
        except IndexError:
            # If we haven't had a full epoch of training, then we don't have any
            # validation results in the dictionary so we must create an empty one.
            # This is required if training is run with steps or epochs set to 0.
            validation_results = {}

        # Add DP metrics to the final epoch validation results
        if self._dp_engine:
            if not self._dp_config:
                raise ValueError(
                    "DP Engine created but no configuration could be found."
                )

            epsilon, alpha = cast(
                RDPAccountant, self._dp_engine.accountant
            ).get_privacy_spent(
                delta=self._dp_config.delta, alphas=self._dp_config.alphas
            )
            validation_results["alpha"] = str(alpha)
            validation_results["epsilon"] = str(epsilon)

        # Return the validation metrics for the final epoch
        return validation_results

    @contextlib.contextmanager
    def _use_datasource(self, datasource: BaseSource) -> Iterator[None]:
        """Context manager which temporarily sets `datasource` to `self._datasource`.

        Args:
            data: Datasource provided to fit method.

        Returns:
            Empty Iterator.
        """
        self._datasource = datasource
        try:
            yield None
        finally:
            self._datasource = None

    @contextlib.contextmanager
    def _use_metrics(
        self, metrics: Optional[MutableMapping[str, Metric]] = None
    ) -> Iterator[None]:
        """Context manager which temporarily sets `metrics` to `self.metrics`.

        Args:
            metrics: Validation metrics to print during training. Defaults to None and
                will instead use metrics appropriate to the task. Optional.

        Returns:
            Empty Iterator.
        """
        metrics_store: Optional[MutableMapping[str, Metric]] = None
        # Stash the old metrics if new ones provided
        if metrics:
            metrics_store = self.metrics
            self.metrics = metrics
        try:
            yield None
        finally:
            # Restore the old metrics if new ones were provided
            if metrics:
                self.metrics = metrics_store

    def _evaluate_local(
        self, test_dl: Optional[BitfountDataLoader] = None, **kwargs: Any
    ) -> EvaluateReturnType:
        """This method runs inference on the test dataloader.

        This is done by calling `self.test_step` under the hood.
        Args:
            test_dl: Optional dataloader to run inference on which takes precedence over
                the dataloader returned by `self.test_dataloader`.

        Returns:
            A tuple of predictions and targets as numpy arrays.
        """
        # Reset metrics
        self._reset_test_attrs()

        self._pl_trainer.test(model=self, dataloaders=cast(DataLoader, test_dl))

        return EvaluateReturnType(
            preds=np.asarray(self._test_preds),
            targs=np.asarray(self._test_targets),
            keys=self._test_keys,
        )

    def _predict_local(self, data: BaseSource, **kwargs: Any) -> PredictReturnType:
        """This method runs inference on the test data, returns predictions.

        This is done by calling `test_step` under the hood. Customise this method as you
        please but it must return a list of predictions and a list of targets. Note that
        as this is the prediction function, only the predictions are returned.

        Returns:
            A numpy array containing the prediction values.
        """
        if data is not None:
            data.load_data()
            if not hasattr(self, "databunch"):
                self._add_datasource_to_schema(data)  # Also sets `self.databunch
            if not self.databunch:
                self._add_datasource_to_schema(data)  # Also sets `self.databunch
            test_dl = self.databunch.get_test_dataloader(self.batch_size)
            if isinstance(test_dl, BitfountDataLoader):
                logger.info(
                    f"Using test portion of dataset for inference - this has "
                    f"{len(test_dl.dataset)} record(s)."
                )
            else:
                raise ValueError("No test data to infer in the provided datasource.")

        self._pl_trainer.test(model=self, dataloaders=cast(DataLoader, test_dl))

        # Reassuring mypy that `self._test_preds` cannot be None at this point
        assert self._test_preds is not None  # nosec assert_used
        return PredictReturnType(preds=self._test_preds, keys=self._test_keys)

    def _reset_test_attrs(self) -> None:
        """Resets test attributes to None."""
        self._test_preds = None
        self._test_targets = None
        self._test_keys = None


@delegates()
class BaseTabNetModel(
    _PyTorchDistributedModelMixIn, _PyTorchNeuralNetworkMixIn, _BaseModel
):
    """TabNet Model as described in https://arxiv.org/abs/1908.07442.

    This is a wrapper around the implementation from DreamQuark. Documentation can be
    found here: https://dreamquark-ai.github.io/tabnet.

    Args:
        virtual_batch_size: Virtual batch size used for ghost batch
            normalization.
        patience: Number of epochs before early stopping.
        scheduler: Learning rate scheduler. Defaults to None.
        scheduler_params: Learning rate scheduler params. Defaults to None.
        embedding_sizes: Embeddings sizes. Defaults to None.
        num_workers: Number of workers for torch DataLoader. Defaults to 0.
        inverse_class_weights: Inverse class weights (only for classification problems).
            Defaults to True.
        mask_type: Mask type. Defaults to "sparsemax".
        decision_prediction_layer_size: Final feedforward layer size. Defaults to 8.
        attention_embedding_layer_size: Attention embedding layer size. Defaults to 8.
        num_steps: Number of steps. Defaults to 3.


    Raises:
        ValueError: If virtual batch size > batch size.
        ValueError: If the `model_structure` does not match the TabNet model.
        ValueError: If training is specified in `steps` rather than `epochs`. Training
            steps are not supported.
    """

    train_dl: _BasePyTorchBitfountDataLoader
    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "virtual_batch_size": fields.Integer(),
        "patience": fields.Integer(),
        "embedding_sizes": fields.Integer(allow_none=True),
        "num_workers": fields.Integer(),
        "inverse_class_weights": fields.Bool(),
        "mask_type": fields.String(),
        "decision_prediction_layer_size": fields.Integer(),
        "attention_embedding_layer_size": fields.Integer(),
        "num_steps": fields.Integer(),
    }

    def __init__(
        self,
        virtual_batch_size: int = 64,
        patience: int = 2,
        embedding_sizes: Optional[Union[int, List[int]]] = None,
        num_workers: int = 0,
        inverse_class_weights: bool = True,
        mask_type: str = "sparsemax",
        decision_prediction_layer_size: int = 8,
        attention_embedding_layer_size: int = 8,
        num_steps: int = 3,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        if self.steps:
            raise ValueError(
                "TabNet does not support steps. Training must be specified in epochs."
            )

        if virtual_batch_size > self.batch_size:
            raise ValueError("Virtual batch size must be smaller than batch size.")

        if (
            not isinstance(self.model_structure, NeuralNetworkPredefinedModel)
            or self.model_structure.name != "TabNet"
        ):
            raise ValueError(
                "Please provide the appropriate Model Structure.",
                "TabNet model can only create TabNet models.",
            )

        self.virtual_batch_size = virtual_batch_size
        self.patience = patience
        if not self.scheduler:
            self.scheduler = Scheduler("StepLR", {"step_size": 50, "gamma": 0.9})
        self.embedding_sizes = embedding_sizes
        self.num_workers = num_workers
        self.inverse_class_weights = inverse_class_weights
        self.mask_type = mask_type
        self.decision_prediction_layer_size = decision_prediction_layer_size
        self.attention_embedding_layer_size = attention_embedding_layer_size
        self.num_steps = num_steps

        # This is unused by the TabNet model but is required for compatibility with
        # DistributedModelProtocol
        self._total_num_batches_trained: int = 0

        # TODO: [BIT-1152] support FederatedAveraging by fixing initialisation
        logger.warning("TabNet model currently does not support FederatedAveraging.")

    @abstractmethod
    def _create_model(self) -> BaseEstimator:
        """Returns appropriate model."""
        raise NotImplementedError

    def get_param_states(self) -> Dict[str, _TensorLike]:
        """See base class."""
        aux = dict(self._model.network.state_dict())  # type: ignore[union-attr] # Reason: _model is initialised in subclass # noqa: B950

        return {key: _AdaptorForPyTorchTensor(value) for key, value in aux.items()}

    def initialise_model(
        self,
        data: Optional[BaseSource] = None,
        context: Optional[TaskContext] = None,
    ) -> None:
        """Any initialisation of models/dataloaders to be done here.

        Initialises the dataloaders and sets `self._model` to be the output from
        `self.create_model`. Any initialisation ahead of federated or local training,
        serialization or deserialization should be done here.

        Args:
            data: The datasource for model training. Defaults to None.
            context: Indicates if the model is running as a modeller or worker.
                If None, there is no difference between modeller and worker.
        """
        self._context = context
        self._initialised = True
        if self._context == TaskContext.MODELLER:
            # In a distributed setting, the Modeller needs to first initialise its
            # own model before it can be used. The pod identifier needs to be set
            # before the model is initialised so the relevant details can be
            # retrieved from the schema. For this we just use the first pod
            # identifier specified in the datastructure as it is assumed the
            # schemas for all the Pods are the same.
            pod_identifiers = self.datastructure.get_pod_identifiers()
            if pod_identifiers:
                self.set_datastructure_identifier(pod_identifiers[0])

        if data is not None:
            if self.datastructure.query:
                table_schema = self.datastructure._override_schema(
                    data_identifier=self._datastructure_identifier
                )
                self.databunch = BitfountDataBunch(
                    data_structure=self.datastructure,
                    schema=table_schema,
                    datasource=data,
                )
            elif self.datastructure.table:
                if context:
                    table_schema = self.schema.get_table_schema(
                        self.datastructure.get_table_name(
                            self._datastructure_identifier
                        )
                    )
                    self.databunch = BitfountDataBunch(
                        data_structure=self.datastructure,
                        schema=table_schema,
                        datasource=data,
                    )
                else:
                    # For local training, we can add the datasource to the schema.
                    data.load_data()
                    self._add_datasource_to_schema(data)

        # TODO: [BIT-1152] initialise model without setting dataloaders
        if self._context != TaskContext.MODELLER:
            self._set_dataloaders(batch_size=self.batch_size)

        self._model = self._create_model()
        # Make sure we only use the tabular part of the data.
        train_x_df_aux = self.train_dl.get_x_dataframe()
        if isinstance(train_x_df_aux, tuple):
            train_x_df, _ = train_x_df_aux
            train_x_df = train_x_df
        else:
            train_x_df = train_x_df_aux

        # Check that a target exists as needed for dataframe indexing below
        # This needs to be _fairly_ lazily checked as databunch may not be set
        # earlier in this method.
        target = self.databunch.target
        if target is None:
            raise ValueError(
                f"No `target` specified in databunch, needed for model evaluation"
                f" and DataFrame indexing in {self.__class__.__name__}"
            )

        # 'Train' with 0 epochs just to set model parameters
        self._model.fit(  # type: ignore[attr-defined] # reason: the model should be set by the time we fit it # noqa: B950
            train_x_df.values,
            self.train_dl.get_y_dataframe()[target].values,
            max_epochs=0,
            virtual_batch_size=self.virtual_batch_size,
            num_workers=self.num_workers,
            weights=int(self.inverse_class_weights),
            drop_last=False,
        )

    def _evaluate_local(
        self, test_dl: Optional[BitfountDataLoader] = None, **kwargs: Any
    ) -> EvaluateReturnType:
        """This method runs inference on the test dataloader.

        This is done by calling `self.test_step` under the hood.
        Args:
            test_dl: Optional dataloader to run inference on which takes precedence over
                the dataloader returned by `self.test_dataloader`.

        Returns:
            A tuple of predictions and targets as numpy arrays.
        """
        # Check that a target exists as needed for dataframe indexing below
        target = self.databunch.target
        if target is None:
            raise ValueError(
                f"No `target` specified in databunch, needed for model evaluation"
                f" and DataFrame indexing in {self.__class__.__name__}"
            )

        if test_dl is None:
            if isinstance(self.test_dl, BitfountDataLoader):
                test_dl = self.test_dl
            else:
                raise ValueError("There is no test data to evaluate the model on.")
        X_aux = test_dl.get_x_dataframe()
        X: pd.DataFrame
        if isinstance(X_aux, tuple):
            X, _ = X_aux
        elif isinstance(X_aux, pd.DataFrame):
            X = X_aux

        # Cast as .values can return custom array types
        Y: np.ndarray = cast(np.ndarray, test_dl.get_y_dataframe()[target].values)

        preds: np.ndarray = (
            self._model.predict_proba(  # type:ignore[union-attr] # reason: the model should be set by the time we evaluate this function # noqa: B950
                X.values
            )
        )

        return EvaluateReturnType(preds, Y)

    def serialize(self, filename: Union[str, os.PathLike]) -> None:
        """Serialize model to file with provided `filename`.

        Args:
            filename: Path to file to save serialized model.
        """
        if not self._initialised:
            # TODO: [BIT-1152] initialise model here instead of logging an error
            logger.error(
                "Can't serialize uninitialized model. "
                "Model can't be initialised without data."
            )
            return
        torch.save(self._model.network.state_dict(), filename)  # type: ignore[union-attr] # reason: model is initialised # noqa: B950

    def deserialize(
        self,
        content: Union[str, os.PathLike, bytes],
        weights_only: bool = True,
        **kwargs: Any,
    ) -> None:
        """Deserialize model.

        :::danger

        If `weights_only` is set to False, this should not be used on a model file that
        has been received across a trust boundary due to underlying use of `pickle` by
        `torch`.
        :::

        Args:
            content: Bytestream or path to file containing serialized model.
            weights_only: If True, only the weights of the model will be loaded.
            **kwargs: Keyword arguments provided to `torch.load` under the hood.
        """
        kwargs.update({"weights_only": weights_only})
        if not self._initialised:
            # TODO: [BIT-1152] initialise model here instead of logging an error
            logger.error(
                "Can't deserialize uninitialized model. "
                "Model can't be initialised without data."
            )
            return
        load_contents = BytesIO(content) if isinstance(content, bytes) else content
        self._model.network.load_state_dict(enhanced_torch_load(load_contents, **kwargs))  # type: ignore[union-attr] # reason: model is initialised # noqa: B950

    def _fit_local(
        self,
        data: BaseSource,
        metrics: Optional[Union[str, List[str], MutableMapping[str, Metric]]] = None,
        **kwargs: Any,
    ) -> Dict[str, str]:
        """Fit model and return results.

        Args:
            data: The data used for model training.
            metrics: list of metrics
                to use on validation set every epoch. Last metric in this list is the
                one to use for early stopping
        """
        if self._initialised:
            logger.debug("Model already initialised, will not reinitialise.")
        else:
            logger.info("Model not yet initialised. Auto-initialising model.")
            self.initialise_model(data=data)

        # Check that a target exists as needed for dataframe indexing below
        target = self.databunch.target
        if target is None:
            raise ValueError(
                f"No `target` specified in databunch, needed for model fit"
                f" and DataFrame indexing in {self.__class__.__name__}"
            )

        if metrics is None:
            metrics = ["logloss"]
        elif isinstance(metrics, str):
            metrics = [metrics]
        elif isinstance(metrics, MutableMapping):
            logger.warning(
                "TabNet models are incompatible with bitfount Metric objects;"
                " will derive TabNet Metric objects using supplied names."
            )
            metrics = [k for k in metrics.keys()]

        if "logloss" not in metrics:
            metrics.insert(0, "logloss")

        # Make sure we only use the tabular part of the data.
        train_x_df_aux = self.train_dl.get_x_dataframe()
        if isinstance(train_x_df_aux, tuple):
            train_x_df, _ = train_x_df_aux
            train_x_df = train_x_df
        else:
            train_x_df = train_x_df_aux

        if not isinstance(self.validation_dl, BitfountDataLoader):
            empty_df = pd.DataFrame(columns=train_x_df.columns)
            self.validation_dl = BitfountDataLoader(
                _BitfountDataset(
                    datasource=DataFrameSource(empty_df),
                    target=target,
                    selected_cols_semantic_types=self.datastructure.selected_cols_w_types,  # noqa: B950
                    selected_cols=self.datastructure.selected_cols,
                    data_split=DataSplit.VALIDATION,
                    schema=self.databunch.schema,
                )
            )
        val_x_df_aux = self.validation_dl.get_x_dataframe()
        if isinstance(val_x_df_aux, tuple):
            val_x_df, _ = val_x_df_aux
        else:
            val_x_df = val_x_df_aux

        self._model.fit(  # type: ignore[union-attr] # reason: the model should be set by the time we fit it # noqa: B950
            train_x_df.values,
            self.train_dl.get_y_dataframe()[target].values,
            eval_set=[
                (
                    val_x_df.values,
                    self.validation_dl.get_y_dataframe()[target].values,
                )
            ],
            eval_metric=metrics,
            max_epochs=self.epochs,
            patience=self.patience,
            batch_size=self.batch_size,
            virtual_batch_size=self.virtual_batch_size,
            num_workers=self.num_workers,
            weights=int(self.inverse_class_weights),
            drop_last=False,
        )

        metrics_results = {
            "validation_loss": "%.4f"
            % self._model.history["val_0_logloss"][-1]  # type: ignore[union-attr] # reason: see below # noqa: B950
            # The model should be set by the time we retrieve metrics
        }

        return metrics_results
