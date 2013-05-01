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
import argparse

# Just a comment
def main():
   gc.enable()
   timer = Timer.Timer("Entire Program", 0, 0)
   parser = argparse.ArgumentParser(prog = "PayMaster", description='Parser for PayMaster')
   parser.add_argument('--version', action='version', version='The PayMaster 1.0')
   parser.add_argument('--file', metavar = '<csv file>', type = argparse.FileType('r'), nargs = 1,
                      help = 'File to read in the training and test sets')
   parser.add_argument(
   parser.add_argument('-c', metavar='<classifier>', type = str, nargs = 1,
                      help='Classifier to be used, could be one of "NBC" or "SVM"')

   parser.add_argument('-r', metavar='<regressor>', type = str, nargs = 1,
                      help='Classifier to be used, could be one of "KNR", "RFR" or "SVR"')

   parser.add_argument('--features', metavar='<number of features to be used>', type=int, nargs = 1,
                      help='Number of features to be used')
   parser.add_argument('--category', metavar = '<category>', type = str, nargs = 1,
                      help = 'Category of jobs')
   args = parser.parse_args(sys.argv[1:])
   if args.c:
      isRegressionOnly = False
      classification = args.c[0]
   if args.r:
      regression = args.r[0]
   if args.features:
      numFeaturesC = args.features[0]
      numFeaturesR = args.features[0]
   if args.category:
      
   #isRegressionOnly = False
   #classification = "NBC"
   #regression = "RFR"
   #numFeaturesC = 1000
   #numFeaturesR = 1000
   
   if classification not in ["NBC", "SVC"] or regression not in ["KNR", "RFR", "SVR", "UWR"]:
      print "Invalid classifier or regressor"
      return
   if len(sys.argv) >= 3:
      print "Processing %s" % (sys.argv[2])
      process(sys.argv[2].lower(), isRegressionOnly, classification, regression, numFeaturesC, numFeaturesR)
      timer.stop()
      return
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
      cats[cat][3] = process(cat, isRegressionOnly, classification, regression, numFeaturesC, numFeaturesR)      
   
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
   
   
def process(categoryToProcess, regressionOnly = False, classification = "NBC",regression = "RFR", numFeaturesC = 1000, numFeaturesR = 1000):
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
   
   categoryTrain = trainSet.getCategory(1, False)
   categoryTest = testSet.getCategory(1, False)
   
   print "Category - %s" % (categoryTrain.getName())
   print "Training set"
   mean = categoryTrain.getMean()
   stdD = categoryTrain.getStdDeviation()
   numD = categoryTrain.getNumDocuments()
   print "\tNum Docs                = %d" % (numD)
   print "\tMean Salary             = %f" % (mean)
   print "\tStd Deviation of Salary = %f" % (stdD)
   print "Test set"
   numD = categoryTest.getNumDocuments()
   print "\tNum Docs                = %d" % (numD)
   
   timer.start("Creating groups and assigning documents", 0, 0)
   trainSet.createGroups()
   trainSet.assignGroups()
   timer.stop()
   
   timer.start("Processing documents, creating reverse index", 0, 0)
   print "Processing documents, creating the reverse index"
   trainSet.processDocuments()
   timer.stop()

   timer.start("Computing all weights", 0, 0)
   print "Computing all weights"
   trainSet.computeAllWeights()
   timer.stop()
   
   #timer = Timer.Timer("Computing all TFIDF values", 0, 0)
   #print "Computing all TFIDF values"
   #trainSet.computeAllTFIDF()
   #timer.stop()
   
   timer = Timer.Timer("Computing all MI and X2 values", 0, 0)
   print "Computing All MI and X2 values"
   trainSet.computeAllMI()
   timer.stop()
   
   #timer = Timer.Timer("Selecting important words", 0, 0)
   #trainSet.findImportantWords(2)
   #timer.stop()
   
      
   meanErrorGroup = 0.0
   count = 0.0
   countCorrect = 0.0
   
   if not regressionOnly:
      if classification == "SVC":
         timer1 = Timer.Timer("SVC Training", 0, 0)
         classifier = Classifier.SVM(categoryTrain)
         # TODO: Add option to send numfeatures
         classifier.train()
         timer1.stop()
         timer1 = Timer.Timer("SVC Classification", 0, 0)
         timer1.pause()
      elif classification == "NBC":
         timer1 = Timer.Timer("NBC Training", 0, 0)
         classifier = Classifier.NaiveBayesClassifier(categoryTrain)
         timer1.stop()
         timer1 = Timer.Timer("NBC Classification", 0, 0)
         timer1.pause()
      
   count0 = 0
   countneg = 0
   countpos = 0
   meanneg = 0.0
   meanpos = 0.0
   meanSalaryError = 0.0
   regressors = {}
   
   timer2 = Timer.Timer(regression + " Regression training", 0, 0)
   if regressionOnly:
      regressor = {  "KNR" : Regressor.KNeighborsRegressor(categoryTrain, False),
                     "RFR" : Regressor.RandomForestRegressor(categoryTrain, False),
                     "SVR" : Regressor.SVMRegressor(categoryTrain, False),
                     "UWR" : Regressor.UniqueWeightsRegressor(categoryTrain, False),
                  }[regression]      
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
            try:
               regressors[classification] = {
                         "KNR" : Regressor.KNeighborsRegressor(categoryTrain.getGroup(classification)),
                         "RFR" : Regressor.RandomForestRegressor(categoryTrain.getGroup(classification)),
                         "SVR" : Regressor.SVMRegressor(categoryTrain.getGroup(classification)),
                         "UWR" : Regressor.UniqueWeightsRegressor(categoryTrain.getGroup(classification)),
               }[regression]
               regressors[classification].train(numFeaturesR)
            except:
               regressors[classification] = Regressor.UniqueWeightsRegressor(categoryTrain.getGroup(classification))
               regressors[classification].train(numFeaturesR)
         timer2.pause()
         regressor = regressors[classification]
         
      
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
   if not regressionOnly:
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
