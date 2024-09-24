import os, sys, shutil

class ILFFFile:

    fname = ''
    mode = 'r'
    encoding = 'utf8'
    nlines = 0
    isILFF = True
    indexBytes = 8
    maxmtimediff = 1

    def __init__(self, fname, mode='r', encoding='utf8', symlinks=True):
#        print('*** create: %s, append=%s' % (fname,append,))
        self.fname = fname
        if encoding is not None:
            self.encoding = encoding
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
#        print('open %s with mode %s' %(self.fname, umode))
        self.file = open(self.fname, mode + 'b')
        if symlinks and os.path.islink(self.fname):
            self.realfname = os.readlink(self.fname)
            if not os.path.isabs(self.realfname):
                self.realfname = os.path.join(os.path.dirname(self.fname), self.realfname)
                # print(f'readlink: {self.fname} => {self.realfname}')
        else:
            self.realfname = self.fname
        (base, notdir) = os.path.split(self.realfname)
        indexDir = os.path.join(base, '.ilff-index')
        try:
            os.mkdir(indexDir)
        except:
            pass
        self.idxfilen = os.path.join(base, '.ilff-index', notdir + '.idx')
        # print(f'index file: {self.fname} => {self.idxfilen}')
        if not os.path.exists(self.idxfilen):
            self.isILFF = False
        if self.isILFF or self.mode != 'r':
            self.idxfile = open(self.idxfilen, umode)
            self.nlines = self.get_nlines()
            self.idx = self.readindex(self.nlines-1)[1]
        else:
            print(f'error: {fname} does not appear to be an indexed file')

    def remove(self):
        self.close()
        os.remove(self.fname)
        os.remove(self.idxfilen)

    def flush(self):
        self.file.flush()
        self.idxfile.flush()

    def close(self):
        self.file.close()
        self.idxfile.close()

    def readint(self, file, lnnum):
        if lnnum < 0:
            return (0, 0)
        idx1 = 0
        if lnnum > 0:
            file.seek((lnnum-1)*self.indexBytes)
            idxdata = file.read(self.indexBytes)
            if len(idxdata) != self.indexBytes:
                if lnnum*self.indexBytes > file.seek(0, os.SEEK_END):
                    print('ILFF: Error: Failed to seek in index/length file to %d of %d. Out of range?' %
                          (lnnum, file.seek(0, os.SEEK_END)/self.indexBytes))
                idx1 = 2**30
            else:
                idx1 = int(0).from_bytes(idxdata, 'little')
        else:
            assert(lnnum == 0)
            file.seek(lnnum*self.indexBytes)
        idxdata = file.read(self.indexBytes)
        if len(idxdata) != self.indexBytes:
            if lnnum*self.indexBytes > file.seek(0, os.SEEK_END):
                print('ILFF: Error: Failed to seek in index/length file to %d of %d. Out of range?' % (lnnum, file.seek(0, os.SEEK_END)/4))
            idx2 = 2**30
        else:
            idx2 = int(0).from_bytes(idxdata, 'little')
        return (idx1, idx2)

    def readindex(self, lnnum):
        return self.readint(self.idxfile, lnnum)

    def get_nlines(self):
        fsz = os.stat(self.idxfilen).st_size
        if fsz % self.indexBytes != 0:
            print('Error!')
        return int(fsz/self.indexBytes)

    def write(self, txt):
        self.appendLine(txt)

    def appendLine(self, txt):
        #        print('*** al %d: %d,%d' % (self.nlines,self.idxfile.tell(), self.lenfile.tell()))
        llen = len(txt)
        if txt[llen-1] == '\n':
            txt = txt[0:llen-1]
        if '\n' in txt:
            print('This is not a line')
            assert(false)
        #self.file.seek(newidx)
        #        print('*** al %d: %d,%d' % (self.nlines,self.idxfile.tell(), self.lenfile.tell()))
        txtdata = txt.encode(self.encoding)
        llen = len(txtdata)+1
        newidx = self.idx + llen
        #  print('*** al %d: %d,%d,%d,%d' % (self.nlines,self.idx,len(txt),newidx,llen))
        self.idxfile.write(newidx.to_bytes(self.indexBytes, 'little'))
        self.idx = newidx
        self.file.write((txtdata + b'\n'))
        self.nlines += 1
        stf = os.stat(self.file.fileno())
        sti = os.stat(self.idxfile.fileno())
        if stf.st_mtime - sti.st_mtime > self.maxmtimediff:
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
            if llen > 0:
                if s[llen-1] != 10:
                    llen += 1
            newidx = newidx + llen
            self.idxfile.write(newidx.to_bytes(self.indexBytes, 'little'))
            if llen == 0:
                break
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
        self.nlines = 0
        self.idx = 0

    def compact(self, empty=''):
        self.flush()
        shutil.copy(self.fname, self.fname + '.bak')
        self.truncate()
        with open(self.fname + '.bak', 'r', encoding=self.encoding) as fcopy:
            self.fromfile(fcopy, empty=empty)
        os.remove(self.fname + '.bak')

    def getline(self, lnnum):
        (idx, idx2) = self.readindex(lnnum)
        len = idx2 - idx
        # print('*** gl: %d,%d,%d,%d' % (lnnum,idx,idx2,len))
        if len == 0:
            return ""
        self.file.seek(idx)
        ln = self.file.read(len-1)
        return ln.decode(self.encoding)

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
        if nlines <= 0:
            return ''
        (idxs, idxs2) = self.readindex(start)
        (idxe, idxe2) = self.readindex(start+nlines-1)
        self.file.seek(idxs)
        ramount = idxe2 - idxs - 1
        ln = b''
        try:
            ln = self.file.read(ramount)
        except BaseException as e:
            print('ilff.getlinestxt: read failed %d-%d: %s' % (idxs, ramount, e))
        return ln.decode(self.encoding)

    def tail(self, lnnum):
        if lnnum > 0:
            lnnum -= 1
        self.idxfile.seek(lnnum*self.indexBytes)
        idx = readindex()
        len = readlen()
        self.file.seek(idx)
        ln = self.file.read(len)
        return len

    def getindex(self):
        for i in range(3):
            self.idxfile.seek(i*self.indexBytes)
            idx = readindex()
            # print('%d: %d - %d' % (i, idx, len))

    def dumpindex(self):
        print('Number of Lines: ', self.get_nlines())
        for i in range(self.get_nlines()):
            (idx1, idx2) = self.readindex(i)
            ln = idx2 - idx1
            print('%d: %d - %d (%d)' % (i, idx1, idx2, ln))

    def eraseLine(self, ind, repl=""):
        #        print('*** al %d: %d,%d' % (self.nlines,self.idxfile.tell(), self.lenfile.tell()))
        (idx, idx2) = self.readindex(ind)
        ln = idx2 - idx
        if ln < 0 or ln > 1e5:
            print('cannot erase line %d of %s (ln %d)' % (ind, self.fname, ln))
            return
        print('erase line %d of %s (ln %d)' % (ind, self.fname, ln))
        newidx = idx + ln
        self.file.seek(idx)
        n = ln - len(repl) -1
        if n < 0:
            print('cannot erase line %d of %s (ln %d)' % (ind, self.fname, n))
            return
        white = ' ' * (n)
        bts = (repl + white).encode(self.encoding)
        print('erase line %d of %s (ln %d), write "%s" at offs %d' % (
            ind, self.fname, ln, bts, self.file.tell()))
        self.file.write(bts[0:ln])
        self.file.flush()

