import ilff

import sys
import argparse


def parseargs(cmdargs=None):

    parser = argparse.ArgumentParser(description='ILFF cat tool')

    parser.add_argument('--version', type=int, nargs='?', const=1, help='Show version')
    parser.add_argument('--verbose', type=int, nargs='?', const=1, help='Verbose output')

    parser.add_argument('--append', '-a', action='store_true', help='Append')

    parser.add_argument('outfile', type=str, nargs='*', help='Output files')


    args = parser.parse_args(cmdargs)

    return args


def run():

    args = parseargs()

    if args.version:
        print(f'ILFF tee version {ilff.VERSION}')
        return

    mode = 'a' if args.append else 'w'

    ofiles = []
    for i in args.outfile:
        il = ilff.ILFFFile(i, mode)
        ofiles.append(il)

    infile = sys.stdin

    while True:
        s = infile.readline()
        if len(s) > 0:

            for of in ofiles:
                of.appendLine(s)

        else:
            if len(s) > 0:
                continue
            else:
                break


if __name__ == "__main__":
    run()
