from sklearn.feature_extraction.text import CountVectorizer
import itertools
import math

class Class:
   def __init__(self, key):
      self.key = key
      self.TP = 0
      self.TN = 0
      self.FP = 0
      self.FN = 0
      self.total = 0
   def __hash__(self):
      return hash(self.key)
   def __eq__(self, other):
      return self.key == other.key
   
   def resetMetrics(self):
      self.TP = 0
      self.TN = 0
      self.FP = 0
      self.FN = 0
   def incrementTP(self):
      self.TP += 1
   def incrementTF(self):
      self.TF += 1
   def incrementFP(self):
      self.FP += 1
   def incrementFN(self):
      self.FN += 1
      
   def getTP(self):
      return self.TP
   def getTN(self):
      return self.TN
   def getFP(self):
      return self.FP
   def getFN(self):
      return self.FN
      
class Classifier:
   def __init__(self, trainingSet):
      self.trainingSet = trainingSet
      self.features = []
      self.vectorizer = None
      self.minMI = 0.0
      numClasses = trainingSet.getNumClasses()
      self.classes = []
      for i in range(numClasses):
         self.classes.append(Class(i))
         
   
   def resetMetrics(self):
      for class0 in self.classes:
         class0.resetMetrics()
   def getMetrics(self, predictions, truths):
      # Expects two arrays of equal length with entries as class keys
      # Class keys should conform to the classes created in this classifier
      sumTP = 0
      sumFP = 0
      sumFN = 0
      RSS = 0
      meanerr = 0.0
      count = 0
      for prediction, truth in itertools.izip(predictions, truths):
         count += 1
         if prediction == truth:
            self.classes[prediction].incrementTP()
            sumTP += 1
         else:
            self.classes[prediction].incrementFP()
            self.classes[truth].incrementFN()
            sumFP += 1
            sumFN += 1
            RSS += (prediction - truth)**2
         meanerr += (abs(prediction - truth) - meanerr)/count
      precision = float(sumTP)/float(sumTP + sumFP)
      recall = float(sumTP)/float(sumTP + sumFN)
      if precision == 0.0 or recall == 0.0:
         maf1 = 0.0
      else:
         maf1 = 2 * precision * recall / (precision + recall)
      results = {}
      results["precision"] = precision
      results["recall"] = recall
      results["maf1"] = maf1
      results["rss"] = RSS
      results["meanerr"] = meanerr
      self.resetMetrics()
      return results
      
class NaiveBayesClassifier(Classifier):
   def findImportantFeatures(self, numFeatures = 500):
      return
      self.features = []
      count = 0
      for key in sorted(trainSet.getVocabulary(), key = lambda word: trainSet.getUniqueWeight(word), reverse=True):
         self.features.append(key)
         count += 1
         if countmi == numFeatures:
            break
   def train(self, numFeatures = 500):
      # TODO: Accumulate the minMI for each group and use it to select only the best n features of each class
      return
      self.findImportantfeatures(numFeatures)
      
   def classify(self, document):
      numTrainDocs = float(self.trainingSet.getNumDocuments())
      sizeTrainVocabulary = self.trainingSet.getSizeOfVocabulary()
      maxLogProbability = None
      predictedClass = False
      for classKey in self.trainingSet.getClasses():
         logProbability  = 0.0
         # P(c) = (No. of docs in c)/(No. of training docs)
         logProbability += math.log(float(self.trainingSet.getNumDocumentsInClass(classKey) + 1), 2)
         features = document.getFeatures()
         numFeaturesUsed = 0.0
         for feature in features:
            #mi = self.trainingSet.index.getMI(feature, self.trainingSet.getGroup(classKey))
            #if not self.trainingSet.isImportantFeature(feature):
            #   continue
            #if mi < 0.0001:
            #   continue
            numFeaturesUsed += 1.0
            # Add one smoothing
            #mi = self.trainingSet.index.getX2(feature, self.trainingSet.getGroup(classKey))
            logProbability += math.log(float(self.trainingSet.getNumTokensInClass(feature, classKey)) + 1.0, 2)# + math.log(mi + 1.0, 2)
         logProbability -= numFeaturesUsed * math.log(float((self.trainingSet.getTotalTokens(classKey) + sizeTrainVocabulary)), 2)
         if maxLogProbability < logProbability:
            maxLogProbability = logProbability
            predictedClass = classKey
            
         # If the log of probabilities for two classes are equal
         elif maxLogProbability == logProbability:
            # Select the class which has more documents assigned to it
            # which would imply a greater value for P(c), 
            # since P(c) = (Num of docs classified as c)/(Num of docs in collection)
            if self.trainingSet.getNumDocumentsInClass(predictedClass) < self.trainingSet.getNumDocumentsInClass(classKey):
               predictedClass = classKey
      return predictedClass
   def classifyAll(self, testSet):
      results = []
      for docKey in testSet.getDocuments():
         document = testSet.getDocument(docKey)
         results.append(self.classify(document))
      return results
class SVM(Classifier):
   def findImportantFeatures(self, numFeatures = 500):
      self.features = []
      count = 0
      for key in sorted(trainSet.getVocabulary(), key = lambda word: trainSet.getUniqueWeight(word), reverse=True):
         self.features.append(key)
         count += 1
         if countmi == numFeatures:
            break

   def train(self, numFeatures = 500):
      self.findImportantFeatures(numFeatures)
      self.classifier = svm.LinearSVC(C = 5.0, dual = True, verbose = 2)
      self.vectorizer = CountVectorizer(vocabulary = self.features, min_df = 1)
      strings = []
      Y = []
      for docKey in trainingSet.getDocuments():
         document = trainingSet.getDocument(docKey)
         strings.append(" ".join(document.getBagOfWords2("all")))
         Y.append(document.getGroup().getKey())
      X = self.vectorizer.fit_transform(strings)
      self.classifier.fit(X, Y)
   def classify(self, document):
      strings = []
      strings.append(" ".join(document.getBagOfWords2("all")))
      Z = self.vectorizer.fit_transform(strings)
      return self.classifer.predict(Z)[0]
   def classifyAll(self, testSet):
      for docKey in categoryTest.getDocuments():
         document = categoryTest.getDocument(docKey)
         strings.append(" ".join(document.getBagOfWords2("all")))
      Z = self.vectorizer.fit_transform(strings)
      return self.classifer.predict(Z)
