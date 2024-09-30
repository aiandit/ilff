__version__ = '0.7.4'

VERSION = __version__

from ilff.ilff import ILFFFile, unlink
from ilff.cilff import CILFFFile
from ilff.ilffgetlines import ILFFGetLines, CILFFGetLines
from . import reindex
