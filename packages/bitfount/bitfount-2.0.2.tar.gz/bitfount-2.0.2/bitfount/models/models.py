"""Backend-agnostic models that have no extra requirements.

:::info

Models defined here cannot be trained in a federated manner.

:::
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from io import BytesIO
import logging
import os

# TODO: [BIT-987] Review use of pickle
import pickle  # nosec B403 # import_pickle
from typing import Any, List, Literal, Mapping, Optional, Union, cast

from marshmallow import fields
import numpy as np
from pandas import DataFrame
import pandas as pd
from sklearn.linear_model import (
    LinearRegression as sklearnLinearRegression,
    LogisticRegression as sklearnLogisticRegression,
)
from sklearn.neighbors import KNeighborsClassifier
import statsmodels.api as sm

from bitfount.data.dataloaders import BitfountDataLoader
from bitfount.data.datasources.base_source import BaseSource
from bitfount.metrics import Metric
from bitfount.models.base_models import ClassifierMixIn, RegressorMixIn, _BaseModel
from bitfount.types import EvaluateReturnType, PredictReturnType
from bitfount.utils import delegates

logger = logging.getLogger(__name__)


@delegates()
class LogisticRegressionClassifier(ClassifierMixIn, _BaseModel):
    """Wrapper around `sklearn.linear_model.LogisticRegression` model.

    For more details on the parameters, go to the scikit-learn documentation.

    Args:
        inverse_regularisation: Inverse regularisation parameter. Defaults to 0.0001.
        max_steps: Maximum number of steps to take. Defaults to 10000.
        model_type: Type of solver to use. Defaults to "lbfgs".
        penalty: Penalty to use. Defaults to "l2".
        early_stopping_tolerance: Tolerance for early stopping. Defaults to 1e-05.
        verbose: Verbosity level. Defaults to 0.

    Attributes:
        inverse_regularisation: Inverse regularisation parameter.
        max_steps: Maximum number of steps to take.
        model_type: Type of solver to use.
        penalty: Penalty to use.
        early_stopping_tolerance: Tolerance for early stopping.
        verbose: Verbosity level.
    """

    fields_dict = {
        "inverse_regularisation": fields.Float(allow_none=True),
        "max_steps": fields.Integer(allow_none=True),
        "model_type": fields.String(allow_none=True),
        "penalty": fields.String(allow_none=True),
        "early_stopping_tolerance": fields.Float(allow_none=True),
        "verbose": fields.Integer(allow_none=True),
    }

    def __init__(
        self,
        inverse_regularisation: Optional[float] = None,
        max_steps: Optional[int] = None,
        model_type: Optional[str] = None,
        penalty: Optional[str] = None,
        early_stopping_tolerance: Optional[float] = None,
        verbose: Optional[int] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.inverse_regularisation = (
            0.0001 if inverse_regularisation is None else inverse_regularisation
        )
        self.max_steps = 10000 if max_steps is None else max_steps
        self.model_type = "lbfgs" if model_type is None else model_type
        self.penalty = "l2" if penalty is None else penalty
        self.early_stopping_tolerance = (
            1e-05 if early_stopping_tolerance is None else early_stopping_tolerance
        )
        self.verbose = 0 if verbose is None else verbose

    def predict(self, *args: Any, **kwargs: Any) -> PredictReturnType:
        """Returns model predictions. Not implemented yet."""
        # TODO: [BIT-2406] Implement this method
        raise NotImplementedError

    def serialize(self, filename: Union[str, os.PathLike]) -> None:
        """Serialize model to file with provided `filename`.

        Args:
            filename: Path to file to save serialized model.
        """
        with open(filename, "wb") as f:
            pickle.dump(self._model, f, protocol=pickle.HIGHEST_PROTOCOL)

    def deserialize(self, content: Union[str, os.PathLike, bytes]) -> None:
        """Deserialize model.

        :::danger

        This should not be used on a model file that has been received across a
        trust boundary due to underlying use of `pickle`.

        :::

        Args:
            content: Byte strem or path to file containing serialized model.
        """
        # TODO: [BIT-987] Review use of pickle.load()
        if isinstance(content, bytes):
            self.model = pickle.load(BytesIO(content))  # nosec B301 # pickle usage
        else:
            with open(content, "rb") as f:
                self._model = pickle.load(f)  # nosec B301 # pickle usage

    def evaluate(
        self, test_dl: Optional[BitfountDataLoader] = None, *args: Any, **kwargs: Any
    ) -> EvaluateReturnType:
        """Perform inference on test set and return predictions and targets.

        Args:
            test_dl: Optional `BitfountDataLoader` object containing test data. If this
                is not provided, the test set from the `BaseSource` used to train the
                model is used if present.

        Returns:
            A tuple of numpy arrays containing the predicted and actual values.

        Raises:
            ValueError: If there is no test data to evaluate the model on
        """
        logger.info("Evaluating logistic regression classifier.")

        if test_dl is None:
            if isinstance(self.test_dl, BitfountDataLoader):
                test_dl = self.test_dl
            else:
                raise ValueError("There is no test data to evaluate the model on.")
        test_df = test_dl.get_x_dataframe()
        test_preds: np.ndarray = cast(
            sklearnLogisticRegression, self._model
        ).predict_proba(test_df)
        test_target = test_dl.get_y_dataframe().to_numpy()

        return EvaluateReturnType(test_preds, test_target)

    def fit(
        self,
        data: Optional[BaseSource] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Trains a model using the training set provided by `data`.

        :::info

        The validation set in `data` is not used when training this model.

        :::

        Args:
            data: `BaseSource` object containing training data.
        """
        logger.info("Fitting logistic regression classifier.")

        if data:
            data.load_data()

        table_schema = self.datastructure.get_table_schema(
            schema=self.schema, datasource=data
        )

        if not self.initialised:
            self.initialise_model(data)
        self.set_number_of_classes(table_schema)
        self._set_dataloaders()

        model = sklearnLogisticRegression(
            C=self.inverse_regularisation,
            random_state=self.seed,
            max_iter=self.max_steps,
            solver=self.model_type,
            verbose=self.verbose,
        )

        # Check that a target exists as needed for dataframe indexing below
        # This needs to be _fairly_ lazily checked as databunch may not be set
        # earlier in this method.
        target = self.databunch.target
        if target is None:
            raise ValueError(
                f"No `target` specified in datastructure, needed for model fitting"
                f" and DataFrame indexing in {self.__class__.__name__}"
            )
        assert self.train_dl is not None  # nosec assert_used # cannot fit on empty data
        model.fit(
            self.train_dl.get_x_dataframe(),
            self.train_dl.get_y_dataframe()[target].to_numpy(),
        )
        self._model = model


