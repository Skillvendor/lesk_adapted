import string
import pdb
from itertools import chain

from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag

from utils import lemmatize, porter, lemmatize_sentence, synset_properties

EN_STOPWORDS = stopwords.words('english')

def compare_overlaps(context, synsets_signatures, \
                     nbest=False, keepscore=False, normalizescore=False):
    overlaplen_synsets = [] # a tuple of (len(overlap), synset).
    for ss in synsets_signatures:
        overlaps = set(synsets_signatures[ss]).intersection(context)
        overlaplen_synsets.append((len(overlaps), ss))

    # Rank synsets from highest to lowest overlap.
    ranked_synsets = sorted(overlaplen_synsets, reverse=True)

    # Normalize scores such that it's between 0 to 1.
    if normalizescore:
        total = float(sum(i[0] for i in ranked_synsets))
        ranked_synsets = [(i/total,j) for i,j in ranked_synsets]

    if not keepscore: # Returns a list of ranked synsets without scores
        ranked_synsets = [i[1] for i in sorted(overlaplen_synsets, \
                                               reverse=True)]

    if nbest: # Returns a ranked list of synsets.
        return ranked_synsets
    else: # Returns only the best sense.
        return ranked_synsets[0]

def simple_signature(ambiguous_word, pos=None, lemma=True, stem=False, \
                     hyperhypo=True, stop=True):

    synsets_signatures = {}
    for ss in wn.synsets(ambiguous_word):

        try:
            if pos and str(ss.pos()) != pos:
                continue
        except:
            if pos and str(ss.pos) != pos:
                continue

        signature = []

        # Includes definition
        ss_definition = synset_properties(ss, 'definition')
        signature+=ss_definition.translate({ord(i):None for i in '!@#$?.,;()'}).split()

        # Includes examples
        ss_examples = synset_properties(ss, 'examples')
        signature+=list(chain(*[i.split() for i in ss_examples]))

        # Includes lemma_names
        ss_lemma_names = synset_properties(ss, 'lemma_names')
        signature+= ss_lemma_names

         # Includes holonyms
        ss_mem_holonyms = synset_properties(ss, 'member_holonyms')
        ss_part_holonyms = synset_properties(ss, 'part_holonyms')
        ss_sub_holonyms = synset_properties(ss, 'substance_holonyms')

        # Includes meronyms
        ss_mem_meronyms = synset_properties(ss, 'member_meronyms')
        ss_part_meronyms = synset_properties(ss, 'part_meronyms')
        ss_sub_meronyms = synset_properties(ss, 'substance_meronyms')

        # Includes similar_tos
        ss_simto = synset_properties(ss, 'similar_tos')

        related_senses = list(set(ss_mem_holonyms+ss_part_holonyms+
                                  ss_sub_holonyms+ss_mem_meronyms+
                                  ss_part_meronyms+ss_sub_meronyms+ ss_simto))


        signature = list([j for j in chain(*[synset_properties(i, 'lemma_names')
                                             for i in related_senses])
                          if j not in EN_STOPWORDS])

        # Optional: includes lemma_names of hypernyms and hyponyms.
        if hyperhypo == True:
            ss_hyponyms = synset_properties(ss, 'hyponyms')
            ss_hypernyms = synset_properties(ss, 'hypernyms')
            ss_hypohypernyms = ss_hypernyms+ss_hyponyms
            signature+= list(chain(*[i.lemma_names() for i in ss_hypohypernyms]))

        # Optional: removes stopwords.
        if stop == True:
            signature = [i for i in signature if i not in EN_STOPWORDS]

        # Lemmatized context is preferred over stemmed context.
        if lemma == True:
            signature = [lemmatize(i) for i in signature]

        # Matching exact words may cause sparsity, so optional matching for stems.
        if stem == True:
            signature = [porter.stem(i) for i in signature]
        synsets_signatures[ss] = signature

    return synsets_signatures

def adapted_lesk(context_sentence, ambiguous_word, \
                pos=None, lemma=True, stem=True, hyperhypo=True, \
                stop=True, context_is_lemmatized=False, \
                nbest=False, keepscore=False, normalizescore=False):

    # Ensure that ambiguous word is a lemma.
    ambiguous_word = lemmatize(ambiguous_word)

    # If ambiguous word not in WordNet return None
    if not wn.synsets(ambiguous_word):
        return None
    # Else return the signature of the ambigous word
    ss_sign = simple_signature(ambiguous_word, pos, lemma, stem, hyperhypo)
    
    # Disambiguate the sense in context.
    if context_is_lemmatized:
        context_sentence = context_sentence.split()
    else:
        context_sentence = lemmatize_sentence(context_sentence)
    best_sense = compare_overlaps(context_sentence, ss_sign, \
                                    nbest=nbest, keepscore=keepscore, \
                                    normalizescore=normalizescore)
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

    pdb.set_trace()
    print right_answers / total_aparitions


bank_sents = ['I went to the bank to deposit my money',
'The river bank was full of dead fishes']

plant_sents = ['The workers at the industrial plant were overworked',
'The plant was no longer bearing flowers']

print("======== adapted_lesk ===========\n")


calculate_accuracy(10)