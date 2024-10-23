from python_files.spalten.PrivacyLevel import PrivacyLevel
import numpy as np
from python_files.spalten.Spalten import Spalten
import pandas as pd
import os

train_data_name = "diabetes_train"
test_data_name = "diabetes_test"

def generalisiere(data, column: Spalten, privacy_levels_to_probability: dict[PrivacyLevel, float]):
    data[column.value.name] = data[column.value.name].astype(object)
    for i in range(len(data[column.value.name])):
        privacy_level = np.random.choice(list(privacy_levels_to_probability.keys()), p=list(privacy_levels_to_probability.values()))
        if privacy_level == PrivacyLevel.LEVEL0:
            continue
        else:
            data.at[i, column.value.name] = column.value.get_key(data.at[i, column.value.name], privacy_level)
    return data

def generalize_uniform_train_and_test_data():
    generalisiere_gleichverteilt(train_data_name)
    generalisiere_gleichverteilt(test_data_name)


def generalisiere_gleichverteilt(dataset_name:str):
    data= pd.read_csv('dataset/' + dataset_name + '.csv')
    for column in Spalten:
        data[column.value.name] = data[column.value.name].astype(object)
        privacy_levels = [PrivacyLevel.LEVEL0]
        #Die PrivacyLevels, die als Key in dict_all vorkommen, werden in privacy_levels hinzu gefügt
        for privacy_level in column.value.dict_all.keys():
            privacy_levels.append(privacy_level)
        
        for i in range(len(data[column.value.name])):
            privacy_level = np.random.choice(privacy_levels)
            if privacy_level == PrivacyLevel.LEVEL0:
                continue
            else:
                data.at[i, column.value.name] = column.value.get_key(data.at[i, column.value.name], privacy_level)
    
    write_to_csv(data, 'dataset/manipuliert/' + dataset_name + '.csv')


def write_to_csv(data, path:str):
    #split path in directory and filename
    outdir = os.path.dirname(path)

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    data.to_csv(path, index=False)