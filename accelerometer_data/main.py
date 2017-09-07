#!/usr/bin/env python3
'''
Script for parsing the accelerometer data
'''
import sys
import csv
import numpy
import scipy

CHANNEL_LINE = 15
UNIT_LINE = 19
DATA_START = 28

def main(args):
    filename = args[1]
    with open(filename, 'r') as data_file:
        lines = [l for l in data_file]

        channels = lines[CHANNEL_LINE]
        units = lines[UNIT_LINE]
        data = lines[DATA_START:]
    pass


#Run main if run
if __name__ == "__main__":
    main(sys.argv)
