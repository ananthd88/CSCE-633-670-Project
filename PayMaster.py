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
      self.refresh(filename, categoryName)
      
   def refresh(self, filename, categoryName):
      self.trainSet = Collection.Collection("Training")
      self.testSet = Collection.Collection("Testing")
      self.categoryName = categoryName
      self.trained = False
      self.documents = []
      self.resetRegressionSettings()
      self.resetStats()
      try:
         reader = csv.DictReader(inputfile)
         count = 0
         for row in reader:
            count += 1
            cat = row["Category"].lower()
            if cat != category:
               continue
            if count % 4 == 0:
               document = self.testSet.addDocument(row)
            else:
               document = self.trainSet.addDocument(row)
               self.documents.append(document.getKey())
      finally:
         inputfile.close()
      self.trainSet.createGroups()
      self.trainSet.assignGroups()
      trainSet.processDocuments()
      trainSet.computeAllWeights()
      #trainSet.computeAllTFIDF()
      trainSet.computeAllMI()

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
      self.regressors = None
      self.numFeaturesC = numFeaturesC
      self.numFeaturesR = numFeaturesR
      resetStats()
      if regressionOnly:
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
            "KNR" : Regressor.KNeighborsRegressor(self.trainSet, False),
            "RFR" : Regressor.RandomForestRegressor(self.trainSet, False),
            "SVR" : Regressor.SVMRegressor(self.trainSet, False),
            "UWR" : Regressor.UniqueWeightsRegressor(self.trainSet, False),
         }[regression]
         self.regressor.train(numFeaturesR)
      except:
         self.regressor = Regressor.UniqueWeightsRegressor(self.trainSet, False)
         self.regressor.train(numFeaturesR)
      return True
   def trainCR(self, classification, regression, numFeaturesC, numFeaturesR):
      self.classifier = {
         "NBC" : Classifier.NaiveBayesClassifier(self.trainSet),
         "SVC" : Classifier.SVM(self.trainSet),
      }[classification]
      classifier.train(numFeaturesC)
      for (key, group) in self.trainSet.getGroups().items():
         if group.getNumDocuments():
            try:
               regressors[key] = {
                  "KNR" : Regressor.KNeighborsRegressor(categoryTrain.getGroup(classification)),
                  "RFR" : Regressor.RandomForestRegressor(categoryTrain.getGroup(classification)),
                  "SVR" : Regressor.SVMRegressor(categoryTrain.getGroup(classification)),
                  "UWR" : Regressor.UniqueWeightsRegressor(categoryTrain.getGroup(classification)),
               }[regression]
               regressors[key].train(numFeaturesR)
            except:
               regressors[key] = Regressor.UniqueWeightsRegressor(categoryTrain.getGroup(classification))
               regressors[key].train(numFeaturesR)
   def getNextDocument(self):
      if self.nextDocument < 0 or self.nextDoc >= len(self.documents):
         return False
      return self.documents[self.nextDocument]
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

      
   def predictNextDocument():
      if self.nextDocument < 0 or self.nextDoc >= len(self.documents):
         return -1.0
      predictedSalary = self.predict(self.documents[self.nextDoc])
      self.nextDoc += 1
      return predictedSalary
   def predictAll(self):
      resetStats()
      for docKey in self.testSet.getDocuments():
         document = testSet.getDocument(docKey)
         self.predict(document)
