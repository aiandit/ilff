
from .ilff import ILFFFile
from .cilff import CILFFFile, CILFFError


class ILFFGetLines:
    ilff = None
    file = None
    lines = None

    def __init__(self, fname, mode='r', encoding='utf8', var='py'):
        # print('*** create: %s, append=%s' % (fname,append,))
        if var == 'py':
            self.ilff = ILFFFile(fname, mode=mode, encoding=encoding)
            if not self.ilff.isILFF:
                print('Index not found, opening normally: %s' % (fname,))
                self.ilff.close()
                self.ilff = None
                self.file = open(fname, mode=mode, encoding=encoding)
        else:
            try:
                self.ilff = CILFFFile(fname, mode=mode, encoding=encoding)
            except CILFFError as ex:
                print('Index not found, opening normally: %s' % (fname,))
                self.file = open(fname, mode=mode, encoding=encoding)
        if self.file:
            self.lines = self.file.read().split('\n')
        print('Opened')

    def getlines(self, offs, ln):
        if self.ilff is not None:
            return self.ilff.getlines(offs, ln)
        else:
            return self.lines[offs:offs+ln]

    def getlinestxt(self, offs, ln):
        if self.ilff is not None:
            return self.ilff.getlinestxt(offs, ln)
        else:
            lines = self.lines[offs:offs+ln]
            return '\n'.join(lines) + '\n'

    def getline(self, offs):
        if self.ilff is not None:
            return self.ilff.getline(offs, ln)
        else:
            return self.lines[offs]

    def nlines(self):
        if self.ilff is not None:
            return self.ilff.get_nlines()
        else:
            return len(self.lines)

    def get_nlines(self):
        return self.nlines()


class CILFFGetLines(ILFFGetLines):

    def __init__(self, fname, mode='r', encoding='utf8'):
        super().__init__(fname, mode=mode, encoding=encoding, var='c')
