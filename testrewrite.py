import ilff

import sys

import random

import time

fname = sys.argv[1]

il = ilff.ILFFFile('test.ilf', append=False)

t0 = time.time()
il.fromfile(open(fname))
t1 = time.time()

print('rewrite', t1-t0)

start = 6
ln = 2

t0 = time.time()
l1 = il.getlines(start, ln)
t1 = time.time()

il.close()

print(t1-t0)

t0 = time.time()
l2 = open('test.ilf', 'r').read().split('\n')[start:start+ln]
t1 = time.time()

print(t1-t0)

print(l1[0:3])
print(l2[0:3])

print(len(l1), len(l2))
assert(l1 == l2)
