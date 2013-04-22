#!/usr/bin/python

import Collection
import Document
import csv
import sys
import math
import re

def main():
   inputfile = open(sys.argv[1], 'rt')
   trainSet = Collection.Collection()
   try:
      reader = csv.DictReader(inputfile)
      count = 0
      print "\n\nProcessing the csv file"
      for row in reader:
         if row["Category"].lower() != "it jobs":
            continue
         document = trainSet.addDocument(row)
         count += 1
         if count % 10000 == 0:
            print "%d-th document" % (count)
      
   finally:
      inputfile.close()
   category = trainSet.getCategory(1, False)
   print "No. of docs in training set = %d" % (category.getNumDocuments())
   print "Mean salary = %f" % (category.getMean())
   print "Std deviation of salary = %f" % (category.getStdDeviation())
   category.processDocuments()
   print "Done"
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
            
if __name__ == '__main__':
    main()
