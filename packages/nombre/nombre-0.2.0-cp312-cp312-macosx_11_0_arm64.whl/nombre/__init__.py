"""nombre is a tool for creating and parsing partition filenames"""

from ._nombre_rust import __version__  # type: ignore
from ._functions import (create_filenames, parse_filename, parse_filenames)
