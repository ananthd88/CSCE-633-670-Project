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
      for prediction, truth in itertools.izip(predictions, truths):
         
         if prediction == truth:
            self.classes[prediction].incrementTP()
            sumTP += 1
         else:
            self.classes[prediction].incrementFP()
            self.classes[truth].incrementFN()
            sumFP += 1
            sumFN += 1
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
      self.resetMetrics()
      return results
      
class NaiveBayesClassifier(Classifier):
   def predict(self, document):
      numTrainDocs = float(self.trainingSet.getNumDocuments())
      sizeTrainVocabulary = self.trainingSet.getSizeOfVocabulary()
      maxLogProbability = None
      predictedClass = False
      for classKey in self.trainingSet.getClasses():
         #print "class = %d - %d/%d" % (classKey, self.trainingSet.getNumDocumentsInClass(classKey), numTrainDocs)
         logProbability  = 0.0
         # P(c) = (No. of docs in c)/(No. of training docs)
         logProbability += math.log(float(self.trainingSet.getNumDocumentsInClass(classKey)), 2) - math.log(numTrainDocs, 2) 
         features = document.getFeatures()
         bagOfWords = document.getBagOfWords("all")
         for feature in features:
            # Add one smoothing
            #print feature + " - " + str(self.trainingSet.getNumTokensInClass(feature, classKey)) + " | ",
            logProbability += math.log(float(self.trainingSet.getNumTokensInClass(feature, classKey)) + 1.0, 2)
         logProbability -= float(len(features)) * math.log(float((self.trainingSet.getTotalTokens(classKey) + sizeTrainVocabulary)), 2)
         if maxLogProbability < logProbability:
            maxLogProbability = logProbability
            #if predictedClass:
            #   print "Changing prediction %d -> %d" % (predictedClass, classKey)
            #else:
            #   print "prediction = %d" % (classKey)
            predictedClass = classKey
            
         # If the log of probabilities for two classes are equal
         elif maxLogProbability == logProbability:
            # Select the class which has more documents assigned to it
            # which would imply a greater value for P(c), 
            # since P(c) = (Num of docs classified as c)/(Num of docs in collection)
            if self.trainingSet.getNumDocumentsInClass(predictedClass) < self.trainingSet.getNumDocumentsInClass(classKey):
               #if predictedClass:
               #   print "$Changing prediction %d -> %d" % (predictedClass, classKey)
               #else:
               #   print "$prediction = %d" % (classKey)
               predictedClass = classKey
      return predictedClass
      
