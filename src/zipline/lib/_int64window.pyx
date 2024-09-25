"""
datetime specialization of AdjustedArrayWindow
"""
from numpy cimport int64_t
import numpy; numpy.import_array()

ctypedef int64_t[:, :] databuffer

include "_windowtemplate.pxi"
