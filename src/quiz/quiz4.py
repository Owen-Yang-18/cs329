# ========================================================================
# Copyright 2020 Emory University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========================================================================
import glob
import itertools
import os
from types import SimpleNamespace
from typing import Iterable, Tuple, Any, List, Set

import ahocorasick

def create_ac(data: Iterable[Tuple[str, Any]]) -> ahocorasick.Automaton:
    """
    Creates the Aho-Corasick automation and adds all (span, value) pairs in the data and finalizes this matcher.
    :param data: a collection of (span, value) pairs.
    """
    AC = ahocorasick.Automaton(ahocorasick.STORE_ANY)

    for span, value in data:
        if span in AC:
            t = AC.get(span)
        else:
            t = SimpleNamespace(span=span, values=set())
            AC.add_word(span, t)
        t.values.add(value)

    AC.make_automaton()
    return AC


def read_gazetteers(dirname: str) -> ahocorasick.Automaton:
    data = []
    for filename in glob.glob(os.path.join(dirname, '*.txt')):
        label = os.path.basename(filename)[:-4]
        for line in open(filename):
            data.append((line.strip(), label))
    return create_ac(data)


def match(AC: ahocorasick.Automaton, tokens: List[str]) -> List[Tuple[str, int, int, Set[str]]]:
    """
    :param AC: the finalized Aho-Corasick automation.
    :param tokens: the list of input tokens.
    :return: a list of tuples where each tuple consists of
             - span: str,
             - start token index (inclusive): int
             - end token index (exclusive): int
             - a set of values for the span: Set[str]
    """
    smap, emap, idx = dict(), dict(), 0
    for i, token in enumerate(tokens):
        smap[idx] = i
        idx += len(token)
        emap[idx] = i
        idx += 1

    # find matches
    text = ' '.join(tokens)
    spans = []
    for eidx, t in AC.iter(text):
        eidx += 1
        sidx = eidx - len(t.span)
        sidx = smap.get(sidx, None)
        eidx = emap.get(eidx, None)
        if sidx is None or eidx is None: continue
        spans.append((t.span, sidx, eidx + 1, t.values))

    return spans

def findMax(sequence):
    k = 1
    sequence.sort(key=lambda x: x[2])
    r1 = sequence[0][2]

    for i in range(1, len(sequence)):
        l = sequence[i][1]
        r2 = sequence[i][2]

        if l > r1:
            r1 = r2
            k += 1
    return k

def nonoverlap(seq):
    seq.sort(key=lambda x:x[2])
    for i in range(len(seq)-1):
        if seq[i+1][1] < seq[i][2]:
            return False
    return True

def bf_remove(sequence):
    k = findMax(sequence)
    maxval = -1
    maxseq = list()
    for seq in itertools.combinations(sequence, k):
        seq = list(seq)
        if nonoverlap(seq):
            total = sum([item[2]-item[1] for item in seq])
            if total > maxval:
                maxval = total
                maxseq = seq
    return maxseq

def remove_overlaps(entities: List[Tuple[str, int, int, Set[str]]]) -> List[Tuple[str, int, int, Set[str]]]:
    """
    :param entities: a list of tuples where each tuple consists of
             - span: str,
             - start token index (inclusive): int
             - end token index (exclusive): int
             - a set of values for the span: Set[str]
    :return: a list of entities where each entity is represented by a tuple of (span, start index, end index, value set)
    """
    # TODO: to be updated
    entities = sorted(entities, key=lambda x:x[1])
    entities.append(('XXX', int(-1), int(-1), {'XXX'}))
    overlap_sequence = []
    nonoverlap_sequence = []
    i = 0
    max = -1
    while i < len(entities) - 1:
        if entities[i][2] > max:
            max = entities[i][2]
        seq = []
        seq.append(entities[i])
        j = i + 1
        while j < len(entities) and entities[j][1] >= 0 and entities[j][1] <= max-1:
            seq.append(entities[j])
            if entities[j][2] > max:
                max = entities[j][2]
            j += 1

        if len(seq) > 1:
            overlap_sequence.append(seq)
        else:
            nonoverlap_sequence.append(seq[0])
        i = j

    for j in range(len(overlap_sequence)):
        if overlap_sequence[j][0][2] >= overlap_sequence[j][-1][1]:
            index = -1
            max = -1
            for i in range(len(overlap_sequence[j])):
                ran = overlap_sequence[j][i][2] - overlap_sequence[j][i][1]
                if ran > max:
                    max = ran
                    index = i
            overlap_sequence[j] = [tuple(overlap_sequence[j][index])]
        else:
            overlap_sequence[j] = bf_remove(overlap_sequence[j])
    final = []
    for ovse in overlap_sequence:
        for item in ovse:
            final.append(item)
    for nose in nonoverlap_sequence:
        final.append(nose)
    final = sorted(final, key=lambda x:x[2])
    return final

