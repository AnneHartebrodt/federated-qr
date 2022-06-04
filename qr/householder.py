import numpy as np
import scipy as sc
import pandas as pd

import qr.shared_functions as sh


def householder_reflection(A):
    n = A.shape[0]
    a_bar = A[:, 0]/np.nanmax(A[:, 0])
    sign = np.sign(a_bar[0])
    u = a_bar +sign*np.linalg.norm(a_bar)*np.identity(n)[0]
    beta = 2/(np.dot(u, u))
    u = np.atleast_2d(u).T
    AQ = A - beta* (u @ u.T) @ A
    return AQ

def orthonormalization(B):
    n = B.shape[0]
    m = B.shape[1]
    for i in range(m):
        B[i:n, i:m] = householder_reflection(B[i:n, i:m])
    return B





if __name__ == '__main__':
    data = sh.generate_random_gaussian(500, 10)

    A = data.copy()
    I = np.identity(10)
    m = 10
    i = 0
    n = 500

    q, r = sc.linalg.qr(A)
    QA = householder_reflection(A)
    AA = orthonormalization(A)

