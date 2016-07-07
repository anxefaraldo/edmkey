from fodules.excel import *
from sklearn import svm
from sklearn.externals import joblib

"""
Prior to these steps you have to run the estimation and evaluation
algorithms, in order to have data to train with.
"""

# This is the merged_results.csv file we are going to train with:
training_file = '/Users/angel/Desktop/20160706092253-test/merged_results.csv'

# we use the whole bmtg collection for training!
features = features_from_csv(training_file, 2, 70)  # only 36 pcp values.
targets = stringcell_from_csv(training_file, 78)    # ground-truth of the file if keyExtended!
# filenames = stringcell_from_csv(training_file, 0)   # col. 0 stores the filename.
print len(features), 'files used for training.'

# here is the actual support vector machine.
svc = svm.LinearSVC()
svc.fit(features, targets)
joblib.dump(svc, './svm_model.pkl')

print "SVM model generated and saved."