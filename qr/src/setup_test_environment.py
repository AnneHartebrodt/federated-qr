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

def setup(file, output_prefix, output_name):

    if op.exists(file):
        data = pd.read_csv(file)
        data = data.values
    else:
        data = sh.generate_random_gaussian(500, 8)

    data_list, choices = sh.partition_data_horizontally(data)
    for d in range(len(data_list)):
        output_dir = op.join(output_prefix, str(d))
        os.makedirs(output_dir, exist_ok=True)
        pd.DataFrame(data_list[d]).to_csv(op.join(output_dir, output_name), sep='\t')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, help=('file'))
    parser.add_argument('-p', '--output_dir', help='output folder')
    parser.add_argument('-o', '--output_name', help='output file')

    args = parser.parse_args()
    print(args)

    setup(args.file, args.output_dir, args.output_name)

