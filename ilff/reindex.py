import ilff

import sys

def run():
    fname = sys.argv[1]
    il = ilff.ILFFFile(fname, mode='a')
    il.buildindex()
    il.close()

if __name__ == "__main__":
    run()

