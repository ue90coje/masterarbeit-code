from python_files.spalten import Age, HoursPerWeek, Race, Sex, NativeCountry, Education, EducationNum, Workclass, FnlWgt, MaritalStatus, Occupation, CapitalGain, CapitalLoss, Relationship
from enum import Enum

class Spalten(Enum):
    AGE = Age
    FNLWGT = FnlWgt
    CAPITAL_GAIN = CapitalGain
    CAPITAL_LOSS = CapitalLoss
    HOURS_PER_WEEK = HoursPerWeek
    SEX = Sex
    WORKCLASS = Workclass
    EDUCATION = Education
    MARITAL_STATUS = MaritalStatus
    OCCUPATION = Occupation
    RELATIONSHIP = Relationship
    RACE = Race
    NATIVE_COUNTRY = NativeCountry