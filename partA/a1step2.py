#!/usr/bin/env python3.4
# a1-step2.py
# Names: Yorick de Boer, Julian Main, Amor Frans

import argparse
import itertools
import re
from collections import Counter
from pprint import pprint

from a1step1 import create_ngrams


def insert_start_stop(corpus_filename):
    """Opens a file and inserts a START and STOP symbol on every double+
    new line"""
    text = open(corpus_filename, 'r').read()
    text = re.sub(r'(\n\n)+', ' 0STOP0 0START0 ', text)
    text = re.sub(r'(\n)', ' ', text)
    text = '0START0' + text
    text = text[:-9]
    return text


def extract_sentences(text_start_stop):
    """Extracts sentences from a text which have as delimiter a START and STOP symbol. Saves each sentence as a list
    element. Every sentence is saved as a list of words. The sentence also includes the start and stop symbols."""
    words = text_start_stop.split()
    sentences = []
    sentence = []
    for word in words:
        sentence.append(word)
        if word == '0STOP0':
            sentences.append(sentence)
            sentence = []
    return sentences


def create_ngrams_all_sentences(sentences, sequence_size):
    """Creates ngrams for all sentences separately and appends them to one flattened list"""
    ngrams = [create_ngrams(sentence, sequence_size) for sentence in sentences]
    flattend_ngrams = list(itertools.chain(*ngrams))
    return flattend_ngrams


def product_list(thelist):
    prod = 1
    for operand in thelist:
        prod *= operand
    return prod


def condition_probability(ngrams, ngrams_1, cond_file):
    """Returns the conditional probability of a sequence of words from a file"""
    ngrams_counted = dict(Counter(ngrams))
    ngrams_1_counted = dict(Counter(ngrams_1))
    probabilities = {}
    cond_file_txt = open(cond_file, 'r')
    for line in cond_file_txt:
        n_list = line.split()
        n_1_list = n_list[:-1]  # Removes the last word from line
        last_word = n_list[-1]  # The word from which the probability needs to be computed

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


def sequence_probability(corpus_start_stop, seq_file):
    """Returns the probability of a sentence based on a ngram model"""
    all_probs = {}
    seq_file_txt = open(seq_file, 'r')
    for line in seq_file_txt:
        list_of_line = line.split()  # Split every sentence into a list
        grams_file = [list_of_line[:-idx] for idx, word in enumerate(list_of_line)]  # Creates list with sentences of
        #  n-1 words
        probabilities = []
        for grams in grams_file:
            length_of_string = len(grams)

            #  Gets n grams based on the length of the current n-1 sentence
            ngrams = create_ngrams(corpus_start_stop, length_of_string)
            ngrams_1 = create_ngrams(corpus_start_stop, length_of_string - 1)
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
        all_probs[line] = product_list(probabilities)
    return all_probs


def scored_permutations(text_start_stop, words):
    permutations = itertools.permutations(words)
    return sequence_probability(text_start_stop, permutations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('corpus', type=str, help='text file of corpus')
    parser.add_argument('-n', type=int, default=3, help='integer for the amount of words in sequence ')
    parser.add_argument('-conditional_prob_file', type=str, help='conditional probability file')
    parser.add_argument('-sequence_prob_file', type=str, help='sequential probability file')
    parser.add_argument('-scored_permutations', type=str, help='set of words as list')
    args = parser.parse_args()

    text_start_stop = insert_start_stop(args.corpus)
    extracted_sentences = extract_sentences(text_start_stop)
    ngrams_all_sentences = create_ngrams_all_sentences(extracted_sentences, args.n)
    ngrams_1_all_sentences = create_ngrams_all_sentences(extracted_sentences, args.n - 1)

    print('\n')
    if args.conditional_prob_file:
        print('Conditional probability:')
        pprint(condition_probability(ngrams_all_sentences, ngrams_1_all_sentences, args.conditional_prob_file))
    if args.sequence_prob_file:
        print('Sequential probability')
        pprint(sequence_probability(text_start_stop, args.sequence_prob_file))
    if args.scored_permutations:
        print('Scored permutations')
        print(args.scored_permutations)
        scored_permutations(text_start_stop, args.scored_permutations)
