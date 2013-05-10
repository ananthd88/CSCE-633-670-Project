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
      self.documents = {}
      
   def getCount(self):
      return self.count
   def incrementCount(self):
      self.count += 1
   def addDocument(self, document):
      if document not in self.documents:
         self.documents[document] = 0
      self.documents[document] += 1
   def hasDocument(self, document):
      return document in self.documents
   def getNumDocuments(self):
      return len(self.documents)
      
class TermEntry:                 # Index -> Dictionary of Terms -> TermEntry
   def __init__(self):
      self.documents = {}        # Hashtable of DocumentEntries
      self.groups = {}       # Hashtable of GroupEntries
      self.totalCount   = 0      # Count of total number of tokens of this term in all the documents in the collection
      self.weight = 0.0
      self.uniqueWeight = 0.0
      self.miValues = []         # List of Mutual Information (MI) values for this term in each category
                                 # indexed by the category's code
      self.x2Values = []         # List of X2 values for this term in each category
                                 # indexed by the category's code

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
   def getGroupEntry(self, group):
      return self.groups.get(group.getKey(), False)
      
   # MI and X2 values
   def initializeMIValues(self, numGroups):
      self.miValues = [0.0] * numGroups
   def initializeX2Values(self, numGroups):
      self.x2Values = [0.0] * numGroups
   
