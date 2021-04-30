import os, sys, shutil

class ILFFFile:

    fname = ''
    mode = 'r'
    encoding = 'utf8'
    nlines = 0
    isILFF = True

    def __init__(self, fname, mode='r', encoding='utf8'):
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
        self.file = open(self.fname, umode)
        (base, notdir) = os.path.split(self.fname)
        indexDir = os.path.join(base, '.ilff-index')
        try:
            os.mkdir(indexDir)
        except:
            pass
        self.lenfilen = os.path.join(base, '.ilff-index', notdir + '.len')
        self.idxfilen = os.path.join(base, '.ilff-index', notdir + '.idx')
        if not os.path.exists(self.lenfilen) or not os.path.exists(self.idxfilen):
            # print('One of index files not found')
            self.isILFF = False
        if self.isILFF or self.mode != 'r':
            imode = mode + ('+b' if '+' not in mode else 'b')
            self.lenfile = open(self.lenfilen, imode)
            self.idxfile = open(self.idxfilen, imode)
            self.nlines = self.get_nlines()

    def remove(self):
        self.close()
        os.remove(self.fname)
        os.remove(self.lenfilen)
        os.remove(self.idxfilen)

    def flush(self):
        self.file.flush()
        self.lenfile.flush()
        self.idxfile.flush()

    def close(self):
        self.file.close()
        self.lenfile.close()
        self.idxfile.close()

    def readint(self, file, lnnum):
        if lnnum < 0:
            return 0
        file.seek(lnnum*4)
        idxdata = file.read(4)
        if len(idxdata) != 4:
            if lnnum*4 > file.seek(0, os.SEEK_END):
                sys.stderr.write('ILFF: Error: Failed to seek in index/length file to %d of %d. Out of range?\n' % (lnnum, file.seek(0, os.SEEK_END)/4))
            idx = 2**30
        else:
            idx = int(0).from_bytes(idxdata, 'little')
        return idx

    def readindex(self, lnnum):
        return self.readint(self.idxfile, lnnum)

    def readlen(self, lnnum):
        return self.readint(self.lenfile, lnnum)

    def get_nlines(self):
        fsz = os.stat(self.idxfilen).st_size
        if fsz % 4 != 0:
            print('Error!')
        return int(fsz/4)

    def appendLine(self, txt):
        #        print('*** al %d: %d,%d' % (self.nlines,self.idxfile.tell(), self.lenfile.tell()))
        llen = len(txt)
        if txt[llen-1] == '\n':
            txt = txt[0:llen-1]
        if '\n' in txt:
            print('This is not a line')
            assert(False)
        idx = self.readindex(self.nlines-1)
        ln = self.readlen(self.nlines-1)
        newidx = idx + ln
        self.file.seek(newidx)
        #        print('*** al %d: %d,%d' % (self.nlines,self.idxfile.tell(), self.lenfile.tell()))
        txtdata = txt.encode(self.encoding)
        llen = len(txtdata)+1
        # print('*** al %d: %d,%d,%d' % (self.nlines,len(txt),newidx,llen))
        self.idxfile.write(newidx.to_bytes(4, 'little'))
        self.lenfile.write(llen.to_bytes(4, 'little'))
        #        self.dumpIndex()
        self.file.write((txtdata + b'\n'))
        self.nlines += 1

    def getindex(self, fname):
        return fname + ".idx"

    def getlength(self, fname):
        return fname + ".len"

    def buildindex(self):
        self.idxfile.seek(0)
        self.lenfile.seek(0)
        self.idxfile.truncate()
        self.lenfile.truncate()
        self.file.seek(0)
        newidx = 0
        while True:
            s = self.file.readline()
            llen = len(s)
            if llen > 0:
                if s[llen-1] != 10:
                    llen += 1
            if llen == 0:
                break
            self.idxfile.write(newidx.to_bytes(4, 'little'))
            self.lenfile.write(llen.to_bytes(4, 'little'))
            newidx = newidx + llen
        self.idxfile.flush()
        self.lenfile.flush()
