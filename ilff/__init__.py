__version__ = '0.7.0'

VERSION = __version__

from ilff.ilff import ILFFFile, ILFFGetLines, unlink
from . import reindex
from ilff.cilff import CILFFFile