class Index:                     # Index for a collection
   def __init__(self, category, indexWithMarkers = False):
      self.vocabulary = {}       # Hashtable of terms pointing to a TermEntry
      self.numDocuments = 0           # Total number of docs indexed
      self.category = category
      self.firstVocabulary = {}
      self.importantWords = set()
      self.numTitleWords = 0
      self.numDescriptionWords = 0
      self.reverseIndexDone = False
      self.computedTFIDF = False
      self.computedWeights = False
      self.indexWithMarkers = False
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
      if len(word) == 0:
         return
      if not self.inVocabulary(word):
         self.vocabulary[word] = TermEntry()
         if word[0:2] == 't_':
            self.numTitleWords += 1
         elif word[0:2] == 'd_':
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
         groupEntry = termEntry.getGroupEntry(group)
         groupEntry.addDocument(document)
         G = group.getNumDocuments()
         TG = groupEntry.getNumDocuments()
         if G < TG:
            raw_input("G < TG for %s, %d" % (word, group.getKey()))
         
         termEntry.getGroupEntry(group).addDocument(document)
         group.incrementTotalTokenCount()
   def findImportantWords2(self, fraction):
      numImportantWords = self.getSizeOfVocabulary()/fraction
      array = []
      count = 0
      for key in sorted(self.vocabulary, key = lambda word: math.fabs(self.vocabulary[word].getUniqueWeight()), reverse=True):
         array.append(key)
         count += 1
         if count == numImportantWords:
            break
      self.importantWords = set(array)
      return array
   def findImportantWords(self, fraction):
      if self.indexWithMarkers:
         numTitleWords, numDescriptionWords = self.numTitleWords/fraction, self.numDescriptionWords/fraction
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
         self.importantWords = set(array)
         return array
      else:
         return findImportantWords2(fraction)
   def getImportantWords(self):
      return self.importantWords
   def isImportantFeature(self, feature):
      return feature in self.importantWords


 
   # Document Processing
   def processDocument2(self, document):
      self.incrementNumDocuments()
      group = document.getGroup()
      if self.indexWithMarkers:
         document.setIndexWithMarkers()
      else:
         document.unsetIndexWithMarkers()
      bagOfWords = document.getBagOfWords2("all")
      for word in bagOfWords:
         self.addToken(word, document, group)
   # TODO: Deprecated code, to be removed
   def processDocument(self, document):
      self.incrementNumDocuments()
      group = document.getGroup()
      spellchecker = Spell_Corrector.SpellCorrector()
      spellchecker.setDictionary(self.firstVocabulary)
      # Title
      bagOfWords = document.getBagOfWords("title")
      title = []
      for word in bagOfWords:
         if self.getCountInFirstVocabulary(word) == 1:
            result = self.wordSplitter(word)
            if result:
               word1, word2 = result
               if word1:   
                  title.append(word1)
                  word1 = "t_" + word1
                  self.addToken(word1, document, group)
               if word2:
                  title.append(word2)
                  word2 = "t_" + word2 
                  self.addToken(word2, document, group)
            else:
               correct_word = spellchecker.correct(word)
               if word != correct_word:
                  title.append(correct_word)
                  correct_word = "t_" + correct_word
                  self.addToken(correct_word, document, group)
         else:
            title.append(word)
            word = "t_" + word
            self.addToken(word, document, group)
      document.setTitle(title)
      
      # Description
      bagOfWords = document.getBagOfWords("description")
      description = []
      for word in bagOfWords:
         if self.getCountInFirstVocabulary(word) == 1:
            result = self.wordSplitter(word)
            if result:
               word1, word2 = result
               if word1:   
                  description.append(word1)
                  word1 = "d_" + word1
                  self.addToken(word1, document, group)
               if word2:
                  description.append(word2)
                  word2 = "d_" + word2 
                  self.addToken(word2, document, group)
            else:
               correct_word = spellchecker.correct(word)
               if word != correct_word:
                  description.append(correct_word)
                  correct_word = "d_" + correct_word
                  self.addToken(correct_word, document, group)   
         else:
            description.append(word)
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

   def computeWeights(self, pctChange, words, wordcloud):
      delta = pctChange/len(words)
      for word in words:
         if not wordcloud.get(word, False):
            #                  +ve count  -ve count  +ve mean delta -ve mean delta
            wordcloud[word] = [1        , 1        , 0.0           , 0.0]
         if delta > 0.0:
            wordcloud[word][0] += 1
            wordcloud[word][2] = wordcloud[word][2] + (delta - wordcloud[word][2])/float(wordcloud[word][0])
         elif delta < 0.0:
            wordcloud[word][1] += 1
            wordcloud[word][3] = wordcloud[word][3] + (delta - wordcloud[word][3])/float(wordcloud[word][1])
            
   def computeAllWeights(self):
      wordcloud = {}
      wordcloudUnique = {}
      # Compute Weights and Unique Weights
      for docKey in self.category.getDocuments():
         document = self.category.getDocument(docKey)
         pctChange = (document.getSalary()/self.category.getMean() - 1.0) * 100
         # Title
         words = document.getBagOfWords2("title")
         self.computeWeights(pctChange, words, wordcloud)
         words = set(words)
         self.computeWeights(pctChange, words, wordcloudUnique)
         
         # Description
         words = document.getBagOfWords2("description")
         self.computeWeights(pctChange, words, wordcloud)
         words = set(words)
         self.computeWeights(pctChange, words, wordcloudUnique)
         
         # Location
         words = document.getBagOfWords2("location")
         self.computeWeights(pctChange, words, wordcloud)
         words = set(words)
         self.computeWeights(pctChange, words, wordcloudUnique)
         
         # Company
         words = document.getBagOfWords2("company")
         self.computeWeights(pctChange, words, wordcloud)
         words = set(words)
         self.computeWeights(pctChange, words, wordcloudUnique)
         
      for word in self.vocabulary.keys():
         weight = math.log(wordcloud[word][0], 10) * wordcloud[word][2] + math.log(wordcloud[word][1], 10) * wordcloud[word][3]
         #uniqueWeight = math.log(wordcloudUnique[word][0], 10) * wordcloudUnique[word][2] + math.log(wordcloudUnique[word][1], 10) * wordcloudUnique[word][3]
         uniqueWeight = math.log(wordcloud[word][0], 10) * wordcloud[word][2] + math.log(wordcloud[word][1], 10) * wordcloud[word][3]
         self.vocabulary[word].setWeight(weight)
         self.vocabulary[word].setUniqueWeight(uniqueWeight)
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
   
   def computeAllMI(self):
      # Compute all MI and X2
      self.initializeAllMI(self.category.getNumGroups())
      for word in self.vocabulary:
         for group in self.category.getGroups():
            self.computeMI(word, group)

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
   def getWeightOf(self, word):
      if self.inVocabulary(word):
         return self.vocabulary[word].getWeight()
      return 0.0
   def getUniqueWeightOf(self, word):
      if self.inVocabulary(word):
         return self.vocabulary[word].getUniqueWeight()
      return 0.0
   def getTFIDFWeightOf(self, word):
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


   
   # MI and X2 values
   def initializeAllMI(self, numGroups):
      for word in self.vocabulary:
         self.vocabulary[word].initializeMIValues(numGroups)
         self.vocabulary[word].initializeX2Values(numGroups)
   def getMI(self, word, group):
      if self.inVocabulary(word):
         return self.vocabulary[word].miValues[group.getKey()]
      return 0.0
   def getX2(self, word, group):
      if self.inVocabulary(word):
         return self.vocabulary[word].x2Values[group.getKey()]
      return 0.0
   def computeMI(self, word, group):
      N  = float(self.getNumDocuments())
      T  = float(self.vocabulary[word].getNumDocuments())
      G  = float(group.getNumDocuments())
      groupEntry = self.vocabulary[word].getGroupEntry(group)
      if groupEntry:
         TG = float(groupEntry.getNumDocuments())
      else:
         TG = 0.0
      NXX = N + 1.0
      N00 = N - T - G + TG + 1.0
      N01 = G - TG + 1.0
      N10 = T - TG + 1.0
      N11 = TG + 1.0
      NX0 = N - G + 1.0
      NX1 = G + 1.0
      N0X = N - T + 1.0
      N1X = T + 1.0
      #print word + "-" + str(group.getKey()) + "|" + str(G) + "|" + str(TG) + "|" + str(NXX) + "-" + str(N00) + "-" + str(N01) + "-" + str(N10) + "-" + str(N11) + "-" + str(NX0) + "-" + str(NX1) + "-" + str(N0X) + "-" + str(N1X)
      mi  = (N11/NXX)*math.log((NXX*N11)/(N1X*NX1)) 
      mi += (N01/NXX)*math.log((NXX*N01)/(N0X*NX1)) 
      mi += (N10/NXX)*math.log((NXX*N10)/(N1X*NX0)) 
      mi += (N00/NXX)*math.log((NXX*N00)/(N0X*NX0))
      
      x2 = (N00 + N01 + N10 + N11)
      x2 *= (N11*N00 - N10*N10)
      x2 *= (N11*N00 - N10*N10)
      x2 /= (N11 + N01)
      x2 /= (N11 + N10)
      x2 /= (N10 + N00)
      x2 /= (N01 + N00)
      self.vocabulary[word].miValues[group.getKey()] = mi
      self.vocabulary[word].x2Values[group.getKey()] = x2
