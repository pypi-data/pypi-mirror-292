"""PyTorch implementations for the Bitfount framework."""

from typing import List

from bitfount.backends.pytorch.data.dataloaders import (
    DEFAULT_BUFFER_SIZE,
    PyTorchBitfountDataLoader,
    PyTorchIterableBitfountDataLoader,
)
from bitfount.backends.pytorch.federated.shim import PyTorchBackendTensorShim
from bitfount.backends.pytorch.loss import SoftDiceLoss, soft_dice_loss
from bitfount.backends.pytorch.models.base_models import PyTorchClassifierMixIn
from bitfount.backends.pytorch.models.bitfount_model import PyTorchBitfountModel
from bitfount.backends.pytorch.models.models import (
    PyTorchImageClassifier,
    PyTorchTabularClassifier,
    TabNetClassifier,
)
from bitfount.backends.pytorch.models.torch_functions.mish import Mish
from bitfount.backends.pytorch.utils import LoggerType, autodetect_gpu

__all__: List[str] = [
    "autodetect_gpu",
    "DEFAULT_BUFFER_SIZE",
    "LoggerType",
    "Mish",
    "PyTorchBackendTensorShim",
    "PyTorchBitfountDataLoader",
    "PyTorchBitfountModel",
    "PyTorchClassifierMixIn",
    "PyTorchImageClassifier",
    "PyTorchIterableBitfountDataLoader",
    "PyTorchTabularClassifier",
    "soft_dice_loss",
    "SoftDiceLoss",
    "TabNetClassifier",
]

# See top level `__init__.py` for an explanation
__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False
