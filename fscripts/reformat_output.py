from fodules.pcp import *
from settings import *


def format_output(filename):

    fa = open(filename, 'r')
    f = fa.readline()
    fa.close()
    f = f.split('\t')
    tonic = f[8][:f[8].find(' ')]
    mode = f[8][f[8].rfind(' ')+1:]
    f[8] = tonic
    f.append(mode)
    tonic = f[3][:f[3].find(' ')]
    mode = f[3][f[3].rfind(' ')+1:]
    f[3] = tonic
    f.insert(4, mode)
    pcp = f[2]
    pcp = pcp.split(',')
    npcp = []
    for item in pcp:
        npcp.append(float(item))
    new_profile = transpose_pcp(npcp, name_to_class(f[9]), HPCP_SIZE)
    new_profile = str(list(new_profile))
    f[2] = new_profile
    f = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t".format(f[0],
                                                                          f[1],
                                                                          f[2][1:-1],
                                                                          f[3],
                                                                          f[4],
                                                                          f[5],
                                                                          f[6],
                                                                          f[7],
                                                                          f[8],
                                                                          f[9],
                                                                          f[10])
    fa = open(filename, 'w')
    fa.write(f)
    fa.close()
