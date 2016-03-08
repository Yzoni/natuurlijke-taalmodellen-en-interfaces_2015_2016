import argparse
import gzip
import itertools
import re
from collections import Counter

from a1step2 import create_ngrams_all_sentences
from a1step3 import conditional_good_turing_smoothing
from a1step3 import get_all_possible_ngram_count


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
            if re.fullmatch('.*``.*', word):
                continue
            if re.fullmatch('([a-zA-z]|-|\')+/[a-zA-z]+', word):
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


def extract_word_sentences(word_pos_sentences):
    sentences_pos = []
    for sentence in word_pos_sentences:
        sentences_pos.append([pos[0] for pos in sentence])
    return sentences_pos


def extract_pos(word_pos_sentences):
    word_pos = list(itertools.chain(*word_pos_sentences))
    word_pos_tuples = [tuple(l) for l in word_pos]
    return [tuple([pos[1]]) for pos in word_pos_tuples]


def extract_word_pos(word_pos_sentences):
    flattened_word_pos_sentences = list(itertools.chain(*word_pos_sentences))
    word_pos_tuples = [tuple(l) for l in flattened_word_pos_sentences]
    return [tuple(reversed(atuple)) for atuple in word_pos_tuples]


def insert_start_stop_list(sentences):
    """Adds start stop symbols to sentences in the form of a list"""
    for sentence in sentences:
        sentence.insert(0, '0START0')
        sentence.append('0STOP0')
    return sentences


def transition_model(word_pos_sentences, k, smoothing='yes'):
    """
    Transition and emission model
    :param word_pos_sentences
    :param k: c < k
    :param smoothing: yes | no
    :return:
    """
    sentences_word_pos = extract_pos_sentences(word_pos_sentences)
    start_stop_sentences_pos = insert_start_stop_list(sentences_word_pos)

    voc_size = get_all_possible_ngram_count(start_stop_sentences_pos, 2)

    trainset_ngrams_all_sentences = create_ngrams_all_sentences(start_stop_sentences_pos, 2)
    trainset_ngrams_1_all_sentences = create_ngrams_all_sentences(start_stop_sentences_pos, 2 - 1)

    ngram_count = dict(Counter(trainset_ngrams_all_sentences))  # {('RBR', 'IN'): 23, ('JJS', 'CD'): 5,...
    n_1_gram_count = dict(Counter(trainset_ngrams_1_all_sentences))  # {('NNS',): 3458, ('JJR',): 193, ('VBN',): 1096,.

    if smoothing == 'yes':
        return conditional_good_turing_smoothing(ngram_count, n_1_gram_count, voc_size, k)
    else:
        return conditional_no_smoothing(ngram_count, n_1_gram_count)


def emission_model(word_pos_sentences, k, smoothing='yes'):
    # Get count for (POSTAG, WORD)
    only_word_pos = extract_word_pos(word_pos_sentences)
    pos_word_count = dict(Counter(only_word_pos))

    # Get count for (POSTAG)
    only_pos = extract_pos(word_pos_sentences)
    pos_count = dict(Counter(only_pos))

    if smoothing == 'yes':
        return conditional_good_turing_smoothing(pos_word_count, pos_count, 1, k)
    else:
        return conditional_no_smoothing(pos_word_count, pos_count)


def conditional_no_smoothing(ngram_count, ngram_1_count):
    """Gets the good turing smoothed count from one ngram"""
    cond_probs = {}
    for ngram in ngram_count:
        count_n_1_gram = ngram_1_count.get(ngram[:-1])
        cond_probs[ngram] = ngram_count[ngram] / count_n_1_gram
    return cond_probs


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
            if previous_prob[0] is 0:
                previous_prob = [0, None]
            cell_dct[state] = previous_prob[0] * t_prob * e_prob
        # Get max from cell_dct
        previous_pos_with_maxvalue = max(cell_dct, key=lambda key: cell_dct[key])
        previous_pos_value = cell_dct.get(previous_pos_with_maxvalue)
        return previous_pos_with_maxvalue, previous_pos_value

    def _backward(self, sentence, maxkey, dct):
        pos_sentence = []
        s_sentence = sentence[1:-1]
        for word in list(reversed(s_sentence)):
            pos_sentence.append(maxkey[1])
            maxkey = dct.get((word, maxkey[1]))
            if maxkey is None:
                return None
        return list(reversed(pos_sentence))  # Remove start symbol

    def _get_last_maxpos_and_max_prob(self, sentence, dct):
        last_word = sentence[-2]
        maxprob = 0
        maxkey = (None, None)
        for state in self.states:
            temp_prob = dct.get((last_word, state))[0]
            if temp_prob > maxprob:
                maxprob = temp_prob
                maxkey = (last_word, state)
        return maxkey, maxprob

    def run(self, sentence):
        dct = self._init_table(sentence[1])  # {(word, current POS) : (prob, previous POS)}
        previous_word = sentence[1]
        for word in sentence[2:-1]:
            for pos in self.states:
                previous_pos, new_max_prob = self._run_cell(previous_word, word, pos, dct)
                dct[(word, pos)] = (new_max_prob, previous_pos)
            previous_word = word
        maxkey, maxprob = self._get_last_maxpos_and_max_prob(sentence, dct)
        pos_sentence = self._backward(sentence, maxkey, dct)

        if pos_sentence is None:  # Probability is 0 for some time step in the backchain
            return None
        return pos_sentence, maxprob


