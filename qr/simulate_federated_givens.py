import numpy as np
import scipy as sc
import pandas as pd

import qr.shared_functions as sh


def compute_givens_parameters(x, y):
    c = x/np.sqrt(x*x+y*y)
    s = y/np.sqrt(x*x+y*y)
    return c, s

def reconstruct_from_givens(c, x):
    d = -((c * c - 1) * x * x / (c * c))
    y= np.sqrt(d)
    return y

def givens_params(x, y):
    if y == 0:
        c = 1
        s = 0
        print('0')

    elif np.abs(y)> np.abs(x):
        t = x/y
        s = 1/np.sqrt(1+t*t)
        c = s* t
    else:
        t = y/x
        c = 1/np.sqrt(1+t*t)
        s = c*t
    return c, s

def reconstruct_from_updated(ai, ai_prev, c,s):
    y = [(a1 - c*a0)/s for a1, a0 in zip(ai, ai_prev)]
    return y

def update_A(A):
    '''
    Attack on the parameters of federated Given's rotation.
    Args:
        A: The input data matrix

    Returns:

    '''
    reconstruction_error = 0
    for i in range(A.shape[1]-1):
        for j in range(i+1, A.shape[1]):
            #c, s = compute_givens_parameters(A[i,i], A[j,i])
            # Compute the Give's parameters
            c,s = givens_params(A[i,i], A[j,i])
            #Log the original data rows before the rotation
            aa0 = A[i].copy()
            aa1 = A[j].copy()
            a1 = A[i]
            a2 = A[j]
            # Apply the transformation on both submatrices
            A[i] = [c*ai+s*aj for ai,aj in zip(a1,a2)]
            A[j]= [c*aj - s*ai for ai,aj in zip(a1,a2)]
            # reconstruct the entries of A[j] base on A[i] before and after the rotation.
            reconstruction_error = reconstruction_error + np.sum(reconstruct_from_updated(A[i], aa0, c, s)-aa1)
            print(reconstruction_error)
    return A, reconstruction_error

if __name__ == '__main__':

    #data = [[1,3,-6,-1], [4,8,7,3], [2,3,4,5],[-9, 6, 3, 2]]
    #data = np.array(data, dtype=float)
    m = 10
    i = 0
    n = 500
    np.random.seed(11)
    reconstruct = 0
    for i in range(10):
        A = sh.generate_random_gaussian(5000, 10)
        QA, rec = update_A(A)
        reconstruct = reconstruct+rec
    print('Average reconstruction error:', str(reconstruct/10))