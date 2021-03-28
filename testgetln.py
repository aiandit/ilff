import ilff

import sys

import random

fname = sys.argv[1]

il = ilff.ILFFFile(fname)

lines = open(fname).read().split('\n')

print('%d lines in %s' % (len(lines), fname))

print('%d lines in %s' % (il.get_nlines(), fname))

for k in range(1000):
    ln = random.sample(range(il.get_nlines()), 1)[0]
#    print(k, ln)
    l = il.getline(ln)
    #l = il.getlines(100, 300)
#    print(l)
#    print(ln)
#    print(type(ln))
#    print(len(lines))
#    print(lines[ln])
#    print(k, ln, l == lines[ln])
    assert(l == lines[ln])
