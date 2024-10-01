import os, sys, shutil, errno

from .ilff import ILFFError

from ctypes import CDLL, POINTER, c_int, c_long, c_char_p, c_void_p

c_long_p = POINTER(c_long)
c_char_pp = POINTER(c_char_p)


def configLib(lib):

    lib.ilffOpen.argtypes = (c_char_p, c_char_p)
    lib.ilffOpen.returntype = c_void_p

    lib.ilffClose.argtypes = (c_void_p,)
    lib.ilffClose.returntype = c_int

    lib.ilffFlush.argtypes = (c_void_p,)
    lib.ilffFlush.returntype = c_int

    lib.ilffTruncate.argtypes = (c_void_p,)
    lib.ilffTruncate.returntype = c_long

    lib.ilffReindex.argtypes = (c_void_p,)
    lib.ilffReindex.returntype = c_long

    lib.ilffDumpindex.argtypes = (c_void_p,)
    lib.ilffDumpindex.returntype = c_long

    lib.ilffNLines.argtypes = (c_void_p,)
    lib.ilffNLines.returntype = c_long

    lib.ilffWrite.argtypes = (c_void_p, c_char_p, c_long)
    lib.ilffWrite.returntype = c_int

    lib.ilffWriteLine.argtypes = (c_void_p, c_char_p, c_long)
    lib.ilffWrite.returntype = c_int

    lib.ilffGetLine.argtypes = (c_void_p, c_long, c_char_p, c_long_p)
    lib.ilffGetLine.returntype = c_int

    lib.ilffGetLines.argtypes = (c_void_p, c_long, c_long, c_char_pp, c_long_p)
    lib.ilffGetLines.returntype = c_int

    lib.ilffGetRange.argtypes = (c_void_p, c_long, c_long, c_char_p, c_long_p)
    lib.ilffGetRange.returntype = c_int

    lib.ilffRemove.argtypes = (c_char_p,)
    lib.ilffRemove.returntype = c_int


def getLib():
    lib = None
    mfile = sys.modules['ilff.cilff'].__file__
    csrcdir = os.path.join(os.path.dirname(mfile), '..', 'src')
    libnames = ['ilff.so', os.path.join(csrcdir, 'ilff.so')]
    for name in libnames:
        try:
            lib = CDLL(name)
            # print(f'found cILFF library {name}')
            break
        except:
            pass
    if lib:
        configLib(lib)
    return lib


class CILFFError(ILFFError):
    def __init__(self, s):
        super().__init__(f'cILFF operation failed: {s}')


class CILFFFile:

    fname = ''
    mode = 'r'
    encoding = 'utf8'
    nameenc = 'utf8'
    isILFF = True
    lib = getLib()
    handle = 0

    def __init__(self, fname, mode='r', encoding='utf8', nameenc='utf8', symlinks=True):
        if self.lib is None:
            raise CILFFError('cILFF library not available')
        self.fname = fname
        self.idxfilen = fname + '.iidx'
        if encoding is not None:
            self.encoding = encoding
        if nameenc is not None:
            self.nameenc = nameenc
        self.mode = mode
        ilfferr = c_int()
        self.handle = self.lib.ilffOpen(self.fname.encode(self.nameenc), self.mode.encode(self.nameenc), ilfferr)
        if self.handle == 0:
            raise CILFFError('open')

    def __del__(self):
        self.close()

    def remove(self, name=None):
        if type(self) == str:
            name = self
            nameenc = CILFFFile.nameenc
        else:
            name = self.fname
            nameenc = self.nameenc
        return CILFFFile.lib.ilffRemove(name.encode(nameenc))

    def close(self):
        if self.handle:
            self.lib.ilffClose(self.handle)
            self.handle = 0

    def dumpindex(self):
        return self.lib.ilffDumpindex(self.handle)

    def buildindex(self):
        return self.reindex()

    def reindex(self):
        return self.lib.ilffReindex(self.handle)

    def truncate(self):
        return self.lib.ilffTruncate(self.handle)

    def flush(self):
        return self.lib.ilffFlush(self.handle)

    def nlines(self):
        return self.lib.ilffNLines(self.handle)

    def get_nlines(self):
        return self.nlines()

    def write(self, txt):
        b = txt.encode(self.encoding)
        return self.lib.ilffWrite(self.handle, b, len(b))

    def appendLine(self, txt):
        b = txt.encode(self.encoding)
        return self.lib.ilffWrite(self.handle, b, len(b))

    def fromfile(self, infile, empty=''):
        while True:
            s = infile.readline()
            if len(s) > 0 and s.strip() != empty:
                self.appendLine(s)
            else:
                if len(s) > 0:
                    continue
                else:
                    break

    def getline(self, lnnum):
        rlen = c_long()
        self.lib.ilffGetLine(self.handle, lnnum, None, rlen)
        if rlen.value < 0:
            raise CILFFError('got negative line size')
        bln = b' ' * rlen.value
        self.lib.ilffGetLine(self.handle, lnnum, bln, rlen)
        tln = bln[0:rlen.value].decode(self.encoding)
        return tln

    def getlines(self, lnnum, nlines):
        rlens = (c_long * nlines)()
        self.lib.ilffGetLines(self.handle, lnnum, nlines, None, rlens, nlines)
        lndata = (c_char_p * nlines)()
        for (i, rlen) in enumerate(rlens):
            lndata[i] = b'\00' * rlen
        self.lib.ilffGetLines(self.handle, lnnum, nlines, lndata, rlens, nlines)
        lines = [ln.decode(self.encoding) for ln in lndata]
        return lines

    def getlines2(self, start, nlines):
        return [ self.getline(start+ln) for ln in range(nlines) ]

    def getlinestxt(self, start, nlines):
        rlen = c_long()
        self.lib.ilffGetRange(self.handle, start, nlines, None, rlen)
        bln = b' ' * rlen.value
        self.lib.ilffGetRange(self.handle, start, nlines, bln, rlen)
        tln = bln[0:rlen.value].decode(self.encoding)
        return tln
