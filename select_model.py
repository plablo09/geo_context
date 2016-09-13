# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from sklearn import preprocessing
#from sklearn.decomposition import PCA as sklearnPCA
from sklearn import svm
from sklearn.metrics import roc_curve, roc_auc_score, f1_score
from sklearn.metrics import make_scorer
from sklearn.cross_validation import StratifiedKFold
from sklearn.grid_search import GridSearchCV
#import matplotlib.pyplot as plt

# set random state for camparability
random_state = np.random.RandomState(0)

# read data
context = pd.read_csv('muestra_variables.csv')
# select variable columns
cols_select = context.columns[6:]
variables = context.ix[:,cols_select]
for c in ['no_se','uname','cont','lat','lon','geom','cve_mza']:
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
Y = data[:,0]
X = data[:,1:]
# Get only positive and negative classes, first with original data
X_bin, Y_bin = X[Y != 2], Y[Y != 2]
# recode class:
Y_bin[Y_bin==3] = 0

scaled_X = preprocessing.scale(X_bin)

# We want 6-fold stratified samples
cv = StratifiedKFold(Y_bin, n_folds=6)

# Setup a param grid
param_grid = {'C': [1, 10, 100, 1000], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']}

# instantiate svm model
svr = svm.SVC()

# Perform cross validation
f1_scorer = make_scorer(f1_score, pos_label=1.0)
clf = GridSearchCV(estimator=svr, param_grid = param_grid, n_jobs=-1,
                   scoring='roc_auc', cv = cv)
clf.fit(X_bin, Y_bin)
clf.best_score_
