import os
import shutil


def move_items_by_estimation(condition, destination, estimations_folder, origin):
    estimations = os.listdir(estimations_folder)
    for item in estimations:
        if '.key' in item:
            e = open(estimations_folder + '/' + item)
            e = e.read()
            if condition in e:
                print 'moving...', item, e
                shutil.move(origin + '/' + item[:-3] + 'wav',
                            destination)


def move_items_by_id(condition, destination, results, origin):
    results = open(results, 'r')
    len_line = 1
    while len_line > 0:
        r = results.readline()
        c = r[r.find('\t') + 1:r.rfind(' (')]
        try:
            c = float(c)
            if condition in r and c < 1:
                print r
                file_name = r[:r.rfind('.key')] + '.key'
                shutil.move(origin + '/' + file_name, destination)
        except ValueError:
            pass
        len_line = len(r)


def move_items(origin, destination):
    estimations = os.listdir(origin)
    for item in estimations:
        if '.key' in item:
            print item
            e = open(origin + '/' + item)
            e = e.readline()
            e = e.split('\t')
            print e[0]
            print e[1]
            if e[0] == e[1]:
                print 'moving...', item, e
                shutil.move(origin + '/' + item,
                            destination)
