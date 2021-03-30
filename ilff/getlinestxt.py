import ilff
import sys

def run():
    ln1 = int(sys.argv[1])
    ln2 = int(sys.argv[2])
    fname = sys.argv[3]
    il = ilff.ILFFFile(fname)
    lns = il.getlinestxt(ln1, ln2)
    print(lns)

if __name__ == "__main__":
    run()
