# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix
from helpers.models import fit_model
from helpers.helpers import make_binary, class_info, flip_labels

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

# Get dataframe and slit in predictor (X) and target (Y):
data = variables.as_matrix()
data_Y = data[:,0]
data_X = data[:,1:]
print("Initial label distribution")
class_info(data_Y)

# Eliminate data labeled 4 (don't know what that means)
data_X, data_Y = data_X[data_Y != 4], data_Y[data_Y != 4]

# Make two binarizations of data, one aggregating POS + Neu and one Neg + Neu
Y_pos_neu = make_binary(data_Y, set((1.,2.)))
Y_neg_neu = make_binary(data_Y, set((3.,2.)))
print("Label distribution after binarization")
print("Pos + Neu")
class_info(Y_pos_neu)
print()
print("Neg + Neu")
class_info(Y_neg_neu)
from sklearn.metrics import confusion_matrix
# test and train split for both binarizations
(X_train_pos_neu, X_test_pos_neu, 
Y_train_pos_neu, Y_test_pos_neu) = train_test_split(data_X, Y_pos_neu,
                                                    test_size=0.4,
                                                    random_state=random_state)

(X_train_neg_neu, X_test_neg_neu, 
Y_train_neg_neu, Y_test_neg_neu) = train_test_split(data_X, Y_neg_neu,
                                                    test_size=0.4,
                                                    random_state=random_state)


# Scale all train samples
X_pos_neu_s = preprocessing.scale(X_train_pos_neu)
X_neg_neu_s = preprocessing.scale(X_train_neg_neu)


# parameters for model fitting
param_grid = {'C': [1, 10, 100, 1000], 'gamma': [0.01,0.001, 0.0001],
              'kernel': ['rbf']}
metrics = ['f1','accuracy','average_precision','roc_auc','recall']

# Fit models and store them
fitted_models_pos_neu = {}
for metric in metrics:
    fitted_models_pos_neu[metric] = fit_model(X_pos_neu_s,Y_train_pos_neu,
                                                param_grid,metric,6)

for metric, model in fitted_models_pos_neu.items():
    print ("Using metric {}".format(metric))
    print("Best parameters set found on development set:")
    print()
    print(model.best_params_)
    print("Grid scores on development set:")
    print()
    for params, mean_score, scores in model.grid_scores_:
        print("%0.3f (+/-%0.03f) for %r"
              % (mean_score, scores.std() * 2, params))

    print()

# Validate on test sample
X_pos_neu_s_test = preprocessing.scale(X_test_pos_neu)
for metric, model in fitted_models_pos_neu.items():
    this_estimator = fitted_models_pos_neu[metric].best_estimator_ 
    this_score = this_estimator.score(X_pos_neu_s_test, Y_test_pos_neu)
    y_pred = this_estimator.fit(X_pos_neu_s_test, Y_test_pos_neu).predict(X_pos_neu_s_test)
    #conf_matrix = confusion_matrix(Y_test_pos_neu,y_pred)
    df_confusion = pd.crosstab(Y_test_pos_neu, y_pred, 
                               rownames=['Actual'], 
                               colnames=['Predicted'], margins=True)
    print ("Using metric {}".format(metric))
    print("Validation score {}".format(this_score))
    print()
    print("Confusion Matrix:")
    print(df_confusion)
    
