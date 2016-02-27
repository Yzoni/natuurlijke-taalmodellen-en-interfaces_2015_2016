import argparse
from collections import Counter
from pprint import pprint

from a1step1 import create_ngrams
from a1step2 import create_ngrams_all_sentences
from a1step2 import extract_sentences
from a1step2 import insert_start_stop


def get_vocabulary_size(text_filename):
    """Returns the amount of words in a text file"""
    f = open(text_filename)
    text = f.read().split()
    return len(Counter(text))


def no_smoothing():
    return -1


def sequential_add_one_smoothing(ngram_count, n_1_gram_count, test_sentences, sequence_size, voc_size):
    if sequence_size > 1:
        voc_size = len(ngram_count)
    probabilities = []
    for sentence in test_sentences:
        sentence_ngrams = create_ngrams(sentence, sequence_size)

        prob = 1
        for p_ngram in sentence_ngrams:
            prob *= conditional_add_one_smoothing(ngram_count, n_1_gram_count, p_ngram, voc_size)
        probabilities.append(prob)
    return probabilities


def conditional_add_one_smoothing(ngram_count, n_1_gram_count, ngram_test, voc_size):
    p_ngram_count = ngram_count.get(ngram_test)  # Returns non if not found
    if p_ngram_count is None:
        p_ngram_count = 1
    else:
        p_ngram_count += 1

    p_n_1_gramn_count = n_1_gram_count.get(ngram_test[:-1])
    if p_n_1_gramn_count is None:
        p_n_1_gramn_count = voc_size
    else:
        p_n_1_gramn_count += voc_size

    return (p_ngram_count / p_n_1_gramn_count)


def sequential_good_turing_smoothing(ngram_count, ngram_1_count, test_sentences, sequence_size, voc_size, k):
    probabilities = []
    nnc_counts = nc_counts(ngram_count)

    for sentence in test_sentences:
        paragraph_ngrams = create_ngrams(sentence, sequence_size)

        prob = 1
        for p_ngram in paragraph_ngrams:
            prob *= conditional_good_turing_smoothing(nnc_counts, ngram_count, ngram_1_count, p_ngram, voc_size, k)
        probabilities.append(prob)
    return probabilities


def conditional_good_turing_smoothing(nnc_counts, ngram_count, ngram_1_count, p_ngram, voc_size, k):
    """Gets the good turing smoothed count from one ngram"""
    cgt = good_turing_count(nnc_counts, ngram_count, p_ngram, voc_size, k)
    c_n_1 = ngram_1_count.get(p_ngram[:-1])
    if c_n_1 is None:
        return 0
    return cgt / c_n_1


def good_turing_count(nc_counts, ngram_count, ngram_test, voc_size, k):
    """Gets the good turing smoothed count from one ngram"""
    c = ngram_count.get(ngram_test)
    if c is None:
        c = 0
    ncounts_inc_zero = [voc_size ** 2 - sum(nc_counts)] + nc_counts
    return good_turing_function(c, ncounts_inc_zero, k)


def nc_counts(ngram_count):
    """Creates a list of Nc counts assumes no gaps"""
    values = [ngram_count.get(key_bigram_count) for key_bigram_count in ngram_count]
    counted_values = list(dict(Counter(values)).values())
    return counted_values


def good_turing_function(r, n, k):
    """Good Turing smoothing function"""
    if 1 <= r <= k:
        return ((r + 1) * (float(n[r + 1]) / n[r]) - r * (float((k + 1) * n[k + 1]) / n[1])) / \
               (1 - (float((k + 1) * n[k + 1]) / n[1]))
    elif r > k:
        return r
    else:  # Unseen r = 0
        return n[r + 1] / n[r]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('training_corpus', type=str, help='text file of training corpus')
    parser.add_argument('test_corpus', type=str, help='text file of test corpus')
    parser.add_argument('-n', type=int, help='value')
    parser.add_argument('-smoothing', type=str, help='smoothing algorithm', default='no')
    args = parser.parse_args()

    corpus_start_stop = insert_start_stop(args.training_corpus)
    corpus_extracted_sentences = extract_sentences(corpus_start_stop)

    test_start_stop = insert_start_stop(args.test_corpus)
    test_extracted_sentences = extract_sentences(test_start_stop)

    corpus_ngrams_all_sentences = create_ngrams_all_sentences(corpus_extracted_sentences, args.n)
    corpus_ngrams_1_all_sentences = create_ngrams_all_sentences(corpus_extracted_sentences, args.n - 1)
    ngram_count = dict(Counter(corpus_ngrams_all_sentences))
    n_1_gram_count = dict(Counter(corpus_ngrams_1_all_sentences))

    voc_size = get_vocabulary_size(args.training_corpus)

    if args.smoothing == 'no':
        no_smoothing()
    elif args.smoothing == 'add1':
        pprint(sequential_add_one_smoothing(ngram_count, n_1_gram_count, test_extracted_sentences, args.n, voc_size))
    elif args.smoothing == 'gt':
        pprint(sequential_good_turing_smoothing(ngram_count, n_1_gram_count, test_extracted_sentences, args.n, voc_size,
                                                5))
