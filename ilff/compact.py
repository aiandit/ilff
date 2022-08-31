import ilff

import sys

def run():
    fname = sys.argv[1]
    empty = ''
    if len(sys.argv) > 2:
        empty = sys.argv[2]
    il = ilff.ILFFFile(fname, mode='r+')
    il.compact(empty=empty)
    il.close()

if __name__ == "__main__":
    run()

