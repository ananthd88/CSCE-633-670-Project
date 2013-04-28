import re
import collections


class SpellCorrector():

  def __init__(self):
	
	self.NWORDS = {}
	self.list_of_words = []
	self.alphabet = 'abcdefghijklmnopqrstuvwxyz'


  def edits1(self, word):
     splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
     deletes    = [a + b[1:] for a, b in splits if b]
     transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
     replaces   = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
     inserts    = [a + c + b     for a, b in splits for c in self.alphabet]
     return set(deletes + transposes + replaces + inserts)


  def known_edits2(self, word):
     return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if e2 in self.list_of_words)


  def known(self, words): 
     return set(w for w in words if w in self.list_of_words)


  def correct(self, word, current_dict = {}):
    
     if len(current_dict) != 0:
	self.NWORDS = current_dict
	self.list_of_words = [x for x in self.NWORDS if self.NWORDS[x] > 1]

     candidates = self.known(self.edits1(word)) or [word]# or self.known_edits2(word)
     if len(candidates) != 1:	
    	return max(candidates, key= lambda known_word: self.NWORDS[known_word])
     else:
	return(candidates.pop())    


  def setDictionary(self,current_dict = {}):
    
     if len(current_dict.keys()) != 0:
	self.NWORDS = current_dict
	self.list_of_words = [x for x in self.NWORDS if self.NWORDS[x] > 1]
	



