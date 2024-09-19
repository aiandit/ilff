import ilff
import sys
from .nlines import parseargs


def run():
    args = parseargs('Show index of ILFF file.')
    for fname in args.infiles:
        il = ilff.ILFFFile(fname)
        il.dumpIndex()


if __name__ == "__main__":
    run()
