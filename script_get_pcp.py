from get_pcps import *
import os

def pcp_sort(pcp):
    """
    Returns a new vector with sorted indexes of the incoming pcp vector.
    """
    pcp = pcp[:]
    idx = []
    for i in range(len(pcp)):
        new_index = pcp.index(np.max(pcp))
        idx.append(new_index)
        pcp[new_index] = -1
    return idx



my_folder =  '/Users/angeluni/Insync/datasets-key/gs/gs-wav'


l = os.listdir(my_folder)

pcps = []
for my_file in l:
    c = global_chroma(my_folder+'/'+my_file)
    print my_file+'\n', c, '\n'
    print pcp_sort(list(c))
    pcps.append(c)