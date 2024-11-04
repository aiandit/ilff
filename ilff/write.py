import ilff
import sys
import argparse
from . import VERSION


def parseargs():
  parser = argparse.ArgumentParser(description='Append line(s) to ILFF file.')

  parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')

  parser.add_argument('infile', metavar='ILFF-File', type=str, help='input file name')
  parser.add_argument('line', type=str, help='line to append')

  args = parser.parse_args()
  return args


def run():
    args = parseargs()

    fname = args.infile

    il = ilff.ILFFFile(fname, 'a')
    if not il.isILFF:
        print(f'{fname} is not an ILFF-File')
        sys.exit(1)

    if args.line and args.line != '-':
        of = open(args.line, 'r')
    else:
        of = sys.stdin

    with of:
      line = of.read()

    il.write(line)


if __name__ == "__main__":
    run()
