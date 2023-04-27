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

async def secure_qr():

    clients = mpc.parties
    
    print(clients)
    bit_length = 0
    secfxp = mpc.SecFxp(64)


    ortho = []
    np.random.seed(12)

    local_data  = sh.generate_random_gaussian(250, 10)

    se = np.dot(local_data[:, 0], local_data[:,0])
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
        print(norms[i-1])
        glist.append(ap / np.sqrt(norms[i-1]))
        print(i)
        for j in range(i):
            print(j)
            ind = i-1
            print(ind)
            rij = np.dot(local_data[:, ind], glist[j])
            r[j, ind] = rij
        
        
        #r = secfxp.array(r)
        # conorms we want to calculate
        sums = []


        print('Compute conorm ')
        ses = []
        for di in range(len(ortho)):
            # local eigenvector snippets
            o = ortho[di]
            # eigenvector norms
            nn = norms[di]
            n = nn + 1e-16

            sum = 0
            # iterate over the local data sets
            # combined with the local eigenvector snippets
            # o takes all othonormal ranks
            # i is the currently to be orthonomalised rank
        
            d = local_data
            o1 = o
            # Compute conorm
            se = np.dot(o1, d[:, i]) / n
            ses.append(se)
        
        
        print(ses)
        ses = np.array(ses)
        print(ses.dtype)
        ses = secfxp.array(ses)

        # Decode sum and store for future reference.
        # print('Done')
        sums = await mpc.output(ses)
        #sums  =  await mpc.output(sums)

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

        se = secfxp(se)
        sum = mpc.sum(mpc.input(se))
    

        # Decode sum and store for future reference.
        print('Norm')
        s  = await mpc.output(sum)

        norms.append(s+1e-15)
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

    # just for convenience stack the data

    #r = computeR(local_data, G_list)
    return ortho, G_list, r, rl, local_data

    


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--file', type=str, help=('file'))
    parser.add_argument('-o', '--output_dir', help='output folder')
    parser.add_argument('-p', '--output_file', help='output file')

    args = parser.parse_args()
    print(args)

    await mpc.start()

    ortho, G_list, r, rl, local_data = await secure_qr()
    #print(ortho)
    print(r)
    await mpc.shutdown()

    import pandas as pd
    import os.path as op
    pd.DataFrame(local_data).to_csv(op.join(args.output_dir, args.output_file))


    q, r2 = la.qr(local_data, mode='economic')
    print(np.linalg.norm(np.abs(r)-np.abs(r2)))



if __name__ == '__main__':

    mpc.run(main())