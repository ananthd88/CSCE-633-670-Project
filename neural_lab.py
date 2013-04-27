import neurolab
import numpy as np
import math
import re
from sklearn.feature_extraction.text import CountVectorizer

class NeuralNetwork:

	def __init__(self):
		self.inp = np.ndarray		# np.linspace(-7, 7,20)
		self.target = np.ndarray	# y = np.sin(x) * 0.5
		self.neurons_per_layer = []
		self.inp_range = []
		self.net = neurolab.net
		self.inp_size = 0
	
	def create_Network(self, inp_range, neurons_per_layer = [], transf = None):
		self.inp_range = inp_range if inp_range is not None else self.inp_range
		self.neurons_per_layer = neurons_per_layer
		self.net = neurolab.net.newff(self.inp_range,neurons_per_layer,transf)
		return(self.net)  
		 	

	def train_Network(self, epochs=500, show=50, goal=0.1):
		error = self.net.train(self.inp,self.target,epochs=500,show=100,goal=0.1)
		

	def setTrainingInputforNN(self, collection = {}, sel_words = []):
		list_of_strings = []
		list_of_salary = []
		count = 0
		sel_words_set = set(sel_words)
		sel_words_list = list(sel_words_set)
		print "Start input calculation"
		for document in collection:
			count += 1
			title = document.getTitle()
			description = document.getDescription()
			salary = (int)(document.getSalaryNorm())
			words = re.split(' ', title) + re.split(' ', description)
			#words = [x for x in words if x in sel_words]
			wordsUnique = set(words)
			wordsUnique = (wordsUnique & sel_words_set)
			words = [x for x in words if x in wordsUnique]
			documentString = ' '.join(words)
			list_of_strings.append(documentString)
			list_of_salary.append(salary)
		
			if not (count%15000):
				print count
				break
			
			
			
		vectorizer = CountVectorizer(vocabulary = sel_words, min_df = 1)	
		self.inp = vectorizer.fit_transform(list_of_strings)
		from sklearn.externals import joblib
		joblib.dump(self.inp.tocsr(), 'dataset_in.joblib')
		
		self.inp_size = len(list_of_strings)
		output = np.array(list_of_salary)
		self.target = output.reshape(len(list_of_strings),1)
		joblib.dump(self.target,'dataset_out.joblib')
		
		print self.inp
		raw_input("Press a key")
		print self.target
		raw_input("Press another key")
		return([self.inp,self.target])


	def setTestInputforNN(self, collection = {}, sel_words = []):
		list_of_strings = []
		list_of_salary = []
		count = 0
		sel_words_set = set(sel_words)
		sel_words_list = list(sel_words_set)
		print "Start input calculation"
		for document in collection:
			count += 1
			title = document.getTitle()
			description = document.getDescription()
			salary = (int)(document.getSalaryNorm())
			words = re.split(' ', title) + re.split(' ', description)
			#words = [x for x in words if x in sel_words]
			wordsUnique = set(words)
			wordsUnique = (wordsUnique & sel_words_set)
			words = [x for x in words if x in wordsUnique]
			documentString = ' '.join(words)
			list_of_strings.append(documentString)
			list_of_salary.append(salary)
		
			if not (count%15000):
				print count
				break
			
			
			
		vectorizer = CountVectorizer(vocabulary = sel_words,min_df = 1)	
		self.inp = vectorizer.fit_transform(list_of_strings)
		from sklearn.externals import joblib
		joblib.dump(self.inp.tocsr(), 'test_dataset_in.joblib')
		
		self.inp_size = len(list_of_strings)
		output = np.array(list_of_salary)
		self.target = output.reshape(len(list_of_strings),1)
		joblib.dump(self.target,'test_dataset_out.joblib')
		
		print self.inp
		raw_input("Press a key")
		print self.target
		raw_input("Press another key")
		return([self.inp,self.target])


			
	def setInputRange(self,X = np.ndarray):
	#	if X.size == 0:
		X = self.inp# if X is not None else X
		#max_input = X.todense().max(axis = 0)
		#min_input = X.todense().min(axis = 0)
		max_input = np.array([50]*self.inp_size)
		min_input = np.array([0]*self.inp_size)
		max_input = max_input.reshape(max_input.shape[0],1)
		min_input = min_input.reshape(min_input.shape[0],1)
		range_matrix = np.concatenate((max_input, min_input), axis=1)
		range_list = range_matrix.tolist()
		#print range_list
		
		self.inp_range = range_list
		return range_list
			
	

