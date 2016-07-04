import numpy as np
from fodules.excel import *
from sklearn import svm
# from sklearn.neighbors import KNeighborsClassifier


# Prior to these steps you have to run the estimation and evaluation
# algorithms, in order to have data to train with.

# This is the merged results file we are going to work with:
data_file = '/Users/angel/Desktop/20160704091316-gs-wav/merged_results.csv'

features = features_from_csv(data_file, 3, 14)  # bins 3-14 contain the Chroma values.
targets = stringcell_from_csv(data_file)
filenames = stringcell_from_csv(data_file, 0)
print features
print targets
print filenames

# Split data in train and test datasets
# A random permutation, to split the data randomly
np.random.seed(0)

indices = np.random.permutation(len(features))
features_train = features[indices[:-10]]
targets_train = targets[indices[:-10]]
filenames_train = filenames[indices[:-10]]
features_test  = features[indices[-10:]]
targets_test  = targets[indices[-10:]]
filenames_test = filenames[indices[-10:]]


svc = svm.SVC(kernel='linear')
svc.fit(features_train, targets_train)
svc.predict(features_test)
