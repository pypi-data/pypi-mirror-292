"""
File: mpiPython.py
Modification Date: 8/13/24
Time Modified: 11:23pm CT
Created by: Judah Nava
Last Modified By: Judah Nava
Organization: Parallel Solvit LLC and MSUM CSIS Department
"""

import os, atexit, subprocess, sys, ctypes as CT

from .mpiPython import (
    MPIpy,
    MPI_Status,
)

class betaMPIpy(MPIpy):
    
    def __init__(self):
        super().__init__()
    
    def Send_beta(self, value, dest, tag, comm_m = MPIpy.cworld ) -> MPI_Status:
        print("This is a command in testing, not ready for production")
        # This needs to support int, float, 
        """
            Here is what is should support:
            Send_beta(3, 1, 1) ;
            Send_beta([3,5], 1, 1) ;
            Send_beta(3.4564, 1, 1) ;
            Send_beta([3.2, 5.9, 1.234], 1, 1) ;
            Send_beta(4j+2, 1, 1) ;
            Send_beta([4j+1, 7.3j+99, 1j+58.3], 1, 1)
        """
        if type(value) is not list:
            value = list(value)



