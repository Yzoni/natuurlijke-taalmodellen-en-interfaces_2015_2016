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
            # P(x|y)
            y = p_ngram[:-1]
            x = p_ngram[-1]

            nprob = smoothed_gt_ngrams.get((y, x))
            if nprob is None:
                nprob = smoothed_gt_ngrams.get(('', ''))
            prob *= nprob

        probabilities.append(prob)
    return probabilities


def conditional_good_turing_smoothing(ngram_counts, ngram_1_counts, voc_size, k):
    """Gets the good turing smoothed count from one ngram"""
    cond_probs = {}
    nnc_counts = nc_counts(ngram_counts)

    for ngram in ngram_counts:
        cgt = good_turing_count(nnc_counts, ngram_counts, ngram, voc_size, k)
        count_n_1_gram = ngram_1_counts.get(ngram[:-1])
        cond_probs[ngram] = cgt / count_n_1_gram

    # For not appearin ngrams
    cgt = good_turing_count(nnc_counts, ngram_counts, (), voc_size, k)
    cond_probs[('', '')] = cgt
    return cond_probs


def good_turing_count(nc_counts, ngram_counts, one_ngram, all_possible_ngramcount, k):
    """Gets the good turing smoothed count from one ngram"""
    c = ngram_counts.get(one_ngram)
    if c is None:
        c = 0
    nc_counts[0] = all_possible_ngramcount - sum(nc_counts.values())
    return good_turing_function(c, nc_counts, k)


def nc_counts(ngram_count):
    """Creates a list of Nc counts assumes no gaps"""
    values = [ngram_count.get(key_bigram_count) for key_bigram_count in ngram_count]
    return dict(Counter(values))


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

    all_possible_ngram_count = get_all_possible_ngram_count(test_extracted_sentences, args.n)

    if args.smoothing == 'no':
        pprint(sequential_no_smoothing(ngram_count, n_1_gram_count, test_extracted_sentences, args.n))
    elif args.smoothing == 'add1':
        pprint(sequential_add_one_smoothing(ngram_count, n_1_gram_count, test_extracted_sentences, args.n,
                                            all_possible_ngram_count))
    elif args.smoothing == 'gt':
        pprint(sequential_good_turing_smoothing(ngram_count, n_1_gram_count, test_extracted_sentences, args.n,
                                                all_possible_ngram_count, 5))
