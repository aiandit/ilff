import ilff

import sys

ln = int(sys.argv[1])
fname = sys.argv[2]

il = ilff.ILFFFile(fname)

print(il.getline(ln))
