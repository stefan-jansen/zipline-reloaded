"""
float specialization of AdjustedArrayWindow
"""
from numpy cimport float64_t
import numpy; numpy.import_array()
ctypedef float64_t[:, :] databuffer

include "_windowtemplate.pxi"
