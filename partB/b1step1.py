#!/usr/bin/env python3.5
__author__ = 'Yorick de Boer [10786015]'
"""
Binarizes a file containing trees, outputting binarized trees as strings.

############################
# (ROOT
#   (S
#       (NP
#           (NNP Ms.)
#           (NNP Haag)
#       )
#       (VP
#           (VBZ plays)
#           (NP
#               (NNP Elianti)
#           )
#       )
#       (. .)
#   )
# )
###########################
# (ROOT
#   (S
#       (NP
#           (NNP Ms.)
#           (@NP->_NNP
#               (NNP Haag)
#           )
#       )
#       (@S->_NP
#           (VP
#               (VBZ plays)
#               (@VP->_VBZ
#                   (NP
#                       (NNP Elianti)
#                   )
#               )
#           )
#           (@S->_NP_VP
#               (. .)
#           )
#       )
#   )
# )
"""

import argparse
import re
import unittest

import progressbar


def parse_to_list(sentence):
    """Returns a nested list from a tree in the form of a string.
    Works by splitting all elements of the string using regex and iterating over them."""
    accum = []
    nested_list = []
    regex = re.compile(r'([^(^)\s]+|\()|(\))')
    for termtypes in re.finditer(regex, sentence):
        tt = termtypes.group(0).strip()
        if tt == '(':
            accum.append(nested_list)
            nested_list = []
        elif tt == ')':
            tmp = nested_list
            nested_list = accum[-1]
            nested_list.append(tmp)
            del accum[-1]
        else:  # A word
            nested_list.append(tt)
    return nested_list[0]  # Remove outer list


def binarize(nested_list):
    """Binarizes a tree in the formatted as a nested list.
    Works by recursively looping over all nested list elements."""
    if isinstance(nested_list, list):
        if len(nested_list) > 2:
            if '@' in nested_list[0]:
                bt = nested_list[0] + '_' + nested_list[1][0]
            else:
                bt = '@' + nested_list[0] + '->_' + nested_list[1][0]
            nested_list[2] = [bt] + nested_list[2:]
            if len(nested_list) > 3:
                del nested_list[3:]
        for idx, e in enumerate(nested_list):
            nested_list[idx] = binarize(e)
    return nested_list


def binarized_to_string(nested_list):
    """Transforms a list to a string, removing list elements"""
    return str(nested_list).replace("[", "(") \
        .replace(']', ')') \
        .replace("')", ")") \
        .replace("('", "(") \
        .replace(', ', ' ') \
        .replace("' ", " ") \
        .replace(" '", " ") \
        .replace('"', '')


