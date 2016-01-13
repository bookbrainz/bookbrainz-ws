import unittest
import tests
import logging
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--logs', help='log level')
args = parser.parse_args()

if args.logs:
    logging.basicConfig(
        format='%(levelname)s:%(message)s',
        level=getattr(logging, args.logs.upper(), None)
    )
else:
    logging.basicConfig(
        format='%(levelname)s:%(message)s',
        level=logging.CRITICAL
    )

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main(tests)
