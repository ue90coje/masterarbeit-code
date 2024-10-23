from enum import Enum
from python_files.spalten.Spalten import Spalten

class Anonymization(Enum):
    no = []
    basic = [Spalten.AGE, Spalten.SEX, Spalten.RACE]
    moderate = [Spalten.AGE, Spalten.SEX, Spalten.RACE, Spalten.NATIVE_COUNTRY, Spalten.EDUCATION, Spalten.OCCUPATION]
    strong = [Spalten.AGE, Spalten.SEX, Spalten.RACE, Spalten.NATIVE_COUNTRY, Spalten.EDUCATION, Spalten.OCCUPATION, 
                  Spalten.MARITAL_STATUS, Spalten.CAPITAL_GAIN, Spalten.CAPITAL_LOSS, Spalten.HOURS_PER_WEEK]
    complete = [e for e in Spalten]

