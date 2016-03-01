import argparse
import gzip
import re
from collections import Counter

from a1step2 import create_ngrams_all_sentences
from a1step3 import conditional_good_turing_smoothing
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
            if re.fullmatch('``/``', word):
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


def extract_word_sentences(word_pos_sentences):
    sentences = []
    for sentence in word_pos_sentences:
        sentences.append([p for pos in sentence for p in pos])
    return sentences


def insert_start_stop_list(sentences_pos):
    """Adds start stop symbols to sentences in the form of a list"""
    for sentence in sentences_pos:
        sentence.insert(0, '0START0')
        sentence.append('0STOP0')
    return sentences_pos


def transition_model(ngram_count, ngram_1_count, sentences, voc_size, k, smoothing='yes'):
    if smoothing == 'yes':
        nnc_counts = nc_counts(ngram_count)
        return conditional_good_turing_smoothing(nnc_counts, ngram_count, ngram_1_count, voc_size, k)
    else:
        for sentence in sentences:
        # TODO SET IN dict
        #conditional_probability(ngram_count, ngram_1_count, )
            pass


def emission_model(ngram_count, ngram_1_count, sentences, voc_size, k, smoothing = 'yes'):
    if smoothing == 'yes':
        nnc_counts = nc_counts(ngram_count)
        return conditional_good_turing_smoothing(nnc_counts, ngram_count, ngram_1_count, voc_size, k)
    else:
        # create dict with now smoothing
        pass
        return -1


def viterbi(obs, states, start_p, trans_p, emit_p):
    V = [{}]
    opt = []
    for i in states:
        V[0][i]=start_p[i]*emit_p[i][obs[0]]
    # Run Viterbi when t > 0
    for t in range(1, len(obs)):
        V.append({})
        for y in states:
            (prob, state) = max((V[t-1][y0] * trans_p[y0][y] * emit_p[y][obs[t]], y0) for y0 in states)
            V[t][y] = prob
    for j in V:
        for x, y in j.items():
            if j[x] == max(j.values()):
                opt.append(x)
    # the highest probability
    h = max(V[-1].values())

    return V


def sentence_no_pos(word_pos_sentences, pos_list):
    sentence_words = []
    for sentence in word_pos_sentences:
        sentence_words.append([word for bigram in sentence for word in bigram
                               if word not in list(pos_list)])
    sentence_words = insert_start_stop_list(sentence_words)
    return sentence_words

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-smoothing', type=str, help='yes|no', default='yes')
    parser.add_argument('-train_set', type=str, help='path to train set')
    parser.add_argument('-test_set', type=str, help='path to test set')
    parser.add_argument('-test_set_predicted', type=str, help='path to test set predicted')
    args = parser.parse_args()

    with gzip.open(args.train_set, 'rb') as f:
        word_pos_sentences = parse_pos_file(f)

    sentences_pos = extract_pos_sentences(word_pos_sentences)

    pos_list = list(set(pos for sentence in sentences_pos for pos in sentence))
    sentences_no_pos = sentence_no_pos(word_pos_sentences, pos_list)
    
    sentences_word_pos = extract_word_sentences(word_pos_sentences)

    start_stop_sentences_pos = insert_start_stop_list(sentences_pos)
    start_stop_sentences_word_pos = insert_start_stop_list(sentences_word_pos)

    n_grams_word_pos_1 = create_ngrams_all_sentences(word_pos_sentences, 1)
    n_grams_word_pos = create_ngrams_all_sentences(word_pos_sentences, 2)
    
    trainset_ngrams_all_sentences = create_ngrams_all_sentences(start_stop_sentences_pos, 2)
    trainset_ngrams_1_all_sentences = create_ngrams_all_sentences(start_stop_sentences_pos, 2 - 1)

    trainset_n_grams_word_pos = create_ngrams_all_sentences(start_stop_sentences_word_pos, 2)
    trainset_n_grams_word_pos_1 = create_ngrams_all_sentences(start_stop_sentences_word_pos, 1)


    ngram_count = dict(Counter(trainset_ngrams_all_sentences))
    n_1_gram_count = dict(Counter(trainset_ngrams_1_all_sentences))

    ngram_count_word_pos = dict(Counter(trainset_n_grams_word_pos))
    ngram_count_word_pos_1 = dict(Counter(trainset_n_grams_word_pos_1))
