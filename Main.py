#!/usr/bin/python

import Collection
import Document
import Timer
import Classifier
import Regressor
import csv
import sys
import math
import re
from sklearn import svm
import gc

# Just a comment
      
def main():
   timer0 = Timer.Timer("Entire program", 0, 0)
   gc.enable()
   inputfile = open(sys.argv[1], 'rt')
   trainSet = Collection.Collection("Training")
   testSet = Collection.Collection("Testing")
   timer = Timer.Timer("Processing csv file", 0, 0)
   try:
      reader = csv.DictReader(inputfile)
      count = 0
      for row in reader:
         count += 1
         #if count % 10000 == 0:
         #   print "%d-th document" % (count)         
         cat = row["Category"].lower()
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
   
   print "Training set"
   for categoryKey, category in trainSet.getCategories().items():
      name = category.getName()
      mean = category.getMean()
      stdD = category.getStdDeviation()
      numD = category.getNumDocuments()
      print "Stats for category: %s" % (name)
      print "\tNum Docs                = %d" % (numD)
      print "\tMean Salary             = %f" % (mean)
      print "\tStd Deviation of Salary = %f" % (stdD)
   print
   print "Test set"
   for categoryKey, category in testSet.getCategories().items():
      name = category.getName()
      numD = category.getNumDocuments()
      print "%s : %d ads" % (name, numD)
   
   timer.start("Creating groups and assigning documents", 0, 0)
   trainSet.createGroups()
   trainSet.assignGroups()
   timer.stop()
   
   timer.start("Processing documents, creating reverse index", 0, 0)
   trainSet.processDocuments()
   timer.stop()

   timer.start("Computing Weights", 0, 0)
   trainSet.computeAllWeights()
   timer.stop()
   
   #timer = Timer.Timer("Computing TFIDF", 0, 0)
   #rainSet.computeAllTFIDF()
   #timer.stop()
   
   timer = Timer.Timer("Computing MI", 0, 0)
   trainSet.computeAllMI()
   timer.stop()
   
   #timer = Timer.Timer("Selecting important words", 0, 0)
   #trainSet.findImportantWords(2)
   #timer.stop()
   
   categoryTrain = trainSet.getCategory(1, False)
   categoryTest = testSet.getCategory(1, False)
      
   
   meanErrorGroup = 0.0
   count = 0.0
   countCorrect = 0.0
   classification = "NB"
   regression = "RF"
   if classification == "SVM":
      timer.start("SVM Learning", 0, 0)
      classifier = Classifer.SVM(categoryTrain)
      # TODO: Add option to send numfeatures
      classifier.train()
      timer.stop()
      timer1 = Timer.Timer("SVM Classification", numD)
   elif classification == "NB":
      timer.start("NB Learning", 0, 0)
      classifier = Classifier.NaiveBayesClassifier(categoryTrain)
      timer.stop()
      #timer.start("NB Classification", 0, 0)
      timer1 = Timer.Timer("NB Classification", numD)      
   
   count0 = 0
   countneg = 0
   countpos = 0
   meanneg = 0.0
   meanpos = 0.0
   meanSalaryError = 0.0
   regressors = {}
   timer1.pause()
   timer2 = Timer.Timer("Regression training & prediction", 0, 0)
   timer2.pause()
   for docKey in categoryTest.getDocuments():
      timer1.unpause()
      timer1.tick()
      document = categoryTest.getDocument(docKey)
      #print "document %d" % (count)
      count += 1.0
      # Classification
      classification = classifier.classify(document)
      predictedGroup = categoryTrain.getGroup(classification)
      actualGroup = categoryTrain.getGroup(categoryTrain.determineGroup(document))
      meanErrorGroup += (abs(classification - actualGroup.getKey()) - meanErrorGroup)/count
      timer1.pause()
      
      # Regression training
      timer2.unpause()
      if not regressors.get(classification, False):
         if regression == "UW":
            regressors[classification] = Regressor.UniqueWeightsRegressor(categoryTrain)
            regressors[classification].train(1000)
         elif regression == "RF":
            regressors[classification] = Regressor.RandomForestRegressor(categoryTrain)
            #print "Regressor training for group %d" % (predictedGroup.getKey())
            regressors[classification].train(1000)
            
      predictedSalary = regressors[classification].predict(document)
      
      actualSalary = document.getSalary()
      meanSalaryError += (math.fabs(predictedSalary - actualSalary) - meanSalaryError) / count
      if predictedSalary > actualSalary:
         countpos += 1
         meanpos += (math.fabs(predictedSalary - actualSalary) - meanpos) / countpos
      elif predictedSalary < actualSalary:
         countneg += 1
         meanneg += (math.fabs(predictedSalary - actualSalary) - meanneg) / countneg
      if math.fabs(predictedSalary - actualSalary) < 3000.0:
         countCorrect += 1
      timer2.pause()
   timer1.stop()
   timer2.stop()
   print "Avg error in salary prediction = %f" % (meanSalaryError)
   print "(Num, Avg) Positive errors = (%d, %f)" % (countpos, meanpos)
   print "(Num, Avg) Negative errors = (%d, %f)" % (countneg, meanneg)
   print "Avg error in group prediction = %f" % (meanErrorGroup)
   print "Count of < 3000.0 error = %d" % (countCorrect)
   
   timer0.stop()
   exit()
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
   
if __name__ == '__main__':
    main()
