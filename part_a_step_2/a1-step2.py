#!/usr/bin/env python3.4
# a1-step2.py
# Names: Yorick de Boer, Julian Main, Amor Frans

import argparse
import re
from collections import Counter

parser = argparse.ArgumentParser()
parser.add_argument('corpus', type=str, help='text file of corpus')
parser.add_argument('-n', type=int, default=3, help='integer for the amount of words in sequence ')
parser.add_argument('-conditional_prob_file', type=str, help='conditional probability file')
parser.add_argument('-sequence_prob_file', type=str, help='sequential probability file')
args = parser.parse_args()


def get_n_gram(corpus, sequence_size):
    """Find frequencies of word sequences in a text file, returns a
    list of tuples."""
    words = re.findall(r'\w+', corpus)
    allngrams = []
    paragraph = []
    for word in words:
        paragraph.append(word)
        if word == "0STOP0":
            ngrams = list(zip(*[paragraph[i:] for i in range(sequence_size)]))
            allngrams += ngrams
            paragraph = []

    return allngrams

def insert_start_stop(corpus_filename):
    text = open(corpus_filename, 'r').read()
    text = re.sub(r'(\n\n)+', ' 0STOP0 0START0 ', text)
    text = re.sub(r'(\n)', ' ', text)
    text = '<START>' + text
    text = text[:-9]
    return text


def condition_probability(ngrams, ngrams_1, file):
    ngrams_counted = dict(Counter(ngrams))
    ngrams_1_counted = dict(Counter(ngrams_1))

    text = open(file, 'r')
    probabilities = {}
    for line in text:
        n_list = line.split()
        n_1_list = n_list[:-1]
        last_word = n_list[-1]

        n_tuple = tuple(n_list)
        n_1_tuple = tuple(n_1_list)

        count_n = ngrams_counted.get(n_tuple)
        count_1_n = ngrams_1_counted.get(n_1_tuple)
        if count_n and count_1_n:
            prob = count_n / count_1_n
            probabilities[last_word] = prob
    return probabilities


def sequence_probability():
    return -1


if __name__ == "__main__":
    text_start_stop = insert_start_stop(args.corpus)
    ngrams = get_n_gram(text_start_stop, args.n)
    ngrams_1 = get_n_gram(text_start_stop, args.n - 1)
    if args.conditional_prob_file:
        print(condition_probability(ngrams, ngrams_1, args.conditional_prob_file))
    if args.sequence_prob_file:
        print(sequence_probability())
