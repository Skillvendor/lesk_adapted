import string
import pdb
from itertools import chain

from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag

from utils import lemmatize, porter, lemmatize_sentence, synset_properties

EN_STOPWORDS = stopwords.words('english')

# def longestSubstringFinder(string1, string2):
#     answer = ""
#     len1, len2 = len(string1), len(string2)
#     for i in range(len1):
#         match = ""
#         for j in range(len2):
#             if (i + j < len1 and string1[i + j] == string2[j]):
#                 match += string2[j]
#             else:
#                 if (len(match) > len(answer)): answer = match
#                 match = ""
#     return answer

def compare_overlaps(context, synsets_signatures):
    overlaplen_synsets = [] # a tuple of (len(overlap), synset)
    for ss in synsets_signatures:
        for context_word in context:
            for context_ss in context_word:
                for gloss in synsets_signatures[ss]:
                    for context_gloss in context_word[context_ss]:
                        # overlaps = longestSubstringFinder(gloss, context_gloss)
                        # pdb.set_trace()
                        gloss_words = gloss.translate({ord(i):None for i in '!@#$?.,;()'}).split()
                        gloss_words = [i for i in gloss_words if i not in EN_STOPWORDS]
                        gloss_words = [lemmatize(i) for i in gloss_words]
                        gloss_words = [porter.stem(i) for i in gloss_words]

                        context_words = context_gloss.translate({ord(i):None for i in '!@#$?.,;()'}).split()
                        context_words = [i for i in context_words if i not in EN_STOPWORDS]
                        context_words = [lemmatize(i) for i in context_words]
                        context_words = [porter.stem(i) for i in context_words]

                        overlaps = set(gloss_words).intersection(set(context_words))
                        # overlaplen_synsets.append((len(overlaps), ss, context_ss))
                        overlaplen_synsets.append((len(overlaps), ss, gloss, context_gloss))

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

        if len(ss_mem_holonyms) > 0:
            signature += [synset_properties(i, 'definition') for i in ss_mem_holonyms]
        if len(ss_part_holonyms) > 0:
            signature += [synset_properties(i, 'definition') for i in ss_part_holonyms]
        if len(ss_sub_holonyms) > 0:
            signature += [synset_properties(i, 'definition') for i in ss_sub_holonyms]

        # # Includes meronyms
        ss_mem_meronyms = synset_properties(ss, 'member_meronyms')
        ss_part_meronyms = synset_properties(ss, 'part_meronyms')
        ss_sub_meronyms = synset_properties(ss, 'substance_meronyms')

        if len(ss_mem_meronyms) > 0:
            signature += [synset_properties(i, 'definition') for i in ss_mem_meronyms]
        if len(ss_part_meronyms) > 0:
            signature += [synset_properties(i, 'definition') for i in ss_part_meronyms]
        if len(ss_sub_meronyms) > 0:
            signature += [synset_properties(i, 'definition') for i in ss_sub_meronyms]

        ss_hyponyms = synset_properties(ss, 'hyponyms')
        if len(ss_hyponyms) > 0:
            signature += [synset_properties(i, 'definition') for i in ss_hyponyms]

        ss_hypernyms = synset_properties(ss, 'hypernyms')
        if len(ss_hypernyms) > 0:
            signature += [synset_properties(i, 'definition') for i in ss_hypernyms]

        # Optional: removes stopwords.
        # signature = [i for i in signature if i not in EN_STOPWORDS]

        # Lemmatized context is preferred over stemmed context.
        # signature = [lemmatize(i) for i in signature]

        # Matching exact words may cause sparsity, so optional matching for stems.
        # signature = [porter.stem(i) for i in signature]
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

bank_sents = ['I went to the bank to deposit my money',
'The river bank was full of dead fishes']

plant_sents = ['The workers at the industrial plant were overworked',
'The plant was no longer bearing flowers']

print("======== adapted_lesk ===========\n")

print("adapted_lesk() ...")
print("Context:", bank_sents[1])
answer = adapted_lesk(bank_sents[1],'bank','n')
# print("Senses ranked by #overlaps:", answer)
best_sense = answer[0][1]
try: definition = best_sense.definition()
except: definition = best_sense.definition
print("Definition:", definition)
# print("Length:", answer[0][0])
print("Words 1:", answer[0][2], " 2:", answer[0][3])
print("\n Test: ", set(answer[0][2].translate({ord(i):None for i in '!@#$?.,;()'}).split()).intersection(set(answer[0][3].translate({ord(i):None for i in '!@#$?.,;()'}).split())))
print
