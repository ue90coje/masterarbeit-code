from python_files.spalten.PrivacyLevel import PrivacyLevel

# Beispiel Dictionary
dict_level1 = {
    "untergewicht": range(int(12), int(19)+1),
    "normal": range(int(20), int(25)+1),
    "uebergewicht": range(int(26), int(30)+1),
    "adipositas1": range(int(31), int(35)+1),
    "adipositas2": range(int(36), int(40)+1),
    "[41-50]": range(int(41), int(50)+1),
    "[51-60]": range(int(51), int(60)+1),
    "[61-70]": range(int(61), int(70)+1),
    "[71-80]": range(int(71), int(80)+1),
    "[>80]": range(int(81), int(98)+1)
}
dict_level2 = {
    "gering": range(int(12), int(25)+1),
    "mittel": range(int(26), int(40)+1),
    "hoch": range(int(41), int(98)+1)
}
dict_level3 = {
    "?": range(int(12), int(98)+1)
}

dict_all = {
    PrivacyLevel.LEVEL1: dict_level1,
    PrivacyLevel.LEVEL2: dict_level2,
    PrivacyLevel.LEVEL2: dict_level3
}

name = "BMI"

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
    if privacy_level == PrivacyLevel.LEVEL3 or privacy_level == PrivacyLevel.LEVEL2:
        return value
    if privacy_level == PrivacyLevel.LEVEL1:
        orignal_value = get_value(value)[0]
        return get_key(orignal_value, PrivacyLevel.LEVEL2)
    if privacy_level == PrivacyLevel.LEVEL0:
        return get_key(value, PrivacyLevel.LEVEL2)