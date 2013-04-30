import Collection
import Document
import Classifier
import Regressor
import csv
import sys
import math
import re
import gc

class PayMaster:
   def __init__(self, filename, categoryName):
      self.filename = filename
      self.refresh(categoryName)
      
   def refresh(self, categoryName):
      print categoryName
      self.trainSet = Collection.Collection("Training")
      self.testSet = Collection.Collection("Testing")
      self.categoryName = categoryName.lower()
      self.trained = False
      self.documents = []
      self.resetRegressionSettings()
      self.resetStats()
      inputfile = open(self.filename, 'rt')
      try:
         reader = csv.DictReader(inputfile)
         count = 0
         for row in reader:
            count += 1
            cat = row["Category"].lower()
            if cat != self.categoryName:
               continue
            if count % 4 == 0:
               document = self.testSet.addDocument(row)
            else:
               document = self.trainSet.addDocument(row)
               self.documents.append(document.getKey())
      finally:
         inputfile.close()
      self.categoryTrain = self.trainSet.getCategory(1, False)
      self.categoryTest = self.testSet.getCategory(1, False)
      self.trainSet.createGroups()
      self.trainSet.assignGroups()
      self.trainSet.processDocuments()
      self.trainSet.computeAllWeights()
      #self.trainSet.computeAllTFIDF()
      self.trainSet.computeAllMI()

   def resetRegressionSettings(self):
      self.regressionOnly = False
      self.classification = None
      self.classifier = None
      self.regression = None
      self.regressor = None
      self.regressors = {}
      self.numFeaturesC = 0
      self.numFeaturesR = 0
   def resetStats(self):
      self.nextDocument = 0
      self.runningMean = 0.0
      self.runningStdVariance = 0.0
      self.predictedCount = 0
      self.posCount = 0
      self.negCount = 0
      self.posMean = 0.0
      self.negMean = 0.0
      self.count3000 = 0
   def train(self, regressionOnly = False, classification = "NBC", regression = "RFR", numFeaturesC = 1000, numFeaturesR = 1000):
      self.regressionOnly = regressionOnly
      self.classification = classification
      self.classifier = None
      self.regression = regression
      self.regressor = None
      self.regressors = {}
      self.numFeaturesC = numFeaturesC
      self.numFeaturesR = numFeaturesR
      self.resetStats()
      if self.regressionOnly:
         if regression not in ["KNR", "RFR", "SVR", "UWR"]:
            return False
         return self.trainR(regression, numFeaturesR)
      else:
         if classification not in ["NBC", "SVC"] or regression not in ["KNR", "RFR", "SVR", "UWR"]:
            return False
         return self.trainCR(classification, regression, numFeaturesC, numFeaturesR)      
   def trainR(self, regression, numFeaturesR):
      try:
         self.regressor = {  
            "KNR" : Regressor.KNeighborsRegressor(self.categoryTrain, False),
            "RFR" : Regressor.RandomForestRegressor(self.categoryTrain, False),
            "SVR" : Regressor.SVMRegressor(self.categoryTrain, False),
            "UWR" : Regressor.UniqueWeightsRegressor(self.categoryTrain, False),
         }[regression]
         self.regressor.train(numFeaturesR)
      except:
         self.regressor = Regressor.UniqueWeightsRegressor(self.categoryTrain, False)
         self.regressor.train(numFeaturesR)
      return True
   def trainCR(self, classification, regression, numFeaturesC, numFeaturesR):
      self.classifier = {
         "NBC" : Classifier.NaiveBayesClassifier(self.categoryTrain),
         "SVC" : Classifier.SVM(self.categoryTrain),
      }[classification]
      self.classifier.train(numFeaturesC)
      for group in self.categoryTrain.getGroups():
         key = group.getKey()
         if group.getNumDocuments():
            try:
               self.regressors[key] = {
                  "KNR" : Regressor.KNeighborsRegressor(group),
                  "RFR" : Regressor.RandomForestRegressor(group),
                  "SVR" : Regressor.SVMRegressor(group),
                  "UWR" : Regressor.UniqueWeightsRegressor(group),
               }[regression]
               self.regressors[key].train(numFeaturesR)
            except:
               self.regressors[key] = Regressor.UniqueWeightsRegressor(group)
               self.regressors[key].train(numFeaturesR)
   def getNextDocument(self):
      if self.nextDocument < 0 or self.nextDocument >= len(self.documents):
         return False
      return self.categoryTrain.getDocument(self.documents[self.nextDocument])
   def predict(self, document):
      if not self.trained:
         return -1.0
      if not self.regressionOnly:
         classification = self.classifier.classify(document)
         self.regressor = self.regressors[classification]
      predictedSalary = self.regressor.predict(document)
      actualSalary = document.getSalary()
      self.predictedCount += 1
      self.runningMean += (math.fabs(predictedSalary - actualSalary) - self.runningMean) / self.predictedCount
      if predictedSalary > actualSalary:
         self.posCount += 1
         self.posMean += (math.fabs(predictedSalary - actualSalary) - self.posMean) / self.posCount
      elif predictedSalary < actualSalary:
         self.negCount += 1
         self.negMean += (math.fabs(predictedSalary - actualSalary) - self.negMean) / self.negCount
      if math.fabs(predictedSalary - actualSalary) < 3000.0:
         self.count3000 += 1
   def getMean(self):
      return self.runningMean
   def getVariance(self):
      if self.predictedCount < 2:
         return 0.0
      return self.runningVariance/(self.predictedCount - 1)
   def getStdDeviation(self):
      return math.sqrt(self.getVariance())
   def getPosMean(self):
      return self.posMean
   def getNegMean(self):
      return self.negMean
   def getCount3000(self):
      return self.count3000
   def getMeanSalary(self):
      return self.categoryTrain.getMean()
   def getStdDeviationSalary(self):
      return self.categoryTrain.getStdDeviation()
      
   def predictNextDocument():
      if self.nextDocument < 0 or self.nextDocument >= len(self.documents):
         return -1.0
      predictedSalary = self.predict(self.documents[self.nextDocument])
      self.nextDocument += 1
      return predictedSalary
   def predictAll(self):
      self.resetStats()
      for docKey in self.categoryTest.getDocuments():
         document = self.categoryTest.getDocument(docKey)
         self.predict(document)
