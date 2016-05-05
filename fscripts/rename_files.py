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
