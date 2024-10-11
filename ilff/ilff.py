import os, sys, shutil, io

class ILFFError(BaseException):
    def __init__(self, s):
        super().__init__(f'cILFF operation failed: {s}')

class ILFFFile:

    fname = ''
    mode = 'r'
    encoding = 'utf8'
    _nlines = 0
    isILFF = True
    indexBytes = 8
    maxmtimediff = 1
    file = None
    idxfile = None
    sep = '\n'
    bsep = b'\n'

    def __init__(self, fname, mode='r', encoding='utf8', symlinks=True, check=True, sep='\n'):
        self.fname = fname
        if encoding is not None:
            self.encoding = encoding
        self.sep = sep
        self.bsep = self.sep.encode(self.encoding)
        self.mode = mode
        if mode == 'r':
            umode = 'r'
        elif mode == 'r+':
            umode = 'r+'
        elif mode == 'w' or mode == 'w+':
            umode = 'w+'
        elif mode == 'a' or mode == 'a+':
            umode = 'a+'
        umode += 'b'
        self.file = open(self.fname, mode + 'b')
        if symlinks and os.path.islink(self.fname):
            self.realfname = os.readlink(self.fname)
            if not os.path.isabs(self.realfname):
                self.realfname = os.path.join(os.path.dirname(self.fname), self.realfname)
        else:
            self.realfname = self.fname
        (base, notdir) = os.path.split(self.realfname)
        indexDir = os.path.join(base, '.ilff-index')
        try:
            os.mkdir(indexDir)
        except:
            pass
        self.idxfilen = os.path.join(base, '.ilff-index', notdir + '.idx')
        if not os.path.exists(self.idxfilen):
            self.isILFF = False
        if self.isILFF or self.mode != 'r':
            self.idxfile = open(self.idxfilen, umode)
            self._nlines = self.get_nlines()
            self.idx = self.readindex(self._nlines-1)[1]
            if check:
                self.check()
            self.file.seek(self.idx)
        else:
            print(f'error: {fname} does not appear to be an indexed file')

    def __del__(self):
        self.close()

    def __str__(self):
        return f'ILFFFile("{self.fname}", nlines={self._nlines}, @{self.idx})'

    def check(self):
        tdiff, stf = self.checkFileTimes()
        tok = tdiff < self.maxmtimediff*2
        iok = self.checkIndex(stf)
        return tok and iok

    def checkFileTimes(self, warn=True):
        stf = os.stat(self.file.fileno())
        sti = os.stat(self.idxfile.fileno())
        if warn and stf.st_mtime - sti.st_mtime > self.maxmtimediff*2:
            print(f'Warning: index file is outdated, consider reindexing {self.fname}')
        return stf.st_mtime - sti.st_mtime, stf

    def checkIndex(self, stf=None):
        if stf is None:
            stf = os.stat(self.file.fileno())
        if self.idx != stf.st_size:
            print(f'Main file size is inconsistent with index. consider reindexing {self.fname}')

    def remove(self):
        if type(self) == str:
            self = ILFFFile(self)
        self.close()
        os.remove(self.fname)
        os.remove(self.idxfilen)

    def flush(self):
        self.file.flush()
        self.idxfile.flush()

    def close(self):
        if self.file:
            self.file.close()
        if self.idxfile:
            self.idxfile.close()

    def readint(self, file, lnnum):
        if lnnum < 0:
            return (0, 0)
        idx1 = 0
        if lnnum > 0:
            file.seek((lnnum-1)*self.indexBytes)
            idxdata = file.read(self.indexBytes)
            if len(idxdata) != self.indexBytes:
                raise ILFFError('ILFF: Error: Failed to seek in index/length file to %d of %d. Out of range?' %
                                (lnnum, file.seek(0, os.SEEK_END)/self.indexBytes))
                idx1 = 2**30
            else:
                idx1 = int(0).from_bytes(idxdata, 'little')
        else:
            assert(lnnum == 0)
            file.seek(lnnum*self.indexBytes)
        idxdata = file.read(self.indexBytes)
        if len(idxdata) != self.indexBytes:
            raise ILFFError('ILFF: Error: Failed to seek in index/length file to %d of %d. Out of range?' %
                            (lnnum, file.seek(0, os.SEEK_END)/4))
            idx2 = 2**30
        else:
            idx2 = int(0).from_bytes(idxdata, 'little')

        if self.mode != 'r':
            file.seek(0, os.SEEK_END)

        return (idx1, idx2)

    def readindex(self, lnnum):
        return self.readint(self.idxfile, lnnum)

    def _ifileSize(self):
        return self.idxfile.seek(0, io.SEEK_END)

    def nlines(self):
        return int(self._ifileSize()/self.indexBytes)

    def get_nlines(self):
        return self.nlines()

    def write(self, txt):
        lns = txt.split(self.sep)
        if len(txt) >= len(self.sep) and txt[len(txt) - len(self.sep):] == self.sep:
            lns = lns[0:-1]
        [self.appendLine(ln) for ln in lns]

    def appendLine(self, txt):
        llen = len(txt)
        if llen >= len(self.sep) and txt[llen - len(self.sep):] == self.sep:
            txt = txt[0:-len(self.sep)]
        txtdata = txt.encode(self.encoding)
        llen = len(txtdata) + len(self.bsep)
        newidx = self.idx + llen
        self.idxfile.write(newidx.to_bytes(self.indexBytes, 'little'))
        self.idx = newidx
        self.file.write(txtdata + self.bsep)
        self._nlines += 1
        tdiff, _ = self.checkFileTimes(False)
        if tdiff > self.maxmtimediff:
            self.idxfile.flush()

    def getIndexFile(self, fname):
        return fname + ".idx"

    def buildindex(self):
        self.idxfile.seek(0)
        self.idxfile.truncate()
        self.file.seek(0)
        newidx = 0
        while True:
            s = self.file.readline()
            llen = len(s)
            if llen == 0:
                break
            newidx = newidx + llen
            self.idxfile.write(newidx.to_bytes(self.indexBytes, 'little'))
        self.idxfile.flush()

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

    def truncate(self):
        self.file.seek(0)
        self.file.truncate()
        self.idxfile.seek(0)
        self.idxfile.truncate()
        self._nlines = 0
        self.idx = 0

    def compact(self, empty=''):
        self.flush()
        shutil.copy(self.fname, self.fname + '.bak')
        self.truncate()
        with open(self.fname + '.bak', 'r', encoding=self.encoding, newline=self.sep) as fcopy:
            self.fromfile(fcopy, empty=empty)
        os.remove(self.fname + '.bak')

    def getline(self, lnnum):
        (idx, idx2) = self.readindex(lnnum)
        len = idx2 - idx
        if len == 0:
            return ""
        self.file.seek(idx)
        ln = self.file.read(len)
        if self.mode != 'r':
            self.file.seek(self.idx)
        return ln.decode(self.encoding)

    def getlines(self, start, nlines):
        (idx, idx2) = self.readindex(start)
        len = idx2 - idx
        self.file.seek(idx)
        res = []
        for k in range(nlines):
            (idx, idx2) = self.readindex(start + k)
            len = idx2 - idx
            ln = self.file.read(len).decode(self.encoding)
            res.append(ln)
        if self.mode != 'r':
            self.file.seek(self.idx)
        return res

    def getlinestxt(self, start, nlines):
        if nlines <= 0:
            return ''
        (idxs, idxs2) = self.readindex(start)
        (idxe, idxe2) = self.readindex(start+nlines-1)
        self.file.seek(idxs)
        ramount = idxe2 - idxs
        ln = b''
        ln = self.file.read(ramount)
        if self.mode != 'r':
            self.file.seek(self.idx)
        return ln.decode(self.encoding)

    def getindex(self):
        for i in range(3):
            self.idxfile.seek(i*self.indexBytes)
            idx = readindex()

    def dumpindex(self):
        print('Number of Lines: ', self.get_nlines())
        for i in range(self.get_nlines()):
            (idx1, idx2) = self.readindex(i)
            ln = idx2 - idx1
            print('%d: %d - %d (%d)' % (i, idx1, idx2, ln))

    def eraseLine(self, ind, repl=""):
        (idx, idx2) = self.readindex(ind)
        ln = idx2 - idx
        self.file.seek(idx)
        n = ln - len(repl) -1
        if n < 0:
            print('cannot erase line %d of %s (ln %d)' % (ind, self.fname, n))
            raise ILFFError('erase')
            return
        white = ' ' * (n)
        bts = (repl + white).encode(self.encoding)
        self.file.write(bts[0:ln])
        self.file.seek(self.idx)


def unlink(name):
    return ILFFFile.remove(name)
