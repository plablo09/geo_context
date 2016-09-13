# -*- coding: utf-8 -*-
import numpy as np 
import pandas as pd
from sklearn import preprocessing
from sklearn.decomposition import PCA as sklearnPCA
from sklearn import svm
from sklearn.metrics import roc_curve, auc
from sklearn.cross_validation import StratifiedKFold
import matplotlib.pyplot as plt
from scipy import interp

#set random state for camparability
random_state = np.random.RandomState(0)

#this function performs stratified k-folds and plots roc curves
def plot_roc(predictor, target):
    
    cv = StratifiedKFold(target, n_folds=6)
    classifier = svm.SVC(probability=True,random_state=random_state)
    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)
    #all_tpr = []
    for i, (train, test) in enumerate(cv):
        probas_ = classifier.fit(predictor[train], 
                                 target[train]).predict_proba(predictor[test])
        # Compute ROC curve and area the curve
        fpr, tpr, thresholds = roc_curve(target[test], 
                                         probas_[:, 1],pos_label=3.0)
        mean_tpr += interp(mean_fpr, fpr, tpr)
        mean_tpr[0] = 0.0
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc))
        
    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')
    
    mean_tpr /= len(cv)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    plt.plot(mean_fpr, mean_tpr, 'k--',
             label='Mean ROC (area = %0.2f)' % mean_auc, lw=2)
    
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic geo_context')
    plt.legend(loc="lower right")
    plt.show()



#read data
context = pd.read_csv('context_nuevo.csv')
#select variable columns
cols_select = context.columns[6:]
variables = context.ix[:,cols_select]
for c in ['no_se','uname','cont','lat','lon','geom','cve_mza']:
    del variables[c]
    
#reclass intervalo as numerical
def intervalo_to_numbers(x):
    equiv = {'sun':0,'mon':1,'tue':2,'wed':3,'thu':4,'fri':5,'sat':6,'sun':7}
    interval = 0.16666*int(x.split('.')[1])
    day = x.split('.')[0]
    valor = equiv[day] + interval
    return valor

reclass = variables['intervalo'].apply(intervalo_to_numbers)

#drop old 'intervalo' column and replace it with numerical values
del variables['intervalo']
variables = variables.join(reclass,how='inner')

#Get dataframe as matrix and scale it:
data = variables.as_matrix()
Y = data[:,0]
X = data[:,1:]
scaled_X = preprocessing.scale(X)

#Perform PCA analysis
pca = sklearnPCA(n_components=0.80,whiten=True)
pca_transform = pca.fit_transform(scaled_X)
pca_transform.shape

#Stratified k-fold
#Get only positive and negative classes, first with original data
X_bin, Y_bin = scaled_X[Y != 2], Y[Y != 2]



#Same with PCA reduced data:
#data = variables.as_matrix()
#Y_pca = pca_transform[:,0]
#X_pca = pca_transform[:,1:]
#X_pca_bin, Y_pca_bin = X_pca[Y != 2], Y[Y != 2]
#cv_pca = StratifiedKFold(Y_pca_bin, n_folds=6)
#for i, (train, test) in enumerate(cv_pca):
#    probas_ = classifier.fit(X_pca_bin[train], Y_bin[train]).predict_proba(X_pca_bin[test])
#    # Compute ROC curve and area the curve
#    fpr, tpr, thresholds = roc_curve(Y_bin[test], probas_[:, 1],pos_label=3.0)
#    mean_tpr += interp(mean_fpr, fpr, tpr)
#    mean_tpr[0] = 0.0
#    roc_auc = auc(fpr, tpr)
#    plt.plot(fpr, tpr, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc))
#    
#plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')
#
#mean_tpr /= len(cv_pca)
#mean_tpr[-1] = 1.0
#mean_auc = auc(mean_fpr, mean_tpr)
#plt.plot(mean_fpr, mean_tpr, 'k--',
#         label='Mean ROC (area = %0.2f)' % mean_auc, lw=2)
#
#plt.xlim([-0.05, 1.05])
#plt.ylim([-0.05, 1.05])
#plt.xlabel('False Positive Rate')
#plt.ylabel('True Positive Rate')
#plt.title('Receiver operating characteristic geo_context')
#plt.legend(loc="lower right")
#plt.show()