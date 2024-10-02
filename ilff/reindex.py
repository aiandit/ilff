import ilff
import sys
from .nlines import parseargs


def run():
    args = parseargs('Refresh index of ILFF file')
    for fname in args.infiles:
        il = ilff.ILFFFile(fname, mode='a+', check=False)
        il.buildindex()
        il.close()


if __name__ == "__main__":
    run()

