import mne
import os
#import argparse

import numpy as np
import pysnirf2 as snirf
import matplotlib.pyplot as plt

from mne.io import read_raw_snirf, read_raw_nirx

def main():
    n_channels = 100 # number of channels
    sampling_rate = 6.1 # sampling rate in Hz
    file_duration = 612 # Duration of file in seconds (overestimating isn't an issue for plotting purposes) (= (# of timesteps) / (sampling rate)
    stimulus_duration = 11 # duration of stimulus in seconds

    #argParser = argparse.ArgumentParser()
    #argParser.add_argument('input', help='Input file path to folder containing SNIRF file(s)')

    #args = argParser.parse_args()

    #print(args.input)

    base_path = os.getcwd()
    to_preproc_path = os.path.join(base_path, "data", "toPreProc")

    snirf_list = {}

    file_index = 0

    for file in os.listdir(to_preproc_path):
        if(file.endswith(".snirf")):
            intensity_data = read_raw_snirf(os.path.join(to_preproc_path, file))
            snirf_list[file_index] = intensity_data
            file_index += 1

            fig = intensity_data.plot(n_channels=n_channels, duration=file_duration)
            fig.figure.savefig(os.path.join(to_preproc_path, file + ".png"))
        else:
            continue

if __name__ == '__main__':
    main()