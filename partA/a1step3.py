import argparse
import re
from collections import Counter
from pprint import pprint

from a1step2 import insert_start_stop


def get_vocabulary_size(text_filename):
    """Returns the amount of words in a text file"""
    f = open(text_filename)
    text = f.read().split()
    return len(Counter(text))


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
            ngrams = get_n_gram_string(paragraph, sequence_size)
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
            paragraph_ngrams = get_n_gram_string(paragraph, sequence_size)

            prob = 1
            for p_ngram in paragraph_ngrams:

                p_ngram_count = ngram_count.get(p_ngram)  # Returns non if not found
                if p_ngram_count is None:
                    p_ngram_count = 1
                else:
                    p_ngram_count += 1

                p_n_1_gramn_count = n_1_gram_count.get(p_ngram[:-1])
                if p_n_1_gramn_count is None:
                    p_n_1_gramn_count = voc_size
                else:
                    p_n_1_gramn_count += voc_size

                prob *= (p_ngram_count / p_n_1_gramn_count)
            probabilities.append(prob)
            del paragraph[:]  # Make list empty for next paragraph
    return probabilities


def good_turing_smoothing(ngram_count, test_file, sequence_size, length_ngrams):
    testtext_start_stop = insert_start_stop(test_file)  # Add start stop symbols to test file
    words = re.findall(r'\w+', testtext_start_stop)
    probabilities = []
    paragraph = []

    values = [ngram_count.get(key_bigram_count) for key_bigram_count in ngram_count]
    counted_values = Counter(values)
    pprint(counted_values)

    for word in words:
        paragraph.append(word)
        if word == "0STOP0":  # Paragraph end
            paragraph_ngrams = get_n_gram_string(paragraph, sequence_size)

            prob = 1
            for p_ngram in paragraph_ngrams:
                c = ngram_count.get(p_ngram)  # Returns non if not found
                if c is not None and c <= 5:  # assignment description says so
                    # Nc+1
                    if c is None:
                        c = 0
                        # Nc+1
                        count_nc1 = counted_values.get(c + 1)
                        prob *= count_nc1 / length_ngrams
                    else:
                        # Nc+1
                        count_nc1 = counted_values.get(c + 1)
                        # Nc
                        count_nc = counted_values.get(c)
                        c_star = ((c + 1) * count_nc1) / count_nc
                        prob *= c_star / length_ngrams
            probabilities.append(prob)
            del paragraph[:]  # Make list empty for next paragraph
    return probabilities


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('training_corpus', type=str, help='text file of training corpus')
    parser.add_argument('test_corpus', type=str, help='text file of test corpus')
    parser.add_argument('-n', type=int, help='value')
    parser.add_argument('-smoothing', type=str, help='smoothing algorithm', default='no')
    args = parser.parse_args()

    text_start_stop = insert_start_stop(args.training_corpus)
    ngrams = get_n_gram_text(text_start_stop, args.n)
    length_ngrams = len(ngrams)
    n_1_grams = get_n_gram_text(text_start_stop, args.n - 1)
    ngram_count = dict(Counter(ngrams))
    n_1_gram_count = dict(Counter(n_1_grams))
    if args.smoothing == 'no':
        no_smoothing()
    elif args.smoothing == 'add1':
        pprint(add_one_smoothing(ngram_count, n_1_gram_count, args.test_corpus, args.n,
                                 get_vocabulary_size(args.training_corpus)))
    elif args.smoothing == 'gt':
        pprint(good_turing_smoothing(ngram_count, args.test_corpus, args.n, length_ngrams))
