from python_files.spalten.PrivacyLevel import PrivacyLevel

# Beispiel Dictionary
dict_level1 = {
    "[0-9]": range(int(0), int(9)+1),
    "[10-19]": range(int(10), int(19)+1),
    "[20-29]": range(int(20), int(29)+1),
    "[30-39]": range(int(30), int(39)+1),
    "[40-49]": range(int(40), int(49)+1),
    "[50-59]": range(int(50), int(59)+1),
    "[60-69]": range(int(60), int(69)+1),
    "[70-79]": range(int(70), int(79)+1),
    "[80-90]": range(int(80), int(90)+1)
}
dict_level2 = {
    "jung": range(int(0), int(29)+1),
    "mittel": range(int(30), int(59)+1),
    "alt": range(int(60), int(90)+1)
}
dict_level3 = {
    "?": range(int(0), int(90)+1)
}

dict_all = {
    PrivacyLevel.LEVEL1: dict_level1,
    PrivacyLevel.LEVEL2: dict_level2,
    PrivacyLevel.LEVEL3: dict_level3
}

name = "age"

# Funktion, um den Wert für einen Schlüssel zu erhalten
def get_value(key):
    for dict_name, age_dict in dict_all.items():
        if key in age_dict:
            return age_dict[key]
    return None
    

# Funktion, um den Schlüssel für einen Wert zu erhalten
def get_key(value, privacy_level: PrivacyLevel):
    for key, age_range in dict_all[privacy_level].items():
        if int(value) in age_range:
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
    if privacy_level == PrivacyLevel.LEVEL3 or privacy_level == PrivacyLevel.LEVEL2:
        return value
    if privacy_level == PrivacyLevel.LEVEL1:
        orignal_value = get_value(value)[0]
        return get_key(orignal_value, PrivacyLevel.LEVEL2)
    if privacy_level == PrivacyLevel.LEVEL0:
        return get_key(value, PrivacyLevel.LEVEL2)