import ilff

import sys

import random

fname = sys.argv[1]

il = ilff.ILFFFile(fname)

for k in range(1000):
    ln = random.sample(range(il.get_nlines()), 1)[0]
    l = il.getline(ln)
    #l = il.getlines(100, 300)
    print(k, ln, l)
