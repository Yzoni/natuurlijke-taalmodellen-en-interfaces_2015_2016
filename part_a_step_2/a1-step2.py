#!/usr/bin/env python3.4
# a1-step2.py
# Names: Yorick de Boer, Julian Main, Amor Frans

import argparse
import re
from collections import Counter
from pprint import pprint


parser = argparse.ArgumentParser()
parser.add_argument('-corpus', type=str, help='text file of corpus')
parser.add_argument('-n', type=int, default=3, help='integer for the amount of words in sequence ')
parser.add_argument('-m', type=int, default=10, help='integer for the amount of top frequencies')
# parser.add_argument('conditional-prob-file', type=str, help='conditional probability file')
args = parser.parse_args()

def get_n_gram(corpus, sequence_size, amount_of_results):
    """Find frequencies of word sequences in a text file, returns a
    list of tuples."""
    words = re.findall(r'\w+', corpus)
    sequences = []
    for id, word in enumerate(words):
        paragraph = []
        paragraph.append(word)
        if word == "0STOP0":
            for j in range(len(words) - sequence_size + 1):
                sequences.append(' '.join(words[id:id + sequence_size]))
    return sequences, Counter(sequences).most_common(amount_of_results)

def insert_start_stop(corpus_filename):
    text = open(corpus_filename, 'r').read()
    text = re.sub(r'(\n\n)+', ' 0STOP0 0START0 ', text)
    text = re.sub(r'(\n)', ' ', text)
    text = '<START>' + text
    text = text[:-9]
    return text

def sequence_probability(sequence, corpus, n_grams, n_min_1_grams):
    pass

txt = insert_start_stop(args.corpus)
s, c = get_n_gram(txt, args.n, args.m)
print(s)
print(c)