class TestBStep1(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.test_string_sentences = [
            '''(ROOT (S (NP (NNP Ms.) (NNP Haag)) (VP (VBZ plays) (NP (NNP Elianti))) (. .)))''',
            '''(ROOT (S (NP (NNP Rolls-Royce) (NNP Motor) (NNPS Cars) (NNP Inc.)) (VP (VBD said) (SBAR (S (NP (PRP it)) (VP (VBZ expects) (S (NP (PRP$ its) (NNP U.S.) (NNS sales)) (VP (TO to) (VP (VB remain) (ADJP (JJ steady)) (PP (IN at) (NP (QP (IN about) (CD 1,200)) (NNS cars))) (PP (IN in) (NP (CD 1990)))))))))) (. .)))''',
            '''(ROOT (S (NP (DT The) (NN luxury) (NN auto) (NN maker)) (NP (JJ last) (NN year)) (VP (VBD sold) (NP (CD 1,214) (NNS cars)) (PP (IN in) (NP (DT the) (NNP U.S.))))))''',
            '''(ROOT (S (`` ``) (ADVP (RB Apparently)) (NP (DT the) (NN commission)) (VP (VBD did) (RB not) (ADVP (RB really)) (VP (VB believe) (PP (IN in) (NP (DT this) (NN ideal))))) (. .) ('' '')))''',
            '''(ROOT (S (CC But) (NP (NP (QP (IN about) (CD 25)) (NN %)) (PP (IN of) (NP (DT the) (NNS insiders)))) (, ,) (PP (VBG according) (PP (TO to) (NP (NNP SEC) (NNS figures)))) (, ,) (VP (VBP file) (NP (PRP$ their) (NNS reports)) (ADVP (RB late))) (. .)))''',
            '''(ROOT (S (ADVP (RB Already)) (, ,) (NP (DT the) (NNS consequences)) (VP (VBP are) (VP (VBG being) (VP (VBN felt) (PP (IN by) (NP (NP (NP (JJ other) (NNS players)) (PP (IN in) (NP (DT the) (JJ financial) (NNS markets)))) (: --) (JJ even) (NP (NNS governments))))))) (. .)))'''
        ]

        self.test_bin_sentences = [
            '''(ROOT (S (NP (NNP Ms.) (@NP->_NNP (NNP Haag))) (@S->_NP (VP (VBZ plays) (@VP->_VBZ (NP (NNP Elianti)))) (@S->_NP_VP (. .)))))''',
            '''(ROOT (S (NP (NNP Rolls-Royce) (@NP->_NNP (NNP Motor) (@NP->_NNP_NNP (NNPS Cars) (@NP->_NNP_NNP_NNPS (NNP Inc.))))) (@S->_NP (VP (VBD said) (@VP->_VBD (SBAR (S (NP (PRP it)) (@S->_NP (VP (VBZ expects) (@VP->_VBZ (S (NP (PRP$ its) (@NP->_PRP$ (NNP U.S.) (@NP->_PRP$_NNP (NNS sales)))) (@S->_NP (VP (TO to) (@VP->_TO (VP (VB remain) (@VP->_VB (ADJP (JJ steady)) (@VP->_VB_ADJP (PP (IN at) (@PP->_IN (NP (QP (IN about) (@QP->_IN (CD 1,200))) (@NP->_QP (NNS cars))))) (@VP->_VB_ADJP_PP (PP (IN in) (@PP->_IN (NP (CD 1990))))))))))))))))))) (@S->_NP_VP (. .)))))''',
            '''(ROOT (S (NP (DT The) (@NP->_DT (NN luxury) (@NP->_DT_NN (NN auto) (@NP->_DT_NN_NN (NN maker))))) (@S->_NP (NP (JJ last) (@NP->_JJ (NN year))) (@S->_NP_NP (VP (VBD sold) (@VP->_VBD (NP (CD 1,214) (@NP->_CD (NNS cars))) (@VP->_VBD_NP (PP (IN in) (@PP->_IN (NP (DT the) (@NP->_DT (NNP U.S.))))))))))))''',
            '''(ROOT (S (`` ``) (@S->_`` (ADVP (RB Apparently)) (@S->_``_ADVP (NP (DT the) (@NP->_DT (NN commission))) (@S->_``_ADVP_NP (VP (VBD did) (@VP->_VBD (RB not) (@VP->_VBD_RB (ADVP (RB really)) (@VP->_VBD_RB_ADVP (VP (VB believe) (@VP->_VB (PP (IN in) (@PP->_IN (NP (DT this) (@NP->_DT (NN ideal))))))))))) (@S->_``_ADVP_NP_VP (. .) (@S->_``_ADVP_NP_VP_. ('' ''))))))))''',
            '''(ROOT (S (CC But) (@S->_CC (NP (NP (QP (IN about) (@QP->_IN (CD 25))) (@NP->_QP (NN %))) (@NP->_NP (PP (IN of) (@PP->_IN (NP (DT the) (@NP->_DT (NNS insiders))))))) (@S->_CC_NP (, ,) (@S->_CC_NP_, (PP (VBG according) (@PP->_VBG (PP (TO to) (@PP->_TO (NP (NNP SEC) (@NP->_NNP (NNS figures))))))) (@S->_CC_NP_,_PP (, ,) (@S->_CC_NP_,_PP_, (VP (VBP file) (@VP->_VBP (NP (PRP$ their) (@NP->_PRP$ (NNS reports))) (@VP->_VBP_NP (ADVP (RB late))))) (@S->_CC_NP_,_PP_,_VP (. .)))))))))''',
            '''(ROOT (S (ADVP (RB Already)) (@S->_ADVP (, ,) (@S->_ADVP_, (NP (DT the) (@NP->_DT (NNS consequences))) (@S->_ADVP_,_NP (VP (VBP are) (@VP->_VBP (VP (VBG being) (@VP->_VBG (VP (VBN felt) (@VP->_VBN (PP (IN by) (@PP->_IN (NP (NP (NP (JJ other) (@NP->_JJ (NNS players))) (@NP->_NP (PP (IN in) (@PP->_IN (NP (DT the) (@NP->_DT (JJ financial) (@NP->_DT_JJ (NNS markets)))))))) (@NP->_NP (: --) (@NP->_NP_: (JJ even) (@NP->_NP_:_JJ (NP (NNS governments)))))))))))))) (@S->_ADVP_,_NP_VP (. .)))))))'''
        ]

    def test_binarize(self):
        for test_string_sentence, test_bin_sentence in zip(self.test_string_sentences, self.test_bin_sentences):
            parsed = parse_to_list(test_string_sentence)
            binarized_list = binarize(parsed)
            self.assertEqual(binarized_to_string(binarized_list), test_bin_sentence)


def binarize_to_file(infile, outfile):
    """Reads all lines form a file, binarizes them, and writes the binarized tree to a new file"""
    f_out = open(outfile, 'w')
    num_lines = sum(1 for _ in open(infile))
    count = 0
    pbar = progressbar.ProgressBar(widgets=[progressbar.Percentage(), progressbar.Bar()], maxval=num_lines).start()

    print('Binarizing...')
    with open(infile, 'r') as f_in:
        for line in f_in:
            count += 1
            pbar.update(count)
            if line == '\n':
                f_out.write('\n')
            else:
                binarized_line = binarized_to_string(binarize(parse_to_list(line)))
                f_out.write(binarized_line + '\n')
    print('Done.')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-infile', type=str, help='Path to file containing S-Expressions')
    parser.add_argument('-outfile', type=str, help='Path to where tot save binary S-Expressions')
    args = parser.parse_args()

    if not args.infile and not args.outfile:
        unittest.main()
    else:
        binarize_to_file(args.infile, args.outfile)
