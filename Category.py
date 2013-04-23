import Index
import math

class Category:      # Class that abstracts a category of documents
   def __init__(self, key, name):
      self.key = key
      self.name = name
      self.documents = {}
      self.companies = {}
      self.groups = []
      self.groupBoundaries = []
      self.runningMean = 0.0
      self.runningVariance = 0.0
      self.index = Index.Index(self)
      self.totalTokenCount = 0
   def __hash__(self):
      return hash(self.key)
   def __eq__(self, other):
      return self.key == other.key

   
   #The basic accessor methods
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
   def incrementTotalTokenCount(self):
      self.totalTokenCount += 1
   def getTotalTokenCount(self):
      return self.totalTokenCount

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
   def processDocuments(self):
      print "Processing documents - Creating the reverse index"
      for key in self.documents:
         self.index.processDocument(self.documents[key])
      self.index.reverseIndexDone = True
      print "Total no. of words in vocabulary = %d" % (self.index.getSizeOfVocabulary())
      print "Total no. of title words in vocabulary = %d" % (self.index.numTitleWords)
      print "Total no. of description words in vocabulary = %d" % (self.index.numDescriptionWords)
   # Computes all weights
   def computeAllWeights(self):
      print "Computing All Weights"
      self.index.computeAllWeights()
   # Computes all  TFIDF
   def computeAllTFIDF(self):
      print "Computing All TFIDF"
      self.index.computeAllTFIDF()
   
   # Groups
   def getNumGroups(self):
      return len(self.groups)
   def getNumClasses(self):
      return self.getNumGroups()
   def assignGroup(self, document):
      salary = document.getSalary()
      count = 0
      assigned = False
      for boundary in self.groupBoundaries:
         if salary < boundary:
            document.setGroup(self.groups[count])
            self.groups[count].addDocument(document)
            assigned = True
            break
         count += 1
      if assigned == False:
         document.setGroup(self.groups[count])
         self.groups[count].addDocument(document)         
   def createGroups(self, numGroups):
      salaries = []
      for key in self.documents:
         document = self.documents[key]
         salaries.append(document.getSalary())
      salaries = sorted(salaries)
      groupSize = self.getNumDocuments()/numGroups
      count = 0
      group = 0
      boundaries = []
      for salary in salaries:
         if count % groupSize == 0:
            boundaries.append(salary)
            count  = 0
         count += 1
      boundaries = boundaries[1:-1]
      self.groupBoundaries = boundaries
      count = 0
      for boundary in boundaries:
         self.groups.append(Group(count))
         count += 1
      self.groups.append(Group(count))
   def getClasses(self):
      return range(self.getNumGroups())
   def getNumDocumentsInClass(self, groupKey):
      if groupKey < 0 or groupKey > self.getNumGroups():
         return 0
      return self.groups[groupKey].getNumDocuments()
   
   
   
   def getXY(self, importantWords):
      output = {}
      numFeatures = len(importantWords)
      numDocuments = self.getNumDocuments()
      output["X"] = [[0.0] * numFeatures] * numDocuments
      output["Y"] = [0] * numDocuments
      docCount = 0
      for key in self.documents:
         document = self.getDocument(key)
         featureArray = output["X"][docCount]
         wordCount = 0
         nonzeroWords = 0
         for word in importantWords:
            # Fill features with TFIDF, 
            # can be replaced with document.getCount(word) instead
            featureArray[wordCount] = document.getCount(word)
            #featureArray[wordCount] = document.getTFIDF(word)
            if featureArray[wordCount] != 0.0:
               nonzeroWords += 1
            wordCount += 1
         output["Y"][docCount] = document.getGroup().getKey()
         #if output["Y"][docCount] != 0:
         #   print "Y[%d] Group - %d, nonzeroWords = %d" % (docCount, output["Y"][docCount], nonzeroWords)
         docCount += 1
      return output
         
   # Wrapper functions over data structures contained in Category instance   
   def getSizeOfVocabulary(self):
      return self.index.getSizeOfVocabulary()
   def getWeightOf(self, word, field):
      return self.index.getWeightOf(word, field)
   def getUniqueWeightOf(self, word, field):
      return self.index.getUniqueWeightOf(word, field)
   def getNumTokensInGroup(self, word, group):
      return self.index.getNumTokensInGroup(word, group)
   def getNumTokensInClass(self, word, groupKey):
      # TODO: Encapsulate self.groups everywhere
      if groupKey < 0 or groupKey > self.getNumGroups():
         return 0
      return self.getNumTokensInGroup(word, self.groups[groupKey])
   def getTotalTokens(self, groupKey):
      if groupKey < 0 or groupKey > self.getNumGroups():
         return 0
      return self.groups[groupKey].getTotalTokenCount()

class Group(Category):
   def __init__(self, key):
      self.key = key
      self.documents = {}
      self.runningMean = 0.0
      self.runningVariance = 0.0
      self.totalTokenCount = 0
