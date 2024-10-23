from enum import Enum
from python_files.spalten.Spalten import Spalten

class Anonymization(Enum):
    no = []
    basic = [Spalten.AGE, Spalten.SEX, Spalten.INCOME, Spalten.EDUCATION]
    moderate = [Spalten.AGE, Spalten.SEX, Spalten.INCOME, Spalten.EDUCATION, Spalten.BMI, Spalten.HIGH_BP, Spalten.HIGH_CHOL, Spalten.STROKE, Spalten.HEART_DISEASEOR_ATTACK]
    strong = [Spalten.AGE, Spalten.SEX, Spalten.INCOME, Spalten.EDUCATION, Spalten.BMI, Spalten.HIGH_BP, Spalten.HIGH_CHOL, Spalten.STROKE, Spalten.HEART_DISEASEOR_ATTACK,
              Spalten.SMOKER, Spalten.PHYS_ACTIVITY, Spalten.FRUITS, Spalten.VEGGIES, Spalten.HVY_ALCOHOL_CONSUMP, Spalten.GEN_HLTH, Spalten.MENT_HLTH, Spalten.PHYS_HLTH, Spalten.DIFF_WALK]
    complete = [e for e in Spalten]