#        print('Index rewritten')

    def fromfile(self, infile):
        while True:
            s = infile.readline()
            if len(s) > 0 and len(s.strip()) > 0:
                self.appendLine(s)
            else:
                if len(s) > 0:
                    continue
                else:
                    break

    def truncate(self):
        self.file.truncate()
        self.lenfile.truncate()
        self.idxfile.truncate()
        self.nlines = 0

    def compact(self):
        self.flush()
        shutil.copy(self.fname, self.fname + '.bak')
        self.truncate()
        self.fromfile(open(self.fname + '.bak', 'r', encoding=self.encoding))

    def getline(self, lnnum):
        idx = self.readindex(lnnum)
        len = self.readlen(lnnum)
#        print('*** gl: %d,%d,%d' % (lnnum,idx,len))
        if len == 0:
            return ""
        self.file.seek(idx)
        ln = self.file.read(len-1)
        return ln.decode(self.encoding)

    def getlines(self, start, nlines):
        idx = self.readindex(start)
        self.file.seek(idx)
        res = []
        for k in range(nlines):
            len = self.readlen(start+k)
            ln = self.file.read(len-1).decode(self.encoding)
            d = self.file.read(1)
            res.append(ln)
        return res

    def getlines2(self, start, nlines):
        return [ self.getline(start+ln) for ln in range(nlines) ]

    def getlinestxt(self, start, nlines):
        idxs = self.readindex(start)
        idxe = self.readindex(start+nlines-1)
        len = self.readlen(start+nlines-1)
        self.file.seek(idxs)
        ramount = idxe - idxs + len - 1
        ln = b''
        try:
            ln = self.file.read(ramount)
        except BaseException as e:
            print('ilff.getlinestxt: read failed %d-%d: %s' % (idxs, ramount, e))
        return ln.decode(self.encoding)

    def tail(self, lnnum):
        if lnnum > 0:
            lnnum -= 1
        self.idxfile.seek(lnnum*4)
        self.lenfile.seek(lnnum*4)
        idx = readindex()
        len = readlen()
        self.file.seek(idx)
        ln = self.file.read(len)
        return len

    def getIndex(self):
        for i in range(3):
            self.idxfile.seek(i*4)
            self.lenfile.seek(i*4)
            idx = readindex()
            len = readlen()
            print('%d: %d - %d' % (i, idx, len))

    def dumpIndex(self):
        for i in range(self.get_nlines()):
            idx = self.readindex(i)
            len = self.readlen(i)
            print('%d: %d - %d' % (i, idx, len))

    def eraseLine(self, ind, repl=""):
        #        print('*** al %d: %d,%d' % (self.nlines,self.idxfile.tell(), self.lenfile.tell()))
        idx = self.readindex(ind)
        ln = self.readlen(ind)
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
#        print('*** create: %s, append=%s' % (fname,append,))
        self.ilff = ILFFFile(fname, mode=mode, encoding=encoding)
        if not self.ilff.isILFF:
            # print('Index not found, opening normally: %s' % (fname,))
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
#        print('getlinestxt')
        if self.ilff is not None:
            return self.ilff.getlinestxt(offs, ln)
        else:
#            print(self.fname, self.mode, self.encoding)
            ifile = open(self.fname, mode='r', encoding=self.encoding)
            lines = ifile.read().split('\n')[offs:offs+ln]
#            print('lns', offs, ln, lines)
            return '\n'.join(lines)

    def getline(self, offs):
        if self.ilff is not None:
            return self.ilff.getline(offs, ln)
        else:
            return open(self.fname, mode='r', encoding=self.encoding).read().split('\n')[offs]

    def get_nlines(self):
        if self.ilff is not None:
            return self.ilff.get_nlines()
        else:
            return len(open(self.fname, mode='r', encoding=self.encoding).read().split('\n'))
