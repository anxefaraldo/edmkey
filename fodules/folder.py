import os
from datetime import datetime


def make_unique_dir(parent, tag=''):
    """
    creates a sub-folder in the specified directory
    with some of the algorithm parameters.
    :type parent: str
    :type tag: str
    """
    now = str(datetime.now())
    now = now[:now.rfind('.')]
    now = now.replace(':', '')
    now = now.replace(' ', '')
    now = now.replace('-', '')
    temp_folder = "{0}/{1}-{2}".format(parent, now, tag)
    try:  # TODO remove parameter info and allow to write it from script as tags
        os.mkdir(temp_folder)
    except OSError:
        print "'{}' already exists.".format(temp_folder)
    return temp_folder


def results_directory(out_dir):
    """
    creates a sub-folder in the specified directory
    with some of the algorithm parameters.
    :type out_dir: str
    """
    if not os.path.isdir(out_dir):
        print("CREATING DIRECTORY '{0}'.".format(out_dir))
        if not os.path.isabs(out_dir):
            raise IOError("Not a valid path name.")
        else:
            os.mkdir(out_dir)
    return out_dir
