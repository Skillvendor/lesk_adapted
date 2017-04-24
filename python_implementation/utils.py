from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import pos_tag, word_tokenize

SS_PARAMETERS_TYPE_MAP = {'definition':str, 'lemma_names':list,
                          'examples':list,  'hypernyms':list,
                         'hyponyms': list, 'member_holonyms':list,
                         'part_holonyms':list, 'substance_holonyms':list,
                         'member_meronyms':list, 'substance_meronyms': list,
                         'part_meronyms':list, 'similar_tos':list, 'holonyms': list,
                         'meronyms': list, 'entailments': list, 'full_hyponyms':list,
                         'full_hypernyms': list, 'attributes': list, 'topic_domains': list, 'similar_tos': list}

def remove_tags(text):
  import re
  tags = {i:" " for i in re.findall("(<[^>\n]*>)",text.strip())}
  no_tag_text = reduce(lambda x, kv:x.replace(*kv), tags.iteritems(), text)
  return " ".join(no_tag_text.split())

def offset_to_synset(offset):
    return wn._synset_from_pos_and_offset(str(offset[-1:]), int(offset[:8]))

def semcor_to_synset(sensekey):
    return wn.lemma_from_key(sensekey).synset

def semcor_to_offset(sensekey):
    synset = wn.lemma_from_key(sensekey).synset
    offset = '%08d-%s' % (synset.offset, synset.pos)
    return offset



porter = PorterStemmer()
wnl = WordNetLemmatizer()

def lemmatize(ambiguous_word, pos=None, neverstem=False,
              lemmatizer=wnl, stemmer=porter):
    if pos:
        lemma = lemmatizer.lemmatize(ambiguous_word, pos=pos)
    else:
        lemma = lemmatizer.lemmatize(ambiguous_word)
    stem = stemmer.stem(ambiguous_word)
    # Ensure that ambiguous word is a lemma.
    if not wn.synsets(lemma):
        if neverstem:
            return ambiguous_word
        if not wn.synsets(stem):
            return ambiguous_word
        else:
            return stem
    else:
     return lemma


def penn2morphy(penntag, returnNone=False):
    morphy_tag = {'NN':wn.NOUN, 'JJ':wn.ADJ,
                  'VB':wn.VERB, 'RB':wn.ADV}
    try:
        return morphy_tag[penntag[:2]]
    except:
        return None if returnNone else ''

def lemmatize_sentence(sentence, neverstem=False, keepWordPOS=False,
                       tokenizer=word_tokenize, postagger=pos_tag,
                       lemmatizer=wnl, stemmer=porter):
    words, lemmas, poss = [], [], []
    for word, pos in postagger(tokenizer(sentence)):
        pos = penn2morphy(pos)
        lemmas.append(lemmatize(word.lower(), pos, neverstem,
                                lemmatizer, stemmer))
        poss.append(pos)
        words.append(word)
    if keepWordPOS:
        return words, lemmas, [None if i == '' else i for i in poss]
    return lemmas

def synset_properties(synset, parameter):
    return_type = SS_PARAMETERS_TYPE_MAP[parameter]
    func = 'synset.' + parameter
    return eval(func) if isinstance(eval(func), return_type) else eval(func)()

def has_synset(word):
    return wn.synsets(lemmatize(word, neverstem=True))
