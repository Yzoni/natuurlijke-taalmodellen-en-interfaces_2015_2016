import argparse
import gzip
import re
from collections import Counter

from a1step2 import create_ngrams_all_sentences
from a1step3 import conditional_good_turing_smoothing


def parse_pos_file(file_stream):
    sentences = []
    sentence = []
    for line in file_stream.readlines():
        dline = line.decode("utf-8")
        dline_split = dline.split()
        for word in dline_split:
            if re.fullmatch('([a-zA-z]|\')+/[a-zA-z]+', word):
                word_tag = word.split('/')
                sentence.append(word_tag)
            if word == '======================================' or word == './.':
                if sentence:
                    sentences.append(sentence)
                    sentence = []
    return sentences


def extract_pos_sentences(word_pos_sentences):
    sentences_pos = []
    for sentence in word_pos_sentences:
        sentences_pos.append([pos[1] for pos in sentence])
    return sentences_pos


def insert_start_stop_list(sentences_pos):
    for sentence in sentences_pos:
        sentence.insert(0, '0START0')
        sentence.extend('0STOP0')
    return sentences_pos


def transition_model(ngram_count, ngram_1_count, smoothing='yes'):
    if smoothing == 'yes':
        conditional_good_turing_smoothing()
    else:
        -1


def emission_model():
    return -1


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
    start_stop_sentences_pos = insert_start_stop_list(sentences_pos)
    trainset_ngrams_all_sentences = create_ngrams_all_sentences(start_stop_sentences_pos, 2)
    trainset_ngrams_1_all_sentences = create_ngrams_all_sentences(start_stop_sentences_pos, 2 - 1)

    ngram_count = dict(Counter(trainset_ngrams_all_sentences))
    n_1_gram_count = dict(Counter(trainset_ngrams_1_all_sentences))
