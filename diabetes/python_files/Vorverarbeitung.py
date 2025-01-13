import pandas as pd
from python_files.spalten.Spalten import Spalten
from python_files.VorverarbeitungsDatensatz import VorverarbeitungsDatensatz
import os
from enum import Enum
from python_files.Anonymization import Anonymization
from sklearn.model_selection import train_test_split


#enum mit drei szenarien
class Preparing_Method(Enum):
    weighted_specialization = "weighted specialization"
    specialization = "specialization"
    forced_generalization = "forced generalization"
    weighted_specialization_highest_confidence = "highest confidence"
    no_preprocessing = "no preprocessing"
    extended_weighted_specialization = "extended weighted specialization"
    complete_weighted_specialization = "complete weighted specialization"
    complete_forced_generalization = "complete forced generalization"
    complete_no_preprocessing = "complete no preprocessing"


NUMERICAL_COLUMNS = [Spalten.AGE, Spalten.BMI, Spalten.GEN_HLTH, Spalten.MENT_HLTH, Spalten.PHYS_HLTH, Spalten.EDUCATION, Spalten.INCOME]


def prepare_specialization(complete_anonymization: bool):
    df = get_anonymized_data(complete_anonymization)
    folder_name = "komplett_spezialisiert" if complete_anonymization else "spezialisiert"
    specialize_data_and_save_to_csv(df, folder_name)

def prepare_forced_generalization(complete_anonymization: bool):
    df = get_anonymized_data(complete_anonymization)
    folder_name = "komplett_zwangsgeneralisiert" if complete_anonymization else "zwangsgeneralisiert"
    preprocess_data_to_highest_privacy_level(df, folder_name)

def prepare_extended_specialization(complete_anonymization: bool):
    df = get_anonymized_data(complete_anonymization)
    folder_name = "komplett_erweitert_spezialisiert" if complete_anonymization else "erweitert_spezialisiert"
    specialize_data_extended_and_save_to_csv(df, folder_name)



def get_anonymized_data(complete_anonymization: bool):
    if not complete_anonymization:
        manipulated_data_train = pd.read_csv('dataset/anonymisiert/diabetes_train.csv')
        manipulated_data_test = pd.read_csv('dataset/anonymisiert/diabetes_test.csv')
        df = pd.concat([manipulated_data_train, manipulated_data_test])
        df = df.reset_index(drop=True)
        return df
    else:
        manipulated_data_train = pd.read_csv('dataset/komplett_anonymisiert/diabetes_train.csv')
        manipulated_data_test = pd.read_csv('dataset/komplett_anonymisiert/diabetes_test.csv')
        df = pd.concat([manipulated_data_train, manipulated_data_test])
        df = df.reset_index(drop=True)
        return df


#daten für erweiterte spezialisierung vorverarbeiten
#Für numerische Spalte AGE werden zusaätzlich neue Einträge erzeugt
def specialize_data_extended_and_save_to_csv(df: pd.DataFrame, folder_name: str):
    #Gehe alle Enums Spalten durch
    for column in Spalten:
        #betrachte nur die Spalten record_id und aktuelle Spalte
        actual_df = df[["record_id", column.value.name]]
        vorverarbeitungs_datensatz = VorverarbeitungsDatensatz(actual_df)
        if column in NUMERICAL_COLUMNS and column != Spalten.AGE:
            vorverarbeitungs_datensatz.ersetze_durch_mittelwert([column])
        else:
            vorverarbeitungs_datensatz.erstelle_neue_zeilen([column])
        #speichere das Dataframe als CSV
        vorverarbeitungs_datensatz.write_to_csv("dataset/" + folder_name + "/" + column.value.name + "_vorverarbeitet.csv")
        print(f"Dataframe {column.value.name} wurde vorverarbeitet und gespeichert")


#daten für spezialisierung vorverarbeiten
def specialize_data_and_save_to_csv(df: pd.DataFrame, folder_name: str):
    #Gehe alle Enums Spalten durch
    for column in Spalten:
        #betrachte nur die Spalten record_id und aktuelle Spalte
        actual_df = df[["record_id", column.value.name]]
        vorverarbeitungs_datensatz = VorverarbeitungsDatensatz(actual_df)
        if column in NUMERICAL_COLUMNS:
            vorverarbeitungs_datensatz.ersetze_durch_mittelwert([column])
        else:
            vorverarbeitungs_datensatz.erstelle_neue_zeilen([column])
        #speichere das Dataframe als CSV
        vorverarbeitungs_datensatz.write_to_csv("dataset/" + folder_name + "/" + column.value.name + "_vorverarbeitet.csv")
        print(f"Dataframe {column.value.name} wurde vorverarbeitet und gespeichert")


