from fodules.excel import *
from sklearn import svm

"""
Prior to these steps you have to run the estimation and evaluation
algorithms, in order to have data to train with.
"""

# This is the merged_results.csv file we are going to train with:
training_file = '/home/angel/Desktop/20160705201411-bmtg-wav/merged_results.csv'

# we use the whole bmtg collection for training!
features = features_from_csv(training_file, 2, 74)  # only 36 pcp values.
targets = stringcell_from_csv(training_file, 78)    # ground-truth of the file if keyExtended!
# filenames = stringcell_from_csv(training_file, 0)   # col. 0 stores the filename.
print len(features), 'files used for training.'

"""
# Split data in train and test datasets
np.random.seed(0)  # A random permutation, to split the data randomly.
indices = np.random.permutation(len(features))
features_train = features[indices[:-10]]
targets_train = targets[indices[:-10]]
filenames_train = filenames[indices[:-10]]
features_test = features[indices[-10:]]
targets_test = targets[indices[-10:]]
filenames_test = filenames[indices[-10:]]
"""

# here is the actual support vector machine.
svc = svm.LinearSVC()
svc.fit(features, targets)

# NOW WE NEED TO LOAD DIFFERENT DATASETS TO TEST!
analysis_file = '/home/angel/Desktop/20160705200749-gs-wav/merged_results.csv'
features = features_from_csv(analysis_file, 2, 74)
filenames = stringcell_from_csv(analysis_file, 0)

an_folder = analysis_file[:analysis_file.rfind('/')]
for i in range(len(features)):
    prediction = svc.predict(features[i].reshape(-1, 72))
    prediction = "{0}, ".format(str(prediction)[2:-2])
    append_results = open(an_folder + '/' + filenames[i] + '.key', 'a')
    append_results.write(prediction)
    append_results.close()
