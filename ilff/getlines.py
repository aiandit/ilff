import ilff
import sys

def run():
    ln1 = int(sys.argv[1])
    ln2 = int(sys.argv[2])
    fname = sys.argv[3]
    il = ilff.ILFFFile(fname)
    lns = il.getlines(ln1, ln2)
    for i in range(ln2):
        print(lns[i])

if __name__ == "__main__":
    run()
