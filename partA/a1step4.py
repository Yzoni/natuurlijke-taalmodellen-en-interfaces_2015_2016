import argparse
import gzip
import itertools
import re
from collections import Counter

from a1step2 import create_ngrams_all_sentences
from a1step3 import conditional_good_turing_smoothing
from a1step3 import get_all_possible_ngram_count
from a1step3 import nc_counts


def parse_pos_file(file_stream):
    """Parser for POS file returns sentences excludes symbols
    :param file_stream file stream
    :return: [[['No', 'RB'], ['it', 'PRP'], ['was', 'VBD'],.....
    """
    sentences = []
    sentence = []
    for line in file_stream.readlines():
        dline = line.decode("utf-8")
        dline_split = dline.split()
        for word in dline_split:
            if re.fullmatch('``\``', word):
                continue
            if re.fullmatch('([a-zA-z]|\')+/[a-zA-z]+', word):
                word_tag = word.split('/')
                sentence.append(word_tag)
            if word == '======================================' or word == './.':
                if sentence:
                    sentences.append(sentence)
                    sentence = []
    return sentences


def extract_pos_sentences(word_pos_sentences):
    """ Returns sentences of POS tags
    :param word_pos_sentences: [[['No', 'RB'], ['it', 'PRP'], ['was', 'VBD'],.....
    :return: [['RB', 'PRP', 'VBD', 'RB', 'NNP', 'NNP'], ['CC', 'IN',.....
    """
    sentences_pos = []
    for sentence in word_pos_sentences:
        sentences_pos.append([pos[1] for pos in sentence])
    return sentences_pos


def extract_pos(word_pos_sentences):
    word_pos = list(itertools.chain(*word_pos_sentences))
    word_pos_tuples = [tuple(l) for l in word_pos]
    return [tuple([pos[1]]) for pos in word_pos_tuples]


def extract_word_pos(word_pos_sentences):
    flattened_word_pos_sentences = list(itertools.chain(*word_pos_sentences))
    word_pos_tuples = [tuple(l) for l in flattened_word_pos_sentences]
    return [tuple(reversed(atuple)) for atuple in word_pos_tuples]


def insert_start_stop_list(sentences_pos):
    """Adds start stop symbols to sentences in the form of a list"""
    for sentence in sentences_pos:
        sentence.insert(0, '0START0')
        sentence.append('0STOP0')
    return sentences_pos


def model(ngram_count, ngram_1_count, voc_size, k, smoothing='yes'):
    """
    Transition and emission model
    :param ngram_count: {('RBR', 'IN'): 23, ('JJS', 'CD'): 5,...
    :param ngram_1_count: {('NNS',): 3458, ('JJR',): 193, ('VBN',): 1096,...
    :param voc_size: vocabulary size
    :param k: c < k
    :param smoothing: yes | no
    :return:
    """
    if smoothing == 'yes':
        nnc_counts = nc_counts(ngram_count)
        return conditional_good_turing_smoothing(nnc_counts, ngram_count, ngram_1_count, voc_size, k)
    else:
        return conditional_no_smoothing(ngram_count, ngram_1_count)


def conditional_no_smoothing(ngram_count, ngram_1_count):
    """Gets the good turing smoothed count from one ngram"""
    cond_probs = {}
    for ngram in ngram_count:
        count_n_1_gram = ngram_1_count.get(ngram[:-1])
        if count_n_1_gram is None:  # if n-1 gram could not be found probability is zero
            cond_probs[ngram] = 0
        else:
            if ngram[0] not in cond_probs:
                cond_probs[ngram[0]] = {}
            cond_probs[ngram[0]][ngram[1]] = ngram_count[ngram] / count_n_1_gram
    return cond_probs


def sentence_no_pos(word_pos_sentences, pos_list):
    sentence_words = []
    for sentence in word_pos_sentences:
        sentence_words.append([word for bigram in sentence for word in bigram
                               if word not in list(pos_list)])
    sentence_words = insert_start_stop_list(sentence_words)
    return sentence_words


