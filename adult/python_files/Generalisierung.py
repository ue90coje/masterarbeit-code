from python_files.spalten.PrivacyLevel import PrivacyLevel
import numpy as np
from python_files.spalten.Spalten import Spalten


def generalisiere(data, column: Spalten, privacy_levels_to_probability: dict[PrivacyLevel, float]):
    data[column.value.name] = data[column.value.name].astype(object)
    for i in range(len(data[column.value.name])):
        privacy_level = np.random.choice(list(privacy_levels_to_probability.keys()), p=list(privacy_levels_to_probability.values()))
        if privacy_level == PrivacyLevel.LEVEL0:
            continue
        else:
            data.at[i, column.value.name] = column.value.get_key(data.at[i, column.value.name], privacy_level)
    return data

def generalisiere_gleichverteilt(data, columns: list[Spalten]):
    for column in columns:
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
    return data