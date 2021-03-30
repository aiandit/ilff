import ilff

import sys

import random

import time

fname = sys.argv[1]

il = ilff.ILFFFile(fname)

start = 11100
ln = 2000

t0 = time.time()
l1 = il.getlinestxt(start, ln)
t1 = time.time()

print(t1-t0)

t0 = time.time()
l2 = "\n".join(open(fname).read().split('\n')[start:start+ln])
t1 = time.time()

print(t1-t0)

print(len(l1), len(l2))
assert(l1 == l2)
