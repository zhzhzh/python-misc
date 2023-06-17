import argparse

parser = argparse.ArgumentParser(description="description")

parser.add_argument('--pa','-a',action='store_true')
parser.add_argument('--pb','-b',action="store_true",default=True)
parser.add_argument('--pc','-c',action="store_true",default=False)

parser.add_argument('--pd','-d',action='store_false')
parser.add_argument('--pe','-e',action="store_false",default=True)
parser.add_argument('--pf','-f',action="store_false",default=False)

parser.add_argument('--skip-check', action='store_true', default=False, help='skip RR status check')

args = parser.parse_args()
print(args)