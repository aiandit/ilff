import ilff
import sys

def run():
    fname = sys.argv[1]
    il = ilff.ILFFFile(fname)
    n = il.get_nlines()
    print(n)
    il.close

if __name__ == "__main__":
    run()
