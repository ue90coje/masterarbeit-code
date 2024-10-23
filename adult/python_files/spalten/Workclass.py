from python_files.spalten.PrivacyLevel import PrivacyLevel

# Beispiel Dictionary
dict_level1 = {
    "private_sector": ['Private'],
    "self_emp": ['Self-emp-inc', 'Self-emp-not-inc'],
    "gov": ['Federal-gov', 'Local-gov', 'State-gov'],
    "without_pay": ['Without-pay']
}
dict_level2 = {
    "?": ['Federal-gov', 'Local-gov', 'Private', 'Self-emp-inc', 'Self-emp-not-inc', 'State-gov', 'Without-pay']
}
dict_all = {
    PrivacyLevel.LEVEL1: dict_level1,
    PrivacyLevel.LEVEL2: dict_level2
}

name = "workclass"

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