from . import converters, utils
try:
    from .conv_impl.spss import SPSSConverter
except ImportError as err:
    SPSSConverter: type = utils.MissingImport(
        name="SPSSConverter", hint="Try installing with the `spss` extra option.",
        err=err)
from .crawl import Crawler, SecurityMode
from .version import CfoodRequiredVersionError, get_caoscrawler_version

__version__ = get_caoscrawler_version()

# Convenience members #########################################################
# mypy: disable-error-code="attr-defined"
converters.SPSSConverter = SPSSConverter
