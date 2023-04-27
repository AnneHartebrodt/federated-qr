import time

import numpy as np
import scipy as sc
import pandas as pd

import qr.shared_functions as sh

import numpy as np
import scipy as sc
import pandas as pd

import qr.shared_functions as sh


def householder_reflection(A_list):
    '''
    Compute one federated Householder transform
    Args:
        A_list: List of input data matrices
    Returns:

    '''
    n= 0
    max = -np.inf
    # Compute the maximal element
    for A in A_list:
        n = n+ A.shape[0]
        max = np.nanmax(A[:, 0])
    sign = -np.sign(A_list[0][0,0])
    beta = 0
    u_list = []
    e = np.identity(n)[0]
    index = 0
    sum = 0
    # Compute the norm of the max scaled vector
    for A in A_list:
        a_bar = A[:, 0]/max
        sum = sum +np.dot(a_bar, a_bar)
    norm = np.sqrt(sum)
    # compute u
    for A in A_list:
        a_bar = A[:, 0] / max
        u = a_bar -sign*norm*e[index:(index)+A.shape[0]]
        index = A.shape[0]+index
        beta = beta+np.dot(u, u)
        u = np.atleast_2d(u).T
        u_list.append(u)
    beta = 2/beta
    # Compute u @ u.T
    u = np.concatenate(u_list, axis=0)
    AR = np.zeros((n,A_list[0].shape[1]))
    index = 0
    # Two communication round are required to perform the
    # reflection
    for A in A_list:
        utu  =  beta* (u @ u.T)
        AR = AR +utu[:, index:(A.shape[0]+index)] @ A
        index = A.shape[0]+index

    AQ_list = []
    index = 0
    # Compute the final tranformed matrix at each site.
    for A in A_list:
        AQ = A - AR[index:(A.shape[0]+index), :]
        index = A.shape[0]+index
        AQ_list.append(AQ)
    return AQ_list, utu, beta, sign, norm, max, u


def reconstuct(datalist):
    # Compute a federated Householder tranform and
    # save the reflector, beta, the sign of the first element of A
    # the norm of the first vector of A, the maximal element and
    # u (only one element required)
    # QA is the transformed matrix
    QA, utu, beta, sign, norm, max, u = householder_reflection(datalist)

    # Compute the square root of the diagonal (divided by beta) to obtain the
    # absolute values of u
    di = np.diag(utu)
    u1 = np.sqrt(di / beta)


    index = 0
    masks = []
    # Without loss of generality we assume
    # that the first client in the list is the attacker
    for d in range(0, len(datalist)):
        l2 = datalist[d].shape[0]
        # get the first column vector of uTu
        m1 = np.sign(utu[index:(index + l2), 0])
        # get the sign of the corresponding entry in u
        # and compute the sign
        mask1 = m1 * np.sign(u[0])
        index = index+l2
        masks.append(mask1)
    mask = np.concatenate(masks)
    # correct the sign of u
    u1 = np.multiply(mask, u1)

    #'untransform' the vector to obtain the original
    # data column.
    e = np.identity(n)[0]
    abar = u1 + sign * norm * e
    abar = abar * max
    return abar

if __name__ == '__main__':
    avg = 0
    m = 10
    n = 5000
    np.random.seed(11)
    difference = []
    import time
    start = time.monotonic()
    for i in range(10):
        data = sh.generate_random_gaussian(n, m)
        datalist, choices = sh.partition_data_horizontally(data)
        A = data.copy()

        q, r = sc.linalg.qr(A)
        QA, ref, beta, sign, norm, max, u = householder_reflection(datalist)
        QA = np.concatenate(QA)

        abar = reconstuct(datalist)
        res = abar.flatten()-A[:, 0].flatten()

        avg = avg +np.sum(res)
    elapsed= time.monotonic()-start
    print('Time elapsed:', str(elapsed/10))
    print('Difference between original and reconstructed over 10 runs:', avg/10)
