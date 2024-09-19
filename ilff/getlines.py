import ilff
import sys
import argparse
from . import VERSION


def parseargs():
  parser = argparse.ArgumentParser(description='Get line range from ILFF file.')

  parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')

  #parser.add_argument('--debug', action='store_true', help='Debug output')
  #parser.add_argument('--verbose', action='store_true', help='Verbose output')

  parser.add_argument('--begin', '-b', type=int, help='Begin index')
  parser.add_argument('--end', '-e', type=int, help='End index')
  parser.add_argument('--number-of-lines', '-n', type=int, help='Number of lines')

  parser.add_argument('--lines', '-l', type=str, help='Line range begin:num')

  parser.add_argument('--outfile', '-o', type=str, help='Output file')

  parser.add_argument('infile', metavar='ILFF-File', type=str, help='Input file name')

  args = parser.parse_args()
  return args


def getRange(args):
    b = None
    e = None
    n = None

    if args.lines:
        items = args.lines.split(':')
        if len(items) < 2:
            print('argument to -l must contain a colon (":")')
            sys.exit(1)

        [b, n] = [int(i) for i in items[0:2]]
    elif args.begin is None:
        print('-l or -b must be given')
        sys.exit(1)
    else:
        b = args.begin

        if args.end is not None:
            e = args.end
            n = e - b
        elif args.number_of_lines is not None:
            n = args.number_of_lines
        else:
            print('-n or -e must be given')
            sys.exit(1)

    return (b, n)


def run():
    args = parseargs()

    (b, n) = getRange(args)

    fname = args.infile

    il = ilff.ILFFFile(fname)

    lns = il.getlines(b, n)

    if args.outfile:
        of = open(args.outfile, 'w')
    else:
        of = sys.stdout

    of.write('\n'.join(lns))
    if n > 0:
        of.write('\n')


if __name__ == "__main__":
    run()
