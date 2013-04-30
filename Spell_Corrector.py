import re
import collections


class SpellCorrector():

  def __init__(self):
	
	self.NWORDS = {}
	self.list_of_words = []
	self.alphabet = 'abcdefghijklmnopqrstuvwxyz'


  def edit_distance1(self,word):
     new_words = []
     for i in range(len(word)):
	new_inserts   = [word[:i] + x + word[i:] for x in self.alphabet]
 	new_deletes   = word[:i] + word[i+1:]
	new_transpose = word[:i] + word[i+1:i+2] + word[i:i+1] + word[i+2:]
	new_replaces  = [word[:i] + x + word[i+1:] for x in self.alphabet]
	new_words.extend(new_inserts + new_replaces) 
     	new_words.append(new_deletes)
	new_words.append(new_transpose)
     return set(new_words)

 
  def known_edits2(self, word):
     return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if e2 in self.list_of_words)


  def known(self, words): 
     return set(w for w in words if w in self.list_of_words)


  def correct(self, word, current_dict = {}):
    
     if len(current_dict) != 0:
	self.NWORDS = current_dict
	self.list_of_words = [x for x in self.NWORDS if self.NWORDS[x] > 1]

     candidates = self.known(self.edit_distance1(word)) or [word]
     if len(candidates) != 1:
    	return max(candidates, key= lambda known_word: self.NWORDS[known_word])
     else:
	return(candidates.pop())


  def setDictionary(self,current_dict = {}):
    
     if len(current_dict.keys()) != 0:
	self.NWORDS = current_dict
	self.list_of_words = [x for x in self.NWORDS if self.NWORDS[x] > 1]
	
