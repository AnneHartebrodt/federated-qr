import numpy as np
import scipy as sc
import pandas as pd

import qr.shared_functions as sh


def compute_givens_parameters(x, y):
    print(x*x+y*y)
    c = x/np.sqrt(x*x+y*y)
    s = y/np.sqrt(x*x+y*y)
    return c, s

def givens_params(x, y):
    print(x)
    if y == 0:
        c = 1
        s = 0

    elif np.abs(y)> np.abs(x):
        t = x/y
        s = 1/np.sqrt(1+t*t)
        c = s* t
    else:
        t = y/x
        c = 1/np.sqrt(1+t*t)
        s = c*t
    return c, s

def update_A(A):
    for i in range(A.shape[1]-1):
        print(i)
        for j in range(i+1, A.shape[1]):
            print(j)
            c, s = compute_givens_parameters(A[i,i], A[j,i])
            print(c,s)
            a1 = A[i]
            a2 = A[j]
            A[i] = [c*ai+s*aj for ai,aj in zip(a1,a2)]
            aj = [c*aj - s*ai for ai,aj in zip(a1,a2)]
            A[j] = aj

    return A

if __name__ == '__main__':

    data = sh.generate_random_gaussian(500, 10)
    data = [[1,3,-6,-1], [4,8,7,3], [2,3,4,5],[-9, 6, 3, 2]]
    data = np.array(data, dtype=float)
    A = data.copy()
    m = 10
    i = 0
    n = 500

    q, r = sc.linalg.qr(A)
    QA = update_A(A)
