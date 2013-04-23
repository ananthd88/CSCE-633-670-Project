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
   def __init__(self):
      self.numDocument = 0
      self.categoryNameToKey = {}
      self.companyNameToKey = {}
      self.categories = {}
      self.companies = {}      
      self.maPrecision = 0.0
      self.maRecall = 0.0
      
   # Documents   
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
      
      dictionary["Id"]              = int(dictionary.get("Id", "0"))
      dictionary["Title"]           = self.filterString(dictionary.get("Title", "").lower(), category)
      dictionary["FullDescription"] = self.filterString(dictionary.get("FullDescription", "").lower(), category)
      dictionary["LocationRaw"]     = dictionary.get("LocationRaw", "").lower()
      dictionary["Category"]        = category
      dictionary["Company"]         = company
      dictionary["SalaryNormalized"]= float(dictionary.get("SalaryNormalized", 0.0))
      document = Document.Document(dictionary)
      category.addDocument(document)
      return document
   def filterString(self, string, category):
      # Split only at whitespaces
      chunks = re.split('\s+', string)
      bag = []
      patterns = re.compile(r'\/|www|\.com|http|:|\.uk')
      stopwords = ["", ".", "a", "an", "and", "are", "as", "at", "be", "for", "have", "if", "in", "is", "of", "on", "or", "our", "s", "the", "this", "to", "we", "will", "with", "work", "you", "your"]
      # Remove chunks that are URLs
      for chunk in chunks:
         if patterns.search(chunk):
            continue
         # Split each chunk
         words = re.split('[^a-zA-Z\+\-]+', chunk)
         for word in words:
            category.index.addToFirstVocabulary(word)
            if word in stopwords:
               continue
            else:
               bag.append(word)
      newString = " ".join(bag)
      index = 0
      while False:
      #while True:
         if index <= len(bag) - 1:
            try:
               index = bag.index("experience", index)
               phrase = bag[max(0, index - 4):min(index + 5, len(bag))]
               phrase = "Experience phrase = " + " ".join(phrase)
               raw_input(phrase)
               index += 1
            except ValueError:
               break
      return newString
   
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
      print "\tKey = %d, Name  = %s" % (key, name)
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
      
   def naiveBayesClassifier(self, train, document):
      print "Starting naive bayes classifier"
      numTrainDocs = float(train.getNumDocuments())
      sizeTrainVocabulary = train.getSizeOfVocabulary()
      maxLogProbability = None
      predictedGroup = False
      for group in train.groups:
         logProbability  = 0.0
         # P(c) = (No. of docs in c)/(No. of training docs)
         logProbability += math.log(float(group.getNumDocs()), 2) - math.log(numTrainDocs, 2) 
         bagOfWords = document.getBagOfWords("all")
         for word in bagOfWords:
            # Add one smoothing
            logProbability += math.log(float(train.getNumTokensInGroup(word, group)) + 1.0, 2)
         logProbability -= float(len(bagOfWords)) * math.log(float((group.getTotalTokens() + sizeTrainVocabulary)), 2)
         if maxLogProbability < logProbability:
            maxLogProbability = logProbability
            predictedGroup = group
         # If the log of probabilities for two classes are equal
         elif maxLogProbability == logProbability:
            # Select the class which has more documents assigned to it
            # which would imply a greater value for P(c), 
            # since P(c) = (Num of docs classified as c)/(Num of docs in collection)
            if predictedGroup.getNumDocuments() < group.getNumDocuments():
               predictedGroup = group
      return predictedGroup