class ILFFGetLines:
    ilff = None

    def __init__(self, fname, mode='r', encoding='utf8'):
        # print('*** create: %s, append=%s' % (fname,append,))
        self.ilff = ILFFFile(fname, mode=mode, encoding=encoding)
        if not self.ilff.isILFF:
            print('Index not found, opening normally: %s' % (fname,))
            self.ilff = None
            self.fname = fname
            self.mode = mode
            self.encoding = encoding

    def getlines(self, offs, ln):
        if self.ilff is not None:
            return self.ilff.getlines(offs, ln)
        else:
            return open(self.fname, mode='r', encoding=self.encoding).read().split('\n')[offs:offs+ln]

    def getlinestxt(self, offs, ln):
        if self.ilff is not None:
            return self.ilff.getlinestxt(offs, ln)
        else:
            ifile = open(self.fname, mode='r', encoding=self.encoding)
            lines = ifile.read().split('\n')[offs:offs+ln]
            return '\n'.join(lines)

    def getline(self, offs):
        if self.ilff is not None:
            return self.ilff.getline(offs, ln)
        else:
            return open(self.fname, mode='r', encoding=self.encoding).read().split('\n')[offs]

    def nlines(self):
        if self.ilff is not None:
            return self.ilff.get_nlines()
        else:
            return len(open(self.fname, mode='r', encoding=self.encoding).read().split('\n'))

    def get_nlines(self):
        return self.nlines()
