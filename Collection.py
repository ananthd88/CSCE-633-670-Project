import Document
import Index
#import Cluster
import Category
import Company
import sys
import math
import random
import re
import os.path
import requests
import json

class Collection:
   def __init__(self, name):
      self.name = name
      self.numDocument = 0
      self.categoryNameToKey = {}
      self.companyNameToKey = {}
      self.categories = {}
      self.companies = {}      
      self.maPrecision = 0.0
      self.maRecall = 0.0
      
   # Documents   
   def getName(self):
      return self.name
   def getNumDocuments(self):
      return self.NumDocuments
   def addDocument(self, dictionary):
      categoryName = dictionary.get("Category", "").lower()
      self.addCategory(categoryName)
      category = self.getCategory(False, categoryName)
      companyName = dictionary.get("Company", "").lower()
      if companyName == "":
         companyName = "NA"
      self.addCompany(companyName)
      company = self.getCompany(False, companyName)
      category.addCompany(company)
      document = {}
      document["Id"]              = int(dictionary.get("Id", "0"))
      document["Title"]           = self.filterString(dictionary.get("Title", "").lower(), category)
      document["FullDescription"] = self.filterString(dictionary.get("FullDescription", "").lower(), category)
      document["LocationRaw"]     = dictionary.get("LocationRaw", "").lower()
      document["Category"]        = category
      document["Company"]         = company
      document["SalaryNormalized"]= float(dictionary.get("SalaryNormalized", 0.0))
      document = Document.Document(document)
      category.addDocument(document)
      return document
   def filterString(self, string, category):
      # Split only at whitespaces
      chunks = re.split('\s+', string)
      bag = []
      patterns = re.compile(r'www\.|\.com|http|:|\.uk|\.net|\.org|\.edu')
      stopwords = ["", ".", "a", "an", "and", "are", "as", "at", "be", "for", "have", "if", "in", "is", "of", "on", "or", "our", "s", "the", "this", "to", "we", "will", "with", "work", "you", "your"]
      # Remove chunks that are URLs
      for chunk in chunks:
         if patterns.search(chunk):
            continue
         #words = re.split('[^0-9a-zA-Z\+\-]+', chunk)
         words = re.split('[^a-zA-Z\+\-]+', chunk)
         for word in words:
            if word in stopwords:
               continue
            else:
               category.index.addToFirstVocabulary(word)
               bag.append(word)
      #newString = " ".join(bag)
      index = 0
      while False:
      #while True:
         if index <= len(bag) - 1:
            try:
               index = bag.index("experience", index)
               phrase = bag[max(0, index - 4):min(index + 5, len(bag))]
               for word in phrase:
                  if word == "years" or word == "one" or word == "two" or word == "three" or word == "four" or word == "five" or word == "six" or word == "seven" or word == "eight" or word == "nine" or word == "ten" or word == "eleven":
                     print "((%s)) " % (word),
                  if re.search('[a-zA-Z\+\-]', word):
                     continue
                  else:
                     print "(%s) " % (word),
                     #break                 
               phrase = " ".join(phrase)
               print phrase
               index += 1
            except ValueError:
               break
      return bag
   
   # Categories
   def hasCategory(self, key, name):
      if key:
         return key in self.categories
      elif name:
         return name in self.categoryNameToKey
      return False
   def addCategory(self, name):
      if self.hasCategory(False, name):      
         return False      
      key = len(self.categories) + 1 # Keys run from 1 to num of categories
      category = Category.Category(key, name)
      self.categoryNameToKey[name] = key
      self.categories[key] = category
      return True
   def getCategory(self, key, name):
      if key:
         if self.hasCategory(key, False):
            return self.categories[key]
      elif name:
         if self.hasCategory(False, name):
            return self.categories[self.getCategoryKey(name)]
      return False
   def getCategoryName(self, key):
      if hasCategory(key, False):
         return self.categories[key].getName()
      return False
   def getCategoryKey(self, name):
      # Expects name in lower case
      return self.categoryNameToKey.get(name, False)
   def processDocuments(self):
      for (key, category) in self.categories.items():
         category.processDocuments()
   def computeAllWeights(self):
      for (key, category) in self.categories.items():
         category.computeAllWeights()
   def computeAllTFIDF(self):
      for (key, category) in self.categories.items():
         category.computeAllTFIDF()
   def computeAllMI(self):
      for (key, category) in self.categories.items():
         category.computeAllMI()
   def createGroups(self):
      for (key, category) in self.categories.items():
         # TODO: Change hard-coded value
         category.createGroups(5)
   def assignGroups(self):
      for (key, category) in self.categories.items():
         category.assignGroups()
   def findImportantWords(self, fraction):
      for (key, category) in self.categories.items():
         category.findImportantWords(fraction)
         
   # Companies
   def hasCompany(self, key, name):
      if key:
         return key in self.companies
      elif name:
         return name in self.companyNameToKey
      return False
   def addCompany(self, name):
      if self.hasCompany(False, name):
         return False
      key = len(self.companies) + 1
      company = Company.Company(key, name)
      self.companyNameToKey[name] = key
      self.companies[key] = company
      return True
   def getCompany(self, key, name):
      if key:
         if self.hasCompany(key, False):
            return self.companies[key]
      elif name:
         if self.hasCompany(False, name):
            return self.companies[self.getCompanyKey(name)]
      return False
   def getCompanyName(self, key):
      if self.hasCompany(key, False):
         return False
      return self.companies[key].getName()
   def getCompanyKey(self, name):
      # Expects name in lower case
      return self.companyNameToKey.get(name, False)
   def getCategories(self):
      return self.categories
   
   
   def printCollection(self):
      for document in self.documents:
         print "%d -> %s" % (document.getKey(), document.getTitle())
      
   def kMeansCluster(self, k, distanceMetric):
      distanceMetricNames = ["Cosine Similarity",
                             "Euclidean distance using normalized TFIDF vectors",
                             "Simple Euclidean distance"]
      print "Running k-means clustering algorithm with k = %d" % (k)
      print "Distance metric being used is %s" % (distanceMetricNames[distanceMetric])
      Cluster.Cluster.numOfClustersCreated = 0
      # Initialization with seeds
      seeds = random.sample(self.documents, k)
      self.clusters = []
      for seed in seeds:
         self.clusters.append(Cluster.Cluster(seed, distanceMetric))
      # Reset the cluster fields populated from any previous runs
      for document in self.documents:
         document.cluster = False
      
      change = True
      iterations = 0
      while(change and iterations < 4):
         print "Iteration %d" % (iterations)
         change = False
         # Assign each document to 'nearest' cluster
         for document in self.documents:
            if document.cluster:
               minDistance = cluster.distanceTo(document)
            else:
               minDistance = sys.float_info.max
            for cluster in self.clusters:
               distance = cluster.distanceTo(document)
               if distance < minDistance:
                  minDistance = distance
                  success = cluster.add(document)
                  if success:
                     change = True
         for cluster in self.clusters:
            cluster.recomputeCentroid()
            
         iterations += 1         
      purityCounts = 0.0
      rssCounts = 0.0
      for cluster in self.clusters:
         cluster.computeMajorityClass()
         purityCounts += cluster.majorityCount
         cluster.computeRSS()
         rssCounts += cluster.rss         
         print cluster
      self.purity = float(purityCounts)/float(len(self.documents))
      self.rss = rssCounts
      print
      print "Finished %d-clustering in %d iterations" % (k, iterations)
      print "Purity for the clustering = %f" % (self.purity)
      print "RSS for clustering = %lf" % (self.rss)
