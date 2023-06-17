import argparse


def get_parser():
    parser = argparse.ArgumentParser(description="Demo for argparse")
    parser.add_argument('--name', default='Great')

    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    print(args)
    name = args.name
    print('Hello {}'.format(name))
