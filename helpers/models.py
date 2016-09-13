# -*- coding: utf-8 -*-
from sklearn import svm
#from sklearn.metrics import roc_auc_score
#from sklearn.metrics import f1_score
#from sklearn.metrics import make_scorer
from sklearn.cross_validation import StratifiedKFold
from sklearn.grid_search import GridSearchCV

def fit_model(predictor,target,grid,metric='f1',folds=6):
    """Perform stratified k-fold cross-validation of SVM model.
    
    predictor: np.array with predictor varables
    target: np.array with target classes. If usin metrics that assume binary
    grid: dictionary with the parameter grid as specified in sklearn.grid_search
    distribution,  then predictor should be binary or it will fail.
    metric: the metric for cross validation.
    
    Returns
    fitted GridSearchCV object
    """    
    
    # instantiate stratified k-fold
    cv = StratifiedKFold(target, n_folds=folds)
    # instantiate svm model
    svr = svm.SVC() 
    # Perform cross validation
    clf = GridSearchCV(estimator=svr, param_grid=grid, n_jobs=-1,
                       scoring=metric, cv = cv)
    clf.fit(predictor, target)
    return clf
