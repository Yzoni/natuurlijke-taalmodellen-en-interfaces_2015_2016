import argparse
import re


parser = argparse.ArgumentParser()
parser.add_argument('training_corpus', type=str, help='text file of training corpus')
parser.add_argument('test_corpus', type=str, help='text file of test corpus')
parser.add_argument('-n', type=str, help='value')
parser.add_argument('-smoothing', type=str, help='smoothing algorithm', default='no')
args = parser.parse_args()


def get_vocabulary_size(text_filename):
    """Returns the amount of words in a text file"""
    word_count = 0

    f = open(text_filename)
    for line in f:
        words = line.split()
        word_count += len(words)
    return word_count


def insert_start_stop(text_filename):
    """Opens a file and inserts a START and STOP symbol on every double+
    new line"""
    text = open(text_filename, 'r').read()
    text = re.sub(r'(\n\n)+', ' 0STOP0 0START0 ', text)
    text = re.sub(r'(\n)', ' ', text)
    text = '<START>' + text
    text = text[:-9]
    return text


if __name__ == "__main__":
    exit(1)
