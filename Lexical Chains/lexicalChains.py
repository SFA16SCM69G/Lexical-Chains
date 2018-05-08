import sys
import nltk
from nltk.corpus import wordnet as wn

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet') #guarantee wordnet from nltk is installed

lexical_chains = [] #empty list to hold all the chains
dictionary = {} #empty dictionary to hold the count of each word encountered

fileName = sys.argv[1] #define file path
File = open(fileName) #open file
lines = File.read() #read all lines

#boolean variable to justify a word is noun or not
is_noun = lambda pos: True if (pos == 'NN' or pos == 'NNS' or pos == 'NNP' or pos == 'NNPS') else False
#extract all nouns
nouns = [word for (word, pos) in nltk.pos_tag(nltk.word_tokenize(lines)) if is_noun(pos)]

#define a chain as a class
class Chain():
    def __init__(self,word,sense):
        self.word = word #word list of chain
        self.sense = sense #sense list of chain
    def getWord(self):
        return self.word

    def getSense(self):
        return self.sense

for word in nouns:
    if word in dictionary:#word already chained
        dictionary[word] = dictionary[word] + 1 #add the word count by 1
        continue
    else:#word not be chained
        dictionary[word] = 1 #initialize the word count
        word_sense = wn.synsets(word,pos='n') #get sense of word
        if len(word_sense) == 0: #word has no defined sense
            chain = Chain([],[]) #initialize a new chain
            chain.word.append(word) #append word to the new chain
            lexical_chains.append(chain) #append the new chain to lexical chains
            continue
        
        newChain = True #initialize the new chain to true
        for chain in lexical_chains: #visit all element in lexical_chains
            if word not in chain.word: #avoid add same word to one chain
                for sense in word_sense:
                    if not newChain:
                        break
                    if sense in chain.sense: #word is synonymy of token
                        chain.word.append(word)
                        for syn in word_sense:
                            chain.sense.append(syn)
                        newChain = False
                        break
                    for synset in chain.sense: #word is antonym of token
                        if sense in synset.lemmas()[0].antonyms():
                            chain.word.append(word)
                            for syn in word_sense:
                                chain.sense.append(syn)
                            newChain = False
                            break
                    for synset in chain.sense: #word is hypernym of token
                        if sense in synset.hypernyms():
                            chain.word.append(word)
                            for syn in word_sense:
                                chain.sense.append(syn)
                            newChain = False
                            break
                    for synset in chain.sense: #word is hyponym of token
                        if sense in synset.hyponyms():
                            chain.word.append(word)
                            for syn in word_sense:
                                chain.sense.append(syn)
                            newChain = False
                            break
        if newChain: #tokens in chain have no relationship with word
            chain = Chain([],[]) #initialize a new chain
            chain.word.append(word) #append word to the new chain
            for synset in word_sense:
                chain.sense.append(synset) #append the sense of word to the new chain
            lexical_chains.append(chain) #append the new chain to lexical chains

#print the lexical chains
index=1
for chain in lexical_chains:
    print ("Chain "+str(index)+": "+", ".join(str(word + "(" + str(dictionary[word]) + ")") for word in chain.getWord()))
    index = index+1
