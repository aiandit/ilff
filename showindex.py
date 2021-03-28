import ilff

import sys

fname = sys.argv[1]

il = ilff.ILFFFile(fname)

il.dumpIndex()

