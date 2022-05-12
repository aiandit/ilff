import unittest

import os
import sys

sys.path.append('..')

import ilff

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

class TestILFFWrites(unittest.TestCase):

    lines = ['aaa', 'bbbb b', 'ccccc cccc cc c']

    def test_01_create(self):
        ilf = ilff.ILFFFile('test.ilff', mode='w', encoding='utf8')
        self.assertTrue(os.path.exists('test.ilff'))
        ilf.close()

    def test_02_append(self):
        ilf = ilff.ILFFFile('test.ilff', mode='w', encoding='utf8')
        print(*map(lambda x: ilf.appendLine(x), self.lines))
        self.assertTrue(os.path.exists('test.ilff'))
        ilf.dumpIndex()
        ilf.close()

    def test_03_get1(self):
        ilf = ilff.ILFFFile('test.ilff', mode='r', encoding='utf8')
        l1 = ilf.getline(0)
        print('L1:', l1)
        self.assertTrue(l1 == 'aaa')
        ilf.close()

    def test_04_get2(self):
        ilf = ilff.ILFFFile('test.ilff', encoding='utf8')
        ilf.dumpIndex()
        for i in range(3):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l, '"%s"' % self.lines[i], l == self.lines[i])
            self.assertTrue(l == self.lines[i])
        ilf.close()

    def test_05_get3(self):
        ilf = ilff.ILFFFile('test.ilff', encoding='utf8')
        for i in range(3):
            l = ilf.getline(i)
            self.assertTrue(l == self.lines[i])
            print('L:', i, l, self.lines[i])
        ilf.close()


class TestILFFWrites(unittest.TestCase):

    lines = ['aaa', 'bbbb b', 'ccccc cccc cc c']

    def test_01_append(self):
        ilf = ilff.ILFFFile('test.ilff', mode='w', encoding='utf8')
        print(*map(lambda x: ilf.appendLine(x), self.lines))
        self.assertTrue(os.path.exists('test.ilff'))
        ilf.close()

    def test_02_get2(self):
        ilf = ilff.ILFFFile('test.ilff', mode='r', encoding='utf8')
        for i in range(3):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l, '"%s"' % self.lines[i], l == self.lines[i])
            self.assertTrue(l == self.lines[i])
        ilf.close()

    def test_03_append(self):
        ilf = ilff.ILFFFile('test.ilff', mode='a', encoding='utf8')
        print(*map(lambda x: ilf.appendLine(x), self.lines))
        self.assertTrue(os.path.exists('test.ilff'))
        ilf.close()

    def test_04_get(self):
        ilf = ilff.ILFFFile('test.ilff', mode='r', encoding='utf8')
        for i in range(6):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l, '"%s"' % self.lines[i % 3], l == self.lines[i % 3])
            self.assertTrue(l == self.lines[i % 3])
        ilf.close()


class TestILFFWrites2(unittest.TestCase):

    lines = ['aaa', 'bbbb b', 'ccccc cccc cc c']

    def test_01_write(self):
        of = open('test.ilff', 'w')
        of.write('\n'.join(self.lines) + '\n')
        of.close()

    def test_01a_buildindex(self):
        ilf = ilff.ILFFFile('test.ilff', 'a+')
        ilf.buildindex()
        ilf.close()

    def test_02_get(self):
        ilf = ilff.ILFFFile('test.ilff')
        for i in range(3):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l, '"%s"' % self.lines[i], l == self.lines[i])
            self.assertTrue(l == self.lines[i])
        ilf.close()

    def test_03_get2(self):
        ilf = ilff.ILFFFile('test.ilff', encoding='utf8')
        for i in range(3):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l)
            self.assertTrue(l == self.lines[i])
        ilf.close()


class TestILFFWrites3(unittest.TestCase):

    lines = ['aaa', 'bbbb b', 'ccccc cccc cc c']

    def test_01_write(self):
        of = open('test.ilff', 'w')
        of.write('\n'.join(self.lines))
        of.close()

    def test_01a_buildindex(self):
        ilf = ilff.ILFFFile('test.ilff', 'a+')
        ilf.buildindex()
        ilf.close()

    def test_02_get(self):
        ilf = ilff.ILFFFile('test.ilff')
        for i in range(3):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l, '"%s"' % self.lines[i], l == self.lines[i])
            self.assertTrue(l == self.lines[i])
        ilf.close()

    def test_03_get2(self):
        ilf = ilff.ILFFFile('test.ilff', encoding='utf8')
        for i in range(3):
            l = ilf.getline(i)
            print('L:', i, '"%s"' % l)
            self.assertTrue(i > 2 or l == self.lines[i])
            self.assertTrue(i <= 2 or l == "")
        ilf.close()


if __name__ == '__main__':
    unittest.main()
