import numpy as np
# import scipy.linalg as la
import shared_functions as sh

import sys
import functools
import scipy.linalg as la
from docopt import docopt
import argparse
import pandas as pd
import os.path as op
import os

def verify_output(q_file_name, r_file_name, directory, number_sites, reference_file, sep):
    q_files = []
    for d in range(number_sites):
        q_files.append(pd.read_csv(op.join(directory, 'results', str(d), q_file_name), sep='\t', header=None).values.T)

    q_full = np.concatenate(q_files)

    r_full = pd.read_csv(op.join(directory,'results', str(0), r_file_name) , sep='\t', header=None).values
    data = pd.read_csv(op.join(directory, 'data', 'full', reference_file), header=None, sep=sep).values

    q, r = la.qr(data, mode='economic')

    print('Absolute Froebenius norm between centralized and SMPC solution')
    print('Q: '+ str(np.linalg.norm(np.abs(q)-np.abs(q_full))))
    print('R: '+ str(np.linalg.norm(np.abs(r)-np.abs(r_full))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--q_file', type=str, help=('file'))
    parser.add_argument('-r', '--r_file', help='output folder')
    parser.add_argument('-d', '--dir', help='output file')
    parser.add_argument('-s', '--number_sites', help='Number of participants', type=int)
    parser.add_argument('-f', '--reference', help='reference full data set ', type=str)
    parser.add_argument('-t', '--separator', help = 'separator for data file', type=str, default='\t')
    args = parser.parse_args()
    print(args)

    verify_output(args.q_file,args.r_file, args.dir, args.number_sites, args.reference, args.separator)
