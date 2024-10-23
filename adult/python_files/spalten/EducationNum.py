from python_files.spalten.PrivacyLevel import PrivacyLevel

# Beispiel Dictionary
dict_level1 = {
    "[1-4]": range(int(1), int(4)+1),
    "[5-8]": range(int(5), int(8)+1),
    "[9-12]": range(int(9), int(12)+1),
    "[13-16]": range(int(13), int(16)+1)
}
dict_level2 = {
    "?": range(int(1), int(16)+1)
}

dict_all = {
    PrivacyLevel.LEVEL1: dict_level1,
    PrivacyLevel.LEVEL2: dict_level2
}

name = "education-num"

# Funktion, um den Wert für einen Schlüssel zu erhalten
def get_value(key):
    for dict_name, age_dict in dict_all.items():
        if key in age_dict:
            return age_dict[key]
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


education_num_mapping = {
    "Preschool": 1,
    "1st-4th": 2,
    "5th-6th": 3,
    "7th-8th": 4,
    "9th": 5,
    "10th": 6,
    "11th": 7,
    "12th": 8,
    "HS-grad": 9,
    "Some-college": 10,
    "Assoc-voc": 11,
    "Assoc-acdm": 12,
    "Bachelors": 13,
    "Masters": 14,
    "Prof-school": 15,
    "Doctorate": 16
}