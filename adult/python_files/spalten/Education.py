from python_files.spalten.PrivacyLevel import PrivacyLevel

# Beispiel Dictionary
dict_level1 = {
    "elementary_school": ["Preschool", "1st-4th", "5th-6th", "7th-8th"],
    "high_school": ["9th", "10th", "11th", "12th"],
    "high_school_graduate": ["HS-grad", "Some-college", "Assoc-voc", "Assoc-acdm"],
    "bachelor_and_higher": ["Bachelors", "Masters", "Prof-school", "Doctorate"]
}
dict_level2 = {
    "?": ["Preschool", "1st-4th", "5th-6th", "7th-8th", "9th", "10th", "11th", "12th", "HS-grad", "Some-college", "Assoc-voc", "Assoc-acdm", "Bachelors", "Masters", "Prof-school", "Doctorate"]
}

dict_all = {
    PrivacyLevel.LEVEL1: dict_level1,
    PrivacyLevel.LEVEL2: dict_level2
}

name = "education"

# Funktion, um den Wert für einen Schlüssel zu erhalten
def get_value(key):
    for dict_name, age_dict in dict_all.items():
        if key in age_dict:
            return age_dict[key]
    return None
    

# Funktion, um den Schlüssel für einen Wert zu erhalten
def get_key(value, privacy_level: PrivacyLevel):
    for key, age_range in dict_all[privacy_level].items():
        if value in age_range:
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