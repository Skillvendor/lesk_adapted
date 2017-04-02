require 'bundler/setup'
require 'lingua/stemmer'
require 'bigdecimal'
require 'rwordnet'
require 'engtagger'


def simple_signature(ambiguous_word, pos=nil, lemma=true, stem=false, hyperhypo=true, stop=true)
  synsets_signatures = {}

  synsets = WordNet::Lemma.find_all(stemmed_ambigous_word).map { |lemma| lemma.synsets }
  synsets.flatten.each do |ss|
    if pos && pos != ss.post
  end
end

def adapted_lesk(ambigous_word, sentence)
  stemmer = Lingua::Stemmer.new(language: 'en')
  stemmed_ambigous_word = stemmer.stem(ambigous_word)
  
  lemma = WordNet::Lemma.find_all(stemmed_ambigous_word)
  synsets = lemmas.map { |lemma| lemma.synsets }
  
  if synsets.count == 0
    puts 'This word is not in WordNet'
    return
  end


end

def stem_text(string)
  stemmed_words = []
  stemmer = Lingua::Stemmer.new(language: 'en')
  string.split(' ').each do |word|
    stemmed_words << stemmer.stem(word)
  end

  stemmed_words.join(' ')
end