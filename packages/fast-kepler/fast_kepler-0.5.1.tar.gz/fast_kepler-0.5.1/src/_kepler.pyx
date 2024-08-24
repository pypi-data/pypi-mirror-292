# Import necessary libraries
from __future__ import absolute_import
import numpy as np
cimport numpy as np
import cython
from libc.math cimport sin, cos

# Wrapping kepler(M,e) and calc_c_rv functions from kepler.c
cdef extern from "kepler.c":
    double kepler(double M, double e)
    double calc_c_rv0(double t, double per, double k, double phase, double e, double cosom, double sinom)
    double calc_c_rv1(double t, double per, double k, double tp, double e, double cosom, double sinom)

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

# Function to calculate kepler array using memory views
@cython.boundscheck(False)
@cython.wraparound(False)
def kepler_array(double[:,] M, double e):
    cdef int size = M.shape[0]
    cdef double[:] E = np.empty(size, dtype=np.float64)

    for i in range(size):
        E[i] = kepler(M[i], e)

    return np.asarray(E)  # Convert back to NumPy array for Python interaction

# Function to calculate radial velocity using calc_rv0
@cython.boundscheck(False)
@cython.wraparound(False)
def calc_rv0(np.ndarray[DTYPE_t, ndim=1] t, double per, double k, double phase, 
                   double e, double om):
    """
    Radial velocity calculation using phase (calc_rv0).
    """
    cdef int size = t.shape[0]
    cdef np.ndarray[DTYPE_t, ndim=1] rv = np.empty_like(t)
    cdef double cosom = cos(om)
    cdef double sinom = sin(om)

    for i in range(size):
        rv[i] = calc_c_rv0(t[i], per, k, phase, e, cosom, sinom)

    return rv

# Function to calculate radial velocity using calc_rv1
@cython.boundscheck(False)
@cython.wraparound(False)
def calc_rv1(np.ndarray[DTYPE_t, ndim=1] t, double per, double k, double tp, 
                   double e, double om):
    """
    Radial velocity calculation using time of periastron passage (calc_rv1).
    """
    cdef int size = t.shape[0]
    cdef np.ndarray[DTYPE_t, ndim=1] rv = np.empty_like(t)
    cdef double cosom = cos(om)
    cdef double sinom = sin(om)

    for i in range(size):
        rv[i] = calc_c_rv1(t[i], per, k, tp, e, cosom, sinom)

    return rv
