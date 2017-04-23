import string
import pdb
from itertools import chain

from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag

from utils import lemmatize, porter, lemmatize_sentence, synset_properties

EN_STOPWORDS = stopwords.words('english')

def score(string1, string2):
    answer_score = 0

    while len(string1) > 0 and len(string2) > 0:
        answer = longest_common_sentence(string1, string2)
        if len(answer.strip()) == 0:
            break
        splitted_answer = answer.split()
        answer_len = len(splitted_answer)
        string1 = string1.replace(answer, "")
        string2 = string2.replace(answer, "")
        answer_score += answer_len * answer_len

    return answer_score

def longest_common_substring(s1, s2):
  m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
  longest, x_longest = 0, 0
  for x in xrange(1, 1 + len(s1)):
    for y in xrange(1, 1 + len(s2)):
      if s1[x - 1] == s2[y - 1]:
        m[x][y] = m[x - 1][y - 1] + 1
        if m[x][y] > longest:
          longest = m[x][y]
          x_longest = x
      else:
        m[x][y] = 0
  return s1[x_longest - longest: x_longest]

def longest_common_sentence(s1, s2):
    s1_words = s1.split(' ')
    s2_words = s2.split(' ')  
    return ' '.join(longest_common_substring(s1_words, s2_words))

def compare_overlaps(context, synsets_signatures):
    overlaplen_synsets = [] # a tuple of (len(overlap), synset)
    for ss in synsets_signatures:
        for context_word in context:
            for context_ss in context_word:
                for gloss in synsets_signatures[ss]:
                    for context_gloss in context_word[context_ss]:
                        
                        gloss_words = gloss.translate({ord(i):None for i in '!@#$?.,;()'}).split()
                        gloss_words = [i for i in gloss_words if i not in EN_STOPWORDS]
                        gloss_words = ' '.join([porter.stem(i) for i in gloss_words])

                        context_words = context_gloss.translate({ord(i):None for i in '!@#$?.,;()'}).split()
                        context_words = [i for i in context_words if i not in EN_STOPWORDS]
                        context_words = ' '.join([porter.stem(i) for i in context_words])

                        overlaps = score(gloss_words, context_words)
                        overlaplen_synsets.append((overlaps, ss, gloss_words, context_words))

    # Rank synsets from highest to lowest overlap.
    ranked_synsets = sorted(overlaplen_synsets, reverse=True)

    return ranked_synsets


def simple_signature(ambiguous_word, pos=None):
    synsets_signatures = {}
    for ss in wn.synsets(ambiguous_word):

        if str(ss.pos()) != pos:
            continue

        signature = []

        # Includes definition
        ss_definition = synset_properties(ss, 'definition')
        signature.append(ss_definition)

        # Include holonyms
        ss_mem_holonyms = synset_properties(ss, 'member_holonyms')
        ss_part_holonyms = synset_properties(ss, 'part_holonyms')
        ss_sub_holonyms = synset_properties(ss, 'substance_holonyms')
        ss_all = ss_mem_holonyms + ss_part_holonyms + ss_sub_holonyms

        if len(ss_all) > 0:
            signature += [' '.join(synset_properties(i, 'definition') for i in ss_all)]
        # # Includes meronyms
        ss_mem_meronyms = synset_properties(ss, 'member_meronyms')
        ss_part_meronyms = synset_properties(ss, 'part_meronyms')
        ss_sub_meronyms = synset_properties(ss, 'substance_meronyms')
        ss_all = ss_mem_meronyms + ss_part_meronyms + ss_sub_meronyms

        if len(ss_all) > 0:
            signature += [' '.join(synset_properties(i, 'definition') for i in ss_all)]

        ss_hyponyms = synset_properties(ss, 'hyponyms')
        if len(ss_hyponyms) > 0:
            signature += [' '.join(synset_properties(i, 'definition') for i in ss_hyponyms)]
        ss_hypernyms = synset_properties(ss, 'hypernyms')
        if len(ss_hypernyms) > 0:
            signature += [' '.join(synset_properties(i, 'definition') for i in ss_hypernyms)]

        synsets_signatures[ss] = signature

    return synsets_signatures

def adapted_lesk(context_sentence, ambiguous_word, pos=None):

    # Ensure that ambiguous word is a lemma.
    ambiguous_word = lemmatize(ambiguous_word)

    # If ambiguous word not in WordNet return None
    if not wn.synsets(ambiguous_word):
        return None
    # Else return the signature of the ambigous word
    word_sign = simple_signature(ambiguous_word, pos)
    context_sign = []
    for word in context_sentence.split():
        if word == ambiguous_word:
            continue
        sign = simple_signature(word, pos)
        context_sign.append(sign)
    best_sense = compare_overlaps(context_sign, word_sign)
    return best_sense

def calculate_accuracy(n):
    total_aparitions = 0
    right_answers = 0

    f = open('line/cord2', 'r')
    cord_line_context = f.read().split()
    cord_line_context = [porter.stem(i) for i in cord_line_context]
    
    indices = (i for i,word in enumerate(cord_line_context) if word=="line")
    neighboring_words = []
    for ind in indices: neighboring_words.append(cord_line_context[ind-n-1:ind]+cord_line_context[ind:ind+n])

    for neighbours in neighboring_words:
        sentence = ' '.join(neighbours)
        answer = adapted_lesk(sentence,'line','n', True, \
                     nbest=True, keepscore=True)

        best_sense = answer[0][1]
        total_aparitions += 1
        if best_sense.name() == 'line.n.18': right_answers += 1 

    print right_answers / total_aparitions


bank_sents = ['I went to the bank to deposit my money',
'The river bank was full of dead fishes']

plant_sents = ['The workers at the industrial plant were overworked',
'The plant was no longer bearing flowers']

print("======== adapted_lesk ===========\n")


print("adapted_lesk() ...")
print("Context:", plant_sents[0])
answer = adapted_lesk(plant_sents[0],'plant','n')
best_sense = answer[0][1]
try: definition = best_sense.definition()
except: definition = best_sense.definition
print("Definition:", definition)

