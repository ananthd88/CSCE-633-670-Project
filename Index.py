import math
import Spell_Corrector
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

   # Basic accessor methods
   def getTotalCount(self):
      return self.totalCount
   def incrementTotalCount(self):
      self.totalCount += 1      
   def getWeight(self):
      return self.weight
   def getUniqueWeight(self):
      return self.uniqueWeight
   def setWeight(self, weight):
      self.weight = float(weight)
   def setUniqueWeight(self, weight):
      self.uniqueWeight = float(weight)
   
   # Methods operating on the documentList
   def getNumDocuments(self):
      return len(self.documents)
   def getDocumentList(self):
      return self.documents
   
   # Methods operating on the groupList
   def getGroupList(self):
      return self.groups
   
   # Methods operating on a particular documentEntry
   def hasDocumentEntry(self, document):
      return document.getKey() in self.documents
   def addDocument(self, document):
      if self.hasDocumentEntry(document):         
         return False
      self.documents[document.getKey()] = DocumentEntry()
      return True
   def getDocumentEntryCount(self, document):        # Get count of tokens of this term in a given document
      if self.hasDocumentEntry(document):
         return self.documents[document.getKey()].getCount()
      return 0
   def incrementDocumentEntryCount(self, document):  # Increment the count of tokens of this term in a given document
      if self.hasDocumentEntry(document):
         self.documents[document.getKey()].incrementCount()
         return True
      return False
   def getTFIDF(self, document):                # Get the TFIDF of term for a particular document
      if self.hasDocumentEntry(document):
         return self.documents[document.getKey()].getTFIDF()
      return 0.0
   def setTFIDF(self, document, tfidf):         # Set the TFIDF of term for a particular document
      if self.hasDocumentEntry(document):
         self.documents[document.getKey()].setTFIDF(tfidf)
         return True
      return False
   
      
   # Methods operating on a particular groupEntry
   def addGroup(self, group):
      if self.hasGroupEntry(group):
         return False
      self.groups[group.getKey()] = GroupEntry()
   def hasGroupEntry(self, group):
      return group.getKey() in self.groups
   def getGroupEntryCount(self, group):
      if self.hasGroupEntry(group):
         return self.groups[group.getKey()].getCount()
      return 0
   def incrementGroupEntryCount(self, group):
      if self.hasGroupEntry(group):
         self.groups[group.getKey()].incrementCount()
         return True
      return False      
   
      
