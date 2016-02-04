#!/usr/bin/env python3.4
# a1-step1.py
# Names: Yorick de Boer, Julian Main, Amor Frans

import argparse
import re
from collections import Counter
from pprint import pprint


parser = argparse.ArgumentParser()
parser.add_argument('corpus', type=str, help='text file of corpus')
parser.add_argument('-n', type=int, default=3, help='integer for the amount of words in sequence ')
parser.add_argument('-m', type=int, default=10, help='integer for the amount of top frequencies')
args = parser.parse_args()


def find_frequencies(corpus, sequence_size, amount_of_results):
    """"Find frequencies of word sequences in a text file, returns a
    list of tuples."""
    text = open(corpus, 'r').read().replace('\n', ' ')
    words = re.findall(r'\w+', text)
    sequences = []
    for i in range(len(words) - sequence_size + 1):
        sequences.append(' '.join(words[i:i + sequence_size]))
    return Counter(sequences).most_common(amount_of_results)


def sum_frequencies(list_tuples):
    """"Sum the second item of all tuples in a list of tuples"""
    return sum(x[1] for x in list_tuples)


def main():
    frequency_list = (find_frequencies(args.corpus, args.n, args.m))
    pprint(frequency_list)
    print('The sum of the frequencies is: {0}'.format(sum_frequencies(frequency_list)))

if __name__ == "__main__":
    main()
