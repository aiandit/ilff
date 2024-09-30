import ilff

import sys

import random

import time

fname = sys.argv[1]

il = ilff.ILFFGetLines(fname)

start = 10
ln = 5

t0 = time.time()
l2 = open(fname).read().split('\n')[start:start+ln] + ['']
t1 = time.time()

print(t1-t0)

l1 = []

t0 = time.time()
l1 = il.getlinestxt(start, ln).split('\n')
t1 = time.time()

print(t1-t0)

print(len(l1), len(l2))
assert(l1 == l2)

l1 = il.getlines(start, ln)
assert(l1 == [l + '\n' for l in l2[0:-1]])

for i in range(ln):
    l1 = il.getline(start+i)
    assert(l1 == l2[i] + '\n')

assert(il.get_nlines() == len(open(fname).read().split('\n')) - 1)
