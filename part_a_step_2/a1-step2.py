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
parser.add_argument('-scored_permutations', type=str, help='set of words as list')
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
    """Opens a file and inserts a START and STOP symbol on every double+
    new line"""
    text = open(corpus_filename, 'r').read()
    text = re.sub(r'(\n\n)+', ' 0STOP0 0START0 ', text)
    text = re.sub(r'(\n)', ' ', text)
    text = '<START>' + text
    text = text[:-9]
    return text


def file_to_list(file):
    """Opens a file and returns every line as a list entry"""
    text = open(file, 'r')
    return [re.sub(r'\n', '', line) for line in text]


def condition_probability(ngrams, ngrams_1, list_of_file):
    """Returns the conditional probability of a sequence of words from a file"""
    ngrams_counted = dict(Counter(ngrams))
    ngrams_1_counted = dict(Counter(ngrams_1))

    probabilities = {}
    for line in list_of_file:
        n_list = line.split()
        n_1_list = n_list[:-1]  # Removes the last word from line
        last_word = n_list[-1]  # The word that from which the probability needs to be computed

        #  Create tuples from the sequence of words because that is how the counted ngrams are stored.
        n_tuple = tuple(n_list)
        n_1_tuple = tuple(n_1_list)

        #  Find the count of the ngrams
        count_n = ngrams_counted.get(n_tuple)
        count_1_n = ngrams_1_counted.get(n_1_tuple)
        if count_n and count_1_n:
            prob = count_n / count_1_n
            probabilities[last_word] = prob
    return probabilities


def sequence_probability(corpus_start_stop, list_of_file):
    """Returns the probability of a sentence based on a ngram model"""
    all_probs = {}
    for line in list_of_file:
        list_of_line = line.split(' ')  # Split every sentence into a list
        grams_file = [list_of_line[:-idx] for idx, word in enumerate(list_of_line)]  # Creates list with sentences of
        #  n-1 words
        probabilities = []
        for grams in grams_file:
            length_of_string = len(grams)

            #  Gets n grams based on the length of the current n-1 sentence
            ngrams, _ = get_n_gram(corpus_start_stop, length_of_string)
            ngrams_1, _ = get_n_gram(corpus_start_stop, length_of_string - 1)
            ngrams_counted = dict(Counter(ngrams))
            ngrams_1_counted = dict(Counter(ngrams_1))

            #  Create tuples from the sequence of words because that is how the counted ngrams are stored.
            n_tuple = tuple(grams)
            n_1_list = grams[:-1]
            n_1_tuple = tuple(n_1_list)

            #  Find the count of the ngrams
            count_n = ngrams_counted.get(n_tuple)
            count_1_n = ngrams_1_counted.get(n_1_tuple)
            if count_n and count_1_n:
                prob = count_n / count_1_n
                probabilities.append(prob)
        prob = 1
        for prob in probabilities:
            prob *= prob
        all_probs[line] = prob
    return all_probs


def scored_permutations(text_start_stop, words):
    permutations = itertools.permutations(words)
    return sequence_probability(text_start_stop, permutations)


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
        pprint(sequence_probability(text_start_stop, list_of_file))
    if args.scored_permutations:
        print('Scored permutations')
        print(args.scored_permutations)
        scored_permutations(text_start_stop, args.scored_permutations)
