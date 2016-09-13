# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from sklearn import preprocessing
from helpers.models import fit_model
from sklearn.cross_validation import train_test_split


# set random state for camparability
random_state = np.random.RandomState(0)

# read data
context = pd.read_csv('data/muestra_variables.csv')
# select variable columns
cols_select = context.columns[6:]
variables = context.ix[:,cols_select]
for c in ['no_se','uname','content','cve_mza']:
    del variables[c]

# reclass intervalo as numerical
def intervalo_to_numbers(x):
    equiv = {'sun':0,'mon':1,'tue':2,'wed':3,'thu':4,'fri':5,'sat':6,'sun':7}
    interval = 0.16666*int(x.split('.')[1])
    day = x.split('.')[0]
    valor = equiv[day] + interval
    return valor

reclass = variables['intervalo'].apply(intervalo_to_numbers)

# drop old 'intervalo' column and replace it with numerical values
del variables['intervalo']
variables = variables.join(reclass,how='inner')

# Get dataframe as matrix and scale it:
data = variables.as_matrix()
data_Y = data[:,0]
data_X = data[:,1:]
# Get only positive and negative classes, first with original data
X, Y = data_X[data_Y != 2], data_Y[data_Y != 2]
X, Y = X[Y != 4], Y[Y != 4]
# recode class:
Y[Y==3] = 0
# Scale sample
scaled_X = preprocessing.scale(X)
# test and train split


param_grid = {'C': [1, 10, 100, 1000], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']}
clf = fit_model(scaled_X,Y,param_grid,'f1',6)
clf.best_score_
