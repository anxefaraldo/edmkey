import os
import argparse


def remove_xml_illegal_chars(a_string, replacement=''):

    illegal_chars = {"&", "<", ">", '"', "'"}
    if any(illegal_char in a_string for illegal_char in illegal_chars):
        for item in illegal_chars:
            a_string = a_string.replace(item, replacement)
    return a_string


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="removes ilegal xml chars from filename.")
    parser.add_argument("dir", help="directory to reformat.")
    ar = parser.parse_args()

    if not os.path.isdir(ar.dir):
        raise parser.error("Warning: {0} is not a directory.".format(ar.dir))
    else:
        l = os.listdir(ar.dir)
        for item in l:
            legal_name = remove_xml_illegal_chars(item)
            os.rename(ar.dir + '/' + item, ar.dir + '/' + legal_name)
