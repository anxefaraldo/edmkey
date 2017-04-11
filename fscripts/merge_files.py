#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

import os


def merge_files(dir_with_files, new_filename):
    o = open(new_filename, 'w')
    e = os.listdir(dir_with_files)
    for item in e:
        if '.key' in item:
            f = open(dir_with_files + '/' + item, 'r')
            l = f.read()
            o.write(l + '\n')
            f.close()
    o.close()


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Merge multiple files into a single one")
    parser.add_argument("dir", help="")
    parser.add_argument("filename", help="")
    args = parser.parse_args()

    print "Merging files..."
    merge_files(args.dir, args.filename)
    print 'Done!'
