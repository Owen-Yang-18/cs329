# ========================================================================
# Copyright 2021 Emory University
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
digits = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve',
          'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
exp = ['', 'thousand', 'million', 'billion', 'trillion']
hundred = ['hundred']
ordinals = ['half', 'halves', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth',
          'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth', 'twentieth', 'thirtieth',
            'fortieth', 'fiftieth', 'sixtieth', 'seventieth', 'eightieth', 'ninetieth', 'hundredth', 'thousandth', 'millionth', 'billionth', 'trillionth']
any = digits + tens + exp + hundred

### Code adapted from class discussion: https://github.com/emory-courses/computational-linguistics/blob/master/src/string_matching.py
def tokenize(text):
    STARTS = ['"', '?', '!']
    ENDS = ["n't", '.', ',', '"', '?', '!']
    tokens = text.split()
    new_tokens = []

    def aux(token):
        hyphen = "-" in token
        if hyphen:
            idx = token.index("-")
            aux(token[:idx])
            new_tokens.append("-")
            aux(token[idx + 1:])
            return

        start = next((t for t in STARTS if token.startswith(t)), None)
        if start:
            n = len(start)
            new_tokens.append(token[:n])
            aux(token[n:])
            return

        end = next((t for t in ENDS if token.endswith(t)), None)
        if end:
            n = len(end)
            t1, t2 = token[:-n], token[-n:]
            if not (t1 in {'Mr', 'Ms'} and t2 == '.'):
                aux(t1)
                new_tokens.append(t2)
                return

        new_tokens.append(token)

    for token in tokens: aux(token)

    return new_tokens

def digit_conversion(list):
    nums = list.copy()
    for j in range(len(nums)):
        nums[j] = nums[j].lower()
    number = []
    i = 0
    while i < len(nums):
        if nums[i] in tens and nums[i + 1] in digits:
            number.append(((tens.index(nums[i]) * 10) + digits.index(nums[i + 1])))
            i += 2
        elif nums[i] in tens:
            number.append(tens.index(nums[i]) * 10)
            i += 1
        elif nums[i] in digits:
            number.append(digits.index(nums[i]))
            i += 1
        elif nums[i] in exp and not number:
            number.append(10 ** (3 * exp.index(nums[i])))
            i += 1
        elif nums[i] in hundred and not number:
            number.append(100)
            i += 1
        elif nums[i] in exp:
            number[-1] *= (10 ** (3 * exp.index(nums[i])))
            i += 1
        elif nums[i] in hundred:
            number[-1] *= 100
            i += 1
        else:
            i += 1

    return sum(number)

def normalize(text):
    # TODO: to be updated
    tokens = tokenize(text)
    tokens.append('.') ### to handle index out of bound exception:: see below
    tokens = ['.'] + tokens ### to handle index out of bound exception:: see below
    words_list = []
    num_list = []
    i = 1

    while i < len(tokens):
        if tokens[i].lower() in any + ordinals:
            j = i + 1
            while(tokens[j].lower() in any or tokens[j] == '-' or tokens[j].lower() in ordinals or tokens[j] == 'point'):
                j += 1
            words_list.append(list(tokens[i:j]))
            i = j
        else:
            i += 1

    i = 0
    while len(words_list) > 0 and i < len(words_list):
        if 'point' in words_list[i]:
            del words_list[i]
        else:
            i += 1

    i = 0
    while len(words_list) > 0 and i < len(words_list):
        if set(words_list[i]).intersection(ordinals):
            del words_list[i]
        else:
            i += 1

    for x in range(len(words_list)):
        idx = tokens.index(words_list[x][0]) - 1
        count = 0
        if tokens[idx] in ['a', 'A']:
            for z in range(len(words_list[x])):
                if words_list[x][z].lower() in exp + hundred or words_list[x][z].lower() == '-':
                    count += 1
        if count == len(words_list[x]):
            words_list[x].insert(0, tokens[idx])

    for k in range(len(words_list)):
        if '-' in words_list[k]:
            w = words_list[k].copy()
            w.remove('-')
            num_list.append(digit_conversion(w))
        else:
            num_list.append(digit_conversion(words_list[k]))

    # Handling single hyphenation
    # Handling (a series) of hyphenation (crazy case)
    for n in range(len(words_list)):
        for p in range(len(words_list[n])):
            if '-' in words_list[n]:
                idx = words_list[n].index('-')
                words_list[n][idx] = words_list[n][idx - 1] + '-' + words_list[n][idx + 1]
                words_list[n].remove(words_list[n][idx - 1])
                words_list[n].remove(words_list[n][idx])

    for m in range(len(words_list)):
        str1 = ' '.join(words_list[m])
        text = text.replace(str1, str(num_list[m]))

    return text


def normalize_extra(text):
    # TODO: to be updated
    return text


if __name__ == '__main__':
    S = [
        'I met twelve people',
        'I have one brother and two sisters',
        'A year has three hundred sixty-five days',
        'I made a million dollars',
        'Professor Zureick-Brown has "Thirty-Three-Thousand twenty one???!!!" cars',
        'There is a two story building costing a Hundred-Million dollars',
        'Andy has two third apples and one million five hundred sixty four halves bananas',
        'Ondy wins thirty-four point six five percents',
        'I am the first one to get a six two hundred twenty-fourth battery'
    ]

    T = [
        'I met 12 people',
        'I have 1 brother and 2 sisters',
        'A year has 365 days',
        'I made 1000000 dollars',
        'Professor Zureick-Brown has "33021???!!!" cars',
        'There is a 2 story building costing 100000000 dollars',
        'Andy has two third apples and one million five hundred sixty four halves bananas',
        'Ondy wins thirty-four point six five percents',
        'I am the first one to get a six two hundred twenty-fourth battery'
    ]

    correct = 0
    for s, t in zip(S, T):
        if normalize(s) == t:
            correct += 1

    print('Score: {}/{}'.format(correct, len(S)))
