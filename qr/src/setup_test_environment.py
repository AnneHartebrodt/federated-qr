#!/usr/bin/env python
"""Usage: smpc_fed_qr.py -f FILE -o FOLDER

Wrapper script taking as input the case and control files.

-h --help               show this
-f --inputfile1 FILE    specify input file
-o --output FOLDER      specify output folder
--verbose    print more text

"""


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

def setup_data(file, output_prefix, output_name, splits, rseed):

    np.random.seed(rseed)

    if op.exists(file):
        data = pd.read_csv(file)
        data = data.values
        
    else:
        print('Generating data')
        output_dir = op.join(output_prefix, 'data', 'full')
        os.makedirs(output_dir, exist_ok=True)
        data = sh.generate_random_gaussian(256, 8)
        pd.DataFrame(data).to_csv(op.join(output_dir, 'data.tsv'), sep='\t', header=False, index=False)

    data_list, choices = sh.partition_data_horizontally(data, splits=splits)
    for d in range(len(data_list)):
        output_dir = op.join(output_prefix, 'data', str(d))
        os.makedirs(output_dir, exist_ok=True)
        pd.DataFrame(data_list[d]).to_csv(op.join(output_dir, output_name), sep='\t', header=False, index=False)

def setup_output(output_prefix, splits):
    for d in range(splits):
        output_dir = op.join(output_prefix, 'results', str(d))
        os.makedirs(output_dir, exist_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, help=('file'))
    parser.add_argument('-p', '--output_dir', help='output folder')
    parser.add_argument('-o', '--output_name', help='output file')
    parser.add_argument('-s', '--number_sites', help='Number of participants', type=int)
    parser.add_argument('-r', '--random', help="Random seed", type = int, default=11)

    args = parser.parse_args()
    print(args)

    setup_data(args.file, args.output_dir, args.output_name, args.number_sites, args.random)
    setup_output(args.output_dir, args.number_sites)
