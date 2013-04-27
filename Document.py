import Index
import re
import math

class Document:         # Class which abstracts documents
   def __init__(self, dictionary):
      # Expects the dictionary to have all the necessary keys
      # TODO:  It might be better to maintain title and description as a list of
      #        words
      self.key                = dictionary["Id"]
      self.title              = dictionary["Title"]
      self.description        = dictionary["FullDescription"]
      self.location           = dictionary["LocationRaw"]
      self.company            = dictionary["Company"]
      self.category           = dictionary["Category"]
      self.salary             = dictionary["SalaryNormalized"]
      self.group              = False
      self.tfidfVector        = {}        # TFIDF vector for the document
      self.tfidfLength        = -1.0      # Length of the TFIDF vector

   def __hash__(self):
      return hash(self.key)
   def __eq__(self, other):
      return self.key == other.key
   
   # General accessor methods that operate on the document's fields
   def getKey(self):
      return self.key
   def getTitle(self):
      return self.title
   def setTitle(self, title):
      self.title = title
   def setDescription(self, description):
      self.description = description
   def getDescription(self):
      return self.description
   def getLocation(self):
      return self.location
   def getCompany(self):
      return self.company
   def getCategory(self):
      return self.category
   def getSalary(self):
      return self.salary
   def getGroup(self):
      return self.group
   def setGroup(self, group):
      self.group = group
      
   # Get words
   def getBagOfWords(self, field = "description"):
      return {
         "title": self.title,#re.split('[ ]+', self.title),
         "description": self.description,#re.split('[ ]+', self.description),
         "all": self.title + self.description,#re.split('[ ]+', self.title) + re.split('[ ]+', self.description)
      }[field]
   def getBagOfWords2(self, field = "description"):
      bag = []
      if field == "all":
         title = self.getBagOfWords("title")
         for word in title:
            bag.append("t_" + word)
         description = self.getBagOfWords("description")
         for word in description:
            bag.append("d_" + word)
         return bag
      return bag
   def getWordDictionary(self, string):
      words = re.split('[ ]+', string)
      dictionary = {}
      for word in words:
         count = dictionary.get(word, False)
         if count:
            dictionary[word] += 1
         else:
            dictionary[word] = 1
      return dictionary
   def getSetOfWords(self):
      return set(self.tfidfVector.keys())
   
   # Features
   def getFeatures(self):
      return self.getBagOfWords2("all")
   
   # Methods that operate on the document's TFIDF vector
   def getTFIDF(self, word):
      documentEntry = self.tfidfVector.get(word, 0)
      if documentEntry:
         return documentEntry.getTFIDF()
      else:
         return 0.0
   def getCount(self, word):
      documentEntry = self.tfidfVector.get(word, 0)
      if documentEntry:
         return documentEntry.getCount()
      else:
         return 0
   def computeTFIDFLength(self):
      self.tfidfLength  = 0.0
      for word in self.tfidfVector:
         tfidf = self.getTFIDF(word)
         self.tfidfLength  += tfidf * tfidf
      self.tfidfLength  = math.sqrt(self.tfidfLength)
      return self.tfidfLength
   def getTFIDFLength(self):
      if self.tfidfLength < 0.0:
         return self.computeTFIDFLength()
      return self.tfidfLength
   def tfidfDotProduct(self, other):
      dotProduct        = 0.0
      for word in self.tfidfVector:
         dotProduct    += self.getTFIDF(word) * other.getTFIDF(word)
      return dotProduct
   def cosineSimilarity(self, other):
      dotProduct        = self.tfidfDotProduct(other)
      return dotProduct/(self.getTFIDFLength() * other.getTFIDFLength())
   def cosineDistanceTo(self, other):
      cosine = self.cosineSimilarity(other)
      if cosine > 1.0 or cosine < -1.0:
         return float(math.pi/2.0)
      return abs(math.acos(cosine))
   def distanceTo(self, other):
      setOfWords        = self.getSetOfWords() | other.getSetOfWords()
      distance          = 0.0
      for word in setOfWords:
         diff           = self.getTFIDF(word) - other.getTFIDF(word)
         distance      += diff * diff
      return math.sqrt(distance)
   def normalDistanceTo(self, other):
      setOfWords        = self.getSetOfWords() | other.getSetOfWords()
      distance          = 0.0
      for word in setOfWords:
         diff           = (self.getTFIDF(word)/self.getTFIDFLength()) - (other.getTFIDF(word)/other.getTFIDFLength())
         distance      += diff * diff
      return math.sqrt(distance)
   def getDifferenceVector(self, other):
      differenceVector = {}
      setOfWords        = self.getSetOfWords() | other.getSetOfWords()
      for word in setOfWords:
         differencevector[word] = self.getTFIDF(word) - other.getTFIDF(word)
      return differenceVector
      
   def joinToIndex(self, word, documentEntry):
      self.tfidfVector[word] = documentEntry
   
   # Miscellaneous stringify methods for document
   def toString(self, keys = {'all': 1}):
      string = ""
      if keys.get("all", False):
         string += "Id = " + str(self.key)
         string += "\nTitle = " + self.title
         string += "\nDescription = " + self.description
         string += "\nLocation = " + self.location
         string += "\nCompany = " + self.company.getName()
         string += "\nCategory = " + self.category.getName()
         string += "\nSalary = " + str(self.salary)
         string += "\nGroup = " + str(self.group.getKey()) 
         string += "\n\tMean group salary = " + str(self.group.getMean())
         string += "\n\tStd dev of group salary = " + str(self.group.getStdDeviation())
      else:
         if keys.get("id", False):
            string += "Id = " + str(self.id)
         if keys.get("title", False):
            string += "\nTitle = "       + self.title
         if keys.get("description", False):
            string += "\nDescription = " + self.description
         if keys.get("location", False):
            string += "\nLocation = " + self.location
         if keys.get("company", False):
            string += "\nCompany = "     + self.company.getName()
         if keys.get("category", False):
            string += "\nCategory = "    + self.category.getName()
         if keys.get("salarynorm", False):
            string += "\nSalaryNorm = "  + str(self.salary)
      return string
   
      
   def document2VowpalData(self):
      # TODO:  To be modified
      string = str(math.log(self.salaryNorm, 10))
      string += " "
      
      string += "|Title "
      wordDictionary = self.getWordDictionary(self.title)
      for (word, count) in wordDictionary.items():
         if len(word) > 1:
            string += word + ":" + str(count) + " "
      #if string[-1] == " ":
      #   string = string[:-1]
      
      string += "|Description "
      wordDictionary = self.getWordDictionary(self.description)
      for (word, count) in wordDictionary.items():
         if len(word) > 1:
            string += word + ":" + str(count) + " "
      #if string[-1] == " ":
      #   string = string[:-1]
      
      string += "|Category "
      wordDictionary = self.getWordDictionary(self.category)
      for (word, count) in wordDictionary.items():
         if len(word) > 1:
            string += word + ":" + str(count) + " "
      #if string[-1] == " ":
      #   string = string[:-1]
      
      string += "|Company "
      wordDictionary = self.getWordDictionary(self.company)
      for (word, count) in wordDictionary.items():
         if len(word) > 1:
            string += word + ":" + str(count) + " "
      if string[-1] == " ":
         string = string[:-1]
      
      return string
