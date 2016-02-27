import argparse
import gzip
import re


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
                    print(sentence)
                    sentences.append(sentence)
                    sentence = []
    return sentences


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('smoothing', type=str, help='yes|no', default='yes')
    parser.add_argument('train_set', type=str, help='path to train set')
    parser.add_argument('-test_set', type=int, help='path to test set')
    parser.add_argument('-test_set_predicted', type=str, help='path to test set predicted')
    args = parser.parse_args()

    with gzip.open('/home/yorick/IdeaProjects/natuurlijke_taalmodellen_en_interfaces/partA/raw/WSJ23.pos.gz',
                   'rb') as f:
        parse_pos_file(f)
