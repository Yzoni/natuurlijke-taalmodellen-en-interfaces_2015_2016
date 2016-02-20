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


def add_one_smoothing(ngram_count, n_1_gram_count, test_sentences, sequence_size, voc_size):
    """
    Returns probabilities as a list for all paragraphs in a test file
    :param ngram_count: dictionary with ngram count from training file
    :param n_1_gram_count: dictionary with ngram - 1 count from training data
    :param test_sentences: list where elements are word lists from sentences
    :param sequence_size: size of the ngram
    :param voc_size: the vocabulary size
    :return: list of probabilities per paragraph
    """
    probabilities = []
    for sentence in test_sentences:
        sentence_ngrams = create_ngrams(sentence, sequence_size)

        prob = 1
        for p_ngram in sentence_ngrams:

            p_ngram_count = ngram_count.get(p_ngram)  # Returns non if not found
            if p_ngram_count is None:
                p_ngram_count = 1
            else:
                p_ngram_count += 1

            p_n_1_gramn_count = n_1_gram_count.get(p_ngram[:-1])
            if p_n_1_gramn_count is None:
                p_n_1_gramn_count = voc_size
            else:
                p_n_1_gramn_count += voc_size

            prob *= (p_ngram_count / p_n_1_gramn_count)
        probabilities.append(prob)
    return probabilities


def good_turing_smoothing(ngram_count, test_sentences, sequence_size, length_ngrams):
    probabilities = []

    values = [ngram_count.get(key_bigram_count) for key_bigram_count in ngram_count]
    counted_values = Counter(values)
    pprint(counted_values)

    for sentence in test_sentences:
        paragraph_ngrams = create_ngrams(sentence, sequence_size)

        prob = 1
        for p_ngram in paragraph_ngrams:
            c = ngram_count.get(p_ngram)  # Returns non if not found
            if c is not None and c <= 5:  # assignment description says so
                # Nc+1
                if c is None:
                    c = 0
                    # Nc+1
                    count_nc1 = counted_values.get(c + 1)
                    prob *= count_nc1 / length_ngrams
                else:
                    # Nc+1
                    count_nc1 = counted_values.get(c + 1)
                    # Nc
                    count_nc = counted_values.get(c)
                    c_star = ((c + 1) * count_nc1) / count_nc
                    prob *= c_star / length_ngrams
        probabilities.append(prob)
    return probabilities


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

    length_ngrams = len(corpus_ngrams_all_sentences)

    if args.smoothing == 'no':
        no_smoothing()
    elif args.smoothing == 'add1':
        pprint(add_one_smoothing(ngram_count, n_1_gram_count, test_extracted_sentences, args.n,
                                 get_vocabulary_size(args.training_corpus)))
    elif args.smoothing == 'gt':
        pprint(good_turing_smoothing(ngram_count, args.test_corpus, args.n, length_ngrams))
