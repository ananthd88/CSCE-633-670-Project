CSCE-633-670-Project
====================

Term project for CSCE 633 &amp; CSCE 670


How to execute the program:
To get help executing the program:
./Main.py -h      OR       ./Main.py --help

Command line interface - Main.py
usage: ./Main.py [-h] [--version] [--file <csv file>] [-c <classifier>]
                 [-r <regressor>] [--features <number of features to be used>]
                 [--category <category>]

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --file <csv file>     File to read in the training and test sets
  -c <classifier>       Classifier to be used, could be one of "NBC" or "SVM"
  -r <regressor>        Regressor to be used, could be one of "KNR", "RFR" or
                        "SVR"
  --features <number of features to be used>
                        Number of features to be used
  --category <category>
                        Category of jobs


Eg.
./Main.py --file Train_preprocessed.csv -c "NBC" -r "KNR" --features 1000
./Main.py --file Train_preprocessed.csv -c "NBC" -r "KNR" --features 1000 --category "it jobs"
./Main.py --file Train_preprocessed.csv -r "KNR"  --category "it jobs"

GUI Interface - Demo.py
./Demo.py <Training & test combo .csv file>
You can edit the advertisement and see the effect of your changes when you predict the salary.

Packages required for installation:
wxPython - GUI for Python (http://www.wxpython.org/)
scikit-learn - Machine Learning in Python (http://scikit-learn.org/)


Training and Test File:
The Training and Test sets are read from a single .csv file.
You can download The original file (ADzuna's dataset from the Kaggle Competetion) from: https://www.dropbox.com/s/0088a9xr7qkubmx/Train_rev1.csv
You can download the preprocessed version of the file from: https://www.dropbox.com/s/0eiz2dg36rax1q3/Train_Test_Processed.csv
The program splits the file as 75% Training set and 25% Test set.

It is advised that you use the preprocessed file since the data has been cleaned, spelling errors have been corrected to a good extend, non-alphebetic symbols have been removed and unused fields (Cotract Type, Source Name, etc) have been removed. Also the preprocessed file is considerably smaller at ~335MB.
