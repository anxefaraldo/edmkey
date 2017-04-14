#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

import os


def change_file_extension(directory, in_ext='txt', out_ext='key'):
    """
    Changes the file extensions
    """
    number_of_files = 0
    list_of_items = os.listdir(directory)
    for item in list_of_items:
        if item[item.rfind('.') + 1:] == in_ext:
            os.rename(directory + '/' + item, directory + '/' + item[:item.rfind('.')] + '.' + out_ext)
            number_of_files += 1
    print number_of_files, 'files converted.'


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="changes the file extension of matching items in a directory.")
    parser.add_argument("dir", help="working dir")
    parser.add_argument("old_ext", help="old file extension")
    parser.add_argument("new_ext", help="new file extension")
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        raise parser.error("Warning: {0} is not a directory.".format(args.dir))
    else:
        print "Processing files..."
        change_file_extension(args.dir, args.old_ext, args.new_ext)
        print 'Done!'



