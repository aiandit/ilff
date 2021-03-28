import ilff

import sys

ln1 = int(sys.argv[1])
ln2 = int(sys.argv[2])
fname = sys.argv[3]

il = ilff.ILFFFile(fname)

for i in range(ln2):
    print(il.getline(ln1 + i))
