import ilff

import sys

def run():
    fname = sys.argv[1]
    il = ilff.ILFFFile(fname)
    il.dumpIndex()

if __name__ == "__main__":
    run()
