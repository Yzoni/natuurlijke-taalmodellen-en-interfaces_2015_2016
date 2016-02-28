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
        sentence.append('0STOP0')
    return sentences_pos


def transition_model(ngram_count, ngram_1_count, smoothing='yes'):
    if smoothing == 'yes':
        conditional_good_turing_smoothing()
    else:
        -1


def emission_model():
    return -1


def viterbi(sentences_training, sentences_test):
    """
     Implementation of the viterbi algorithm.
    :param sentences_test: pos tagged sentences with start/stop symbols 
    from testset
    :param sentences_training: pos tagged sentences with start/stop symbols
    from trainingset
    """
    
    # transition_matrix[(a_i, a_j)]=probability of transitioning from a_i to a_j
    # In this case: the probability that tag a_j follow tag a_i
    transition_matrix = {}
    
    # output_matrix[(b_i, o_j)]=prob of emitting o_j from b_i
    # In this case: the probability that tag b_i emits tag o_j
    output_matrix = {}

    # best_paths[sentence] = best sequence of tags for sentence
    best_paths = {}

    for sentence in sentences:
        #calculate best_path for sentence
        pass
    return best_paths


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

    best_paths = viterbi(start_stop_sentences_pos)
    
    trainset_ngrams_all_sentences = create_ngrams_all_sentences(start_stop_sentences_pos, 2)
    trainset_ngrams_1_all_sentences = create_ngrams_all_sentences(start_stop_sentences_pos, 2 - 1)

    ngram_count = dict(Counter(trainset_ngrams_all_sentences))
    n_1_gram_count = dict(Counter(trainset_ngrams_1_all_sentences))