#zwangsgeneralisierte Daten vorverarbeiten
def preprocess_data_to_highest_privacy_level(df: pd.DataFrame, folder_name: str):
    #Gehe alle Enums Spalten durch
    for column in Spalten:
        for index, row in df.iterrows():
            df.at[index, column.value.name] = column.value.get_highest_privacy_value(row[column.value.name])
        print(f"Spalte {column.value.name} wurde vorverarbeit")
    
    write_to_csv(df, "dataset/" + folder_name + "/vorverarbeitet.csv")

def write_to_csv(data, path:str):
    #split path in directory and filename
    outdir = os.path.dirname(path)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    data.to_csv(path, index=False)

def get_anonymized_data_analysis(anonymization: Anonymization):
    df_train = pd.read_csv('dataset/anonymisiert/diabetes_train.csv')
    df_train.drop(columns=['record_id', "Diabetes_binary"], inplace=True)
    df_test = pd.read_csv('dataset/anonymisiert/diabetes_test.csv')
    df_test.drop(columns=['record_id', "Diabetes_binary"], inplace=True)
    total_features = len(df_train.columns)
    total_generalized_train = 0
    total_missing_train = 0
    total_generalized_test = 0
    total_missing_test = 0
    for column in anonymization.value:
        generalized_train, missing_train = get_data_analysis_by_column(column, df_train)
        total_generalized_train += generalized_train
        total_missing_train += missing_train
        generalized_test, missing_test = get_data_analysis_by_column(column, df_test)
        total_generalized_test += generalized_test
        total_missing_test += missing_test

    generalized_ratio_train = total_generalized_train/total_features
    missing_ratio_train = total_missing_train/total_features
    original_ratio_train = 1 - generalized_ratio_train - missing_ratio_train
    generalized_ratio_test = total_generalized_test/total_features
    missing_ratio_test = total_missing_test/total_features
    original_ratio_test = 1 - generalized_ratio_test - missing_ratio_test
    generalized_ratio = (generalized_ratio_train + generalized_ratio_test)/2
    missing_ratio = (missing_ratio_train + missing_ratio_test)/2
    original_ratio = (original_ratio_train + original_ratio_test)/2
    print(f"Train: Original: {original_ratio_train}, Generalized: {generalized_ratio_train}, Missing: {missing_ratio_train}")
    print(f"Test: Original: {original_ratio_test}, Generalized: {generalized_ratio_test}, Missing: {missing_ratio_test}")
    print(f"Total: Original: {original_ratio}, Generalized: {generalized_ratio}, Missing: {missing_ratio}")


        

def get_data_analysis_by_column(column: Spalten, df):
    print(f"Spalte {column.value.name} wird analysiert")
    print(f"Anzahl Einträge: {df[column.value.name].count()}")
    total_values = df[column.value.name].count()
    original = 0
    generalized = 0
    missing = 0
    #Gehe jeden Wert der Spalte durch
    for index, row in df.iterrows():
        value = row[column.value.name]
        if value == "?":
            missing += 1
        elif column.value.is_generalized(value):
            generalized += 1
        else:
            original += 1
    print(f"Original: {original/total_values}, Generalized: {generalized/total_values}, Missing: {missing/total_values}")
    return generalized/total_values, missing/total_values


def clean_and_split_data(dataset_name: str):
    """
    This function cleans the dataset and splits it into a training and a test set.
    
    Parameters:
        dataset_name: The name of the dataset. The dataset should be stored in the 'dataset' folder as a CSV file. Don't include the file extension.
    """
    data= pd.read_csv('dataset/' + dataset_name + '.csv', na_values=['?'])
    data.dropna(inplace=True)
    data = convert_floats_to_ints(data)
    data.to_csv('dataset/' + dataset_name + '_cleaned.csv', index_label='record_id')
    data= pd.read_csv('dataset/' + dataset_name + '_cleaned.csv')
    data_train, data_test = train_test_split(data, test_size=0.2, random_state=0)
    data_train.shape, data_test.shape
    data_train.to_csv('dataset/' + dataset_name + '_train.csv', index=False)
    data_test.to_csv('dataset/' + dataset_name + '_test.csv', index=False)

def convert_floats_to_ints(df):
    for col in df.columns:
        # Nur auf float-Spalten anwenden
        if pd.api.types.is_float_dtype(df[col]):
            # Bedingung: Wert ist float und gleich dem gerundeten Wert
            df[col] = df[col].apply(lambda x: int(x) if x.is_integer() else x)
    return df