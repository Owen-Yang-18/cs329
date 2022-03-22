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


# def remove_overlaps(entities: List[Tuple[str, int, int, Set[str]]]) -> List[Tuple[str, int, int, Set[str]]]:
#     """
#     :param entities: a list of tuples where each tuple consists of
#              - span: str,
#              - start token index (inclusive): int
#              - end token index (exclusive): int
#              - a set of values for the span: Set[str]
#     :return: a list of entities where each entity is represented by a tuple of (span, start index, end index, value set)
#     """
#     # TODO: to be updated
#     entities = sorted(entities, key=lambda x:x[1])
#     print(entities)
#     entities.append(('XXX', int(-1), int(-1), {'XXX'}))
#     overlap_sequence = []
#     nonoverlap_sequence = []
#     i = 0
#     max = -1
#     while i < len(entities) - 1:
#         if entities[i][2] > max:
#             max = entities[i][2]
#         seq = []
#         seq.append(entities[i])
#         j = i + 1
#         while j < len(entities) and entities[j][1] >= 0 and entities[j][1] <= max:
#             seq.append(entities[j])
#             if entities[j][2] > max:
#                 max = entities[j][2]
#             j += 1
#
#         if len(seq) > 1:
#             overlap_sequence.append(seq)
#         else:
#             nonoverlap_sequence.append(seq[0])
#         i = j
#     print(overlap_sequence)
#     for j in range(len(overlap_sequence)):
#         if overlap_sequence[j][0][2] >= overlap_sequence[j][-1][1]:
#             index = -1
#             max = -1
#             for i in range(len(overlap_sequence[j])):
#                 ran = overlap_sequence[j][i][2] - overlap_sequence[j][i][1]
#                 if ran > max:
#                     max = ran
#                     index = i
#             overlap_sequence[j] = list(overlap_sequence[j][index])
#
#     print(overlap_sequence)
#     return []

def check_overlap(entities: List[Tuple[str, int, int, Set[str]]]):
    # check whether overlap exists given a list of entities
    entities = sorted(entities, key= lambda x:(x[1],x[2]), reverse=True)
    for i in range(len(entities)-1):
        if entities[i+1][2] > entities[i][1]:
            return True
    return False

def get_longer(entities: List[Tuple[str, int, int, Set[str]]]):
    # for a list with length 2
    if entities[0][2]-entities[0][1]>entities[1][2]-entities[1][1]:
        return entities[0]
    else:
        return entities[1]


def get_clean(entities: List[Tuple[str, int, int, Set[str]]]):
    # for a list with length > 2
    clean = [entities]
    while len(clean)!=0:
        current = clean.pop(-1)
        if not check_overlap(current):
            return current
        else:
            for i in range(len(current)):
                a = sorted(current, key= lambda x:x[2]-x[1])
                a.pop(i)
                clean.insert(0,a)

def remove_overlaps(entities: List[Tuple[str, int, int, Set[str]]]) -> List[Tuple[str, int, int, Set[str]]]:
    """
    :param entities: a list of tuples where each tuple consists of
             - span: str,
             - start token index (inclusive): int
             - end token index (exclusive): int
             - a set of values for the span: Set[str]
    :return: a list of entities where each entity is represented by a tuple of (span, start index, end index, value set)
    """

    overlap = []
    total_overlap = []
    end = False

    entities = sorted(entities, key=lambda x: (x[1], x[2]))

    for i in range(len(entities)-2,-1,-1):
        if entities[i+1][1] < entities[i][2]:
            overlap.append(entities.pop(i+1))
            end = True
        elif end:
            overlap.append(entities.pop(i+1))
            end = False
            total_overlap.append(overlap)
            overlap = []
    if end:
        overlap.append(entities.pop(0))
        total_overlap.append(overlap)

    clean_all = []
    print(total_overlap)
    for theoverlap in total_overlap:
        if len(theoverlap) == 2:
            clean_all.append(get_longer(theoverlap))
        else:
            clean_all.extend(get_clean(theoverlap))

    entities.extend(clean_all)

    return sorted(entities, key= lambda x:(x[1],x[2]))


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
    return []


if __name__ == '__main__':
    gaz_dir = 'ner'
    AC = read_gazetteers('ner')

    tokens = 'Atlantic City of Georgia'.split()
    entities = match(AC, tokens)
    entities = [('Atlantic City', 0, 2, {'us_city'}), ('Georgia', 3, 4, {'us_state', 'country'}), ('Georgia', 6, 14, {'us_state', 'country'}), ('Georgia', 12, 27, {'us_state', 'country'}),
                ('Georgia', 25, 33, {'us_state', 'country'}), ('Georgia', 30, 38, {'us_state', 'country'}), ('Georgia', 54, 56, {'us_state', 'country'})]
    entities = remove_overlaps(entities)
    print(entities)
