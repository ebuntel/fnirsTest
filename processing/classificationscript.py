import torch 
import os

import numpy as np

# Load data from each folder in /data/toPreProc/

data_dict = {}
label_dict = {}

for folder in os.listdir('data/toPreProc/'):
    print("Folder name: ", folder)
    data_dict[folder] = np.load(f'data/toPreProc/{folder}/{folder}PreprocessedData.npy')
    labels = np.load(f'data/toPreProc/{folder}/{folder}Labels.npy', allow_pickle=True)
    label_dict[folder] = labels[:-1, 2]
    print("Data shape: ", data_dict[folder].shape)
    print("Label shape: ", label_dict[folder].shape)
