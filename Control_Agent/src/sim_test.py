#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' Doc String

Description: test to see if python runs with eyesim software
Date Last Edited: 13 apr 2022

 !!Useful with debugging!!

'''
__author__ = "Brandon Colelough"
__copyright__ = "Open Source"
__credits__ = [""]
__license__ = "Open Source"
__version__ = "1.0.1"
__maintainer__ = "Brandon Colelough"
__email__ = "brandon.colelough1234@gmail.com"
__status__ = "Production"

# Imports Go Here!

try:
    from eye import *
    import random
except ImportError:
    raise ImportError('Import test failed')

SAFE = 200
def rand_drive():
    LCDMenu("","","","END")
    while (KEYRead() != KEY4):
        if (PSDGet(1)>SAFE and PSDGet(2)>SAFE and PSDGet(3)>SAFE):
          LCDPrintf("straight\n")
          VWStraight(50,500)  # not required to wait

        else:
           VWStraight(-25,500)
           VWWait()
           LCDPrintf("turning \n")
           direc = int ((random.random()-0.5) * 360)  # [-0.5 .. +0.5] * 360
           VWTurn(direc, 90)
           VWWait()

class sim_test:
    """Class Description"""
    pass  # do nothing

if __name__ == '__main__':  # code to execute if called from command-line
    rand_drive()
