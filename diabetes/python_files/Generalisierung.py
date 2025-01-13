from python_files.spalten.PrivacyLevel import PrivacyLevel
import numpy as np
from python_files.spalten.Spalten import Spalten
import pandas as pd
import os

train_data_name = "diabetes_train"
test_data_name = "diabetes_test"

def generalize_uniform_train_and_test_data(with_level0:bool = True):
    generalisiere_gleichverteilt(train_data_name, with_level0)
    generalisiere_gleichverteilt(test_data_name, with_level0)

def generalisiere(data, column: Spalten, privacy_levels_to_probability: dict[PrivacyLevel, float]):
    data[column.value.name] = data[column.value.name].astype(object)
    for i in range(len(data[column.value.name])):
        privacy_level = np.random.choice(list(privacy_levels_to_probability.keys()), p=list(privacy_levels_to_probability.values()))
        if privacy_level == PrivacyLevel.LEVEL0:
            continue
        else:
            data.at[i, column.value.name] = column.value.get_key(data.at[i, column.value.name], privacy_level)
    return data


def generalisiere_gleichverteilt(dataset_name:str, with_level0: bool):
    data= pd.read_csv('dataset/' + dataset_name + '.csv')
    for column in Spalten:
        data[column.value.name] = data[column.value.name].astype(object)
        if with_level0:
            privacy_levels = [PrivacyLevel.LEVEL0]
        else:
            privacy_levels = []
        #Die PrivacyLevels, die als Key in dict_all vorkommen, werden in privacy_levels hinzu gefügt
        for privacy_level in column.value.dict_all.keys():
            privacy_levels.append(privacy_level)
        
        for i in range(len(data[column.value.name])):
            privacy_level = np.random.choice(privacy_levels)
            if privacy_level == PrivacyLevel.LEVEL0:
                continue
            else:
                data.at[i, column.value.name] = column.value.get_key(data.at[i, column.value.name], privacy_level)
    
    if with_level0:
        write_to_csv(data, 'dataset/anonymisiert/' + dataset_name + '.csv')
    else:
        write_to_csv(data, 'dataset/komplett_anonymisiert/' + dataset_name + '.csv')


def write_to_csv(data, path:str):
    #split path in directory and filename
    outdir = os.path.dirname(path)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    data.to_csv(path, index=False)