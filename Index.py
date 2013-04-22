import math
class DocumentEntry:             # Index -> Dictionary of Terms -> TermEntry -> List Of DocumentEntry -> DocumentEntry
   def __init__(self):
      self.count = 0             # Count of number of times tokens of this term appears in a particular document
      self.tfidf = 0.0           # TFIDF of this term in this document
   
   def getCount(self):
      return self.count   
   def incrementCount(self):
      self.count += 1
      
   def getTFIDF(self):
      return self.tfidf   
   def setTFIDF(self, tfidf):
      self.tfidf = tfidf
   
class GroupEntry:                # Index -> Dictionary of Terms -> TermEntry -> List Of GroupEntry -> GroupEntry
   def __init__(self):
      self.count = 0             # Count of number of times tokens of this term appears in a particular group
   
   def getCount(self):
      return self.count
   def incrementCount(self):
      self.count += 1
      
class TermEntry:                 # Index -> Dictionary of Terms -> TermEntry
   def __init__(self):
      self.documents = {}        # Hashtable of DocumentEntries
      self.groups = {}       # Hashtable of GroupEntries
      self.totalCount   = 0      # Count of total number of tokens of this term in all the documents in the collection
      self.weight = 0.0
      self.uniqueWeight = 0.0

   # Methods operating on the documentList
   def getNumDocuments(self):
      return len(self.documents)
   def addDocument(self, document):
      if self.hasDocumentEntry(document):         
         return False
      self.documents[document.getKey()] = DocumentEntry()
      return True
   def getDocumentList(self):
      return self.documents
   
   # Basic accessor methods
   def getWeight(self):
      return self.weight
   def getUniqueWeight(self):
      return self.uniqueWeight
   def setWeight(self, weight):
      self.weight = float(weight)
   def setUniqueWeight(self, weight):
      self.uniqueWeight = float(weight)
   
   # Methods operating on a particular documentEntry
   def getDocumentEntryCount(self, document):        # Get count of tokens of this term in a given document
      if self.hasDocumentEntry(document):
         return self.documents[document.getKey()].getCount()
      return 0
   def incrementDocumentEntryCount(self, document):  # Increment the count of tokens of this term in a given document
      if self.hasDocumentEntry(document):
         self.documents[document.getKey()].incrementCount()
         return True
      return False
   def getTFIDF(self, document):                # Get the TFIDF for of term for a particular document
      if self.hasDocumentEntry(document):
         return self.documents[document.getKey()].getTFIDF()
      return 0.0
   def setTFIDF(self, document, tfidf):         # Set the TFIDF for of term for a particular document
      if self.hasDocumentEntry(document):
         self.documents[document.getKey()].setTFIDF(tfidf)
         return True
      return False
   def hasDocumentEntry(self, document):
      return document.getKey() in self.documents

   # Methods operating on the groupList
   def getGroups(self):
      return self.groups
   def addgroup(self, group):
      if self.hasGroupEntry(group):
         return False
      self.groups[group.getKey()] = GroupEntry()
   def hasGroupEntry(self, group):
      return group.getKey() in self.groups
      
   # Methods operating on a particular groupEntry
   def getGroupEntryCount(self, group):
      if self.hasGroupEntry(group):
         return self.groups[group.getKey()].getCount()
      return 0
   def incrementGroupEntryCount(self, group):
      if self.hasGroupEntry(group):
         self.groups[group.getKey()].incrementCount()
         return True
      return False      
   
   def getTotalCount(self):
      return self.totalCount
   def incrementTotalCount(self):
      self.totalCount += 1      
      
