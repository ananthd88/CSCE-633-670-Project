#!/usr/bin/python

import csv
import Spell_Corrector
import sys
import re
import Timer

def add2Vocabulary1(word):
   if not vocabulary1.get(word, False):
      vocabulary1[word] = 0
   vocabulary1[word] += 1
   
def add2Vocabulary2(word):
   if not vocabulary2.get(word, False):
      vocabulary2[word] = 0
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
      if word in vocabulary2:
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
         if getCount1(word1) > 1:
            if word2 not in stopwords:
               if getCount1(word2) > 1:
                  return [word1, word2]
               else:
                  continue
            else:
               return [word1, False]
         else:
            continue
      else:
         if word2 not in stopwords:
            if getCount1(word2) > 1:
               return [False, word2]
            else:
               continue
         else:
            return [False, False]
   return False

stopwords = set(["", ".", "a", "an", "and", "are", "as", "at", "be", "for", "have", "if", "in", "is", "of", "on", "or", "our", "s", "the", "this", "to", "we", "will", "with", "work", "you", "your"])
collection = []
vocabulary1 = {}
vocabulary2 = {}
corrections = {}

def main():
   fin = open(sys.argv[1], 'rt')
   fieldnames = ["Id", "Title", "FullDescription", "Company", "Category", "SalaryNormalized"]
   reader = csv.DictReader(fin)
   count  = 0
   timer = Timer.Timer("Reading documents")
   for row in reader:
      count += 1
      if count % 10000 == 0:
         print "%dth document read" % (count)
      #if not row["Category"].lower() == "part time jobs":
      #   continue
      bag = filterString(row["Title"].lower()) + filterString(row["FullDescription"].lower())
      
      for word in bag:
         #if word in stopwords:
         #   continue
         add2Vocabulary1(word)
      #collection.append(newrow)
   fin.close()
   timer.stop()
   
   print "Num words in vocab 1 = %d" % (len(vocabulary1))
   print "Num words in vocab 2 = %d" % (len(vocabulary2))
   print "Num words corrected  = %d" % (len(corrections))
   
   raw_input("Abt to do spell correction, press any key")
   
   timer = Timer.Timer("Spell correction")
   spellchecker = Spell_Corrector.SpellCorrector()
   spellchecker.setDictionary(vocabulary1)
      
   for (word, count) in vocabulary1.items():
      if word in stopwords:
         continue
      if count == 1:
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
               add2Vocabulary2(correct_word)
               print "%s -> %s" % (word, correct_word)
               corrections[word] = correct_word
      else:
         add2Vocabulary2(word)
   print "Num words in vocab 1 = %d" % (len(vocabulary1))
   print "Num words in vocab 2 = %d" % (len(vocabulary2))
   print "Num words corrected  = %d" % (len(corrections))
   timer.stop()
   
   raw_input("Abt to write, press any key")
   
   timer = Timer.Timer("Writing back to file")
   fout = open(sys.argv[2], 'w')
   writer = csv.DictWriter(fout, fieldnames=fieldnames)
   headers = dict( (n,n) for n in fieldnames )
   writer.writerow(headers)
   count = 0
   
   fin = open(sys.argv[1], 'rt')
   reader = csv.DictReader(fin)
   for row in reader:
      count += 1
      if count % 10000 == 0:
         print "%dth document read" % (count)
      #if not row["Category"].lower() == "part time jobs":
      #   continue
      newrow = {}
      newrow["Id"] = int(row["Id"])
      newrow["Title"] = filterList(filterString(row["Title"].lower()))
      newrow["FullDescription"] = filterList(filterString(row["FullDescription"].lower()))
      newrow["Company"] = row["Company"].lower()
      newrow["Category"] = row["Category"].lower()
      newrow["SalaryNormalized"] = float(row["SalaryNormalized"])
      writer.writerow(row)
      
      if count % 10000 == 0:
         print "%d ads read" % (count)
      count += 1
   print "Num words in vocab 1 = %d" % (len(vocabulary1))
   print "Num words in vocab 2 = %d" % (len(vocabulary2))
   print "Num words corrected  = %d" % (len(corrections))
   print "Done"
   timer.stop()
   
   fout.close()
if __name__ == '__main__':
    main()
