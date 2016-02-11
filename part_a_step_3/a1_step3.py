import argparse

parser = argparse.ArgumentParser()
parser.add_argument('training_corpus', type=str, help='text file of training corpus')
parser.add_argument('test_corpus', type=str, help='text file of test corpus')
parser.add_argument('-n', type=str, help='value')
parser.add_argument('-smoothing', type=str, help='smoothing algorithm', default='no')
args = parser.parse_args()


def get_vocabulary_size(training_corpus):
    """Returns the amount of words in a text file"""
    word_count = 0

    f = open(training_corpus)
    for line in f:
        words = line.split()
        word_count += len(words)
    return word_count

if __name__ == "__main__":
    exit(1)
