#!/usr/bin/python

import Collection
import Document
import Timer
import Classifier
import csv
import sys
import math
import re
from sklearn import svm
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestRegressor
import gc

# Just a comment
      
def main():
   timer0 = Timer.Timer("Entire program", 0, 0)
   gc.enable()
   inputfile = open(sys.argv[1], 'rt')
   trainSet = Collection.Collection("Training")
   testSet = Collection.Collection("Testing")
   timer = Timer.Timer("Processing csv file", 0, 0)
   try:
      reader = csv.DictReader(inputfile)
      count = 0
      for row in reader:
         count += 1
         #if count % 10000 == 0:
         #   print "%d-th document" % (count)         
         cat = row["Category"].lower()
         if cat != "legal jobs":
            continue         
         # TODO: Remove restriction (read only every 100th document)
         if count % 4 == 0:
            document = testSet.addDocument(row)
         else:
            document = trainSet.addDocument(row)
   finally:
      inputfile.close()
      timer.stop()
   
   print "Training set"
   for categoryKey, category in trainSet.getCategories().items():
      name = category.getName()
      mean = category.getMean()
      stdD = category.getStdDeviation()
      numD = category.getNumDocuments()
      print "Stats for category: %s" % (name)
      print "\tNum Docs                = %d" % (numD)
      print "\tMean Salary             = %f" % (mean)
      print "\tStd Deviation of Salary = %f" % (stdD)
   print
   print "Test set"
   for categoryKey, category in testSet.getCategories().items():
      name = category.getName()
      numD = category.getNumDocuments()
      print "%s : %d ads" % (name, numD)
   
   timer.start("Creating groups and assigning documents", 0, 0)
   trainSet.createGroups()
   trainSet.assignGroups()
   timer.stop()
   
   timer.start("Processing documents, creating reverse index", 0, 0)
   trainSet.processDocuments()
   timer.stop()

   timer.start("Computing Weights", 0, 0)
   trainSet.computeAllWeights()
   timer.stop()
   
   #timer = Timer.Timer("Computing TFIDF", 0, 0)
   #rainSet.computeAllTFIDF()
   #timer.stop()
   
   timer = Timer.Timer("Computing MI", 0, 0)
   trainSet.computeAllMI()
   timer.stop()
   
   #timer = Timer.Timer("Selecting important words", 0, 0)
   #trainSet.findImportantWords(2)
   #timer.stop()
   
   categoryTrain = trainSet.getCategory(1, False)
   categoryTest = testSet.getCategory(1, False)
      
   
   meanError = 0.0
   meanErrorGroup = 0.0
   count = 0.0
   countCorrect = 0
   #XY = categoryTrain.getXY(None)
   #X = XY["X"]
   #Y = XY["Y"]
   classifyingAlgo = "NB"
   if classifyingAlgo == "SVM":
      timer.start("SVM Learning", 0, 0)
      lin_clf = svm.LinearSVC(C = 5.0, dual = True, verbose = 2)
      vectorizer = CountVectorizer(vocabulary = categoryTrain.getVocabulary().keys(), min_df = 1)
      strings = []
      Y = []
      for docKey in categoryTrain.getDocuments():
         document = categoryTrain.getDocument(docKey)
         strings.append(" ".join(document.getBagOfWords2("all")))
         Y.append(document.getGroup().getKey())
      X = vectorizer.fit_transform(strings)
      lin_clf.fit(X, Y)
      timer.stop()
      timer.start("SVM Classification", 0, 0)
      for docKey in categoryTest.getDocuments():
         document = categoryTest.getDocument(docKey)
         strings.append(" ".join(document.getBagOfWords2("all")))
      Z = vectorizer.fit_transform(strings)
      array = lin_clf.predict(Z)
   elif classifyingAlgo == "NB":
      timer.start("NB Learning", 0, 0)
      nb = Classifier.NaiveBayesClassifier(categoryTrain)
      timer.stop()
      timer.start("NB Classification", numD)
   
   count0 = 0
   countneg = 0
   countpos = 0
   meanneg = 0.0
   meanpos = 0.0
   
   milimits = {}
   predictors = {}
   importantWords = {}
   vectorizers = {}
   for docKey in categoryTest.getDocuments():
      timer.tick()
      count += 1.0
      document = categoryTest.getDocument(docKey)
      if classifyingAlgo == "SVM":
         classification = array[count0]
      elif classifyingAlgo == "NB":
         classification = nb.predict(document)
      predictedGroup = categoryTrain.getGroup(classification)
      
      # Select the top 1000 important words for this group
      if not milimits.get(classification, False):
         countmi = 0
         words = []
         for key in sorted(categoryTrain.getVocabulary(), key = lambda word: categoryTrain.getMI(word, predictedGroup), reverse=True):
            words.append(key)
            countmi += 1
            if countmi == 3000:
               milimits[classification] = categoryTrain.getMI(key, predictedGroup)
               importantWords[classification] = words
               break
         # Predictors
         randForest = RandomForestRegressor()
         vectorizer = CountVectorizer(vocabulary = importantWords[classification], min_df = 1)
         strings = []
         Y = []
         for docKey in predictedGroup.getDocuments():
            doc = categoryTrain.getDocument(docKey)
            strings.append(" ".join(doc.getBagOfWords2("all")))
            Y.append(doc.getSalary())
         X = vectorizer.fit_transform(strings).toarray()
         randForest.fit(X, Y)
         predictors[classification] = randForest
         vectorizers[classification] = vectorizer
      
      
      
      count0 += 1
      strings = []
      strings.append(" ".join(document.getBagOfWords2("all")))
      Z = vectorizers[classification].fit_transform(strings).toarray()
      result = predictors[classification].predict(Z)
      
      actualGroup = categoryTrain.determineGroup(document)
      meanErrorGroup = meanErrorGroup + (abs(classification - actualGroup) - meanErrorGroup)/count
      predictedSalary = result[0]
      #predictedSalary = categoryTrain.getGroup(classification).getMean()
      #stdDeviation = categoryTrain.getGroup(classification).getStdDeviation()
      #predictionMI = 0.0
      #predictionWeight = 0.0
      #redictionUniqueWeight = 0.0
      
      #for word in set(document.getBagOfWords2("all")):
      #   mi = categoryTrain.getMI(word, predictedGroup)
      #   if mi < milimits[classification]:
      #      continue
      #   predictionWeight += categoryTrain.getUniqueWeightOf(word) * 5
      #   predictionMI += mi
      #for word in document.getBagOfWords2("all"):
      #   predictionWeight += categoryTrain.getWeightOf(word)
      #   predictionMI += categoryTrain.getMI(word, predictedGroup)
      #prediction = predictionWeight #- float(int(predictionWeight/math.fabs(predictionWeight))) * predictionMI # * predictionMI# * 10.0
      #predictedSalary *= (1 + prediction/100.0)
      #predictedSalary += (prediction/100.0) * stdDeviation
      actualSalary = document.getSalary()
      meanError += (math.fabs(predictedSalary - actualSalary) - meanError) / count
      if predictedSalary > actualSalary:
         countpos += 1
         meanpos += (math.fabs(predictedSalary - actualSalary) - meanpos) / countpos
      elif predictedSalary < actualSalary:
         countneg += 1
         meanneg += (math.fabs(predictedSalary - actualSalary) - meanneg) / countneg
      if math.fabs(predictedSalary - actualSalary) < 3000.0:
         countCorrect += 1
      #truth = document.getGroup().getKey()
      #print "%d (%d, %d)" % (document.getKey(), document.getGroup().getKey(), prediction)
      #predictions.append(prediction)
      #truths.append(truth)
   #metrics = nb.getMetrics(predictions, truths)
   #print "Precision  = %f" % (metrics["precision"])
   #print "Recall     = %f" % (metrics["recall"])
   #print "MAF1       = %f" % (metrics["maf1"])
   #print "RSS        = %d" % (metrics["rss"])
   #print "Avg error  = %f" % (metrics["meanerr"])
   print "Avg error in salary prediction = %f" % (meanError)
   print "(Num, Avg) Positive errors = (%d, %f)" % (countpos, meanpos)
   print "(Num, Avg) Negative errors = (%d, %f)" % (countneg, meanneg)
   print "Avg error in group prediction = %f" % (meanErrorGroup)
   print "Count of < 3000.0 error = %d" % (countCorrect)
   timer.stop()
   exit()
   #timer = Timer.Timer("Computing X, Y")
   #dictionary = category.getXY(importantWords)
   #timer.stop()
   
   #timer = Timer.Timer("Learning X, Y")
   #clf = category.mNBlearnXY(dictionary["X"], dictionary["Y"])
   #timer.stop()
   
   #raw_input("Press any key to go to the word prompt")
   print "Weights prompt"
   do = False
   while do:
      word = raw_input("Enter a word\n> ").lower()
      if word != "":
         words = re.split('_', word)
         if not categoryTrain.index.inVocabulary(word):
            print "%s was not found in the vocabulary" % (word)
            continue
         field = {"t": "title", "d": "description"}[words[0]]
         print "Word weight = %f" % (categoryTrain.getWeightOf(words[1], field))
         print "Unique word weight = %f" % (categoryTrain.getUniqueWeightOf(words[1], field))         
      else:
         do = False
   
   print "Document prompt (for Training set)"
   do = False
   while do:
      key = raw_input("Enter a doc id\n> ")
      if key != "":
         key = int(key)
         document = categoryTrain.getDocument(key)
         if document:
            print document.toString()
         else:
            print "Document not found in training set"
      else:
         do = False
   timer0.stop()
if __name__ == '__main__':
    main()
