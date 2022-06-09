import ilff
import sys

def run():
    if len(sys.argv) < 2:
        print('Usage: ilff-nlines filename')
        return
    for i in range(len(sys.argv) - 1):
        fname = sys.argv[i+1]
        il = ilff.ILFFFile(fname)
        if il.isILFF:
            print(fname, il.get_nlines())
        else:
            print(fname, "not an ILFF file")

if __name__ == "__main__":
    run()
