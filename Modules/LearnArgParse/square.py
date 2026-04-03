import argparse


def get_parser():
    parser = argparse.ArgumentParser(description="Calculate square of a given number")
    parser.add_argument("-number", type=int)

    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    res = args.number**2
    print(f"square of {args.number} is {res}")
