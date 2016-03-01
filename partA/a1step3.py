import argparse
import itertools
from collections import Counter
from pprint import pprint

from a1step1 import create_ngrams
from a1step2 import conditional_probability
from a1step2 import create_ngrams_all_sentences
from a1step2 import extract_sentences
from a1step2 import insert_start_stop


def get_all_possible_ngram_count(list_sentences, n):
    """Returns the amount of words in a text file"""
    flattened_sentences = itertools.chain(*list_sentences)
    unique_words = list(set(flattened_sentences))
    return len(unique_words) ** n


def sequential_no_smoothing(ngram_count, n_1_gram_count, test_sentences, sequence_size):
    probabilities = []
    for sentence in test_sentences:
        sentence_ngrams = create_ngrams(sentence, sequence_size)

        prob = 1
        for p_ngram in sentence_ngrams:
            prob *= conditional_probability(ngram_count, n_1_gram_count, p_ngram)
        probabilities.append(prob)
    return probabilities


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
    """Good turing smoothed probability of a whole sentence"""
    probabilities = []
    nnc_counts = nc_counts(ngram_count)
    smoothed_gt_ngrams = conditional_good_turing_smoothing(nnc_counts, ngram_count, ngram_1_count, voc_size, k)
    for sentence in test_sentences:
        paragraph_ngrams = create_ngrams(sentence, sequence_size)

        prob = 1
        for p_ngram in paragraph_ngrams:
            # find ngram in dict P(x|y)
            y = p_ngram[:-1]
            x = p_ngram[-1]

            xdict = smoothed_gt_ngrams.get(y[0])
            if xdict is not None:
                ss = xdict.get(x[0])
                if ss is not None:
                    prob *= ss
                else:
                    prob = 0
            else:
                prob = 0
        probabilities.append(prob)
    return probabilities


def conditional_good_turing_smoothing(nc_counts, ngram_count, ngram_1_count, voc_size, k):
    """Gets the good turing smoothed count from one ngram"""
    cond_probs = {}
    for ngram in ngram_count:
        cgt = good_turing_count(nc_counts, ngram_count, ngram, voc_size, k)
        count_n_1_gram = ngram_1_count.get(ngram[:-1])
        if count_n_1_gram is None:  # if n-1 gram could not be found probability is zero
            cond_probs[ngram] = 0
        else:
            if ngram[0] not in cond_probs:
                cond_probs[ngram[0]] = {}
            cond_probs[ngram[0]][ngram[1]] = cgt / count_n_1_gram
    return cond_probs


def good_turing_count(nc_counts, ngram_count, one_ngram, all_possible_ngramcount, k):
    """Gets the good turing smoothed count from one ngram"""
    c = ngram_count.get(one_ngram)
    if c is None:
        c = 0
    ncounts_inc_zero = [all_possible_ngramcount - sum(nc_counts)] + nc_counts
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

    all_possible_ngram_count = get_all_possible_ngram_count(test_extracted_sentences, n)

    if args.smoothing == 'no':
        pprint(sequential_no_smoothing(ngram_count, n_1_gram_count, test_extracted_sentences, args.n))
    elif args.smoothing == 'add1':
        pprint(sequential_add_one_smoothing(ngram_count, n_1_gram_count, test_extracted_sentences, args.n,
                                            all_possible_ngram_count))
    elif args.smoothing == 'gt':
        pprint(sequential_good_turing_smoothing(ngram_count, n_1_gram_count, test_extracted_sentences, args.n,
                                                all_possible_ngram_count,
                                                5))
