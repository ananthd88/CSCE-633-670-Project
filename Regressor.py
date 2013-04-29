from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestRegressor as RFR
import itertools
import math

class Regressor:
   def __init__(self, trainSet):
      self.trainSet  = trainSet
      self.features     = {}
      self.minMI        = 0.0
      self.vectorizer   = None
      self.regressor    = None

   def train(self, numFeatures = 0):
      return
   def predict(self, testSet = False):
      return

class UniqueWeightsRegressor(Regressor):
   def train(self, numFeatures = 500):
      count = 0
      for key in sorted(self.trainSet.getVocabulary(), key = lambda word: self.trainSet.getMI(word, self.trainSet), reverse=True):
         count += 1
         if countmi == numFeatures:
            self.minMI = self.trainSet.getMI(key, self.trainSet)
            break
      
   def predict(self, document):
      predictedSalary   = self.trainSet.getMean()
      stdDeviation      = self.trainSet.getStdDeviation()
      prediction        = 0.0
      
      for word in set(document.getBagOfWords2("all")):
         if self.minMI:
            mi = self.trainSet.getMI(word, self.trainSet)
            if mi < self.minMI:
               continue
         prediction += self.group.getUniqueWeightOf(word) * 5
      predictedSalary += (prediction/100.0) * stdDeviation
      return predictedSalary
      
class RandomForestRegressor(Regressor):
   def findImportantFeatures(self, numFeatures = 500):
      self.features = []
      count = 0
      for key in sorted(self.trainSet.getVocabulary(), key = lambda word: self.trainSet.getMI(word, self.trainSet), reverse=True):
         self.features.append(key)
         count += 1
         if count == numFeatures:
            self.minMI = self.trainSet.getMI(key, self.trainSet)
            break
      
   def train(self, numFeatures = 500):
      # Should call findImportantFeatures() before a call to this function
      self.findImportantFeatures(numFeatures)
      self.regressor = RFR()
      self.vectorizer = CountVectorizer(vocabulary = self.features, min_df = 1)
      strings = []
      Y = []
      for docKey in self.trainSet.getDocuments():
         document = self.trainSet.getDocument(docKey)
         strings.append(" ".join(document.getBagOfWords2("all")))
         Y.append(document.getSalary())
      X = self.vectorizer.fit_transform(strings).toarray()
      self.regressor.fit(X, Y)
         
   def predict(self, document):
      strings = []
      strings.append(" ".join(document.getBagOfWords2("all")))
      Z = self.vectorizer.fit_transform(strings).toarray()
      return self.regressor.predict(Z)