class Index:                     # Index for a collection
   def __init__(self, category):
      self.vocabulary = {}       # Hashtable of terms pointing to a TermEntry
      self.numDocuments = 0           # Total number of docs indexed
      self.category = category
      self.firstVocabulary = {}
      self.importantWords = {}
      self.numTitleWords = 0
      self.numDescriptionWords = 0
      self.reverseIndexDone = False
      self.computedTFIDF = False
      self.computedWeights = False
      self.stopwords = ["", ".", "a", "an", "and", "are", "as", "at", "be", "for", "have", "if", "in", "is", "of", "on", "or", "our", "s", "the", "this", "to", "we", "will", "with", "work", "you", "your"] 
   

      
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
   def inFirstVocabulary(self, word):
      return word in self.firstVocabulary
   def addToFirstVocabulary(self, word):
      if not self.inFirstVocabulary(word):
         self.firstVocabulary[word] = 0
      self.firstVocabulary[word] += 1
   def getCountInFirstVocabulary(self, word):
      if not self.inFirstVocabulary(word):
         return 0
      return self.firstVocabulary[word]
   def addToken(self, word, document, group):
      # TODO: This is the place to increment total token count in category
      if not self.inVocabulary(word):
         self.vocabulary[word] = TermEntry()
         if word[0] == 't':
            self.numTitleWords += 1
         elif word[0] == 'd':
            self.numDescriptionWords += 1
      termEntry = self.vocabulary[word]
      termEntry.incrementTotalCount()
      if document:
         termEntry.addDocument(document) # Not added if already exists in list
         termEntry.incrementDocumentEntryCount(document)
      if group:
         if not termEntry.hasGroupEntry(group):
            termEntry.addGroup(group)
         termEntry.incrementGroupEntryCount(group)
         group.incrementTotalTokenCount()
   def findImportantWords(self, numTitleWords, numDescriptionWords):
      array = []
      titleCount = 0
      descriptionCount = 0
      for key in sorted(self.vocabulary, key = lambda word: math.fabs(self.vocabulary[word].getUniqueWeight()), reverse=True):
         if key[0] == 't' and titleCount < numTitleWords:
            array.append(key)
            titleCount += 1
         elif key[0] == 'd' and descriptionCount < numDescriptionWords:
            array.append(key)
            descriptionCount += 1
         if titleCount == numTitleWords and descriptionCount == numDescriptionWords:
            break
      return array


 
   # Document Processing
   def processDocument(self, document):
      self.incrementNumDocuments()
      group = document.getGroup()
      spellchecker = Spell_Corrector.SpellCorrector()
      spellchecker.setDictionary(self.firstVocabulary)
      # Title
      bagOfWords = document.getBagOfWords("title")
      title = ""
      for word in bagOfWords:
         if self.getCountInFirstVocabulary(word) == 1:
	    result = self.wordSplitter(word)
            if result:
               word1, word2 = result
	       if word1:	
                  title += " " + word1
	          word1 = "t_" + word1
		  self.addToken(word1, document, group)
	       if word2:
		  title += " " + word2
                  word2 = "t_" + word2 
                  self.addToken(word2, document, group)
	    else:
	       print word
	       correct_word = spellchecker.correct(word)
	       print correct_word
	       if word != correct_word:
		  title += " " + correct_word
		  correct_word = "t_" + correct_word
	          self.addToken(correct_word, document, group)

         else:
	    title += " " + word
            word = "t_" + word
            self.addToken(word, document, group)            
      document.setTitle(title)      
      
      # Description
      bagOfWords = document.getBagOfWords("description")
      description = ""
      for word in bagOfWords:
         if self.getCountInFirstVocabulary(word) == 1:
            result = self.wordSplitter(word)
            if result:
               word1, word2 = result
	       if word1:	
                  description += " " + word1
	          word1 = "d_" + word1
		  self.addToken(word1, document, group)
	       if word2:
		  description += " " + word2
                  word2 = "d_" + word2 
                  self.addToken(word2, document, group)
	    else:
	       print "Desc :: ",word
	       correct_word = spellchecker.correct(word)
	       print "Desc :: ",correct_word
	       if word != correct_word:
		  description += " " + correct_word
		  correct_word = "d_" + correct_word
	          self.addToken(correct_word, document, group)	
         else:
            description += " " + word
            word = "d_" + word
            self.addToken(word, document, group)            
      document.setDescription(description)
   
   def wordSplitter(self, word):
      length = len(word)
      for i in range(1, length):
         word1    = word[:i]
         word2    = word[i:]
         if self.getCountInFirstVocabulary(word1) > 1 and self.getCountInFirstVocabulary(word2) > 1:
            return [word1, word2]
	 elif word1 in self.stopwords and self.getCountInFirstVocabulary(word2) > 1:
	    return [False, word2]
	 elif self.getCountInFirstVocabulary(word1) > 1 and word2 in self.stopwords:
	    return [word1, False]
  	 elif word1 in self.stopwords and word2 in self.stopwords:
	    return [False,False]
      return False

   def computeAllWeights(self):
      # Compute Weights and Unique Weights
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
      for word in self.vocabulary.keys():
         self.vocabulary[word].setWeight(wordcloud[word][1])
         self.vocabulary[word].setUniqueWeight(wordcloudUnique[word][1])
      self.computedWeights = True
         
   def computeAllTFIDF(self):
      # Compute TFIDF
      numDocs = self.getNumDocuments()
      logNumDocs = math.log(float(numDocs), 2)
      vocabulary = self.getVocabulary()
      for word in vocabulary.keys():
         documentList = self.getDocumentListFor(word)
         df = len(documentList)
         logdf = logNumDocs - math.log(float(df), 2)
         for (docKey, documentEntry) in documentList.items():
            tf = documentEntry.getCount()
            logtf = 1.0 + math.log(float(tf), 2)
            tfidf = logtf * logdf
            documentEntry.setTFIDF(tfidf)
            self.category.getDocument(docKey).joinToIndex(word, documentEntry)
      self.computedTFIDF = True
   
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
   def getTFIDFWeightOf(self, word, document, field = "description"):
      word = {"title": "t_" + word, "description": "d_" + word}[field]
      if self.inVocabulary(word):
         return self.vocabulary[word].getTFIDF(document)
      return 0.0
   def getDocumentCount(self, word, document):
      if not self.isInDocument(word, document):
         return 0
      return self.vocabulary[word].getDocumentCount(document)
   
   # TODO: To be re-written
   # Word should have t_ or d_ markers
   def getNumTokensInGroup(self, word, group):
      if not self.inVocabulary(word):
         return 0
      return self.vocabulary[word].getGroupEntryCount(group)


   
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
      
      
   
