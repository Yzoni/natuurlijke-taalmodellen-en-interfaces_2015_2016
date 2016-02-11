import argparse

parser = argparse.ArgumentParser()
parser.add_argument('traing_corpus', type=str, help='text file of train corpus')
parser.add_argument('test_corpus', type=str, help='text file of test corpus')
parser.add_argument('-n', type=str, help='value')
parser.add_argument('-smoothing', type=str, help='smoothing algorithm', default='no')
args = parser.parse_args()

if __name__ == "__main__":
    exit(1)
