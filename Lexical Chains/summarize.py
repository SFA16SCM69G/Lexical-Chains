import sys
import re
import nltk
from nltk.corpus import wordnet as wn

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet') #guarantee wordnet from nltk is installed

lexical_chains = [] #empty list to hold all the chains
sentences = [] #empty list to hold all sentences
dictionary = {} #empty dictionary to hold the count of each word encountered

fileName = sys.argv[1] #define file path
File = open(fileName) #open file
lines = File.read() #read all lines

#boolean variable to justify a word is can be used or not
is_nv = lambda pos: True if (pos == 'NN' or pos == 'NNS' or pos == 'NNP' or pos == 'NNPS') else False
                             # or pos == 'VB' or pos == 'VBD' or pos == 'VBG' or pos == 'VBN' or pos == 'VBP' or pos == 'VBZ' and pos != 'MD') else False

#extract all nouns and verbs except auxiliary
nvs = [word for (word, pos) in nltk.pos_tag(nltk.word_tokenize(lines)) if is_nv(pos)]


#define a chain as a class
class Chain():
    def __init__(self,word,sense):
        self.word = word #word list of chain
        self.sense = sense #sense list of chain
        self.weight = 1 #weight is the total word count for a chain

#define a sentence as a class
class Sentence():
    def __init__(self,context,score): #score records the summarization weight of a sentence
        self.context = context #context of a sentence
        self.score = score #score records the summarization weight of a sentence

#Split text file into sentence properly
#This function from https://stackoverflow.com/questions/4576077/python-split-text-on-sentences
caps = "([A-Z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

sentence_list = split_into_sentences(lines)

for word in nvs:
    if word in dictionary:#word already chained
        for chain in lexical_chains:
            if word in chain.word:
                chain.weight = chain.weight + 1 #add the weight of chain by 1
                break
        dictionary[word] = dictionary[word] + 1 #add the word count by 1
        continue
    else:#word not be chained
        dictionary[word] = 1 #initialize the word count
        word_sense = wn.synsets(word) #get sense of word
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
                        chain.weight = chain.weight + 1 #add the weight of chain by 1
                        newChain = False
                        break
                    for synset in chain.sense: #word is antonym of token
                        if sense in synset.lemmas()[0].antonyms():
                            chain.word.append(word)
                            for syn in word_sense:
                                chain.sense.append(syn)
                            chain.weight = chain.weight + 1 #add the weight of chain by 1
                            newChain = False
                            break
                    for synset in chain.sense: #word is hypernym of token
                        if sense in synset.hypernyms():
                            chain.word.append(word)
                            for syn in word_sense:
                                chain.sense.append(syn)
                            chain.weight = chain.weight + 1 #add the weight of chain by 1
                            newChain = False
                            break
                    for synset in chain.sense: #word is hyponym of token
                        if sense in synset.hyponyms():
                            chain.word.append(word)
                            for syn in word_sense:
                                chain.sense.append(syn)
                            chain.weight = chain.weight + 1 #add the weight of chain by 1
                            newChain = False
                            break
        if newChain: #tokens in chain have no relationship with word
            chain = Chain([],[]) #initialize a new chain
            chain.word.append(word) #append word to the new chain
            for synset in word_sense:
                chain.sense.append(synset) #append the sense of word to the new chain
            lexical_chains.append(chain) #append the new chain to lexical chains

#Compute the score for each sentence based on the weight of each chain
for context in sentence_list:
    score = 0
    for word in nltk.word_tokenize(context):
        for chain in lexical_chains:
            if word in chain.word:
                score = score + chain.weight
                break
    sentence = Sentence(context,score)
    sentences.append(sentence)

sentences = sorted(sentences,key=lambda sentence: sentence.score,reverse=True)

ratio = float(sys.argv[2])
for i in range(int(len(sentences) * ratio)):
    print (sentences[i].context)
    print ('')
