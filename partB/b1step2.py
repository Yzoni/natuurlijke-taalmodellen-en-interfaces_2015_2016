import argparse
import re
import unittest

import progressbar

from b1step1 import binarized_to_string
from b1step1 import parse_to_list


def vertical_markovization(nested_list, v_order=2):
    """Executes vertical markovization on a tree in the formatted as a nested list."""
    root, nested_list_noroot = nested_list[0], nested_list[1]
    vertical_markov = [vertical_markovization_recursive(nested_list_noroot, root, v_order)]
    vertical_markov.insert(0, root)
    return vertical_markov


def vertical_markovization_recursive(nested_list, root, v_order=2):
    """Recursive function for the vertical markovization of a tree formatted as a nested list.
    Works by recursively looping over all nested list elements."""
    if v_order == 1:
        return nested_list
    elif v_order == 2:
        if isinstance(nested_list, list):
            if len(nested_list) > 2 or isinstance(nested_list[1], list):
                previous = re.search('\w+', root).group(0)
                nested_list[0] = nested_list[0] + '^' + previous
                nested_list[1] = nested_list[1:][0]
                root = nested_list[0]
            for idx, e in enumerate(nested_list):
                nested_list[idx] = vertical_markovization_recursive(e, root, v_order)
        return nested_list
    else:
        raise ValueError('Vertical order > 2 not implemented')


def horizontal_markovization_recursive(nested_list, h_order=2):
    """Executes horizontal markovization on a tree in the formatted as a nested list.
    Works by recursively looping over all nested list elements."""
    h_order_cor = h_order - 1
    if isinstance(nested_list, list):
        if len(nested_list) > 2:
            if '@' in nested_list[0]:
                all_but_first = nested_list[0].split('_')[1:]
                first = nested_list[0].split('_')[0]
                last_h_order = all_but_first[-h_order_cor:]
                last_h_order[:0] = [first]
                merged = '_'.join(last_h_order)
                rm = ''.join(re.search('([^(^)]+)+', nested_list[1][0]).group(0))
                bt = merged + '_' + rm
            else:
                rm = ''.join(re.search('([^(^)]+)+', nested_list[1][0]).group(0))
                bt = '@' + nested_list[0] + '->_' + rm
            nested_list[2] = [bt] + nested_list[2:]
            if len(nested_list) > 3:
                del nested_list[3:]
        for idx, e in enumerate(nested_list):
            nested_list[idx] = horizontal_markovization_recursive(e, h_order)
    return nested_list


def vertical_horizonantal_markovization(nested_list, h_order=2, v_order=2):
    """Executes both horizontal and vertical markovization on a tree"""
    vertically_markovized = vertical_markovization(nested_list, v_order)
    horizontally_markovized = horizontal_markovization_recursive(vertically_markovized, h_order)
    return horizontally_markovized


