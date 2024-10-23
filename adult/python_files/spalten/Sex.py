from python_files.spalten.PrivacyLevel import PrivacyLevel


dict_level1 = {
    "?": ['Male', 'Female']
}

dict_all = {
    PrivacyLevel.LEVEL1: dict_level1
}

name = "sex"

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
    if privacy_level == PrivacyLevel.LEVEL1 or privacy_level == PrivacyLevel.LEVEL0:
        return value