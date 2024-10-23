from python_files.spalten.PrivacyLevel import PrivacyLevel

# Beispiel Dictionary
dict_level1 = {
    "[0-99]": range(int(0), int(99)+1),
    "[100-999]": range(int(100), int(999)+1),
    "[1000-1999]": range(int(1000), int(1999)+1),
    "[2000-4999]": range(int(2000), int(4999)+1),
    "[5000-9999]": range(int(5000), int(9999)+1),
    "[10000-19999]": range(int(10000), int(19999)+1),
    "[20000-99999]": range(int(20000), int(99999)+1)
}
dict_level2 = {
    "?": range(int(0), int(99999)+1)
}

dict_all = {
    PrivacyLevel.LEVEL1: dict_level1,
    PrivacyLevel.LEVEL2: dict_level2
}

name = "capital-gain"

# Funktion, um den Wert für einen Schlüssel zu erhalten
def get_value(key):
    for dict_name, dict in dict_all.items():
        if key in dict:
            return dict[key]
    return None
    

# Funktion, um den Schlüssel für einen Wert zu erhalten
def get_key(value, privacy_level: PrivacyLevel):
    for key, range in dict_all[privacy_level].items():
        if int(value) in range:
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