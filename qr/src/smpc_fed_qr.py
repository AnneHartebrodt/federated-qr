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

# import mpyc as m
# import mpyc.sectypes as s
from mpyc.runtime import mpc
import sys
import functools
import scipy.linalg as la
from docopt import docopt
import argparse
import pandas as pd
import os.path as op


async def secure_qr(local_data):

    secfxp = mpc.SecFxp(64)


    ortho = []
    np.random.seed(12)

    se = np.dot(local_data[:, 0], local_data[:,0])
    print(se)
    se = secfxp(se)
    sum = mpc.sum(mpc.input(se))
    

    # Decode sum and store for future reference.
    s  = await mpc.output(sum)

    print(s)

    ortho.append(local_data[:,0])
    norms = [s]


    #Initial residual arrays
    r = np.zeros((local_data.shape[1], local_data.shape[1]))
    rl = [np.zeros((local_data.shape[1], local_data.shape[1])) for d in local_data]
    
    glist = []
    ap = local_data[:,0]

    print(r)
    # i = number of column vectors
    print('Local residuals')
    for i in range(1, local_data.shape[1]):
        print('Norm')
        print(norms[i-1])
        glist.append(ap / np.sqrt(norms[i-1]))
        for j in range(i):
            ind = i-1
            rij = np.dot(local_data[:, ind], glist[j])
            r[j, ind] = rij
        

        print('Compute conorm ')
        ses = []
        for di in range(len(ortho)):
            # local eigenvector snippets
            o = ortho[di]
            # eigenvector norms
            nn = norms[di]
            n = nn #+ 1e-16
            # Compute conorm
            se = np.dot(o, local_data[:, i]) / n
            print(se)
            ses.append(se)
        
        
        print('Input conorms')
        print(ses)
        ses = np.array(ses)
#        ses = secfxp.array(ses)

        # Decode sum and store for future reference.
        # print('Done')
        inp = mpc.input(list(map(secfxp, ses)))
        sums = functools.reduce(mpc.vector_add, inp)
        sums = await mpc.output(sums)
        #sums  =  await mpc.output(sums)
        print('Output conroms')
        print(sums)

         # init norm of the current vector

        # ap = newly reorthogonalised eigenvector snippet
        ap = local_data[:, i]
        for j in range(len(sums)):
            # reorthonogonalise
            ap = ap - sums[j] * ortho[j]

        # compute the local norm of the freshly orthogonalised
        # eigenvector snippet
        se = np.dot(ap, ap)
        print(se)
        print(type(se))
        
        se = secfxp(se)
        sum = mpc.sum(mpc.input(se))
        s  = await mpc.output(sum)
        print(s)
        print(type(s))
        norms.append(s)
        ortho.append(ap)


   

    i = local_data.shape[1]
    ind = i - 1
    glist.append(ap / np.sqrt(norms[i-1]))
    for j in range(i):
        rij = np.dot(local_data[:, ind], glist[j])
        r[j, ind] = rij
        
    G_list = []

    # normalise the vector norms to unit norm.
    for i in range(len(ortho)):
        # norms are still squared
        G_list.append(ortho[i] / np.sqrt(norms[i]))

    r = np.array(r)
    print(r)
    inp = mpc.input(list(map(secfxp, r.flatten())))
    r = functools.reduce(mpc.vector_add, inp)
    r = await mpc.output(r)
    print(r)
    rd = int(np.sqrt(len(r)))
    r = np.reshape(r, (rd,rd))
    # just for convenience stack the data
    print(r)
    #r = computeR(local_data, G_list)
    return ortho, G_list, r, rl, local_data

    


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--file', type=str, help=('file'))
    parser.add_argument('-o', '--output_dir', help='output folder')
    parser.add_argument('-p', '--output_file_prefix', help='output file')

    args = parser.parse_args()
    print(args)

    await mpc.start()

    data = pd.read_csv(args.file, sep='\t', header=None).values

    print(data)
    ortho, G_list, r, rl, local_data = await secure_qr(data)
    #print(ortho)
    print(r)
    await mpc.shutdown()


    pd.DataFrame(G_list).to_csv(op.join(args.output_dir, args.output_file_prefix+'_Q.tsv'), header=False, index=False, sep='\t')
    pd.DataFrame(r).to_csv(op.join(args.output_dir, args.output_file_prefix+'_R.tsv'), header=False, index=False, sep='\t')



if __name__ == '__main__':

    mpc.run(main())


