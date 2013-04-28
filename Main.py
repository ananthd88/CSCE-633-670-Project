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
from sklearn.feature_extraction.text import CountVectorizer

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
         cat = row["Category"].lower()
         count += 1
         if count % 10000 == 0:
            print "%d-th document" % (count)
         #if row["Category"].lower() != "engineering jobs":
         if cat != "it jobs":
            continue
         
         # TODO: Remove restriction (read only every 100th document)
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
   trainSet.createGroups()
   trainSet.assignGroups()
   timer.stop()
   
   timer = Timer.Timer("Processing documents, creating reverse index")
   trainSet.processDocuments()
   timer.stop()
   
   #timer = Timer.Timer("Computing Weights")
   #trainSet.computeAllWeights()
   #timer.stop()
   
   #timer = Timer.Timer("Computing TFIDF")
   #rainSet.computeAllTFIDF()
   #timer.stop()
   
   #timer = Timer.Timer("Computing MI")
   #trainSet.computeAllMI()
   #timer.stop()
   
   #timer = Timer.Timer("Selecting important words")
   #trainSet.findImportantWords(2)
   #timer.stop()
   
   timer = Timer.Timer("SVM Predictions")
   #nb = Classifier.NaiveBayesClassifier(categoryTrain)
   
   predictions = []
   truths = []
   meanError = 0.0
   meanErrorGroup = 0.0
   count = 0.0
   countCorrect = 0
   #XY = categoryTrain.getXY(None)
   #X = XY["X"]
   #Y = XY["Y"]
   lin_clf = svm.LinearSVC()
   vectorizer = CountVectorizer(vocabulary = categoryTrain.getVocabulary().keys(), min_df = 1)
   strings = []
   Y = []
   for docKey in categoryTrain.getDocuments():
      document = categoryTrain.getDocument(docKey)
      strings.append(" ".join(document.getBagOfWords2("all")))
      Y.append(document.getGroup().getKey())
   X = vectorizer.fit_transform(strings)
   lin_clf.fit(X, Y)
   
   for docKey in categoryTest.getDocuments():
      document = categoryTest.getDocument(docKey)
      strings.append(" ".join(document.getBagOfWords2("all")))
   Z = vectorizer.fit_transform(strings)
   array = lin_clf.predict(Z)
   count0 = 0
   for docKey in categoryTest.getDocuments():
      count += 1.0
      document = categoryTest.getDocument(docKey)
      #classification = nb.predict(document)
      classification = array[count0]
      count0 += 1
      actualGroup = categoryTrain.determineGroup(document)
      meanErrorGroup = meanErrorGroup + (abs(classification - actualGroup) - meanErrorGroup)/count
      predictedSalary = categoryTrain.getGroup(classification).getMean()
      #prediction = 0.0
      #for word in document.getBagOfWords("title"):
      #   prediction += categoryTrain.getWeightOf(word, "title")# * categoryTrain.index.getTFIDFWeightOf(word, document, "title")
      #for word in document.getBagOfWords("description"):
      #   prediction += categoryTrain.getWeightOf(word, "description")# * categoryTrain.index.getTFIDFWeightOf(word, document, "description")
      #predictedSalary *= (1 + prediction/100.0)
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
