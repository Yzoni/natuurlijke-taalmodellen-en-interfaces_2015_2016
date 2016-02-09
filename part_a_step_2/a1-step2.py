#!/usr/bin/env python3.4
# a1-step2.py
# Names: Yorick de Boer, Julian Main, Amor Frans

import argparse
import itertools
import re
from collections import Counter
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument('corpus', type=str, help='text file of corpus')
parser.add_argument('-n', type=int, default=3, help='integer for the amount of words in sequence ')
parser.add_argument('-conditional_prob_file', type=str, help='conditional probability file')
parser.add_argument('-sequence_prob_file', type=str, help='sequential probability file')
parser.add_argument('-args.scored_permutations', type=str, help='set of words as list')
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

    return allngrams, Counter(allngrams).most_common(10)

def insert_start_stop(corpus_filename):
    text = open(corpus_filename, 'r').read()
    text = re.sub(r'(\n\n)+', ' 0STOP0 0START0 ', text)
    text = re.sub(r'(\n)', ' ', text)
    text = '<START>' + text
    text = text[:-9]
    return text


def file_to_list(file):
    text = open(file, 'r')
    return [line for line in text]


def condition_probability(ngrams, ngrams_1, list_of_file):
    ngrams_counted = dict(Counter(ngrams))
    ngrams_1_counted = dict(Counter(ngrams_1))

    probabilities = {}
    for line in list_of_file:
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


def sequence_probability(list_of_file):
    return -1


def scored_permutations(words):
    permutations = itertools.permutations(words)
    return sequence_probability(permutations)


if __name__ == "__main__":
    text_start_stop = insert_start_stop(args.corpus)
    ngrams, most_common = get_n_gram(text_start_stop, args.n)
    ngrams_1, _ = get_n_gram(text_start_stop, args.n - 1)
    print('Most common ngrams:')
    pprint(most_common)
    print('\n')
    if args.conditional_prob_file:
        print('Conditional probability:')
        list_of_file = file_to_list(args.conditional_prob_file)
        pprint(condition_probability(ngrams, ngrams_1, list_of_file))
    if args.sequence_prob_file:
        print('Sequential probability')
        list_of_file = file_to_list(args.sequence_prob_file)
        pprint(sequence_probability(list_of_file))
    if args.scored_permutations:
        scored_permutations(args.scored_permutations)
