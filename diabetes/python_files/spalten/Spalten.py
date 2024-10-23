from python_files.spalten import Age, HighBP, HighChol, CholCheck, Sex, BMI, Smoker, Stroke, HeartDiseaseorAttack, PhysActivity, Fruits, Veggies, HvyAlcoholConsump, AnyHealthcare
from python_files.spalten import NoDocbcCost, GenHlth, MentHlth, PhysHlth, DiffWalk, Education, Income
from enum import Enum

class Spalten(Enum):
    HIGH_BP = HighBP
    HIGH_CHOL = HighChol
    CHOL_CHECK = CholCheck
    BMI = BMI
    SMOKER = Smoker
    STROKE = Stroke
    HEART_DISEASEOR_ATTACK = HeartDiseaseorAttack
    PHYS_ACTIVITY = PhysActivity
    FRUITS = Fruits
    VEGGIES = Veggies
    HVY_ALCOHOL_CONSUMP = HvyAlcoholConsump
    ANY_HEALTHCARE = AnyHealthcare
    NODOCBC_COST = NoDocbcCost
    GEN_HLTH = GenHlth
    MENT_HLTH = MentHlth
    PHYS_HLTH = PhysHlth
    DIFF_WALK = DiffWalk
    SEX = Sex
    AGE = Age
    EDUCATION = Education
    INCOME = Income