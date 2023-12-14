import mne
import os
import argparse

import numpy as np
import pysnirf2 as snirf
import matplotlib.pyplot as plt

from mne.io import read_raw_snirf, read_raw_nirx

def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument('input', help='Input file path to SNIRF file')

    args =argParser.parse_args()

    print(args.input)

if __name__ == '__main__':
    main()