import ilff

import sys

def run():
    fname = sys.argv[1]
    il = ilff.ILFFFile(fname, mode='w')
    il.remove()

if __name__ == "__main__":
    run()

