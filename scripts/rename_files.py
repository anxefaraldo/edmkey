import os
import re
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reformats dataset filenames.")
    parser.add_argument("dir", help="directory to reformat.")
    ar = parser.parse_args()

    if not os.path.isdir(ar.dir):
        raise parser.error("Warning: {0} is not a directory.".format(ar.dir))
    else:
        l = os.listdir(ar.dir)
        for item in l:
            if 'Hip-Hop' in item:
                os.rename(ar.dir + '/' + item, ar.dir + '/' + re.sub("Hip-Hop", 'Hip Hop', item))
            elif 'Psy-Trance' in item:
                os.rename(ar.dir + '/' + item, ar.dir + '/' + re.sub('Psy-Trance', 'Psy Trance', item))
            elif "&" in item:
                os.rename(ar.dir + '/' + item, ar.dir + '/' + re.sub('&', 'and', item))
            else:
                pass

# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reformats dataset filenames.")
    parser.add_argument("dir", help="directory to reformat.")
    ar = parser.parse_args()

    if not os.path.isdir(ar.dir):
        raise parser.error("Warning: {0} is not a directory.".format(ar.dir))
    else:
        l = os.listdir(ar.dir)
        print ar.dir + '/'
        for item in l:
            if "&amp;" in item:
                os.rename(ar.dir + '/' + item, ar.dir + '/' + re.sub('&amp;', '&', item))
            if "&apos;" in item:
                os.rename(ar.dir + '/' + item, ar.dir + '/' + re.sub('&apos;', "'", item))
            if " mino.key" in item:
                os.rename(ar.dir + '/' + item, ar.dir + '/' + re.sub(" mino.key", ' minor.key', item))

"""
if "&amp;" in filename:
                    filename = re.sub("&amp;", "&", filename)
                if "♯" in filename:
                    filename = re.sub("♯", '#', filename)
                if '—' in filename:
                    filename = re.sub("—", "-", filename)
                if '&#39;' in filename:
                    filename = re.sub("&#39;", "'", filename)
                if '&#34;' in filename:
                    filename = re.sub("&#34;", '"', filename)
                if '/' in filename:
                    filename = re.sub("/", ', ', filename)
                # if '&gt;' in filename:
                    filename = re.sub("&gt;", ">", filename)
                # if '(' in filename:
                    filename = re.sub("\(", " (", filename)

"""
