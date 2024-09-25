"""
bool specialization of AdjustedArrayWindow
"""
from numpy cimport uint8_t
import numpy; numpy.import_array()

ctypedef uint8_t[:, :] databuffer

include "_windowtemplate.pxi"
