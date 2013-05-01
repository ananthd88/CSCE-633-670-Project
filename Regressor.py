from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor as RFR
from sklearn.neighbors import KNeighborsRegressor as KNR
from sklearn.svm import SVR
import itertools
import math

class Regressor:
   def __init__(self, trainSet, isGroup = True):
      self.trainSet     = trainSet
      self.features     = {}
      self.minMI        = 0.0
      self.vectorizer   = None
      self.regressor    = None
      self.isGroup      = isGroup

   def train(self, numFeatures = 0):
      return
   def predict(self, testSet = False):
      return

class UniqueWeightsRegressor(Regressor):
   def train(self, numFeatures = 500):
      count = 0
      if self.isGroup:
         for key in sorted(self.trainSet.getVocabulary(), key = lambda word: self.trainSet.getMI(word, self.trainSet), reverse=True):
            count += 1
            if count == numFeatures:
               self.minMI = self.trainSet.getMI(key, self.trainSet)
               break
      else:
         for key in sorted(self.trainSet.getVocabulary(), key = lambda word: self.trainSet.getUniqueWeightOf(word), reverse=True):
            count += 1
            if count == numFeatures:
               self.minMI = self.trainSet.getUniqueWeightOf(key)
               break
   def predict(self, document):
      predictedSalary   = self.trainSet.getMean()
      stdDeviation      = self.trainSet.getStdDeviation()
      prediction        = 0.0
      
      for word in set(document.getBagOfWords2("all")):
         if self.minMI and self.trainSet.getMI(word, self.trainSet) < self.minMI:
            continue
         prediction += self.trainSet.getUniqueWeightOf(word) * 5
      predictedSalary += (prediction/100.0) * stdDeviation
      return predictedSalary
      
class RandomForestRegressor(Regressor):
   def findImportantFeatures(self, numFeatures = 500):
      self.features = []
      count = 0
      if self.isGroup:
         for key in sorted(self.trainSet.getVocabulary(), key = lambda word: self.trainSet.getMI(word, self.trainSet), reverse=True):
            self.features.append(key)
            count += 1
            if count == numFeatures:
               self.minMI = self.trainSet.getMI(key, self.trainSet)
               break
      else:
         for key in sorted(self.trainSet.getVocabulary(), key = lambda word: self.trainSet.getUniqueWeightOf(word), reverse=True):
            self.features.append(key)
            count += 1
            if count == numFeatures:
               self.minMI = self.trainSet.getUniqueWeightOf(key)
               break
   def train(self, numFeatures = 500):
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
      return self.regressor.predict(Z)[0]
      
class KNeighborsRegressor(Regressor):
   def findImportantFeatures(self, numFeatures = 500):
      self.features = []
      count = 0
      if self.isGroup:
         for key in sorted(self.trainSet.getVocabulary(), key = lambda word: self.trainSet.getMI(word, self.trainSet), reverse=True):
            self.features.append(key)
            count += 1
            if count == numFeatures:
               self.minMI = self.trainSet.getMI(key, self.trainSet)
               break
      else:
         for key in sorted(self.trainSet.getVocabulary(), key = lambda word: self.trainSet.getUniqueWeightOf(word), reverse=True):
            self.features.append(key)
            count += 1
            if count == numFeatures:
               self.minMI = self.trainSet.getUniqueWeightOf(key)
               break
   def train(self, numFeatures = 500):
      self.regressor = KNR(n_neighbors=5,weights='uniform')
      #self.findImportantFeatures(numFeatures)
      self.vectorizer = TfidfVectorizer(vocabulary=self.trainSet.getVocabulary().keys(),use_idf=True,min_df=1)
      #self.vectorizer = TfidfVectorizer(vocabulary=self.features, use_idf=True, min_df=1)
      strings = []
      Y = []
      for docKey in self.trainSet.getDocuments():
         document = self.trainSet.getDocument(docKey)
         strings.append(" ".join(document.getBagOfWords2("all")))
         Y.append(document.getSalary())
      self.vectorizer.fit(strings)
      X = self.vectorizer.transform(strings)
      self.regressor.fit(X, Y)
   def predict(self, document):
      strings = []
      strings.append(" ".join(document.getBagOfWords2("all")))
      Z = self.vectorizer.transform(strings).todense()
      return self.regressor.predict(Z)[0]

class SVMRegressor(Regressor):
   def findImportantFeatures(self, numFeatures = 1000):
      #Selecting the important features
      self.features = []
      count = 0
      print "SVR Regrerssor features - ",
      for key in sorted(self.trainSet.getVocabulary(), key = lambda word: self.trainSet.getUniqueWeightOf(word), reverse=True):
         count += 1
         self.features.append(key)
         print key, " ",
         if count == numFeatures:
            break
   def train(self, numFeatures = 1000):
      self.findImportantFeatures(numFeatures)
      self.vectorizer = CountVectorizer(vocabulary = self.features,min_df = 1)
      self.regressor = SVR(kernel='linear', C=25, epsilon=10)
      strings = []
      Y = []
      for docKey in self.trainSet.getDocuments():
         document = self.trainSet.getDocument(docKey)
         strings.append(" ".join(document.getBagOfWords2("all")))
         Y.append(document.getSalary())
      X = self.vectorizer.fit_transform(strings)
      self.regressor.fit(X,Y)
      self.regressor.score(X, Y)
   def predict(self, document):
      strings = []
      strings.append(" ".join(document.getBagOfWords2("all")))
      Z = self.vectorizer.fit_transform(strings)
      return self.regressor.predict(Z)[0]
