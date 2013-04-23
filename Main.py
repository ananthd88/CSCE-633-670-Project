#!/usr/bin/python

import Collection
import Document
import Timer
import csv
import sys
import math
import re

      
def main():
   timer0 = Timer.Timer("Entire program")
   timer = Timer.Timer("Processing csv file")
   inputfile = open(sys.argv[1], 'rt')
   trainSet = Collection.Collection()
   try:
      reader = csv.DictReader(inputfile)
      count = 0
      for row in reader:
         if row["Category"].lower() != "it jobs":
            continue
         document = trainSet.addDocument(row)
         count += 1
         if count % 10000 == 0:
            print "%d-th document" % (count)
      
   finally:
      inputfile.close()
      timer.stop()
   category = trainSet.getCategory(1, False)
   print "No. of docs in training set = %d" % (category.getNumDocuments())
   print "Mean salary = %f" % (category.getMean())
   print "Std deviation of salary = %f" % (category.getStdDeviation())
   
   timer = Timer.Timer("Creating groups and assigning documents")
   category.createGroups(5)
   for key in category.getDocuments():
      document = category.getDocument(key)
      category.assignGroup(document)
   timer.stop()
   
   timer = Timer.Timer("Processing documents, creating reverse index")
   category.processDocuments()
   timer.stop()
   
   timer = Timer.Timer("Computing Weights")
   category.computeAllWeights()
   timer.stop()
   
   timer = Timer.Timer("Computing TFIDF")
   category.computeAllTFIDF()
   timer.stop()
   
   timer = Timer.Timer("Selecting important words")
   importantWords = category.index.findImportantWords(2470, 13930)
   timer.stop()
   
   #timer = Timer.Timer("Computing X, Y")
   #dictionary = category.getXY(importantWords)
   #timer.stop()
   
   #timer = Timer.Timer("Learning X, Y")
   #clf = category.mNBlearnXY(dictionary["X"], dictionary["Y"])
   #timer.stop()
   
   raw_input("Press any key to go to the word prompt")
   print "Weights prompt"
   do = True
   while do:
      word = raw_input("Enter a word\n> ").lower()
      if word != "":
         words = re.split('_', word)
         if not category.index.inVocabulary(word):
            print "%s was not found in the vocabulary" % (word)
            continue
         field = {"t": "title", "d": "description"}[words[0]]
         print "Word weight = %f" % (category.getWeightOf(words[1], field))
         print "Unique word weight = %f" % (category.getUniqueWeightOf(words[1], field))         
      else:
         do = False
   
   print "Document prompt"
   do = True
   while do:
      key = raw_input("Enter a doc id\n> ")
      if key != "":
         key = int(key)
         document = category.getDocument(key)
         if document:
            print document.toString()
         else:
            print "Document not found"
      else:
         do = False
   timer0.stop()
if __name__ == '__main__':
    main()