@delegates()
class RegBoostRegressor(RegressorMixIn, _BaseModel):
    """Gradient Boosted Linear Regression Model.

    Implementation of "RegBoost: a gradient boosted multivariate regression algorithm"
    by Li et al. (2020). For more details, see the paper:
    https://www.emerald.com/insight/content/doi/10.1108/IJCS-10-2019-0029/full/html

    Args:
        learning_rate: Learning rate for gradient boosting. Defaults to 0.1.
        max_depth: Maximum depth of tree (number of nodes between root and leaf).
            A depth of 0 is equivalent to a single Linear Regression model. Defaults to
                10.
        min_data_points_per_node: Minimum number of data points required to split a
            node. Defaults to 5.
        stepwise_regression: Whether stepwise regression should go "forward" or
            "backward". Defaults to "forward".
        stepwise_regression_threshold: Threshold for stepwise regression. Defaults to
            0.15.

    Attributes:
        learning_rate: Learning rate for gradient boosting.
        max_depth: Maximum depth of tree (number of nodes between root and leaf).
        min_data_points_per_node: Minimum number of data points required to split a
            node.
        stepwise_regression: Whether stepwise regression should go "forward" or
            "backward".
        stepwise_regression_threshold: Threshold for stepwise regression.
    """

    fields_dict = {
        "learning_rate": fields.Float(allow_none=True),
        "max_depth": fields.Integer(allow_none=True),
        "min_data_points_per_node": fields.Integer(allow_none=True),
        "stepwise_regression": fields.String(allow_none=True),
        "stepwise_regression_threshold": fields.Float(allow_None=True),
    }

    def __init__(
        self,
        learning_rate: float = 0.1,
        max_depth: int = 10,
        min_data_points_per_node: int = 5,
        stepwise_regression: Literal["forward", "backward"] = "forward",
        stepwise_regression_threshold: float = 0.15,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_data_points_per_node = min_data_points_per_node
        self.stepwise_regression = stepwise_regression
        self.stepwise_regression_threshold = stepwise_regression_threshold

    def predict(self, *args: Any, **kwargs: Any) -> PredictReturnType:
        """Returns model predictions. Not implemented yet."""
        # TODO: [BIT-2406] Implement this method
        raise NotImplementedError

    class _ModelTreeSide(Enum):
        """Represents the side which a node represents in ModelTree."""

        POSITIVE = auto()
        NEGATIVE = auto()

    @dataclass
    class _ModelTree:
        """Core RegBoost model. Binary decision Tree of Linear Regressors.

        Args:
            data_indices: np array of data indices
            depth: number of parent nodes above this node until the root node
            side: -ve or +ve
        """

        data_indices: np.ndarray
        depth: int
        side: Optional[RegBoostRegressor._ModelTreeSide] = None

        def __post_init__(self) -> None:
            self.model = sklearnLinearRegression()
            self.classifier: Optional[KNeighborsClassifier] = (
                None  # only used at inference time
            )
            self.features: List[str] = []
            self.negatives: Optional[RegBoostRegressor._ModelTree] = None
            self.positives: Optional[RegBoostRegressor._ModelTree] = None

        def __str__(self) -> str:
            """Prints model structure depth first vertically."""
            ret = (
                "┃\t" * self.depth
                + "┣"
                + repr(
                    f"Depth: {self.depth}, "
                    + f"Features: {len(self.features)}, "
                    + f"Data: {len(self.data_indices)}"
                )
                + "\n"
            )
            for child in [self.negatives, self.positives]:
                if child is not None:
                    ret += child.__str__()
            return ret

        def fit(self, *args: Any, **kwargs: Any) -> sklearnLinearRegression:
            """Call self.model fit method."""
            return self.model.fit(*args, **kwargs)

        def predict(self, *args: Any, **kwargs: Any) -> List[np.ndarray]:
            """Call self.model predict method."""
            return [np.asarray(i) for i in self.model.predict(*args, **kwargs)]

        @property
        def is_leaf(self) -> bool:
            """Returns boolean indicating whether this node is a leaf node."""
            return self.positives is None and self.negatives is None

        def add_child(
            self,
            side: RegBoostRegressor._ModelTreeSide,
            data_indices: np.ndarray,
        ) -> RegBoostRegressor._ModelTree:
            """Add child node (either `negatives` or `positives`) and return it.

            Args:
                side: -ve or +ve
                data_indices: np array of data indices

            Returns:
                RegBoostRegressor._ModelTree: the child node just created
            """
            model = RegBoostRegressor._ModelTree(data_indices, self.depth + 1, side)
            if side == RegBoostRegressor._ModelTreeSide.NEGATIVE:
                self.negatives = model
            elif side == RegBoostRegressor._ModelTreeSide.POSITIVE:
                self.positives = model

            return model

    def _fit_model_tree(
        self,
        model: _ModelTree,
        parent_preds: Optional[np.ndarray] = None,
        parent_features: Optional[List[str]] = None,
    ) -> None:
        """Fits `model` recursively.

        Builds `model` tree recursively depth-first and fits the Linear Regression
        model at each node.
        """
        # Check that a target exists as needed for dataframe indexing below
        target = self.datastructure.target
        if target is None:
            raise ValueError(
                f"No `target` specified in datastructure, needed for model fitting"
                f" and DataFrame indexing in {self.__class__.__name__}"
            )
        assert self.train_dl is not None  # nosec assert_used # cannot fit on empty data
        data = self.train_dl.get_x_dataframe()

        if isinstance(data, DataFrame):
            X = data.loc[model.data_indices]
        else:
            X, _ = data
            X = X.loc[model.data_indices]
        y = (
            self.train_dl.get_y_dataframe()[target]
            .to_numpy()[model.data_indices]
            .astype(np.float32)
        )

        # Update target to be the residual from parent * learning rate
        if parent_preds is not None:
            y -= self.learning_rate * parent_preds

        # Subset features to same as parent
        if parent_features is not None:
            X = X[parent_features]

        # Perform stepwise regression feature selection if we have more than one feature
        if len(X.columns) > 1:
            model.features = self._perform_stepwise_regression(X, y)
            X = X[model.features]
        else:
            model.features = parent_features or list(X.columns)

        # Fit linear regression model
        model.fit(X, y)

        # If we haven't reached the maximum depth, create positive and negative children
        if model.depth < self.max_depth:
            preds = np.asarray(model.predict(X))

            for side, indices in zip(
                RegBoostRegressor._ModelTreeSide,
                [preds <= y, preds > y],
            ):
                # Only create children if there are enough data points for both children
                if (
                    indices.sum() >= self.min_data_points_per_node
                    and (len(preds) - indices.sum()) >= self.min_data_points_per_node
                ):
                    model_ = model.add_child(side, X.index[indices])

                    # Add parent predictions to current predictions
                    new_preds = preds[indices]
                    if parent_preds is not None:
                        new_preds += parent_preds[indices]

                    # Fit child model tree
                    self._fit_model_tree(model_, new_preds, model.features)

    def _perform_stepwise_regression(self, X: pd.DataFrame, y: np.ndarray) -> List[str]:
        """Performs either forward or backward stepwise regression.

        Args:
            X (pd.DataFrame): dataframe of features
            y (np.ndarray): target array

        Raises:
            ValueError: if stepwise regression direction not supported

        Returns:
            List[str]: list of new features
        """
        if self.stepwise_regression == "forward":
            features = self._forward_stepwise_regression(
                X, y, self.stepwise_regression_threshold
            )
        elif self.stepwise_regression == "backward":
            features = self._backward_stepwise_regression(
                X, y, self.stepwise_regression_threshold
            )
        else:
            raise ValueError(
                "Stepwise regression only supports 'forward' and 'backward'"
            )
        return features

    @staticmethod
    def _forward_stepwise_regression(
        X: pd.DataFrame, y: np.ndarray, p_threshold: float
    ) -> List[str]:
        """Perform forward stepwise regression.

        Starts off with no features and keeps adding them until we reach p_threshold.
        """
        included: List[str] = []
        while True:
            if len(included) == len(X.columns):
                break

            p_values = {}
            for feature in [i for i in X.columns if i not in included]:
                model = sm.OLS(
                    y, sm.add_constant(pd.DataFrame(X[included + [feature]]))
                )
                results = model.fit()
                p_values[feature] = results.pvalues[feature]
            getter: Any = p_values.get
            best_feature = min(p_values, key=getter)
            best_pval = p_values[best_feature]

            if best_pval > p_threshold:
                break

            included.append(best_feature)

        return included or [best_feature]

    @staticmethod
    def _backward_stepwise_regression(
        X: pd.DataFrame, y: np.ndarray, p_threshold: float
    ) -> List[str]:
        """Perform backward stepwise regression.

        Starts off with all features and keeps removing them until we reach p_threshold.
        """
        included = list(X.columns)
        while True:
            if len(included) == 1:
                break

            model = sm.OLS(y, sm.add_constant(X[included]))
            results = model.fit()

            # use all coefs except intercept
            p_values = dict(results.pvalues.iloc[1:])
            getter: Any = p_values.get
            worst_feature = max(p_values, key=getter)
            worst_pval = p_values[worst_feature]

            if worst_pval <= p_threshold:
                break

            included.remove(worst_feature)

        return included

    def fit(
        self,
        data: Optional[BaseSource] = None,
        metrics: Optional[Mapping[str, Metric]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Trains a model using the training set provided by the BaseSource object."""
        logger.info("Fitting RegBoost regressor.")
        self.initialise_model(data)
        self._set_dataloaders()
        assert self.train_dl is not None  # nosec assert_used # cannot fit on empty data
        model = self._ModelTree(np.array(range(len(self.train_dl))), 0)
        self._fit_model_tree(model)
        self._model: RegBoostRegressor._ModelTree = model

    def evaluate(
        self, test_dl: Optional[BitfountDataLoader] = None, *args: Any, **kwargs: Any
    ) -> EvaluateReturnType:
        """Perform inference on test set and return predictions and targets.

        Args:
            test_dl: Optional `BitfountDataLoader` object containing test data. If this
                is not provided, the test set from the `BaseSource` used to train the
                model is used if present.

        Returns:
            A tuple of numpy arrays containing the predicted and actual values.

        Raises:
            ValueError: If there is no test data to evaluate the model on
        """
        logger.info("Evaluating RegBoost regressor.")

        k = cast(int, kwargs.get("k"))
        if test_dl is None:
            if isinstance(self.test_dl, BitfountDataLoader):
                test_dl = self.test_dl
            else:
                raise ValueError("There is no test data to evaluate the model on.")

        test_df = test_dl.get_x_dataframe()
        if isinstance(test_df, tuple):
            raise ValueError(
                "Multiple dataframes retrieved unexpectedly; "
                "this model does not support combination tabular and image data."
            )

        # Check that a target exists as needed for dataframe indexing below
        # This needs to be _fairly_ lazily checked as databunch may not be set
        # earlier in this method.
        target = self.databunch.target
        if target is None:
            raise ValueError(
                f"No `target` specified in datastructure, needed for evaluation"
                f" and DataFrame indexing in {self.__class__.__name__}"
            )

        test_target = test_dl.get_y_dataframe()[target].to_numpy().astype(np.float32)
        test_preds = self._evaluate_model_tree(self._model, test_df, k)
        test_preds_aggregated = self._aggregate_model_predictions(test_preds)

        return EvaluateReturnType(test_preds_aggregated, test_target)

    def _evaluate_model_tree(
        self, model: _ModelTree, test_df: pd.DataFrame, k: int
    ) -> List[List[float]]:
        """Recursively run inference on ModelTree and return final predictions."""
        if model.classifier is None:
            self._fit_model_tree_classifier(model, k)
        test_df = test_df[model.features]
        tree_classes = self._eval_model_tree_classifier(model, test_df)
        preds = np.reshape(
            np.asarray(model.predict(test_df)), (len(test_df), 1)
        ).tolist()

        # Split data into positives and negatives based on classifier results
        for indices, model_ in zip(
            [tree_classes == 1, tree_classes == 0],
            [model.positives, model.negatives],
        ):
            # If child model exists and there is at least one data point for that branch
            # Evaluate on that branch and append predictions to parent predictions
            if model_ is not None and sum(indices) > 0:
                child_preds = self._evaluate_model_tree(model_, test_df[indices], k)
                preds = self._append_model_predictions(preds, child_preds, indices)
        predictions: List[List[float]] = preds
        return predictions

    def _aggregate_model_predictions(self, preds: List[List[float]]) -> np.ndarray:
        """Aggregate all model predictions for each data point and return predictions.

        Learning rate applied to all predictions apart from the last one. This modifies
        the `preds` object.
        """
        preds_aggregated = []
        # pred_list: List[float]
        for pred_list in preds:
            preds_aggregated.append(
                pred_list[-1] + (sum(pred_list[:-1]) * self.learning_rate)
            )
        predictions: np.ndarray = np.asarray(preds_aggregated)
        return predictions

    @staticmethod
    def _append_model_predictions(
        parent_preds: List[List[float]],
        child_preds: List[List[float]],
        indices: List[bool],
    ) -> List[List[float]]:
        """Appends `child_preds` to corresponding `indices` in `parent_preds`."""
        i = 0
        for pred, idx in zip(parent_preds, indices):
            if idx:
                pred.extend(child_preds[i])
                i += 1
        return parent_preds

    def _fit_model_tree_classifier(self, model: _ModelTree, k: int) -> None:
        """Fit ModelTree classifier with training data."""
        if model.negatives is not None and model.positives is not None:
            model.classifier = KNeighborsClassifier(n_neighbors=k)
            assert (
                self.train_dl is not None
            )  # nosec assert_used # cannot fit on empty data -m
            X = self.train_dl.get_x_dataframe()
            if isinstance(X, tuple):
                raise ValueError(
                    "Multiple dataframes retrieved unexpectedly; "
                    "this model does not support combination tabular and image data."
                )

            X = X[model.features].loc[
                np.concatenate(
                    [model.positives.data_indices, model.negatives.data_indices]
                )
            ]
            y = [1 for _ in model.positives.data_indices] + [
                0 for _ in model.negatives.data_indices
            ]
            if isinstance(model.classifier, KNeighborsClassifier):
                model.classifier.fit(X, y)

    @staticmethod
    def _eval_model_tree_classifier(
        model: _ModelTree, test_df: pd.DataFrame
    ) -> np.ndarray:
        """Run inference on ModelTree classifier to return corresponding classes.

        Doesn't run the model if there is only one class available.
        """
        class_predictions: Union[List[int], np.ndarray]
        if isinstance(model.classifier, KNeighborsClassifier):
            class_predictions = model.classifier.predict(test_df)
        elif model.negatives is None:
            class_predictions = [1 for _ in range(len(test_df))]
        else:  # if model.positives is None:
            class_predictions = [0 for _ in range(len(test_df))]

        return np.asarray(class_predictions)

    def serialize(self, filename: Union[str, os.PathLike]) -> None:
        """Serialize model to file with provided `filename`.

        Args:
            filename: Path to file to save serialized model.
        """
        with open(filename, "wb") as f:
            pickle.dump(self._model, f, protocol=pickle.HIGHEST_PROTOCOL)

    def deserialize(self, content: Union[str, os.PathLike, bytes]) -> None:
        """Deserialize model.

        :::danger

        This should not be used on a model file that has been received across a
        trust boundary due to underlying use of `pickle`.

        :::

        Args:
            content: Byte stream or path to file containing serialized model.
        """
        self._set_dataloaders()
        with open(content, "rb") as f:
            # TODO: [BIT-987] Review use of pickle.load()
            self._model = pickle.load(f)  # nosec B301 # pickle usage
