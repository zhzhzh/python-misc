import argparse

def get_parser() -> argparse.ArgumentParser:
    new_parser = argparse.ArgumentParser(description='Tool to manager Pluto Alert DLs')
    new_parser.add_argument('--operation', default='get_member', help='execution operation', choices=['get_member', 'new_dl', 'add_member', 'set_public'])
    new_parser.add_argument('--dl', default=[], help='DL names to operation', nargs='*')
    new_parser.add_argument('--checkpoint', default=[], help='checkpoints to operation', nargs='*')
    new_parser.add_argument('--member', default=[], help='members to operation', nargs='*')
    new_parser.add_argument('--debug', action='store_true', default=False, help='set logger level to debug')
    return new_parser

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    print(f'Input args: {args}')
