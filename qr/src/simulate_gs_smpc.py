"""
    Copyright (C) 2020 Anne Hartebrodt

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

    Authors: Anne Hartebrodt

"""

import numpy as np
import scipy.linalg as la
import qr.shared_functions as sh
import mpyc as m
import mpyc.sectypes as s
from mpyc.runtime import mpc


def simulate_federated_qr(local_data):
    """
    Simulate federated orthonormalisation of a horizontally split
    data matrix.
    Args:
        local_data: Local datasets formatted as numpy arrays.

    Returns: The orthogonal vectors, as concatenated matrix and individual snippets.

    """
    bit_length = 0
    secfxp = mpc.SecFxp(bit_length)

    encrypt = True

    aplist = []
    ortho = []
    np.random.seed(12)

    if encrypt:
        sum =  secfxp(1e-16)
    else:
        sum =  1e-16


    # Compute first squared eigenvector norm
    print("First eigenvector norm")
    for d in range(len(local_data)):
        # Compute local inner product
        se = np.dot(local_data[d][:, 0], local_data[d][:,0])
        if encrypt:
            se = secfxp(se)
        # Aggregator action 
        sum = sum+se 
        aplist.append(local_data[d][:,0])
    ortho.append(aplist)


    # ortho [eigenvector rank] [data set]
    # list of lists containing the already
    #  orthogonal eigenvectors
    norms = [sum]
    # iterate over the eigenvectors
   
    if encrypt:
        print(np.sqrt(mpc.output(norms[0])))
    else:
        print(np.sqrt(norms[0]))


    a = secfxp(3)
    b = secfxp(5)

    d = secfxp.array(np.array([2,3]))

    c = mpc.output(a)
    np.sqrt(mpc.output(a).result())
    glist = []
    if encrypt:
        r = secfxp.array(np.zeros((local_data[0].shape[1], local_data[0].shape[1])))
        rl = secfxp.array([np.zeros((local_data[0].shape[1], local_data[0].shape[1])) for d in local_data])
    else:
        r = np.zeros((local_data[0].shape[1], local_data[0].shape[1]))
        rl = [np.zeros((local_data[0].shape[1], local_data[0].shape[1])) for d in local_data]

    for i in range(1, local_data[0].shape[1]):
        if encrypt:
            glist.append([a / np.sqrt(mpc.output(norms[i-1])) for a in aplist])
        else:
            glist.append([a / np.sqrt(norms[i-1]) for a in aplist])
        
        print('Local residuals')
        for j in range(i):
            for d in range(len(local_data)):
                ind = i-1
                if encrypt:
                    r[j, ind] = r[j, ind] + secfxp(np.dot(local_data[d][:, ind], glist[j][d]))
                    rl[d][j, ind] = secfxp(np.dot(local_data[d][:, ind], glist[j][d]))
                else:
                    r[j, ind] = r[j, ind] + np.dot(local_data[d][:, ind], glist[j][d])
                    rl[d][j, ind] = np.dot(local_data[d][:, ind], glist[j][d])
        
        # conorms we want to calculate
        sums = []

        aplist = []
        # iterate over the all already orthonormal eigenvector snippet
        # lists and the associated norms

        for di in range(len(ortho)):
            # local eigenvector snippets
            o = ortho[di]
            # eigenvector norms
            if encrypt:
                nn = mp.output(norms[di])
                print(nn)
            else:
                nn = norms[di]

            n = nn + 1e-16

            if encrypt:
                secfxp(0)   
            else:
                sum = 0
            # iterate over the local data sets
            # combined with the local eigenvector snippets
            # o takes all othonormal ranks
            # i is the currently to be orthonomalised rank
            for ik in range(len(local_data)):
                d = local_data[ik]
                o1 = o[ik]
                # Compute conorm
                se = np.dot(o1, d[:, i]) / n
                if encrypt:
                    se = secfxp(se)   
                sum = sum + se
            sums.append(sum)

        # init norm of the current vector
        if encrypt:
            norm = secfxp(0)   
        else:
            norm = 0


        print('Orthogonalise local')
        for d in range(len(local_data)):
            # ap = newly reorthogonalised eigenvector snippet
            ap = local_data[d][:, i]
            for j in range(len(sums)):
                # reorthonogonalise
                if encrypt:
                    print('Plain')
                    print(mpc.output(sums[j]) * ortho[j][d])
                    print('subs')
                    ap = ap - mpc.output(sums[j]) * ortho[j][d]

                else:
                    ap = ap - sums[j] * ortho[j][d]

            # compute the local norm of the freshly orthogonalised
            # eigenvector snippet
            se = np.dot(ap, ap)
            if encrypt:
                se = secfxp(se)   
            norm = norm + se
            aplist.append(ap)
        
        print('Done')
        norms.append(norm+1e-15)
        ortho.append(aplist)

    i = local_data[0].shape[1]
    ind = i - 1
    if encrypt:
        # assuming the output of QR will be plain text this does
        # not consititute a privacy breach, bc. the user can recompute it anyways
        # from the before after matrix.
        glist.append([a /  np.sqrt(mpc.output(norms[i-1])) for a in aplist])
    else:
        glist.append([a /  np.sqrt(norms[i-1]) for a in aplist])
    for d in range(len(local_data)):
        for j in range(i):
            r[j, ind] = r[j, ind] + np.dot(local_data[d][:, ind], glist[j][d])
            rl[d][j, ind] = np.dot(local_data[d][:, ind], glist[j][d])
    G_list = []

    # normalise the vector norms to unit norm.
    print("Last eigenvector norm")

    for d in range(len(local_data)):
        oo = []
        for i in range(len(ortho)):
            # norms are still squared
            oo.append(ortho[i][d] / np.sqrt(norms[i]))
        oo = np.stack(oo, axis = 1)
        G_list.append(oo)

    # just for convenience stack the data
    ortho = np.concatenate(G_list, axis=0)
    #r = computeR(local_data, G_list)
    return ortho, G_list, r, rl

def computeR(data_list, q_list):
    for a in range(data_list[0].shape[1]):
        for e in range(q_list[0].shape[1]):
            for d,g in zip(data_list, q_list):
                r[e,a] = r[e,a] + np.dot(d[:, a], g[:,e])
    return r


if __name__ == '__main__':
    ###Simulate a test
    data = sh.generate_random_gaussian(500, 10)
    q, r = la.qr(data, mode='economic')

    data_list, choice = sh.partition_data_horizontally(data, 3)
    ortho, G_list, r2, rl = simulate_federated_qr(data_list)

    print(np.linalg.norm(np.abs(q)-np.abs(ortho)))
    print(np.linalg.norm(np.abs(r)-np.abs(r2)))

