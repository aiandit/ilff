import ilff

import sys

import random

import time

fname = sys.argv[1]

il = ilff.ILFFFile(fname)

start = 101100
ln = 3

t0 = time.time()
l2 = open(fname).read().split('\n')[start:start+ln]
t1 = time.time()

print(t1-t0)
print(l2[0:3])

l1 = []

t0 = time.time()
l1 = il.getlinestxt(start, ln)
print('Text:', l1, len(l1))
l1 = l1.split('\n')
print('Text:', l1, len(l1))
t1 = time.time()

print(t1-t0)
print(l1[0:3])

print(len(l1), len(l2))
assert(l1 == [''])
assert(l2 == [])
