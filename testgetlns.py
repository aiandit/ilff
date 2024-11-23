import ilff

import sys

import random

import time

fname = sys.argv[1]

il = ilff.open(fname)

start = 110
ln = 25

t0 = time.time()
l1 = il.getlines(start, ln)
t1 = time.time()

print(t1-t0)

t0 = time.time()
l2 = open(fname).read().split('\n')[start:start+ln]
l2 = [ l + '\n' for l in l2 ]
t1 = time.time()

print(t1-t0)

print(l1[0:3])
print(l2[0:3])

print(len(l1), len(l2))
assert(l1 == l2)
