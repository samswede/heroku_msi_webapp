import pickle
import os
import numpy as np


def convert_numbers_to_strings(input_list):
    return [str(item) for item in input_list]

def convert_strings_to_numbers(input_list):
    return [int(item) if item.isdigit() else item for item in input_list]

def load_data_dict(file_name):
    with open(f'{file_name}.pickle', 'rb') as handle:
        loaded_dict = pickle.load(handle)
    return loaded_dict

def save_data_dict(file_name, map_labels_to_indices):
    # assuming map_labels_to_indices is your dictionary
    with open(f'{file_name}.pickle', 'wb') as handle:
        pickle.dump(map_labels_to_indices, handle, protocol=pickle.HIGHEST_PROTOCOL)
    pass

def combine_all_vectors_and_labels(path):
    file_list = [file for file in os.listdir(path) if file.endswith('.npy')]
    
    # Preallocate a list of arrays
    arrays_list = []
    
    label_to_index = {}
    
    for index, file in enumerate(file_list):
        array = np.load(os.path.join(path, file))
        arrays_list.append(array)
        # Extract the label name from the file name by removing '.npy' and add it to the dictionary
        label_name = os.path.splitext(file)[0].replace('diffusion_profile_', '')
        label_to_index[label_name] = index
    
    # Stack all arrays at once
    combined_array = np.vstack(arrays_list)
    
    return combined_array, label_to_index

def load_diffusion_profiles(data_path):
    # Load diffusion profiles
    with np.load(f'{data_path}compressed_diffusion_profiles.npz') as data:
        drug_diffusion_profiles = data['arr1']
        indication_diffusion_profiles = data['arr2']
    return drug_diffusion_profiles, indication_diffusion_profiles

def load_dictionaries(data_path):
    map_drug_diffusion_labels_to_indices = load_data_dict(f'{data_path}map_drug_labels_to_indices')
    map_drug_diffusion_indices_to_labels = {v: k for k, v in map_drug_diffusion_labels_to_indices.items()}
    map_indication_diffusion_labels_to_indices = load_data_dict(f'{data_path}map_indication_labels_to_indices')
    map_indication_diffusion_indices_to_labels = {v: k for k, v in map_indication_diffusion_labels_to_indices.items()}
    
    return map_drug_diffusion_labels_to_indices, map_drug_diffusion_indices_to_labels, map_indication_diffusion_labels_to_indices, map_indication_diffusion_indices_to_labels
