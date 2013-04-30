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
   timer = Timer.Timer("Entire Program", 0, 0)
   if len(sys.argv) >= 3:
      print "Processing %s" % (sys.argv[2])
      process(sys.argv[2].lower(), False, "NB", "RF", 1000, 1000)
      timer.stop()
      return
   
   gc.enable()
   inputfile = open(sys.argv[1], 'rt')
   cats = {}
   try:
      reader = csv.DictReader(inputfile)
      for row in reader:
         cat = row["Category"].lower()
         if not cats.get(cat, False):
            cats[cat] = [0, 0, 0, 0.0]
         cats[cat][0] += 1
         if cats[cat][0] % 4 == 0:
            cats[cat][2] += 1
         else:
            cats[cat][1] += 1
      
   finally:
      inputfile.close()
   for cat in cats:
      cats[cat][3] = process(cat, False, "NB", "RF", 1000, 1000)
   
   total = [0, 0, 0, 0.0, 0.0]
   for cat in cats:
      print "\"%s\", %d, %d, %d, %f" % (cat, cats[cat][0], cats[cat][1], cats[cat][2], cats[cat][3])
      total[0] += cats[cat][0]
      total[1] += cats[cat][1]
      total[3] = (total[3] * total[2] + cats[cat][3] * cats[cat][2]) / (total[2] + cats[cat][2])
      total[4] = total[4] + (cats[cat][3] * cats[cat][2] - total[4]) / (total[2] + cats[cat][2])
      total[2] += cats[cat][2]
   print "\"%s\", %d, %d, %d, %f, %f" % ("total", total[0], total[1], total[2], total[3], total[4])
   timer.stop()
def process(categoryToProcess, regressionOnly = False, classification = "NB", regression = "RF", numFeaturesC = 1000, numFeaturesR = 1000):
   #categoryToProcess = "it jobs"
   timer0 = Timer.Timer("Processing " + categoryToProcess, 0, 0)
   inputfile = open(sys.argv[1], 'rt')
   trainSet = Collection.Collection("Training")
   testSet = Collection.Collection("Testing")
   timer = Timer.Timer("Processing csv file", 0, 0)
   try:
      reader = csv.DictReader(inputfile)
      count = 0
      for row in reader:
         count += 1
         cat = row["Category"].lower()
         if cat != categoryToProcess:
            continue
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
   
   if not regressionOnly:
      if classification == "SVM":
         timer1 = Timer.Timer("SVM Training", 0, 0)
         classifier = Classifer.SVM(categoryTrain)
         # TODO: Add option to send numfeatures
         classifier.train()
         timer1.stop()
         timer1 = Timer.Timer("SVM Classification", 0, 0)
         timer1.pause()
      elif classification == "NB":
         timer1 = Timer.Timer("NB Training", 0, 0)
         classifier = Classifier.NaiveBayesClassifier(categoryTrain)
         timer1.stop()
         timer1 = Timer.Timer("NB Classification", 0, 0)
         timer1.pause()
      
   count0 = 0
   countneg = 0
   countpos = 0
   meanneg = 0.0
   meanpos = 0.0
   meanSalaryError = 0.0
   regressors = {}
   
   timer2 = Timer.Timer("Regression training", 0, 0)
   if regressionOnly:
      if regression == "UW":
         regressor = Regressor.UniqueWeightsRegressor(categoryTrain, False)
      elif regression == "RF":
         regressor = Regressor.RandomForestRegressor(categoryTrain, False)
      regressor.train(numFeaturesR)
   timer2.pause()
   
   timer3 = Timer.Timer("Regression prediction", numD)
   timer3.pause()
   
   for docKey in categoryTest.getDocuments():
      count += 1.0
      document = categoryTest.getDocument(docKey)
      if not regressionOnly:
         # Classification
         timer1.unpause()
         classification = classifier.classify(document)
         predictedGroup = categoryTrain.getGroup(classification)
         actualGroup = categoryTrain.getGroup(categoryTrain.determineGroup(document))
         meanErrorGroup += (abs(classification - actualGroup.getKey()) - meanErrorGroup)/count
         timer1.pause()
         
      # Regression training
      if not regressionOnly:
         timer2.unpause()
         if not regressors.get(classification, False):
            if regression == "UW":
               #regressors[classification] = Regressor.UniqueWeightsRegressor(categoryTrain, False)
               regressors[classification] = Regressor.UniqueWeightsRegressor(categoryTrain.getGroup(classification))
               regressors[classification].train(numFeaturesR)
            elif regression == "RF":
               #regressors[classification] = Regressor.RandomForestRegressor(categoryTrain, False)
               regressors[classification] = Regressor.RandomForestRegressor(categoryTrain.getGroup(classification))
               #print "Regressor training for group %d" % (predictedGroup.getKey())
               regressors[classification].train(numFeaturesR)
         regressor = regressors[classification]
         timer2.pause()
      
      # Regression prediction
      timer3.unpause()
      timer3.tick()
      predictedSalary = regressor.predict(document)
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
      timer3.pause()
   timer3.stop()
   timer1.stop()
   timer2.stop()
   print "Avg error in salary prediction = %f" % (meanSalaryError)
   print "(Num, Avg) Positive errors = (%d, %f)" % (countpos, meanpos)
   print "(Num, Avg) Negative errors = (%d, %f)" % (countneg, meanneg)
   print "Avg error in group prediction = %f" % (meanErrorGroup)
   print "Count of < 3000.0 error = %d" % (countCorrect)
   
   timer0.stop()
   return meanSalaryError
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