def to_bilou(tokens: List[str], entities: List[Tuple[str, int, int, str]]) -> List[str]:
    """
    :param tokens: a list of tokens.
    :param entities: a list of tuples where each tuple consists of
             - span: str,
             - start token index (inclusive): int
             - end token index (exclusive): int
             - a named entity tag
    :return: a list of named entity tags in the BILOU notation with respect to the tokens
    """
    # TODO: to be updated
    result = ["O"] * len(tokens)
    for item in entities:
        word, bow, eow, tag = item
        tokens = word.split()
        if len(tokens) == 1:
            result[bow] = "U-" + tag
        else:
            for tok in tokens:
                if tokens.index(tok) == 0:
                    result[bow] = "B-" + tag
                elif tokens.index(tok) == len(tokens) - 1:
                    result[bow + tokens.index(tok)] = "L-" + tag
                else:
                    result[bow + tokens.index(tok)] = "I-" + tag

    return result

if __name__ == '__main__':
    gaz_dir = '../../res/ner'
    AC = read_gazetteers('C:/Users/Owen/PycharmProjects/cs329/res/ner')

    tokens = 'Atlantic City of Georgia'.split()
    entities = match(AC, tokens)
    # Uncomment below for some edgy cases, especially the first one
    # entities = [('Atlantic City', 0, 2, {'us_city'}), ('Georgia', 3, 4, {'us_state', 'country'}), ('Georgia', 6, 14, {'us_state', 'country'}), ('Georgia',12, 27, {'us_state', 'country'}),
    #            ('Georgia', 25, 33, {'us_state', 'country'}), ('Georgia', 30, 38, {'us_state', 'country'}), ('Georgia', 54, 56, {'us_state', 'country'})]
    # entities = [('Atlantic City', 0, 2, {'us_city'}), ('Georgia', 3, 4, {'us_state', 'country'}),
    #             ('Georgia', 6, 10, {'us_state', 'country'}), ('Georgia', 8, 20, {'us_state', 'country'}), ('Georgia', 12, 15, {'us_state', 'country'})
    #             , ('Georgia', 17, 24, {'us_state', 'country'}), ('Georgia', 22, 50, {'us_state', 'country'}), ('Georgia', 28, 33, {'us_state', 'country'}), ('Georgia', 34, 46, {'us_state', 'country'})]
    # entities = [('Atlantic City', 0, 2, {'us_city'}), ('Georgia', 2, 4, {'us_state', 'country'}),
    #             ('Georgia', 6, 10, {'us_state', 'country'}), ('Georgia', 8, 20, {'us_state', 'country'}),
    #             ('Georgia', 12, 25, {'us_state', 'country'})
    #     , ('Georgia', 27, 34, {'us_state', 'country'}), ('Georgia', 32, 38 , {'us_state', 'country'}),
    #             ('Georgia', 39, 43, {'us_state', 'country'}), ('Georgia', 44, 46, {'us_state', 'country'})]
    entities = remove_overlaps(entities)
    print(entities)

    tokens = 'Jinho is a professor at Emory University in the United States of America'.split()
    entities = [
        ('Jinho', 0, 1, 'PER'),
        ('Emory University', 5, 7, 'ORG'),
        ('United States of America', 9, 13, 'LOC')
    ]
    tags = to_bilou(tokens, entities)
    for token, tag in zip(tokens, tags): print(token, tag)
