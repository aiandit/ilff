import ilff
from . import VERSION
import sys
import argparse


def parseargs(help):
  parser = argparse.ArgumentParser(description=help)

  parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')

  #parser.add_argument('--debug', action='store_true', help='Debug output')
  #parser.add_argument('--verbose', action='store_true', help='Verbose output')

  parser.add_argument('infiles', metavar='ILFF-File', nargs='*', type=str, help='Input file')

  args = parser.parse_args()
  return args


def run():

    args = parseargs('Get line range from ILFF file.')

    for fname in args.infiles:
        il = ilff.ILFFFile(fname)
        if il.isILFF:
            print(fname, il.get_nlines())
        else:
            print(fname, "not an ILFF file")


if __name__ == "__main__":
    run()
