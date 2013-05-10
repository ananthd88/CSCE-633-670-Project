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
import warnings

class Main:
   
   def parseCommandLine(self):
      parser = argparse.ArgumentParser(prog = "PayMaster", description='Parser for PayMaster')
      parser.add_argument('--crossvalidate', action='store_true', help = 'Cross validate with all models')
      parser.add_argument('--version', action='version', version='The PayMaster 1.0')
      parser.add_argument('--file', metavar = '<csv file>', type = str, nargs = 1, required = True,
                         help = 'File to read in the training and test sets')
      parser.add_argument('-c', metavar='<classifier>', type = str, nargs = 1, choices = ["NBC", "SVC"],
                         help = 'Classifier to be used, could be one of "NBC" or "SVM"')
      parser.add_argument('-r', metavar='<regressor>', type = str, nargs = 1, choices = ["KNR", "RFR", "SVR"],
                         help = 'Regressor to be used, could be one of "KNR", "RFR" or "SVR"')
      parser.add_argument('-f', metavar='<number of features to be used>', type=int, nargs = 1,
                         help='Number of features to be used')
      parser.add_argument('--category', metavar = '<category>', type = str, nargs = 1,
                         help = 'Category of jobs')
      args = parser.parse_args(sys.argv[1:])
      if args.c:
         self.isRegressionOnly = False
         self.classification   = args.c[0]
      else:
         self.isRegressionOnly = True
         self.classification   = False
      if args.r:
         self.regression       = args.r[0]
      else:
         self.regression       = "KNR"
      if args.f:
         self.numFeaturesC     = args.f[0]
         self.numFeaturesR     = args.f[0]         
      else:
         self.numFeaturesC     = 1000
         self.numFeaturesR     = 1000
      if args.crossvalidate:
         self.crossValidate    = True
         if not args.category:
            print "Please provide a category"
            parser.print_usage()
            return False
      else:
         self.crossValidate    = False
      if args.category:
         self.category         = args.category[0].lower()
      else:
         self.category         = False
      if args.file:
         self.file             = args.file[0]
      return True

   def constructModels(self):
      timer = Timer.Timer("Constructing Models", 0, 0)
      self.classifier = None
      self.regressor  = None
      self.regressors = None
      if not self.isRegressionOnly:
         if self.classification == "SVC":
            timer1 = Timer.Timer(self.classification + " Training", 0, 0)
            self.classifier = Classifier.SVM(self.trainingSet)
            # TODO: Add option to send numfeatures
            self.classifier.train()
            timer1.stop()         
         elif self.classification == "NBC":
            timer1 = Timer.Timer(self.classification + " Training", 0, 0)
            self.classifier = Classifier.NaiveBayesClassifier(self.trainingSet)
            timer1.stop()
         self.regressors = {}
         timer1 = Timer.Timer(self.regression + " Training", 0, 0)
         for classification in range(self.trainingSet.getNumGroups()):
            try:
               self.regressors[classification] = {
                         "KNR" : Regressor.KNeighborsRegressor(self.trainingSet.getGroup(classification)),
                         "RFR" : Regressor.RandomForestRegressor(self.trainingSet.getGroup(classification)),
                         "SVR" : Regressor.SVMRegressor(self.trainingSet.getGroup(classification)),
                         "UWR" : Regressor.UniqueWeightsRegressor(self.trainingSet.getGroup(classification)),
               }[self.regression]
               self.regressors[classification].train(self.numFeaturesR)
            except:
               self.regressors[classification] = Regressor.UniqueWeightsRegressor(self.trainingSet.getGroup(classification))
               self.regressors[classification].train(self.numFeaturesR)
         timer1.stop()
      else:
         timer1 = Timer.Timer(self.regression + " Training", 0, 0)
         self.regressor = {
                        "KNR" : Regressor.KNeighborsRegressor(self.trainingSet, False),
                        "RFR" : Regressor.RandomForestRegressor(self.trainingSet, False),
                        "SVR" : Regressor.SVMRegressor(self.trainingSet, False),
                        "UWR" : Regressor.UniqueWeightsRegressor(self.trainingSet, False),
                     }[self.regression]
         self.regressor.train(self.numFeaturesR)
         timer1.stop()
      timer.stop()

   def crossValidateModels(self):
      timer = Timer.Timer("Cross Validation", 0, 0)
      self.constructDatasets()
      classifiers = ["", "NBC", "SVC"]
      regressors  = ["KNR", "RFR", "SVR"]
      performance = {}
      print
      for classifier in classifiers:
         if classifier == "":
            self.isRegressionOnly = True               
         else:
            self.isRegressionOnly = False
         self.classification = classifier
         for regressor in regressors:
            self.regression = regressor
            self.constructModels()
            stats = self.test()
            if self.isRegressionOnly:
               performance[regressor] = stats
            else:
               performance[classifier+regressor] = stats
      
      print "Mean Salary             = %8.2f" % (stats["meanSalary"])
      print "Std Deviation of Salary = %8.2f" % (stats["stdDeviation"])
      print " Method -      MAE, Numb+, MeanErr+, Numb-, MeanErr-, Numb3000"
      for key in sorted(performance, key = lambda combo: performance[combo]["MAE"], reverse=False):
         stats = performance[key]
         print "%7s - %8.2f, %5d, %8.2f, %5d, %8.2f, %8d" % (key, stats["MAE"], stats["countpos"], stats["meanpos"], stats["countneg"], stats["meanneg"], stats["count3000"])
      timer.stop()
      return

   def constructDatasets(self):
      timer0 = Timer.Timer("Constructing datasets", 0, 0)
      
      trainSet = Collection.Collection("Training")
      testSet = Collection.Collection("Testing")
      try:
         inputfile = open(self.file, 'rt')
         reader = csv.DictReader(inputfile)
         count = 0
         for row in reader:
            count += 1
            cat = row["Category"].lower()
            if cat != self.category:
               continue
            if count % 4 == 0:
               document = testSet.addDocument(row)
            else:
               document = trainSet.addDocument(row)
      finally:
         inputfile.close()
      self.trainingSet = trainSet.getCategory(1, False)
      self.testSet     =  testSet.getCategory(1, False)
      print "Category - %s" % (self.trainingSet.getName())
      print "Training set"
      mean = self.trainingSet.getMean()
      stdD = self.trainingSet.getStdDeviation()
      numD = self.trainingSet.getNumDocuments()
      print "\tNum Docs                = %d" % (numD)
      print "\tMean Salary             = %f" % (mean)
      print "\tStd Deviation of Salary = %f" % (stdD)
      print "Test set"
      numD = self.testSet.getNumDocuments()
      print "\tNum Docs                = %d" % (numD)
      
      timer = Timer.Timer("Creating groups and assigning documents", 0, 0)
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
      timer0.stop()

   def test(self):
      if self.isRegressionOnly:
         print "Testing with %s regressor" % (self.regression)
      else:
         print "Testing with %s classifier & %s regressor" % (self.classification, self.regression)
      timer = Timer.Timer("Testing Model", self.testSet.getNumDocuments())
      meanErrorGroup = 0.0
      count          = 0.0
      count3000      = 0.0
      count0 = 0
      countneg = 0
      countpos = 0
      meanneg = 0.0
      meanpos = 0.0
      meanSalaryError = 0.0
      for docKey in self.testSet.getDocuments():
         timer.tick()
         count += 1.0
         document = self.testSet.getDocument(docKey)
         if not self.isRegressionOnly:
            # Classification
            classification  = self.classifier.classify(document)
            predictedGroup  = self.trainingSet.getGroup(classification)
            actualGroup     = self.trainingSet.getGroup(self.trainingSet.determineGroup(document))
            meanErrorGroup += (abs(classification - actualGroup.getKey()) - meanErrorGroup)/count
            self.regressor  = self.regressors[classification]
         # Regression
         with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            predictedSalary = self.regressor.predict(document)
         actualSalary = document.getSalary()
         meanSalaryError += (math.fabs(predictedSalary - actualSalary) - meanSalaryError) / count
         if predictedSalary > actualSalary:
            countpos += 1
            meanpos += (math.fabs(predictedSalary - actualSalary) - meanpos) / countpos
         elif predictedSalary < actualSalary:
            countneg += 1
            meanneg += (math.fabs(predictedSalary - actualSalary) - meanneg) / countneg
         if math.fabs(predictedSalary - actualSalary) < 3000.0:
            count3000 += 1
      timer.stop()
      print "Mean absolute error in salary prediction = %f" % (meanSalaryError)
      print "Positive errors (Num, Avg)               = (%4d, %8.2f)" % (countpos, meanpos)
      print "Negative errors (Num, Avg)               = (%4d, %8.2f)" % (countneg, meanneg)
      print "Mean absolute error in group prediction  = %f" % (meanErrorGroup)
      print "Count of predictions with error < 3000.0 = %d (%f" % (count3000, count3000*100/count), "%)"
      print
      stats = {}
      stats["MAE"] = meanSalaryError
      stats["countpos"] = countpos
      stats["countneg"] = countneg
      stats["meanpos"] = meanpos
      stats["meanneg"] = meanneg
      stats["count3000"] = count3000
      stats["meanSalary"] = self.trainingSet.getMean()
      stats["stdDeviation"] = self.trainingSet.getStdDeviation()
      return stats
      
      