class Index:                     # Index for a collection
   def __init__(self, category):
      self.vocabulary = {}       # Hashtable of terms pointing to a TermEntry
      self.numDocuments = 0           # Total number of docs indexed
      self.category = category
   # Methods that operate on the number of documents
   def getNumDocuments(self):
      return self.numDocuments
   def incrementNumDocuments(self):
      self.numDocuments += 1
   
   # Methods that operate on all the TermEntries in the Vocabulary or the Vocabulary itself
   def getVocabulary(self):
      return self.vocabulary
   def getSizeOfVocabulary(self):
      return len(self.vocabulary)
   def inVocabulary(self, word):
      return word in self.vocabulary
   def addToken(self, word, document, group):
      if not self.inVocabulary(word):
         self.vocabulary[word] = TermEntry()
      termEntry = self.vocabulary[word]
      if document:
         termEntry.addDocument(document) # Not added if already exists in list
         termEntry.incrementDocumentEntryCount(document)
      #if group:
      #   if not termEntry.hasGroup(group):
      #      termEntry.adGroup(group)
      #   termEntry.incrementGroupEntryCount(group)
      
   def processDocument(self, document):
      self.incrementNumDocuments()
      group = False
      # Title
      bagOfWords = document.getBagOfWords("title")
      for word in bagOfWords:
         word = "t_" + word
         self.addToken(word, document, group)
         
      # Description
      bagOfWords = document.getBagOfWords("description")
      for word in bagOfWords:
         word = "d_" + word
         self.addToken(word, document, group)
   
   def computeAllTFIDF(self):
      print "Computing All TFIDF"
      wordcloud = {}
      wordcloudUnique = {}
      for docKey in self.category.getDocuments():
         document = self.category.getDocument(docKey)
         pctChange = (document.getSalary()/self.category.getMean() - 1.0) * 100
         # Title
         words = document.getBagOfWords("title")
         for word in words:
            word = "t_" + word
            if not wordcloud.get(word, False):
               wordcloud[word] = [0.0, 0.0]
            wordcloud[word][0] += 1.0
            wordcloud[word][1] = wordcloud[word][1] + (pctChange/len(words) - wordcloud[word][1])/wordcloud[word][0]
         wordsSet = set(words)
         for word in wordsSet:
            word = "t_" + word
            if not wordcloudUnique.get(word, False):
               wordcloudUnique[word] = [0.0, 0.0]
            wordcloudUnique[word][0] += 1.0
            wordcloudUnique[word][1] = wordcloudUnique[word][1] + (pctChange/len(wordsSet) - wordcloudUnique[word][1])/wordcloudUnique[word][0]
         
         # Description
         words = document.getBagOfWords("description")
         for word in words:
            word = "d_" + word
            if not wordcloud.get(word, False):
               wordcloud[word] = [0.0, 0.0]
            wordcloud[word][0] += 1.0
            wordcloud[word][1] = wordcloud[word][1] + (pctChange/len(words) - wordcloud[word][1])/wordcloud[word][0]
         wordsSet = set(words)
         for word in wordsSet:
            word = "d_" + word
            if not wordcloudUnique.get(word, False):
               wordcloudUnique[word] = [0.0, 0.0]
            wordcloudUnique[word][0] += 1.0
            wordcloudUnique[word][1] = wordcloudUnique[word][1] + (pctChange/len(wordsSet) - wordcloudUnique[word][1])/wordcloudUnique[word][0]
         
      
      
      numDocs = self.getNumDocuments()
      logNumDocs = math.log(float(numDocs), 2)
      vocabulary = self.getVocabulary()
      for word in vocabulary.keys():
         self.vocabulary[word].setWeight(wordcloud[word][1])
         self.vocabulary[word].setUniqueWeight(wordcloudUnique[word][1])
         documentList = self.getDocumentListFor(word)
         df = len(documentList)
         logdf = logNumDocs - math.log(float(df), 2)
         for (docKey, documentEntry) in documentList.items():
            tf = documentEntry.getCount()
            logtf = 1.0 + math.log(float(tf), 2)
            tfidf = logtf * logdf
            documentEntry.setTFIDF(tfidf)
            self.category.getDocument(docKey).joinToIndex(word, documentEntry)
   
   def getWeightOf(self, word, field = "description"):
      word = {"title": "t_" + word, "description": "d_" + word}[field]
      if self.inVocabulary(word):
         return self.vocabulary[word].getWeight()
      return 0.0
   def getUniqueWeightOf(self, word, field = "description"):
      word = {"title": "t_" + word, "description": "d_" + word}[field]
      if self.inVocabulary(word):
         return self.vocabulary[word].getUniqueWeight()
      return 0.0
   def getTFIDFWeightOf(self, word, field = "description", document):
      word = {"title": "t_" + word, "description": "d_" + word}[field]
      if self.inVocabulary(word):
         return self.vocabulary[word].getTFIDF(document)
      return 0.0
   # Wrappers to operate on data in Index -> TermEntry
   def getDocumentListFor(self, word):
      if not self.inVocabulary(word):
         return {}
      return self.vocabulary[word].getDocumentList()
   def numDocumentsContaining(self, word):
      return len(self.getDocumentList(word))
   def isInDocument(self, word, document):
      if not self.inVocabulary(word):
         return False
      return self.vocabulary[word].isDocumentPresent(document)
   #def getCategoryList(self, word):
   #   if not self.inVocabulary(word):
   #      return {}
   #   return self.vocabulary[word].getCategoryList()
   #def numCategoriesContaining(self, word):
   #   return len(self.getCategoryList(word))
   #def isInCategory(self, word, category):
   #   if not self.inVocabulary(word):
   #      return False
   #   return self.vocabulary[word].isCategoryPresent(category)
   
   # Wrappers to operate on data in Index -> TermEntry -> DocumentEntry
   def getDocumentCount(self, word, document):
      if not self.isInDocument(word, document):
         return 0
      return self.vocabulary[word].getDocumentCount(document)
      
   # Wrappers to operate on data in Index -> TermEntry -> CategoryEntry
   #def getCategoryCount(self, word, category):
   #   if not self.isInCategory(word, category):
   #      return 0
   #   return self.vocabulary[word].getCategoryCount(category)
            
   
   
   
   
   
   #def getMI(self, word, category):
   #   if self.vocabulary.get(word, False):
   #      return self.vocabulary[word].miValues[category.getCode()]
   #   return 0.0
   #def getX2(self, word, category):
   #   if self.vocabulary.get(word, False):
   #      return self.vocabulary[word].x2Values[category.getCode()]
   #   return 0.0
   #def computeMI(self, word, category):
   #   N  = float(self.getNumDocs())
   #   T  = float(self.vocabulary[word].getNumDocs())
   #   C  = float(category.getNumDocs())
   #   categoryEntry = self.vocabulary[word].getCategoryList().get(category, False)
   #   if not categoryEntry:
   #      TC = 0.0
   #   else:
   #      TC = float(categoryEntry.getNumDocs())
   #   
   #   NXX = N + 1.0
   #   N00 = N - T - C + TC + 1.0
   #   N01 = C - TC + 1.0
   #   N10 = T - TC + 1.0
   #   N11 = TC + 1.0
   #   NX0 = N - C + 1.0
   #   NX1 = C + 1.0
   #   N0X = N - T + 1.0
   #   N1X = T + 1.0
   #   
   #   mi  = (N11/NXX)*math.log((NXX*N11)/(N1X*NX1)) 
   #   mi += (N01/NXX)*math.log((NXX*N01)/(N0X*NX1)) 
   #   mi += (N10/NXX)*math.log((NXX*N10)/(N1X*NX0)) 
   #   mi += (N00/NXX)*math.log((NXX*N00)/(N0X*NX0))
   #   
   #   x2 = (N00 + N01 + N10 + N11)
   #   x2 *= (N11*N00 - N10*N10)
   #   x2 *= (N11*N00 - N10*N10)
   #   x2 /= (N11 + N01)
   #   x2 /= (N11 + N10)
   #   x2 /= (N10 + N00)
   #   x2 /= (N01 + N00)
   #   self.vocabulary[word].miValues[category.getCode()] = mi
   #   self.vocabulary[word].x2Values[category.getCode()] = x2
      
      
   
