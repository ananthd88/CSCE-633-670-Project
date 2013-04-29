#!/usr/bin/python

import csv
import Spell_Corrector
import sys
import re
import Timer
import math

def add2Vocabulary1(word):
   if not vocabulary1.get(word, False):
      vocabulary1[word] = 0
   vocabulary1[word] += 1
   
def add2Vocabulary2(word):
   if not vocabulary2.get(word, False):
      vocabulary2[word] = vocabulary1[word] - 1
   vocabulary2[word] += 1
   
def filterString(string):
   chunks = re.split('\s+', string)
   bag = []
   patterns = re.compile(r'www\.|\.com|http|:|\.uk|\.net|\.org|\.edu')
   # Remove chunks that are URLs
   for chunk in chunks:
      if patterns.search(chunk):
         continue
      words = re.split('[^a-zA-Z\+\-]+', chunk)
      for word in words:
         bag.append(word)
   return bag

def filterList(words):
   string = []
   for word in words:
      if word in stopwords:
         continue
      elif word in vocabulary2:
         string.append(word)
      elif word in corrections:
         string.append(corrections[word])
   return " ".join(string)
   
def getCount1(word):
   if word in vocabulary1:
      return vocabulary1[word]
   return 0
   
def wordSplitter(word):
   length = len(word)
   result = []
   for i in range(1, length):
      word1    = word[:i]
      word2    = word[i:]
      if word1 not in stopwords:
         if getCount1(word1) >= minCount:
            if word2 not in stopwords:
               if getCount1(word2) >= minCount:
                  return [word1, word2]
               else:
                  continue
            else:
               return [word1, False]
         else:
            continue
      else:
         if word2 not in stopwords:
            if getCount1(word2) >= minCount:
               return [False, word2]
            else:
               continue
         else:
            return [False, False]
   return False

stopwords = set(["", ".", "a", "an", "and", "are", "as", "at", "be", "d", "e", "for", "have", "hi", "i", "if", "in", "is", "m", "of", "on", "or", "our", "p", "s", "t", "the", "this", "to", "we", "will", "with", "work", "you", "your"])
collection = []
vocabulary1 = {}
vocabulary2 = {}
corrections = {}
minCount = 3
toolbarWidth = 100

def main():
   fin = open(sys.argv[1], 'rt')
   fieldnames = ["Id", "Title", "FullDescription", "LocationNormalized", "LocationRaw", "Company", "Category", "SalaryNormalized"]
   reader = csv.DictReader(fin)
   timer = Timer.Timer("Reading documents", 0, 0)
   count = 0
   for row in reader:
      #if row["Category"].lower() != "it jobs":
      #   continue
      bag = filterString(row["Title"].lower()) + filterString(row["FullDescription"].lower())      
      for word in bag:
         add2Vocabulary1(word)
      count += 1
   fin.close()
   timer.stop()
   numAds = count
   
   numWords = len(vocabulary1)
   timer.start("Spell correction", numWords)
   spellchecker = Spell_Corrector.SpellCorrector()
   spellchecker.setDictionary(vocabulary1)
   for (word, count) in vocabulary1.items():
      timer.tick()
      if word in stopwords:
         continue
      if count < minCount:
         result = wordSplitter(word)
         if result:
            word1, word2 = result
            if word1:   
               add2Vocabulary2(word1)
            if word2:
               add2Vocabulary2(word2)
         else:
            correct_word = spellchecker.correct(word)            
            if word != correct_word:
               if correct_word not in stopwords:
                  add2Vocabulary2(correct_word)
               #print "%s -> %s" % (word, correct_word)
               corrections[word] = correct_word
            else:
               if count == minCount - 1:
                  add2Vocabulary2(word)
      else:
         add2Vocabulary2(word)
   timer.stop()
   
   #for key in sorted(vocabulary2, key = lambda word: vocabulary2[word], reverse=True):
   #   print "%20s - %5d" % (key, vocabulary2[key])

   
   
   timer.start("Writing back to file", 0, 0)
   fout = open(sys.argv[2], 'w')
   writer = csv.DictWriter(fout, fieldnames=fieldnames)
   headers = dict( (n,n) for n in fieldnames )
   writer.writerow(headers)
   count = 0
   
   fin = open(sys.argv[1], 'rt')
   reader = csv.DictReader(fin)
   for row in reader:
      #timer.tick()
      #if row["Category"].lower() != "it jobs":
      #   continue
      
      count += 1
      newrow = {}
      newrow["Id"] = int(row["Id"])
      newrow["Title"] = filterList(filterString(row["Title"].lower()))
      newrow["FullDescription"] = filterList(filterString(row["FullDescription"].lower()))
      newrow["Company"] = row["Company"].lower()
      newrow["Category"] = row["Category"].lower()
      newrow["SalaryNormalized"] = float(row["SalaryNormalized"])
      newrow["LocationNormalized"] = row["LocationNormalized"]
      newrow["LocationRaw"] = row["LocationRaw"]
      
      writer.writerow(newrow)
      
      if count % 10000 == 0:
         print "%d ads written" % (count)
      count += 1
   timer.stop()
   print "Num words in vocab 1 = %d" % (len(vocabulary1))
   print "Num words in vocab 2 = %d" % (len(vocabulary2))
   print "Num words corrected  = %d" % (len(corrections))   
   print "Done"
   
   fout.close()
if __name__ == '__main__':
    main()