def main():
   gc.enable()
   timer = Timer.Timer("Entire Program", 0, 0)
   handle = Main()
   
   if not handle.parseCommandLine():
      timer.stop()
      return
   if handle.crossValidate:
      handle.crossValidateModels()
   elif handle.category:
      handle.constructDatasets()
      handle.constructModels()
      handle.test()
   else:
      inputfile = open(handle.file, 'rt')
      cats = {}
      total = [0, 0, 0, 0.0, 0, 0.0, 0, 0.0, 0, 0.0, 0.0]
      try:
         reader = csv.DictReader(inputfile)
         count = 0
         mean  = 0.0
         var   = 0.0
         for row in reader:
            cat = row["Category"].lower()
            count += 1
            oldmean = mean
            mean  += (float(row["SalaryNormalized"]) - mean) / count
            var   += (float(row["SalaryNormalized"]) - oldmean) * (float(row["SalaryNormalized"]) - mean)
            if not cats.get(cat, False):
               cats[cat] = [0, 0, 0, 0.0, 0, 0.0, 0, 0.0, 0, 0.0, 0.0]
            # Total no. of job ads for this category
            cats[cat][0] += 1
            if cats[cat][0] % 4 == 0:
               # No. of samples in test set
               cats[cat][2] += 1
            else:
               # No. of samples in training set
               cats[cat][1] += 1
         
      finally:
         inputfile.close()
      for cat in cats:
         # Mean Absolute Error
         handle.category = cat
         handle.constructDatasets()
         handle.constructModels()
         stats = handle.test()
         cats[cat][3] = stats["MAE"]
         cats[cat][4] = stats["countpos"]
         cats[cat][5] = stats["meanpos"]
         cats[cat][6] = stats["countneg"]
         cats[cat][7] = stats["meanneg"]
         cats[cat][8] = stats["count3000"]
         cats[cat][9] = stats["meanSalary"]
         cats[cat][10]= stats["stdDeviation"]
         
      
      print "Category, Mean Salary, SD Salary, Total ads, Train size, Test size, MAE, No. +ve errors, Mean +ve error, No. -ve error, Mean -ve error, Count < 3000.0 errors"
      for cat in cats:
         print "\"%33s\", %8.2f, %8.2f, %5d, %5d, %5d, %8.2f, %5d, %8.2f, %5d, %8.2f, %5d" % (cat, cats[cat][9], cats[cat][10], cats[cat][0], cats[cat][1], cats[cat][2], cats[cat][3], cats[cat][4], cats[cat][5], cats[cat][6], cats[cat][7], cats[cat][8])
         total[0] += cats[cat][0]
         total[1] += cats[cat][1]
         
         total[2] += cats[cat][2]
         total[3] = total[3] + (cats[cat][3] * cats[cat][2] - total[3]) / total[2]
         
         total[4] += cats[cat][4]
         total[5] = total[5] + (cats[cat][5] * cats[cat][4] - total[5]) / total[4]
         
         total[6] += cats[cat][6]
         total[7] = total[7] + (cats[cat][7] * cats[cat][6] - total[7]) / total[6]
         
         total[8] += cats[cat][8]
      total[9] = mean
      total[10] = math.sqrt(var/(count-1))
      print "\"%33s\", %8.2f, %8.2f, %5d, %5d, %5d, %8.2f, %5d, %8.2f, %5d, %8.2f, %5d" % ("Total", total[9], total[10], total[0], total[1], total[2], total[3], total[4], total[5], total[6], total[7], total[8])
   timer.stop()
   return
      
   def weightsPrompt(category):
      print "Welcome to the Weights Prompt"
      do = True
      while do:
         word = raw_input("Enter a word\n> ").lower()
         if word != "":
            if not category.index.inVocabulary(word):
               print "%s was not found in the vocabulary" % (word)
               continue
            print "Word weight = %f" % (category.getWeightOf(word))
            print "Unique word weight = %f" % (category.getUniqueWeightOf(word))
         else:
            do = False

   def documentPrompt(category):
      print "Welcome to the Documents Prompt"
      do = True
      while do:
         key = raw_input("Enter a doc id\n> ")
         if key != "":
            key = int(key)
            document = category.getDocument(key)
            if document:
               print document.toString()
            else:
               print "Document not found in training set"
         else:
            do = False

   def yesNoPrompt(prompt):
      answer = raw_input(prompt + " (Yes/No) -- ").lower()
      if answer == "y" or answer == "yes":
         return True
      else:
         return False

if __name__ == '__main__':
    main()
