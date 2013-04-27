#!/usr/bin/python

import Collection
import Document
import Timer
import Classifier
import csv
import sys
import math
import re
from sklearn import svm

# Just a comment
      
def main():
   timer0 = Timer.Timer("Entire program")
   timer = Timer.Timer("Processing csv file")
   inputfile = open(sys.argv[1], 'rt')
   trainSet = Collection.Collection("Training")
   testSet = Collection.Collection("Testing")
   try:
      reader = csv.DictReader(inputfile)
      count = 0
      for row in reader:
         #if row["Category"].lower() != "engineering jobs":
         if row["Category"].lower() != "it jobs":
            continue
         count += 1
         if count % 10000 == 0:
            print "%d-th document" % (count)
         # TODO: Remove restriction (read only every 100th document)
         #if count % 100 == 0:
         #   document = trainSet.addDocument(row)
         if count % 4 == 0:
            document = testSet.addDocument(row)            
         else:
            document = trainSet.addDocument(row)
   finally:
      inputfile.close()
      timer.stop()
   
   categoryTrain = trainSet.getCategory(1, False)
   categoryTest = testSet.getCategory(1, False)
   print "No. of docs in training set = %d" % (categoryTrain.getNumDocuments())
   print "Mean salary = %f" % (categoryTrain.getMean())
   print "Std deviation of salary = %f" % (categoryTrain.getStdDeviation())
   
   print "No. of docs in test set = %d" % (categoryTest.getNumDocuments())
   print "Mean salary = %f" % (categoryTest.getMean())
   print "Std deviation of salary = %f" % (categoryTest.getStdDeviation())
   
   timer = Timer.Timer("Creating groups and assigning documents")
   #categoryTrain.createGroups(10)
   trainSet.createGroups()
   for key in categoryTrain.getDocuments():
      document = categoryTrain.getDocument(key)
      categoryTrain.assignGroup(document)
   timer.stop()
   
   timer = Timer.Timer("Processing documents, creating reverse index")
   categoryTrain.processDocuments()
   timer.stop()
   
   timer = Timer.Timer("Computing Weights")
   categoryTrain.computeAllWeights()
   timer.stop()
   
   #timer = Timer.Timer("Computing TFIDF")
   #categoryTrain.computeAllTFIDF()
   #timer.stop()
   
   #timer = Timer.Timer("Computing MI")
   #categoryTrain.computeAllMI()
   #timer.stop()
   
   #timer = Timer.Timer("Selecting important words")
   #importantWords = categoryTrain.index.findImportantWords(2470, 13930)
   #timer.stop()
   
   timer = Timer.Timer("NB Predictions")
   nb = Classifier.NaiveBayesClassifier(categoryTrain)
   predictions = []
   truths = []
   meanError = 0.0
   meanErrorGroup = 0.0
   count = 0.0
   countCorrect = 0
   XY = categoryTrain.getXY(None)
   X = XY["X"]
   Y = XY["Y"]
   lin_clf = svm.LinearSVC()
   raw_input("Abt to train. press any key...")
   lin_clf.fit(X, Y)
   print "Trained"
   exit()
   for docKey in categoryTest.getDocuments():
      count += 1.0
      document = categoryTest.getDocument(docKey)
      #classification = categoryTrain.determineGroup(document)
      
      classification = nb.predict(document)
      actualGroup = categoryTrain.determineGroup(document)
      meanErrorGroup = meanErrorGroup + (abs(classification - actualGroup) - meanErrorGroup)/count
      predictedSalary = categoryTrain.getGroup(classification).getMean()
      prediction = 0.0
      for word in document.getBagOfWords("title"):
         prediction += categoryTrain.getWeightOf(word, "title")# * categoryTrain.index.getTFIDFWeightOf(word, document, "title")
      for word in document.getBagOfWords("description"):
         prediction += categoryTrain.getWeightOf(word, "description")# * categoryTrain.index.getTFIDFWeightOf(word, document, "description")
      predictedSalary *= (1 + prediction/100.0)
      actualSalary = document.getSalary()
      meanError = meanError + (math.fabs(predictedSalary - actualSalary) - meanError) / count
      if math.fabs(predictedSalary - actualSalary) < 3000.0:
         countCorrect += 1
      #truth = document.getGroup().getKey()
      #print "%d (%d, %d)" % (document.getKey(), document.getGroup().getKey(), prediction)
      #predictions.append(prediction)
      #truths.append(truth)
   #metrics = nb.getMetrics(predictions, truths)
   #print "Precision  = %f" % (metrics["precision"])
   #print "Recall     = %f" % (metrics["recall"])
   #print "MAF1       = %f" % (metrics["maf1"])
   #print "RSS        = %d" % (metrics["rss"])
   #print "Avg error  = %f" % (metrics["meanerr"])
   print "Avg error in salary prediction = %f" % (meanError)
   print "Avg error in group prediction = %f" % (meanErrorGroup)
   print "Count of < 3000.0 error = %d" % (countCorrect)
   timer.stop()
   #timer = Timer.Timer("Computing X, Y")
   #dictionary = category.getXY(importantWords)
   #timer.stop()
   
   #timer = Timer.Timer("Learning X, Y")
   #clf = category.mNBlearnXY(dictionary["X"], dictionary["Y"])
   #timer.stop()
   
   #raw_input("Press any key to go to the word prompt")
   print "Weights prompt"
   do = False
   while do:
      word = raw_input("Enter a word\n> ").lower()
      if word != "":
         words = re.split('_', word)
         if not categoryTrain.index.inVocabulary(word):
            print "%s was not found in the vocabulary" % (word)
            continue
         field = {"t": "title", "d": "description"}[words[0]]
         print "Word weight = %f" % (categoryTrain.getWeightOf(words[1], field))
         print "Unique word weight = %f" % (categoryTrain.getUniqueWeightOf(words[1], field))         
      else:
         do = False
   
   print "Document prompt (for Training set)"
   do = False
   while do:
      key = raw_input("Enter a doc id\n> ")
      if key != "":
         key = int(key)
         document = categoryTrain.getDocument(key)
         if document:
            print document.toString()
         else:
            print "Document not found in training set"
      else:
         do = False
   timer0.stop()
if __name__ == '__main__':
    main()
