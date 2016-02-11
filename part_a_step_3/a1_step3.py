import argparse
import re
from collections import Counter

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


def get_n_gram_string(text_string, sequence_size):
    return list(zip(*[text_string[i:] for i in range(sequence_size)]))


def get_n_gram_text(text_string, sequence_size):
    """Find frequencies of word sequences in a text string returns a
    list of tuples."""
    words = re.findall(r'\w+', text_string)
    allngrams = []
    paragraph = []
    for word in words:
        paragraph.append(word)
        if word == "0STOP0":
            ngrams = get_n_gram_string(text_string, sequence_size)
            allngrams += ngrams
            del paragraph[:]  # Make list empty for next paragraph

    return allngrams


def no_smoothing():
    return -1


def add_one_smoothing(ngram_count, n_1_gram_count, test_file, sequence_size, voc_size):
    """
    Returns probabilities as a list for all paragraphs in a test file
    :param ngram_count: dictionary with ngram count from training file
    :param n_1_gram_count: dictionary with ngram - 1 count from training data
    :param test_file: file to test
    :param sequence_size: size of the ngram
    :param voc_size: the vocabulary size
    :return: list of probabilities per paragraph
    """
    testtext_start_stop = insert_start_stop(test_file)  # Add start stop symbols to test file
    words = re.findall(r'\w+', testtext_start_stop)
    probabilities = []
    paragraph = []
    for word in words:
        paragraph.append(word)
        if word == "0STOP0":  # Paragraph end
            paragraph.append(word)  # Add stop symbol to paragraph

            paragraph_string = ' '.join(paragraph)  # get_n_gram() expects a string
            paragraph_ngrams = get_n_gram_string(paragraph_string, sequence_size)

            prob = 1
            for p_ngram in paragraph_ngrams:
                p_ngram_count = ngram_count.get(tuple(p_ngram)) + 1
                p_n_1_gramn_count = n_1_gram_count.get(tuple(p_ngram[:-1])) + voc_size
                prob *= (p_ngram_count / p_n_1_gramn_count)
            probabilities.append(prob)
            del paragraph[:]  # Make list empty for next paragraph
    return probabilities


def good_turing_smoothing():
    return -1


if __name__ == "__main__":
    text_start_stop = insert_start_stop(args.training_corpus)
    ngrams = get_n_gram_text(text_start_stop, args.n)
    n_1_grams = get_n_gram_text(text_start_stop, args.n - 1)
    ngram_count = dict(Counter(ngrams))
    n_1_gram_count = dict(Counter(n_1_grams))

    if args.smoothing == 'no':
        no_smoothing()
    elif args.smoothing == 'add1':
        add_one_smoothing(ngram_count, n_1_gram_count, args.test_corpus, args.n,
                          get_vocabulary_size(args.training_corpus))
    elif args.smoothing == 'gt':
        good_turing_smoothing()
