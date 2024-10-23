import pandas as pd
from python_files.spalten.Spalten import Spalten
from python_files.Anonymization import Anonymization
import dask.dataframe as dd
from python_files.Vorverarbeitung import Szenario

class Data_Loader:
    szenario1_path = "dataset/szenario1/"
    scenario6_path = "dataset/szenario6/"
    sceanrio_3_file_path = "dataset/szenario3/vorverarbeitet.csv"
    generalized_train_path = "dataset/manipuliert/diabetes_train.csv"
    generalized_test_path = "dataset/manipuliert/diabetes_test.csv"
    normal_path = "dataset/"
    NUMERICAL_COLUMNS = [Spalten.AGE, Spalten.BMI, Spalten.GEN_HLTH, Spalten.MENT_HLTH, Spalten.PHYS_HLTH, Spalten.EDUCATION, Spalten.INCOME]

    def __init__(self, szeanrio: Szenario):
        self.data_train_original = pd.read_csv('dataset/diabetes_train.csv')
        self.data_test_original = pd.read_csv('dataset/diabetes_test.csv')
        self.data_train = dd.from_pandas(self.data_train_original, npartitions=16)
        self.data_test = dd.from_pandas(self.data_test_original, npartitions=16)
        self.szenario = szeanrio

    def preprocess_scenario_1_and_2(self, columns: list[Spalten], manipulate_test_data: bool):
        for column in columns:
            preprocessed_df = pd.read_csv(self.szenario1_path + column.value.name + "_vorverarbeitet.csv")
            for column_to_drop in preprocessed_df.columns:
                if column_to_drop != "record_id":
                    self.data_train = self.data_train.drop(column_to_drop, axis=1)
                    if manipulate_test_data:
                        self.data_test = self.data_test.drop(column_to_drop, axis=1)
            preprocessed_ddf = dd.from_pandas(preprocessed_df, npartitions=16)

            self.data_train = dd.merge(self.data_train, preprocessed_ddf, on='record_id')
            self.data_train.repartition(npartitions=16)
            if manipulate_test_data:
                self.data_test = dd.merge(self.data_test, preprocessed_ddf, on='record_id')
                self.data_test.repartition(npartitions=16)

            print(f"Merged {columns.index(column)+1}/{len(columns)} columns.")


    # Funktion zum Erstellen des kartesischen Produkts für eine Gruppe
    def cartesian_product(self, group1, group2):
        return pd.merge(group1, group2, on='record_id')

    #def get_data_original(self):
        #return self.data_train_original, self.data_test_original
    
    def get_data(self):
        self.set_types()
        # for column in self.CATEGORICAL_COLUMNS:
        #     self.data_train[column] = self.data_train[column].astype('category')
        #Ordne die Spalten von data_train und data_test in der gleichen Reihenfolge an
        self.data_train = self.data_train.reset_index(drop=True)
        self.data_test = self.data_test.reset_index(drop=True)
        column_order = list(self.data_test.columns)
        self.data_train = self.data_train[column_order].reset_index(drop=True)
        #self.data_test = self.data_test[self.data_train.columns].reset_index(drop=True)
        return self.data_train, self.data_test
    
    def set_types(self):
        data_original = pd.concat([self.data_train_original, self.data_test_original], ignore_index=True)
        all_data = dd.concat([self.data_train, self.data_test], ignore_index=True)
        if self.szenario == Szenario.Szenario3 or self.szenario == Szenario.Szenario5:
            all_data = all_data.compute()
        for column in data_original.columns:
            if self.szenario == Szenario.Szenario3 or self.szenario == Szenario.Szenario5:
                if column != "record_id" and column != "Diabetes_binary":
                    all_data[column] = all_data[column].astype('category')
                    self.data_train[column] = self.data_train[column].astype('category').cat.set_categories(all_data[column].cat.categories)
                    self.data_test[column] = self.data_test[column].astype('category').cat.set_categories(all_data[column].cat.categories)
                    
                     
            elif column not in map(lambda x: x.value.name, self.NUMERICAL_COLUMNS):
                data_original[column] = data_original[column].astype('category')
                self.data_train[column] = self.data_train[column].astype('category').cat.set_categories(data_original[column].cat.categories)
                self.data_test[column] = self.data_test[column].astype('category').cat.set_categories(data_original[column].cat.categories)
            else:
                try:
                    self.data_train[column] = self.data_train[column].astype('int32')
                    self.data_test[column] = self.data_test[column].astype('int32')
                except ValueError:
                    print(f"Spalte {column} konnte nicht in int32 konvertiert werden.")
                    raise ValueError
    
    def preprocess_scenario_3(self, user_group: Anonymization, manipulate_test_data: bool):
        vorverarbeitet = pd.read_csv(self.sceanrio_3_file_path)
        #spalten von vorverarbeitet als string
        print("Alle vorverarbeitet Spalten: " + str(vorverarbeitet.columns))
        #map user group values zu spaltennamen
        spaltennamen = list(map(lambda x: x.value.name, user_group.value))
        print("Spalten der User Group: " + str(spaltennamen))
        #nur die spalten behalten, die in der user group sind
        vorverarbeitet = vorverarbeitet.drop([column for column in vorverarbeitet.columns if column not in spaltennamen and column != "record_id"], axis=1)
        for column_to_drop in vorverarbeitet.columns:
            if column_to_drop != "record_id":
                self.data_train = self.data_train.drop(column_to_drop, axis=1)
                if manipulate_test_data:
                    self.data_test = self.data_test.drop(column_to_drop, axis=1)

        #Spalten von vorverarbeitet
        print("Spalten übrig: " + str(vorverarbeitet.columns))
        preprocessed_ddf = dd.from_pandas(vorverarbeitet, npartitions=2)

        self.data_train = dd.merge(self.data_train, preprocessed_ddf, on='record_id')
        self.data_train.repartition(npartitions=2)
        if manipulate_test_data:
            self.data_test = dd.merge(self.data_test, preprocessed_ddf, on='record_id')
            self.data_test.repartition(npartitions=2)

    def preprocess_scenario_5(self, anonymization: Anonymization, manipulate_test_data: bool):
        generalized = pd.concat([pd.read_csv(self.generalized_train_path), pd.read_csv(self.generalized_test_path)], ignore_index=True)
        spaltennamen = list(map(lambda x: x.value.name, anonymization.value))
        generalized = generalized.drop([column for column in generalized.columns if column not in spaltennamen and column != "record_id"], axis=1)
        for column_to_drop in generalized.columns:
            if column_to_drop != "record_id":
                self.data_train = self.data_train.drop(column_to_drop, axis=1)
                if manipulate_test_data:
                    self.data_test = self.data_test.drop(column_to_drop, axis=1)

        generalized_ddf = dd.from_pandas(generalized, npartitions=2)
        self.data_train = dd.merge(self.data_train, generalized_ddf, on='record_id')
        self.data_train.repartition(npartitions=2)
        if manipulate_test_data:
            self.data_test = dd.merge(self.data_test, generalized_ddf, on='record_id')
            self.data_test.repartition(npartitions=2)

    def preprocess_scenario_6(self, anonymization: Anonymization, manipulate_test_data: bool):
        for column in anonymization.value:
            preprocessed_df = pd.read_csv(self.scenario6_path + column.value.name + "_vorverarbeitet.csv")
            for column_to_drop in preprocessed_df.columns:
                if column_to_drop != "record_id":
                    self.data_train = self.data_train.drop(column_to_drop, axis=1)
                    if manipulate_test_data:
                        self.data_test = self.data_test.drop(column_to_drop, axis=1)
            preprocessed_ddf = dd.from_pandas(preprocessed_df, npartitions=16)

            self.data_train = dd.merge(self.data_train, preprocessed_ddf, on='record_id')
            self.data_train.repartition(npartitions=16)
            if manipulate_test_data:
                self.data_test = dd.merge(self.data_test, preprocessed_ddf, on='record_id')
                self.data_test.repartition(npartitions=16)

            print(f"Merged {anonymization.value.index(column)+1}/{len(anonymization.value)} columns.")
        