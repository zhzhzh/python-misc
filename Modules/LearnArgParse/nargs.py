# file-name: nargs.py
import argparse

def get_parser():
    parser = argparse.ArgumentParser(
        description='nargs demo')
    parser.add_argument('-name', required=True, nargs='+')

    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    print(args.name)
    names = ', '.join(args.name)
    print('Hello to {}'.format(names))