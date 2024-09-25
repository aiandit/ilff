import ilff

import sys

import random

import time

random.seed(time.time())

fname = sys.argv[1]

il = ilff.ILFFFile(fname)

lines = open(fname).read().split('\n')

print('%d lines in %s' % (len(lines), fname))

print('%d lines in %s' % (il.get_nlines(), fname))

for k in range(15):
    ln = k
#    print(k, ln)
    l = il.getline(ln)
    #l = il.getlines(100, 300)
#    print(ln)
#    print(l)
#    print(type(ln))
#    print(len(lines))
#    print(lines[ln])
#    print(k, ln, l == lines[ln])
    assert(l == lines[ln] + '\n')

for k in range(100):
    ln = random.sample(range(il.get_nlines()), 1)[0]
#    print(k, ln)
    l = il.getline(ln)
    #l = il.getlines(100, 300)
#    print(ln)
#    print(l)
#    print(type(ln))
#    print(len(lines))
#    print(lines[ln])
    assert(l == lines[ln] + '\n')
