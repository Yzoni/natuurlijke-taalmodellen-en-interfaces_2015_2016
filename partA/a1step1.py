#!/usr/bin/env python3.4
# a1-step1.py
# Names: Yorick de Boer, Julian Main, Amor Frans

import argparse
from collections import Counter
from pprint import pprint


def file_to_list(corpus):
    with open(corpus, 'r') as corpus_txt:
        word_list = [word for line in corpus_txt for word in line.split()]
    return word_list


def create_ngrams(word_list, sequence_size):
    """"Find frequencies of word sequences in a text file, returns a
    list of tuples."""
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

    list_of_words = file_to_list(args.corpus)
    ngrams = create_ngrams(list_of_words, args.n)
    counted_ngrams = count_ngrams(ngrams)
    mostcommon_ngrams = counted_ngrams.most_common(args.m)
    pprint(mostcommon_ngrams)

    print('The sum of the frequencies is: {0}'.format(sum(counted_ngrams.values())))
