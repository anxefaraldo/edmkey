from fodules.excel import *
from sklearn.externals import joblib


# NOW WE NEED TO LOAD DIFFERENT DATASETS TO TEST!
analysis_file = '/Users/angel/Desktop/20160706092253-test/merged_results.csv'
features = features_from_csv(analysis_file, 2, 70)
filenames = stringcell_from_csv(analysis_file, 0)
svc = joblib.load('./svm_model.pkl')
an_folder = analysis_file[:analysis_file.rfind('/')]
for i in range(len(features)):
    prediction = svc.predict(features[i].reshape(-1, 68))
    prediction = "{0}, ".format(str(prediction)[2:-2])
    print prediction
    """
    append_results = open(an_folder + '/' + filenames[i] + '.key', 'a')
    append_results.write(prediction)
    append_results.close()
    """