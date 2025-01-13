import pandas as pd
from python_files.spalten.Spalten import Spalten
from python_files.Anonymization import Anonymization
import dask.dataframe as dd
from python_files.Vorverarbeitung import Preparing_Method
from python_files.Szenario import Szenario

class Data_Loader:
    generalized_train_path = "dataset/anonymisiert/diabetes_train.csv"
    generalized_test_path = "dataset/anonymisiert/diabetes_test.csv"
    complete_generalized_train_path = "dataset/komplett_anonymisiert/diabetes_train.csv"
    complete_generalized_test_path = "dataset/komplett_anonymisiert/diabetes_test.csv"
    specialized_path = "dataset/spezialisiert/"
    extended_specialized_path = "dataset/erweitert_spezialisiert/"
    forced_generalized_path = "dataset/zwangsgeneralisiert/"
    complete_specialized_path = "dataset/komplett_spezialisiert/"
    complete_extended_specialized_path = "dataset/komplett_erweitert_spezialisiert/"
    complete_forced_generalized_path = "dataset/komplett_zwangsgeneralisiert/"
    NUMERICAL_COLUMNS = [Spalten.AGE, Spalten.BMI, Spalten.GEN_HLTH, Spalten.MENT_HLTH, Spalten.PHYS_HLTH, Spalten.EDUCATION, Spalten.INCOME]
    partition_size = 32

    def __init__(self, method: Preparing_Method, szeanrio: Szenario):
        self.data_train_original = pd.read_csv('dataset/diabetes_train.csv')
        self.data_test_original = pd.read_csv('dataset/diabetes_test.csv')
        self.data_train = dd.from_pandas(self.data_train_original, npartitions=self.partition_size)
        self.data_test = dd.from_pandas(self.data_test_original, npartitions=self.partition_size)
        self.szenario = szeanrio
        self.method = method

        
    def preprocess(self, columns: list[Spalten]):
        if self.method == Preparing_Method.forced_generalization:
            self.preprocess_forced_generalization(prepared_dataset_path=self.forced_generalized_path, columns=columns)
        elif self.method == Preparing_Method.complete_forced_generalization:
            self.preprocess_forced_generalization(prepared_dataset_path=self.complete_forced_generalized_path, columns=columns)
        elif self.method == Preparing_Method.specialization or self.method == Preparing_Method.weighted_specialization or self.method == Preparing_Method.weighted_specialization_highest_confidence:
            self.preprocess_specialization(prepared_dataset_path=self.specialized_path, columns=columns)
        elif self.method == Preparing_Method.complete_weighted_specialization:
            self.preprocess_specialization(prepared_dataset_path=self.complete_specialized_path, columns=columns)
        elif self.method == Preparing_Method.extended_weighted_specialization:
            self.preprocess_specialization(prepared_dataset_path=self.extended_specialized_path, columns=columns)
        elif self.method == Preparing_Method.no_preprocessing:
            self.preprocess_no_preprocessing(generalized_train_data=self.generalized_train_path, generalized_test_data=self.generalized_test_path, columns=columns)
        elif self.method == Preparing_Method.complete_no_preprocessing:
            self.preprocess_no_preprocessing(generalized_train_data=self.complete_generalized_train_path, generalized_test_data=self.complete_generalized_test_path, columns=columns)


    def preprocess_forced_generalization(self, prepared_dataset_path: str, columns: list[Spalten]):
        vorverarbeitet = pd.read_csv(prepared_dataset_path + "vorverarbeitet.csv")
        #spalten von vorverarbeitet als string
        print("Alle vorverarbeitet Spalten: " + str(vorverarbeitet.columns))
        #map user group values zu spaltennamen
        spaltennamen = list(map(lambda x: x.value.name, columns))
        print("Spalten der User Group: " + str(spaltennamen))
        #nur die spalten behalten, die in der anonymisierungs gruppe sind
        vorverarbeitet = vorverarbeitet.drop([column for column in vorverarbeitet.columns if column not in spaltennamen and column != "record_id"], axis=1)
        for column_to_drop in vorverarbeitet.columns:
            if column_to_drop != "record_id":
                if self.szenario == Szenario.szenario1 or self.szenario == Szenario.szenario2:
                    self.data_train = self.data_train.drop(column_to_drop, axis=1)
                if self.szenario == Szenario.szenario2 or self.szenario == Szenario.szenario3:
                    self.data_test = self.data_test.drop(column_to_drop, axis=1)

        #Spalten von vorverarbeitet
        print("Spalten übrig: " + str(vorverarbeitet.columns))
        preprocessed_ddf = dd.from_pandas(vorverarbeitet, npartitions=2)

        if self.szenario == Szenario.szenario1 or self.szenario == Szenario.szenario2:
            self.data_train = dd.merge(self.data_train, preprocessed_ddf, on='record_id')
            self.data_train.repartition(npartitions=2)
        if self.szenario == Szenario.szenario2 or self.szenario == Szenario.szenario3:
            self.data_test = dd.merge(self.data_test, preprocessed_ddf, on='record_id')
            self.data_test.repartition(npartitions=2)
    
    def preprocess_specialization(self, prepared_dataset_path: str, columns: list[Spalten]):
        for column in columns:
            preprocessed_df = pd.read_csv(prepared_dataset_path + column.value.name + "_vorverarbeitet.csv")
            for column_to_drop in preprocessed_df.columns:
                if column_to_drop != "record_id":
                    if self.szenario == Szenario.szenario1 or self.szenario == Szenario.szenario2:
                        self.data_train = self.data_train.drop(column_to_drop, axis=1)
                    if self.szenario == Szenario.szenario2 or self.szenario == Szenario.szenario3:
                        self.data_test = self.data_test.drop(column_to_drop, axis=1)
            preprocessed_ddf = dd.from_pandas(preprocessed_df, npartitions=self.partition_size)

            if self.szenario == Szenario.szenario1 or self.szenario == Szenario.szenario2:
                self.data_train = dd.merge(self.data_train, preprocessed_ddf, on='record_id')
                self.data_train.repartition(npartitions=self.partition_size)
            if self.szenario == Szenario.szenario2 or self.szenario == Szenario.szenario3:
                self.data_test = dd.merge(self.data_test, preprocessed_ddf, on='record_id')
                self.data_test.repartition(npartitions=self.partition_size)

            print(f"Merged {columns.index(column)+1}/{len(columns)} columns.")


    def preprocess_no_preprocessing(self, generalized_train_data: str, generalized_test_data: str, columns: list[Spalten]):
        generalized = pd.concat([pd.read_csv(generalized_train_data), pd.read_csv(generalized_test_data)], ignore_index=True)
        spaltennamen = list(map(lambda x: x.value.name, columns))
        generalized = generalized.drop([column for column in generalized.columns if column not in spaltennamen and column != "record_id"], axis=1)
        for column_to_drop in generalized.columns:
            if column_to_drop != "record_id":
                if self.szenario == Szenario.szenario1 or self.szenario == Szenario.szenario2:
                    self.data_train = self.data_train.drop(column_to_drop, axis=1)
                if self.szenario == Szenario.szenario2 or self.szenario == Szenario.szenario3:
                    self.data_test = self.data_test.drop(column_to_drop, axis=1)

        generalized_ddf = dd.from_pandas(generalized, npartitions=2)
        if self.szenario == Szenario.szenario1 or self.szenario == Szenario.szenario2:
            self.data_train = dd.merge(self.data_train, generalized_ddf, on='record_id')
            self.data_train.repartition(npartitions=2)
        if self.szenario == Szenario.szenario2 or self.szenario == Szenario.szenario3:
            self.data_test = dd.merge(self.data_test, generalized_ddf, on='record_id')
            self.data_test.repartition(npartitions=2)
    
    
    def get_data(self):
        self.set_types()
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
        if self.method == Preparing_Method.forced_generalization or self.method == Preparing_Method.no_preprocessing or self.method == Preparing_Method.complete_forced_generalization or self.method == Preparing_Method.complete_no_preprocessing:
            all_data = all_data.compute()
        for column in data_original.columns:
            if self.method == Preparing_Method.forced_generalization or self.method == Preparing_Method.no_preprocessing or self.method == Preparing_Method.complete_forced_generalization or self.method == Preparing_Method.complete_no_preprocessing:
                if column != "record_id" and column != "Diabetes_binary":
                    all_data[column] = all_data[column].astype('category')
                    self.data_train[column] = self.data_train[column].astype('category').cat.set_categories(all_data[column].cat.categories)
                    self.data_test[column] = self.data_test[column].astype('category').cat.set_categories(all_data[column].cat.categories)
                    
                     
            elif column not in map(lambda x: x.value.name, self.NUMERICAL_COLUMNS) and column != "record_id":
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