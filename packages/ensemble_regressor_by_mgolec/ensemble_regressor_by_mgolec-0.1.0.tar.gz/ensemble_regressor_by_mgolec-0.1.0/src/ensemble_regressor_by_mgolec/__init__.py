# read version from installed package
from importlib.metadata import version
__version__ = version("ensemble_regressor_by_mgolec")

from .regressor import Regressor
from .ensemble_regressor import EnsembleRegressor