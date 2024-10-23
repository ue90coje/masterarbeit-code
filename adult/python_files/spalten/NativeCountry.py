from python_files.spalten.PrivacyLevel import PrivacyLevel

# Beispiel Dictionary
dict_level1 = {
    "Europa": ['Germany', 'Greece', 'England', 'Italy', 'Poland', 'Portugal', 'Ireland', 'France', 'Hungary', 'Holand-Netherlands', 'Scotland', 'Yugoslavia', ],
    "Amerika": ['United-States', 'Canada', 'Cuba', 'Mexico', 'Ecuador', 'Puerto-Rico', 'Outlying-US(Guam-USVI-etc)', 'Columbia', 'Nicaragua', 'Peru', 'Honduras', 'Jamaica', 'Dominican-Republic', 'El-Salvador', 'Haiti', 'Guatemala', 'Trinadad&Tobago'],
    "Asien": ['India', 'Japan', 'China', 'Iran', 'Philippines', 'Vietnam', 'Taiwan', 'Cambodia', 'Thailand', 'Hong', 'Laos', ],
    "Afrika": ['South']
}
dict_level2 = {
    "?": ['United-States', 'Cambodia', 'England', 'Puerto-Rico', 'Canada', 'Germany', 'Outlying-US(Guam-USVI-etc)', 'India', 'Japan', 'Greece', 'South', 'China', 'Cuba', 'Iran', 'Honduras', 'Philippines', 'Italy', 'Poland', 'Jamaica', 'Vietnam', 'Mexico', 'Portugal', 'Ireland', 'France', 'Dominican-Republic', 'Laos', 'Ecuador', 'Taiwan', 'Haiti', 'Columbia', 'Hungary', 'Guatemala', 'Nicaragua', 'Scotland', 'Thailand', 'Yugoslavia', 'El-Salvador', 'Trinadad&Tobago', 'Peru', 'Hong', 'Holand-Netherlands']
}

dict_all = {
    PrivacyLevel.LEVEL1: dict_level1,
    PrivacyLevel.LEVEL2: dict_level2
}

name = "native-country"

# Funktion, um den Wert für einen Schlüssel zu erhalten
def get_value(key):
    for dict_name, dict in dict_all.items():
        if key in dict:
            return dict[key]
    return None
    

# Funktion, um den Schlüssel für einen Wert zu erhalten
def get_key(value, privacy_level: PrivacyLevel):
    for key, range in dict_all[privacy_level].items():
        if value in range:
            return key
    
    raise ValueError(f"Der Wert {value} vom Typ {type(value)} wurde nicht gefunden in der Rubrik {name}")

# Funktion, die überrüft, ob ein Wert ein Key eines Dictionaries ist
def is_generalized(key):
    for dict_name, dict in dict_all.items():
        if key in dict:
            return True
    return False


def get_privacy_level_for_value(value):
    for privacy_level, values in dict_all.items():
        if value in values.keys():
            return privacy_level
    return PrivacyLevel.LEVEL0

def get_highest_privacy_value(value):
    privacy_level = get_privacy_level_for_value(value)
    if privacy_level == PrivacyLevel.LEVEL2 or privacy_level == PrivacyLevel.LEVEL1:
        return value
    if privacy_level == PrivacyLevel.LEVEL0:
        return get_key(value, PrivacyLevel.LEVEL1)