class viterbi:
    def __init__(self, trans_model, emiss_model):
        self.t_model = trans_model
        self.e_model = emiss_model
        self.states = self.get_states()  # are pos tags

    def get_states(self):
        key_list = [key for key in self.t_model]
        unique_states_1, unique_states_2 = zip(*key_list)
        return list(set(list(unique_states_1) + list(unique_states_2)))

    def _init_table(self, first_word):
        dct = {}
        for state in self.states:
            e_prob = self.e_model.get((state, first_word))
            if e_prob is None:
                e_prob = 0
            t_prob = self.t_model.get(('0START0', state))
            if t_prob is None:
                t_prob = 0
            dct[(first_word, state)] = (t_prob * e_prob, None)
        return dct

    def _run_cell(self, previous_word, word, current_pos, full_dct):
        cell_dct = {}
        e_prob = self.e_model.get((current_pos, word))
        if e_prob is None:
            return None, 0
        for state in self.states:
            t_prob = self.t_model.get((current_pos, state))
            if t_prob is None:
                t_prob = 0
            previous_prob = full_dct.get((previous_word, state))
            if previous_prob is None:
                previous_prob = [0, None]
            cell_dct[state] = previous_prob[0] * t_prob * e_prob
        # Get max from cell_dct
        previous_pos_with_maxvalue = max(cell_dct, key=lambda key: cell_dct[key])
        previous_pos_value = cell_dct.get(previous_pos_with_maxvalue)
        return previous_pos_with_maxvalue, previous_pos_value

    def _backward(self, sentence, maxprob_pos, dct):
        pos_sentence = []
        pos_sentence.append(maxprob_pos)
        for word in list(reversed(sentence))[1:-1]:
            maxprob_pos = dct.get(word, maxprob_pos)
            pos_sentence.append(maxprob_pos)
        return list(reversed(pos_sentence))

    def _get_previous_pos_and_max_prob(self, sentence, dct):
        last_word = sentence[-2]
        last_timestep = [dct.get((last_word, state)) for state in self.states]
        probs, previous_pos = zip(*last_timestep)
        max_index, max_value = max(enumerate(probs), key=lambda p: p[1])
        return previous_pos[max_index], max_value

    def run(self, sentence):
        dct = self._init_table(sentence[1])  # {(word, current POS) : (prob, previous POS)}
        previous_word = sentence[1]
        for word in sentence[2:-1]:
            for pos in self.states:
                previous_pos, new_max_prob = self._run_cell(previous_word, word, pos, dct)
                dct[(word, pos)] = (new_max_prob, previous_pos)
            previous_word = word
        pos_max_prob, max_prob = self._get_previous_pos_and_max_prob(sentence, dct)
        pos_sentence = self._backward(sentence, pos_max_prob, dct)
        return pos_sentence, max_prob


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-smoothing', type=str, help='yes|no', default='yes')
    parser.add_argument('-train_set', type=str, help='path to train set')
    parser.add_argument('-test_set', type=str, help='path to test set')
    parser.add_argument('-test_set_predicted', type=str, help='path to test set predicted')
    args = parser.parse_args()

    all_possible_ngram_count = get_all_possible_ngram_count(args.test_set, 2)

    with gzip.open(args.train_set, 'rb') as f:
        word_pos_sentences = parse_pos_file(f)

    with gzip.open(args.test_set, 'rb') as f:
        word_pos_test_sentences = parse_pos_file(f)

    # OBSERVATIONS
    sentences_pos = extract_pos_sentences(word_pos_sentences)
    pos_list = list(set(pos for sentence in sentences_pos for pos in sentence))
    sentences_no_pos = sentence_no_pos(word_pos_sentences, pos_list)

    # TRANSITION MODEL
    sentences_word_pos = extract_pos_sentences(word_pos_sentences)
    start_stop_sentences_pos = insert_start_stop_list(sentences_word_pos)

    trainset_ngrams_all_sentences = create_ngrams_all_sentences(start_stop_sentences_pos, 2)
    trainset_ngrams_1_all_sentences = create_ngrams_all_sentences(start_stop_sentences_pos, 2 - 1)

    ngram_count = dict(Counter(trainset_ngrams_all_sentences))
    n_1_gram_count = dict(Counter(trainset_ngrams_1_all_sentences))

    # EMISSION MODEL
    # Get count for (POSTAG, WORD)
    only_word_pos = extract_word_pos(word_pos_sentences)
    pos_word_count = dict(Counter(only_word_pos))

    # Get count for (POSTAG)
    only_pos = extract_pos(word_pos_sentences)
    pos_count = dict(Counter(only_pos))

    # CREATE MODELS
    trans_model = model(ngram_count, n_1_gram_count, all_possible_ngram_count, 4, smoothing='yes')
    emiss_model = model(pos_word_count, pos_count, all_possible_ngram_count, 1, smoothing='yes')

    viterbi_model = viterbi(trans_model, emiss_model)
    viterbi_model.run(sentences_no_pos[1])

if __name__ == "__main__":
    main()