def calculate_accuracy(generated_pos_sentences, validation_pos_sentences):
    correct_count = 0
    total_not_none_count = 0
    for generated_pos_sentence, validation_pos_sentence in zip(generated_pos_sentences, validation_pos_sentences):
        if len(validation_pos_sentence) < 15:
            if generated_pos_sentence is not None:
                if generated_pos_sentence[0] == validation_pos_sentence:
                    correct_count += 1
                total_not_none_count += 1
    return (correct_count / total_not_none_count) * 100, total_not_none_count


def percentage_dif(generated_pos_sentences, validation_pos_sentences):
    percentages_thesame = []
    for generated_pos_sentence, validation_pos_sentence in zip(generated_pos_sentences, validation_pos_sentences):
        if len(validation_pos_sentence) < 15:
            if generated_pos_sentence is not None:
                difference = set(generated_pos_sentence[0]) ^ set(validation_pos_sentence)
                len_pos = len(validation_pos_sentence)
                len_dif = len_pos - (len(difference) / 2)
                percentages_thesame.append((len_dif / len_pos) * 100)
    return sum(percentages_thesame) / len(percentages_thesame)


def save_lists_to_file(filename, sentences1, sentences2):
    f = open(filename, 'w')
    for sentence1, sentence2 in zip(sentences1, sentences2):
        if sentence2 is not None and len(sentence1) < 15:
            f.write(' '.join(sentence1) + '\n')
            f.write(' '.join(sentence2[0]) + '\n')
            f.write('\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-smoothing', type=str, help='yes|no', default='yes')
    parser.add_argument('-train_set', type=str, help='path to train set')
    parser.add_argument('-test_set', type=str, help='path to test set')
    parser.add_argument('-test_set_predicted', type=str, help='path to save the predicted pos sentences')
    args = parser.parse_args()

    with gzip.open(args.train_set, 'rb') as f:
        word_pos_sentences = parse_pos_file(f)

    with gzip.open(args.test_set, 'rb') as f:
        word_pos_test_sentences = parse_pos_file(f)

    # CREATE MODELS
    trans_model = transition_model(word_pos_sentences, 4, smoothing=args.smoothing)
    emiss_model = emission_model(word_pos_sentences, 1, smoothing=args.smoothing)
    viterbi_model = viterbi(trans_model, emiss_model)

    # GENERATE POS SENTENCES FROM TEST WORD SENTENCES
    test_sentences = extract_word_sentences(word_pos_test_sentences)
    start_stop_test = insert_start_stop_list(test_sentences)
    test_sentence_no_pos = extract_word_sentences(word_pos_test_sentences)
    generated_pos_sentence = [viterbi_model.run(word_sentence) for word_sentence in start_stop_test]

    # GENERATE WORD SENTENCES FOR VALIDATION OF GENERATED POS SENTENCES
    validation_pos_sentences = extract_pos_sentences(word_pos_test_sentences)

    # PRINT ACCURACY OF GENERATED POS SENTENCES
    percentage_correct, total_non_none = calculate_accuracy(generated_pos_sentence, validation_pos_sentences)
    print('Percentage correct ' + str(percentage_correct))
    percentage_difference = percentage_dif(generated_pos_sentence, validation_pos_sentences)
    print('Percentage difference ' + str(percentage_difference))

    # SAVE GENERATED POS SENTENCES TO FILE
    save_lists_to_file(args.test_set_predicted, test_sentence_no_pos, generated_pos_sentence)


if __name__ == "__main__":
    main()
