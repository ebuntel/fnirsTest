'''
BUGS:
* Data files with mismatched gender/ age can cause errors in preprocessing. 
* Data files with different annotation schemes / numbers of classes can cause errors. 
'''

import mne
import os
import snirf
#import argparse

import numpy as np
#import pysnirf2 as snirf
import matplotlib.pyplot as plt

from mne.io import read_raw_snirf, read_raw_nirx
from itertools import compress

def main():
    n_channels = 100 # number of channels
    sampling_rate = 6.1 # sampling rate in Hz
    file_duration = 612 # Duration of file in seconds (overestimating isn't an issue for plotting purposes) (= (# of timesteps) / (sampling rate)
    stimulus_duration = 11 # duration of stimulus in seconds
    bandpass_upper_limit = 0.8 # Upper limit (in HZ) of frequencies allowed by the bandpass filter
    bandpass_lower_limit = 0.03 # Lower limit (in HZ) of frequencies allowed by the bandpass filter

    # Class names for reading from data file. 
    # Currently set to classes used in NATO alphabet experiment
    name_dict = {'1.0' : "Alpha", '2.0' : "Beta", '3.0' : "Charlie", '4.0' : "Delta", '5.0' : "Echo", '6.0' : "Foxtrot", '7.0' : "Golf", '8.0' : "Hotel", '9.0' : "India", '10.0' : "Juliet", 
                 '11.0' : "Kilo", '12.0' : "Lima", '13.0' : "Mike", '14.0' : "November", '15.0' : "Oscar", '16.0' : "Papa", '17.0' : "Quebec", '18.0' : "Romeo", '19.0' : "Sierra", 
                 '20.0' : "Tango", '21.0' : "Uniform", '22.0' : "Victor", '23.0' : "Whiskey", '24.0' : "X-Ray", '25.0' : "Yankee", '26.0' : "Zulu", '0.0' : "End"}
    # Here is the other class name dictionary for the other experiment
    # Initial experiment:
    # name_dict = {'1.0' : "Panther", '2.0' : "Beetle", '3.0' : "Concept", '4.0' : "Object", '5.0' : "Treat", '6.0' : "Express", '7.0' : "Chosen", '8.0' : "Enjoyed"}
    # New 8 words experiment:
    # name_dict = {'1.0' : "Panther", '2.0' : "Beetle", '3.0' : "Drill", '4.0' : "Axe", '5.0' : "Library", '6.0' : "Hospital", '7.0' : "Kitchen", '8.0' : "Bedroom"}

    base_path = os.getcwd()
    to_preproc_path = os.path.join(base_path, "processing", "data", "toPreProc")

    snirf_list = {}

    file_index = 0

    for direc in os.listdir(to_preproc_path):
        if(os.path.isdir(os.path.join(to_preproc_path, direc))):
            # Read from nirx data folder
            intensity_data = read_raw_nirx(os.path.join(to_preproc_path, direc), verbose=True)
            snirf_list[file_index] = intensity_data
            file_index += 1

            intensity_data.load_data() # Load data

            # Fix annotations
            intensity_data.annotations.set_durations(11)
            print(intensity_data.annotations)
            labels = intensity_data.annotations.to_data_frame() # Convert annotations to dataframe
            print(labels)
            segments = intensity_data.annotations.rename(name_dict) # Rename annotations based on above annotation dictionary

            # Save labels
            with open(os.path.join(to_preproc_path, direc, direc + "Labels.npy"), 'wb') as fileToWrite:
                np.save(arr=np.array(labels), file=fileToWrite)

            # Check which channels are short-distance but don't (currently) remove them 
            channels = mne.pick_types(intensity_data.info, fnirs=True)
            channel_distances = mne.preprocessing.nirs.source_detector_distances(intensity_data.info, picks=channels)
            #num_of_short_channels = 100-np.shape((intensity_data.pick(channels[channel_distances > 0.01])))[0]

            # Save raw intensity data
            fig = intensity_data.plot(n_channels=n_channels, duration=file_duration)
            fig.figure.savefig(os.path.join(to_preproc_path, direc, direc + ".png"))

            # Convert to optical density
            #print(np.shape(intensity_data))
            noisy_snirf_od = mne.preprocessing.nirs.optical_density(intensity_data)
            fig = noisy_snirf_od.plot(n_channels=100, duration=file_duration, show_scrollbars=True)
            fig.figure.savefig(os.path.join(to_preproc_path, direc, direc + "OpticalDensity.png"))

            # Use Temporal Derivative Distribution Repair (TDDR) to denoise the data
            denoised_snirf_od = mne.preprocessing.nirs.temporal_derivative_distribution_repair(noisy_snirf_od)
            fig = denoised_snirf_od.plot(n_channels=100, duration=file_duration, show_scrollbars=True)
            fig.figure.savefig(os.path.join(to_preproc_path, direc, direc + "DenoisedOpticalDensity.png"))

            # Check scalp coupling index
            # Scalp Coupling Index (SCI) is a measure of the quality of the optical contact between the optodes and the scalp.
            scalp_index = mne.preprocessing.nirs.scalp_coupling_index(denoised_snirf_od)
            fig, ax = plt.subplots(layout="constrained")
            ax.hist(scalp_index)
            ax.set(xlabel="Scalp Coupling Index", ylabel="Count", xlim=[0, 1])
            fig.figure.savefig(os.path.join(to_preproc_path, direc, direc + "ScalpCouplingIndex.png"))

            # Mark bad channels
            denoised_snirf_od.info['bads'] = list(compress(denoised_snirf_od.ch_names, scalp_index < 0.5))

            # Interpolate bad channels
            denoised_snirf_od.interpolate_bads(reset_bads=True, method = dict(fnirs = 'nearest'))

            # Convert to haemoglobin using the beer lambert law
            haemo =  mne.preprocessing.nirs.beer_lambert_law(denoised_snirf_od, ppf=0.5)
            fig = haemo.plot(n_channels=100, duration=file_duration)
            fig.figure.savefig(os.path.join(to_preproc_path, direc, direc + "UnfilteredHaemoglobin.png"))

            # Filter the haemoglobin data
            filtered_haemo = haemo.copy()
            filtered_haemo.filter(0.03, 0.8, h_trans_bandwidth=0.2, l_trans_bandwidth=0.02) # Band-pass filtering the data
            fig = filtered_haemo.plot(n_channels=100, duration=file_duration)
            fig.figure.savefig(os.path.join(to_preproc_path, direc, direc + "FilteredHaemoglobin.png"))

            # Clean up data into epochs
            events, event_dict = mne.events_from_annotations(filtered_haemo)
            #reject_criteria = dict(hbo=80e-6)

            epochs = mne.Epochs(
                filtered_haemo,
                events, 
                event_id=event_dict, 
                tmin=0, tmax=stimulus_duration,
                reject_by_annotation=True, 
                baseline=(0, 0)
            )
            epochs.drop_bad()
            fig = epochs.plot_drop_log()
            fig.figure.savefig(os.path.join(to_preproc_path, direc, direc + "DropLog.png"))

            # Print some info for log purposes
            print(np.shape(epochs.get_data()))
            print(epochs.info)
            print(epochs.event_id)

            # Finally, save the preprocessed epochs into a data file
            preprocessed_epochs = epochs.get_data(copy=True)
            print(np.shape(preprocessed_epochs))

            with open(os.path.join(to_preproc_path, direc, direc + "PreprocessedData.npy"), 'wb') as fil:
                np.save(arr=preprocessed_epochs, file=fil)
        else:
            continue

    

if __name__ == '__main__':
    main()