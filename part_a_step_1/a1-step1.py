#!/usr/bin/env python3.4
# a1-step1.py
# Names: Yorick de Boer, Julian Main, Amor Frans

import argparse
from collections import Counter
from pprint import pprint


def create_ngrams(corpus, sequence_size):
    """"Find frequencies of word sequences in a text file, returns a
    list of tuples."""
    with open(corpus, 'r') as corpus_txt:
        word_list = [word for line in corpus_txt for word in line.split()]
    ngrams = list(zip(*[word_list[i:] for i in range(sequence_size)]))
    return ngrams


def count_ngrams(ngrams_list):
    """Returns a counted dictionary"""
    return Counter(ngrams_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('corpus', type=str, help='text file of corpus')
    parser.add_argument('-n', type=int, default=3, help='integer for the amount of words in sequence ')
    parser.add_argument('-m', type=int, default=10, help='integer for the amount of top frequencies')
    args = parser.parse_args()

    ngrams = (count_ngrams(create_ngrams(args.corpus, args.n)))
    mostcommon_ngrams = ngrams.most_common(args.m)
    pprint(mostcommon_ngrams)

    print('The sum of the frequencies is: {0}'.format(sum(ngrams.values())))
