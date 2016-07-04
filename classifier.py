import numpy as np
from fodules.excel import *
from sklearn import svm


# Prior to these steps you have to run the estimation and evaluation
# algorithms, in order to have data to train with.

# This is the merged results file we are going to work with:
data_file = '/home/angel/Desktop/20160704175022-bmtg-wav/merged_results.csv'

features = features_from_csv(data_file, 3, 39)  # bins 3-14 contain the Chroma values.
targets = stringcell_from_csv(data_file)
filenames = stringcell_from_csv(data_file, 0)
print len(features)
print len(targets)
print len(filenames)

# Split data in train and test datasets
# A random permutation, to split the data randomly
np.random.seed(0)
indices = np.random.permutation(len(features))
features_train = features[indices[:-10]]
targets_train = targets[indices[:-10]]
filenames_train = filenames[indices[:-10]]
features_test = features[indices[-10:]]
targets_test = targets[indices[-10:]]
filenames_test = filenames[indices[-10:]]

# here is the actual support vector machine.
svc = svm.SVC(kernel='linear')
svc.fit(features_train, targets_train)
svc.predict(features_test)
