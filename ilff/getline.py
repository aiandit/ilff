import ilff
import sys

def run():
    ln = int(sys.argv[1])
    fname = sys.argv[2]
    il = ilff.ILFFFile(fname)
    print(il.getline(ln))

if __name__ == "__main__":
    run()
