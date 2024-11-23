__version__ = '25.5'

VERSION = __version__

from ilff.ilff import ILFFFile, unlink, open
try:
    import aiofiles
    from ilff.ailff import AILFFFile, open as async_open
except:
    pass
from ilff.cilff import CILFFFile
from ilff.ilffgetlines import ILFFGetLines, CILFFGetLines
from . import reindex
