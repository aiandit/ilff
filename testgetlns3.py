import ilff

import sys

import random

import time

fname = sys.argv[1]

il = ilff.ILFFFile(fname)

start = 101
ln = 2

t0 = time.time()
l1 = il.getlinestxt(start, ln).split('\n')
t1 = time.time()

print(t1-t0)

t0 = time.time()
l2 = open(fname).read().split('\n')[start:start+ln] + ['']
t1 = time.time()

print(t1-t0)

print(l1[0:3])
print(l2[0:3])

print(len(l1), len(l2))
assert(l1 == l2)
