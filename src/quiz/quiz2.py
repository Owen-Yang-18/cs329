# ========================================================================
# Copyright 2022 Emory University
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
import json
import math
from typing import Dict, Any, List

from vector_space_models import term_frequencies, document_frequencies


def cosine(x1: Dict[str, float], x2: Dict[str, float]) -> float:
    # TODO: to be updated
    inner_product = sum(((s1 * x2.get(term, 0)) for term, s1 in x1.items()))
    x11 = sum((s2) ** 2 for term, s2 in x1.items()) ** 0.5
    x22 = sum((s3) ** 2 for term, s3 in x2.items()) ** 0.5
    return inner_product / (x11 * x22)

def vectorize(documents: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    # Feel free to update this function
    def ntf(documents):
        tfs = term_frequencies(documents)
        alpha = 0.2
        out = dict()

        for key, counts in tfs.items():
            argmax = max(dict(counts.items()).values())
            out[key] = {t: alpha + (1.0 - alpha) * (tf / argmax) for t, tf in counts.items()}
        return out

    def wf(documents):
        tfs = term_frequencies(documents)
        out = dict()

        for key, counts in tfs.items():
            out[key] = {t: 1 + math.log(tf) if tf > 0.0 else 0 for t, tf in counts.items()}
        return out

    def tf_idfs(fables) -> Dict[str, Dict[str, int]]:
        tfs = term_frequencies(fables)
        dfs = document_frequencies(fables)
        out = dict()
        D = len(tfs)

        for dkey, term_counts in tfs.items():
            out[dkey] = {t: tf * math.log(D / dfs[t]) for t, tf in term_counts.items()}

        return out

    return tf_idfs(documents)

def similar_documents(X: Dict[str, Dict[str, float]], Y: Dict[str, Dict[str, float]]) -> Dict[str, str]:
    # Feel free to update this function
    def most_similar(Y: Dict[str, Dict[str, float]], X: Dict[str, float]) -> str:
        dic = {}
        for key in Y.keys():
            dic[key] = cosine(Y[str(key)], X)
        return max(dic.items(), key=lambda x: x[1])[0]

    return {k: most_similar(Y, x) for k, x in X.items()}

if __name__ == '__main__':
    fables = json.load(open('../../res/vsm/aesopfables.json'))
    fables_alt = json.load(open('../../res/vsm/aesopfables-alt.json'))

    v_fables = vectorize(fables)
    v_fables_alt = vectorize(fables_alt)

    for x, y in similar_documents(v_fables_alt, v_fables).items():
        print('{} -> {}'.format(x, y))