"""Common code"""

from .check_update import check_update
from .database import build_database_url
from .discord_common import error_embed, make_embed, list_message
from .make_logger import make_logger
from .file_utils import remove_bom_inplace
from .text_utils import str2bool

__version__ = "0.2.0.post2"

__all__ = [
    "__version__",
    "make_logger",
    "make_embed",
    "error_embed",
    "list_message",
    "build_database_url",
    "check_update",
    "remove_bom_inplace",
    "str2bool",
]
