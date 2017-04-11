#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

import os


def prepend_to_filename(directory, substring, prepend):
    list_of_files = os.listdir(directory)
    for item in list_of_files:
        if substring in item:
            filename = directory + '/' + item
            print 'Renaming', item
            os.rename(filename, directory + '/' + prepend + item)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Prepends a string to matching audiofiles")
    parser.add_argument("dir", help="working directory")
    parser.add_argument("substring", help="look for substring in file before prepend")
    parser.add_argument("prepend", help="string to prepend")
    args = parser.parse_args()

    print "Processing files..."
    prepend_to_filename(args.dir, args.substring, args.prepend)
    print 'Done!'
