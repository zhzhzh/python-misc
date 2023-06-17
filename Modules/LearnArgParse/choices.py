import argparse


def get_parser():
    parser = argparse.ArgumentParser(
        description='choices demo')
    parser.add_argument('-arch', required=True, choices=['1', '2'])

    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    print(args)
    print('the arch of CNN is {}'.format(args.arch))
