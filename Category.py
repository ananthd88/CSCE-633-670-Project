import Index
import math

class Category:      # Class that abstracts a category of documents
   def __init__(self, key, name):
      self.key = key
      self.name = name
      self.documents = {}
      self.companies = {}
      self.groups = {}
      self.runningMean = 0.0
      self.runningVariance = 0.0
      self.index = Index.Index(self)      
   def __hash__(self):
      return hash(self.key)
   def __eq__(self, other):
      return self.key == other.key
   
   # Basic accessor methods
   def getKey(self):
      return self.key
   def getName(self):
      return self.name
   def getMean(self):
      return self.runningMean
   def getVariance(self):
      return self.runningVariance/(self.getNumDocuments() - 1)
   def getStdDeviation(self):
      return math.sqrt(self.getVariance())
   
   # Documents
   def getNumDocuments(self):
      return len(self.documents)
   def hasDocument(self, document):
      return document.getKey() in self.documents
   def addDocument(self, document):
      # Expects a valid document object as input
      # Only adds to the collection of documents in category & computes mean
      # and variance.
      # Does not compute any weights or tfidf
      if self.hasDocument(document):
         return False
      self.documents[document.getKey()] = document
      oldMean = self.runningMean
      oldVari = self.runningVariance
      newSal  = document.getSalary()
      newNum  = float(self.getNumDocuments())
      newMean = oldMean + (newSal - oldMean) / newNum
      newVari = oldVari + (newSal - oldMean) * (newSal - newMean)
      self.runningMean = newMean
      self.runningVariance = newVari
      return True
   def getDocument(self, key):
      if key in self.documents:
         return self.documents[key]
      return False
   def getDocuments(self):
      # Returns list of document keys
      return self.documents.keys()
   def predictSalary(self, document):
      # Stub for method that uses weights/uniqueWeights of terms to predict 
      # the salary
      return 0.0

   # Companies
   def hasCompany(self, company):
      return company.getKey() in self.companies
   def addCompany(self, company):
      # Expects a valid company object as input
      if self.hasCompany(company):
         return False
      self.companies[company.getKey()] = company
      return True
   def getCompanies(self):
      # Returns list of company keys
      return self.companies.keys()
   
   # Index
   # Populates the reverse index
   # Computes all weights and TFIDF
   def processDocuments(self):
      print "Processing documents"
      for key in self.documents:
         self.index.processDocument(self.documents[key])
      self.index.computeAllTFIDF()
   
   # Wrapper functions over data structures contained in Category instance   
   def getSizeOfVocabulary(self):
      return self.index.getSizeOfVocabulary()
   def getWeightOf(self, word, field):
      return self.index.getWeightOf(word, field)
   def getUniqueWeightOf(self, word, field):
      return self.index.getUniqueWeightOf(word, field)
   
class Group(Category):
   def __init__(self, key):
      self.key = key
      self.documents = {}