class TestBStep2(unittest.TestCase):
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

        self.test_markov_sentences = [
            '''(ROOT (S^ROOT (NP^S (NNP Ms.) (@NP^S->_NNP (NNP Haag))) (@S^ROOT->_NP (VP^S (VBZ plays) (@VP^S->_VBZ (NP^VP (NNP Elianti)))) (@S^ROOT->_NP_VP (. .)))))''',
            '''(ROOT (S^ROOT (NP^S (NNP Rolls-Royce) (@NP^S->_NNP (NNP Motor) (@NP^S->_NNP_NNP (NNPS Cars) (@NP^S->_NNP_NNPS (NNP Inc.))))) (@S^ROOT->_NP (VP^S (VBD said) (@VP^S->_VBD (SBAR^VP (S^SBAR (NP^S (PRP it)) (@S^SBAR->_NP (VP^S (VBZ expects) (@VP^S->_VBZ (S^VP (NP^S (PRP$ its) (@NP^S->_PRP$ (NNP U.S.) (@NP^S->_PRP$_NNP (NNS sales)))) (@S^VP->_NP (VP^S (TO to) (@VP^S->_TO (VP^VP (VB remain) (@VP^VP->_VB (ADJP^VP (JJ steady)) (@VP^VP->_VB_ADJP (PP^VP (IN at) (@PP^VP->_IN (NP^PP (QP^NP (IN about) (@QP^NP->_IN (CD 1,200))) (@NP^PP->_QP (NNS cars))))) (@VP^VP->_ADJP_PP (PP^VP (IN in) (@PP^VP->_IN (NP^PP (CD 1990))))))))))))))))))) (@S^ROOT->_NP_VP (. .)))))''',
            '''(ROOT (S^ROOT (NP^S (DT The) (@NP^S->_DT (NN luxury) (@NP^S->_DT_NN (NN auto) (@NP^S->_NN_NN (NN maker))))) (@S^ROOT->_NP (NP^S (JJ last) (@NP^S->_JJ (NN year))) (@S^ROOT->_NP_NP (VP^S (VBD sold) (@VP^S->_VBD (NP^VP (CD 1,214) (@NP^VP->_CD (NNS cars))) (@VP^S->_VBD_NP (PP^VP (IN in) (@PP^VP->_IN (NP^PP (DT the) (@NP^PP->_DT (NNP U.S.))))))))))))''',
            '''(ROOT (S^ROOT (`` ``) (@S^ROOT->_`` (ADVP^S (RB Apparently)) (@S^ROOT->_``_ADVP (NP^S (DT the) (@NP^S->_DT (NN commission))) (@S^ROOT->_ADVP_NP (VP^S (VBD did) (@VP^S->_VBD (RB not) (@VP^S->_VBD_RB (ADVP^VP (RB really)) (@VP^S->_RB_ADVP (VP^VP (VB believe) (@VP^VP->_VB (PP^VP (IN in) (@PP^VP->_IN (NP^PP (DT this) (@NP^PP->_DT (NN ideal))))))))))) (@S^ROOT->_NP_VP (. .) (@S^ROOT->_VP_. ('' ''))))))))''',
            '''(ROOT (S^ROOT (CC But) (@S^ROOT->_CC (NP^S (NP^NP (QP^NP (IN about) (@QP^NP->_IN (CD 25))) (@NP^NP->_QP (NN %))) (@NP^S->_NP (PP^NP (IN of) (@PP^NP->_IN (NP^PP (DT the) (@NP^PP->_DT (NNS insiders))))))) (@S^ROOT->_CC_NP (, ,) (@S^ROOT->_NP_, (PP^S (VBG according) (@PP^S->_VBG (PP^PP (TO to) (@PP^PP->_TO (NP^PP (NNP SEC) (@NP^PP->_NNP (NNS figures))))))) (@S^ROOT->_,_PP (, ,) (@S^ROOT->_PP_, (VP^S (VBP file) (@VP^S->_VBP (NP^VP (PRP$ their) (@NP^VP->_PRP$ (NNS reports))) (@VP^S->_VBP_NP (ADVP^VP (RB late))))) (@S^ROOT->_,_VP (. .)))))))))''',
            '''(ROOT (S^ROOT (ADVP^S (RB Already)) (@S^ROOT->_ADVP (, ,) (@S^ROOT->_ADVP_, (NP^S (DT the) (@NP^S->_DT (NNS consequences))) (@S^ROOT->_,_NP (VP^S (VBP are) (@VP^S->_VBP (VP^VP (VBG being) (@VP^VP->_VBG (VP^VP (VBN felt) (@VP^VP->_VBN (PP^VP (IN by) (@PP^VP->_IN (NP^PP (NP^NP (NP^NP (JJ other) (@NP^NP->_JJ (NNS players))) (@NP^NP->_NP (PP^NP (IN in) (@PP^NP->_IN (NP^PP (DT the) (@NP^PP->_DT (JJ financial) (@NP^PP->_DT_JJ (NNS markets)))))))) (@NP^PP->_NP (: --) (@NP^PP->_NP_: (JJ even) (@NP^PP->_:_JJ (NP^NP (NNS governments)))))))))))))) (@S^ROOT->_NP_VP (. .)))))))'''
        ]

    def test_binarize(self):
        for test_string_sentence, test_bin_sentence in zip(self.test_string_sentences, self.test_markov_sentences):
            parsed = parse_to_list(test_string_sentence)
            binarized_list = vertical_horizonantal_markovization(parsed)
            self.assertEqual(binarized_to_string(binarized_list), test_bin_sentence)


def markov_to_file(infile, outfile, h_order, v_order):
    """Reads all lines form a file, markovizes them, and writes the markov tree to a new file"""
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
                binarized_line = binarized_to_string(
                    vertical_horizonantal_markovization(parse_to_list(line), h_order, v_order))
                f_out.write(binarized_line + '\n')
    print('Done.')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-input', type=str, help='Path to file containing S-Expressions')
    parser.add_argument('-output', type=str, help='Path to save markov S-Expressions')
    parser.add_argument('-hor', type=int, help='Horizontal markovization parameter')
    parser.add_argument('-ver', type=int, help='Vertical markovization parameter')
    args = parser.parse_args()

    if not args.input and not args.output:
        unittest.main()
    else:
        markov_to_file(args.input, args.output, args.hor, args.ver)
