import pandas as pd
import numpy as np
from python_files.spalten.Spalten import Spalten
from python_files.VorverarbeitungsDatensatz import VorverarbeitungsDatensatz
import os
from enum import Enum
from python_files.UserGroups import Anonymization
from sklearn.model_selection import train_test_split


#enum mit drei szenarien
class Szenario(Enum):
    Szenario1 = "weighted specialization"
    Szenario2 = "specialization"
    Szenario3 = "forced generalization"
    Szenario4 = "maximum certainty"
    Szenario5 = "no preprocessing"
    Szenario6 = "specialization numerical"





def prepare_generalized_data(szenario: Szenario):
    manipulated_data_train = pd.read_csv('dataset/manipuliert/adult_train.csv')
    manipulated_data_test = pd.read_csv('dataset/manipuliert/adult_test.csv')
    df = pd.concat([manipulated_data_train, manipulated_data_test])
    df = df.reset_index(drop=True)

    if szenario == Szenario.Szenario1 or szenario == Szenario.Szenario2:
        prepare_columns_and_save_to_csv(df)
    elif szenario == Szenario.Szenario3:
        preprocess_data_to_highest_privacy_level(df)
    elif szenario == Szenario.Szenario6:
        specialize_data_with_numerical(df)
    else:
        print("Szenario nicht vorhanden")


def specialize_data_with_numerical(df: pd.DataFrame):
    #Gehe alle Enums Spalten durch
    for column in Spalten:
        #betrachte nur die Spalten record_id und aktuelle Spalte
        actual_df = df[["record_id", column.value.name]]
        vorverarbeitungs_datensatz = VorverarbeitungsDatensatz(actual_df)
        if column in [Spalten.FNLWGT, Spalten.CAPITAL_GAIN, Spalten.CAPITAL_LOSS, Spalten.HOURS_PER_WEEK]:
            vorverarbeitungs_datensatz.ersetze_durch_mittelwert([column])
        else:
            vorverarbeitungs_datensatz.erstelle_neue_zeilen_v2([column])
        #speichere das Dataframe als CSV
        vorverarbeitungs_datensatz.write_to_csv("dataset/szenario6/" + column.value.name + "_vorverarbeitet.csv")
        print(f"Dataframe {column.value.name} wurde vorverarbeitet und gespeichert")


#daten für szenario 1 und 2 vorverarbeiten
def prepare_columns_and_save_to_csv(df: pd.DataFrame):
    #Gehe alle Enums Spalten durch
    for column in Spalten:
        #betrachte nur die Spalten record_id und aktuelle Spalte
        actual_df = df[["record_id", column.value.name]]
        vorverarbeitungs_datensatz = VorverarbeitungsDatensatz(actual_df)
        if column in [Spalten.AGE, Spalten.FNLWGT, Spalten.CAPITAL_GAIN, Spalten.CAPITAL_LOSS, Spalten.HOURS_PER_WEEK]:
            vorverarbeitungs_datensatz.ersetze_durch_mittelwert([column])
        else:
            vorverarbeitungs_datensatz.erstelle_neue_zeilen_v2([column])
        #speichere das Dataframe als CSV
        vorverarbeitungs_datensatz.write_to_csv("dataset/vorverarbeitet/" + column.value.name + "_vorverarbeitet.csv")
        print(f"Dataframe {column.value.name} wurde vorverarbeitet und gespeichert")

def preprocess_data_to_highest_privacy_level(df: pd.DataFrame):
    #Gehe alle Enums Spalten durch
    for column in Spalten:
        for index, row in df.iterrows():
            df.at[index, column.value.name] = column.value.get_highest_privacy_value(row[column.value.name])
        print(f"Spalte {column.value.name} wurde vorverarbeit")
    
    df.to_csv("dataset/szenario3/vorverarbeitet.csv", index=False)


def get_data_analysis(anonymization: Anonymization):
    df_train = pd.read_csv('dataset/manipuliert/adult_train.csv')
    df_train.drop(columns=['record_id', "income"], inplace=True)
    df_test = pd.read_csv('dataset/manipuliert/adult_test.csv')
    df_test.drop(columns=['record_id', "income"], inplace=True)
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
    data= pd.read_csv('dataset/diabetes.csv', na_values=['?'])
    data.dropna(inplace=True)
    data.to_csv('dataset/diabetes_cleaned.csv', index_label='record_id')
    data= pd.read_csv('dataset/diabetes_cleaned.csv')
    data_train, data_test = train_test_split(data, test_size=0.2, random_state=0)
    data_train.shape, data_test.shape
    data_train.to_csv('dataset/diabetes_train.csv', index=False)
    data_test.to_csv('dataset/diabetes_test.csv', index=False)