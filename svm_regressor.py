import numpy as np
import math
import sys

from sklearn.externals import joblib
tr_inp_matrix = joblib.load('dataset_in.joblib')
tr_out_matrix = joblib.load('dataset_out.joblib')

test_inp_matrix = joblib.load('test_dataset_in.joblib')
test_out_matrix = joblib.load('test_dataset_out.joblib')


from sklearn.svm import SVR
tr_out_matrix = tr_out_matrix.tolist()
tr_out_list = []
for each_list in tr_out_matrix:
	tr_out_list.extend(each_list)

test_out_matrix = test_out_matrix.tolist()
test_out_list = []
for each_list in test_out_matrix:
	test_out_list.extend(each_list)

svr_lin = SVR(kernel='linear', C=1010101010)#,e = 0.1)
svr_lin.fit(tr_inp_matrix, tr_out_list)

#svr_rbf = SVR(kernel = 'rbf', C=1)
#svr_rbf.fit(tr_inp_matrix, tr_out_list)

out = svr_lin.predict(test_inp_matrix)
#out = svr_rbf.predict(test_inp_matrix)

error_mean = 0.0
for i in range(len(test_out_list)):
	error = math.fabs(out[i] - test_out_list[i])
	error_mean = error_mean + (error - error_mean)/(i+1)

print "Average mean error is :",error_mean
sys.exit(0)

