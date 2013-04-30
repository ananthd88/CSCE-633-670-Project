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
      self.refresh(, filename, categoryName)
      
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
      self.regressor = {  
         "KNR" : Regressor.KNeighborsRegressor(self.trainSet, False),
         "RFR" : Regressor.RandomForestRegressor(self.trainSet, False),
         "SVR" : Regressor.SVMRegressor(self.trainSet, False),
         "UWR" : Regressor.UniqueWeightsRegressor(self.trainSet, False),
      }[regression]
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
            regressors[key] = {
               "KNR" : Regressor.KNeighborsRegressor(categoryTrain.getGroup(classification)),
               "RFR" : Regressor.RandomForestRegressor(categoryTrain.getGroup(classification)),
               "SVR" : Regressor.SVMRegressor(categoryTrain.getGroup(classification)),
               "UWR" : Regressor.UniqueWeightsRegressor(categoryTrain.getGroup(classification)),
            }[regression]
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
      
# Just a comment
def main():
   gc.enable()
   timer = Timer.Timer("Entire Program", 0, 0)
   
   isRegressionOnly = True
   classification = "NB"
   regression = "KNR"
   numFeaturesC = 1000
   numFeaturesR = 1000
   
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
def process(categoryToProcess, regressionOnly = False, classification = "NB", regression = "RFR", numFeaturesC = 1000, numFeaturesR = 1000):
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
            regressors[classification] = {  
                      "KNR" : Regressor.KNeighborsRegressor(categoryTrain.getGroup(classification)),
                      "RFR" : Regressor.RandomForestRegressor(categoryTrain.getGroup(classification)),
                      "SVR" : Regressor.SVMRegressor(categoryTrain.getGroup(classification)),
                      "UWR" : Regressor.UniqueWeightsRegressor(categoryTrain.getGroup(classification)),
            }[regression]      
         regressor = regressors[classification]
         regressor.train(numFeaturesR)            
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
