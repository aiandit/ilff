import ilff
import sys
import argparse


def parseargs():
  parser = argparse.ArgumentParser(description='Get line from ILFF file.')

  #parser.add_argument('--debug', action='store_true', help='Debug output')
  #parser.add_argument('--verbose', action='store_true', help='Verbose output')

  parser.add_argument('--outfile', '-o', type=str, help='Output file')

  parser.add_argument('infile', metavar='ILFF-File', type=str, help='Input file name')
  parser.add_argument('line', metavar='Line number', type=int, nargs='+', help='Line number')

  args = parser.parse_args()
  return args


def run():
    args = parseargs()

    fname = args.infile

    il = ilff.ILFFFile(fname)
    if not il.isILFF:
        print(f'{fname} is not an ILFF-File')
        sys.exit(1)

    if args.outfile:
        of = open(args.outfile, 'w')
    else:
        of = sys.stdout

    for ln in args.line:
        l = il.getline(ln)
        of.write(l)
        of.write('\n')


if __name__ == "__main__":
    run()
