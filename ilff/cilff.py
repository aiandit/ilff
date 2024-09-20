import os, sys, shutil

from ctypes import CDLL, POINTER, c_int, c_long, c_char_p, c_void_p

c_long_p = POINTER(c_long)


def configLib(lib):

    lib.ilffOpen.argtypes = (c_char_p, c_char_p)
    lib.ilffOpen.returntype = c_void_p

    lib.ilffClose.argtypes = (c_void_p,)
    lib.ilffClose.returntype = c_int

    lib.ilffFlush.argtypes = (c_void_p,)
    lib.ilffFlush.returntype = c_int

    lib.ilffWrite.argtypes = (c_void_p, c_char_p, c_long)
    lib.ilffWrite.returntype = c_int

    lib.ilffWriteLine.argtypes = (c_void_p, c_char_p, c_long)
    lib.ilffWrite.returntype = c_int

    lib.ilffGetLine.argtypes = (c_void_p, c_long, c_char_p, c_long_p)
    lib.ilffGetLine.returntype = c_int

    lib.ilffGetRange.argtypes = (c_void_p, c_long, c_long, c_char_p, c_long_p)
    lib.ilffGetRange.returntype = c_int


class CILFFError(BaseException):
    def __init__(self, s):
        super().__init__(f'CILFF operation "{s}" failed')


class CILFFFile:

    fname = ''
    mode = 'r'
    encoding = 'utf8'
    nameenc = 'utf8'
    isILFF = True
    lib = None
    handle = 0

    def __init__(self, fname, mode='r', encoding='utf8', nameenc='utf8', symlinks=True):
        self.lib = CDLL('ilff.so')
        configLib(self.lib)

        self.fname = fname
        self.idxfilen = fname + '.iidx'
        if encoding is not None:
            self.encoding = encoding
        if nameenc is not None:
            self.nameenc = nameenc
        self.mode = mode
        self.handle = self.lib.ilffOpen(self.fname.encode(self.nameenc), self.mode.encode(self.nameenc))
        if self.handle == 0:
            raise CILFFError('open')

    def __del__(self):
        self.close()

    def close(self):
        if self.handle:
            self.lib.ilffClose(self.handle)
            self.handle = 0

    def flush(self):
        self.lib.ilffFlush(self.handle)

    def get_nlines(self):
        return self.lib.ilffNLines(self.handle)

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
        bln = b' ' * rlen.value
        self.lib.ilffGetLine(self.handle, lnnum, bln, rlen)
        tln = bln[0:rlen.value].decode(self.encoding)
        return tln

    def getlines(self, start, nlines):
        (idx, idx2) = self.readindex(start)
        len = idx2 - idx
        self.file.seek(idx)
        res = []
        for k in range(nlines):
            (idx, idx2) = self.readindex(start + k)
            len = idx2 - idx
            ln = self.file.read(len-1).decode(self.encoding)
            d = self.file.read(1)
            res.append(ln)
        return res

    def getlines2(self, start, nlines):
        return [ self.getline(start+ln) for ln in range(nlines) ]

    def getlinestxt(self, start, nlines):
        rlen = c_long()
        self.lib.ilffGetRange(self.handle, start, nlines, None, rlen)
        bln = b' ' * rlen.value
        self.lib.ilffGetRange(self.handle, start, nlines, bln, rlen)
        tln = bln[0:rlen.value].decode(self.encoding)
        return tln
