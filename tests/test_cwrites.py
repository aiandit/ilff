import unittest

import os
import sys

sys.path.append('..')

import ilff

class TestCILFFWrites1(unittest.TestCase):

    lines = ['aaa', 'bbbb b', 'ccccc cccc cc c']

    def test_01_create(self):
        ilf = ilff.CILFFFile('test.ilff', mode='w', encoding='utf8')
        self.assertTrue(os.path.exists('test.ilff'))
        ilf.close()

    def test_02_write(self):
        ilf = ilff.CILFFFile('test.ilff', mode='w', encoding='utf8')
        print(*map(lambda x: ilf.appendLine(x), self.lines))
        self.assertTrue(os.path.exists('test.ilff'))
        ilf.close()

    def test_03_get1(self):
        ilf = ilff.CILFFFile('test.ilff', mode='r', encoding='utf8')
        l1 = ilf.getline(0)
        print('L1:', l1)
        self.assertTrue(l1 == 'aaa')
        ilf.close()

    def test_04_get2(self):
        ilf = ilff.CILFFFile('test.ilff', encoding='utf8')
        for i in range(3):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l, '"%s"' % self.lines[i], l == self.lines[i])
            self.assertTrue(l == self.lines[i])
        ilf.close()

    def test_05_get3(self):
        ilf = ilff.CILFFFile('test.ilff', encoding='utf8')
        for i in range(3):
            l = ilf.getline(i)
            self.assertTrue(l == self.lines[i])
            print('L:', i, l, self.lines[i])
        ilf.close()

    def test_06_getlns(self):
        ilf = ilff.CILFFFile('test.ilff', encoding='utf8')
        lns = ilf.getlines(0, 3)
        self.assertTrue(lns == self.lines)
        ilf.close()

    def test_07_getlnstxt(self):
        ilf = ilff.CILFFFile('test.ilff', encoding='utf8')
        lns = ilf.getlinestxt(0, 3)
        self.assertTrue(lns == '\n'.join(self.lines))
        ilf.close()


class TestCILFFWrites2(unittest.TestCase):

    lines = ['aaa', 'bbbb b', 'ccccc cccc cc c']

    def test_01_append(self):
        ilf = ilff.CILFFFile('test.ilff', mode='w', encoding='utf8')
        print(*map(lambda x: ilf.appendLine(x), self.lines))
        self.assertTrue(os.path.exists('test.ilff'))
        ilf.close()

    def test_02_get2(self):
        ilf = ilff.CILFFFile('test.ilff', mode='r', encoding='utf8')
        for i in range(3):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l, '"%s"' % self.lines[i], l == self.lines[i])
            self.assertTrue(l == self.lines[i])
        self.assertTrue(ilf.nlines() == 3)
        ilf.close()

    def test_03_append(self):
        ilf = ilff.CILFFFile('test.ilff', mode='a', encoding='utf8')
        print(*map(lambda x: ilf.appendLine(x), self.lines))
        self.assertTrue(os.path.exists('test.ilff'))
        self.assertTrue(ilf.nlines() == 6)
        ilf.close()

    def test_04_get(self):
        ilf = ilff.CILFFFile('test.ilff', mode='r', encoding='utf8')
        for i in range(6):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l, '"%s"' % self.lines[i % 3], l == self.lines[i % 3])
            self.assertTrue(l == self.lines[i % 3])
        ilf.close()

    def test_05_getlns(self):
        ilf = ilff.ILFFFile('test.ilff', encoding='utf8')
        lns1 = ilf.getlinestxt(0, 3)
        lns = ilf.getlines(0, 3)
        print(ilf.nlines())
        self.assertTrue(lns == self.lines)
        lns = ilf.getlines(3, 3)
        self.assertTrue(lns == self.lines)
        ilf.close()

    def test_06_getlnstxt(self):
        ilf = ilff.CILFFFile('test.ilff', encoding='utf8')
        lns = ilf.getlinestxt(0, 6)
        self.assertTrue(lns == '\n'.join(self.lines + self.lines))
        ilf.close()


class TestCILFFWrites3(unittest.TestCase):

    lines = ['aaa', 'bbbb b', 'ccccc cccc cc c']

    fname = 'testw2.ilff'

    def test_01_write(self):
        of = open(self.fname, 'w')
        of.write('\n'.join(self.lines) + '\n')
        of.close()

    def test_01a_buildindex(self):
        ilf = ilff.CILFFFile(self.fname, 'a+')
        ilf.buildindex()
        ilf.close()

    def test_02_get(self):
        ilf = ilff.CILFFFile(self.fname)
        for i in range(3):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l, '"%s"' % self.lines[i], l == self.lines[i])
            self.assertTrue(l == self.lines[i])
        ilf.close()

    def test_03_get2(self):
        ilf = ilff.CILFFFile(self.fname, encoding='utf8')
        for i in range(3):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l)
            self.assertTrue(l == self.lines[i])
        ilf.close()


class TestCILFFWrites4(unittest.TestCase):

    lines = ['aaa', 'bbbb b', 'ccccc cccc cc c']

    def test_01_write(self):
        of = open('test.ilff', 'w')
        of.write('\n'.join(self.lines))
        of.close()

    def test_01a_buildindex(self):
        ilf = ilff.CILFFFile('test.ilff', 'a+')
        ilf.buildindex()
        ilf.close()

    def test_02_get(self):
        ilf = ilff.CILFFFile('test.ilff')
        for i in range(3):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l, '"%s"' % self.lines[i], l == self.lines[i])
            self.assertTrue(l == self.lines[i])
        ilf.close()

    def test_03_get2(self):
        ilf = ilff.CILFFFile('test.ilff', encoding='utf8')
        for i in range(3):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l)
            self.assertTrue(i > 2 or l == self.lines[i])
            self.assertTrue(i <= 2 or l == "")
        ilf.close()


if __name__ == '__main__':
    unittest.main()
