#Klasse deren Konstruktor ein Dataframe entgegennimmt und die Methoden zur Vorverarbeitung des Dataframes enthält
#Die Methoden sind:
#-ersetze_durch_mittelwert: ersetzt generalisierte Werte eines Intervalls durch den mittleren Wert des Intervalls
#-erstelle_neue_zeilen: erstellt neue Zeilen mit konkreten Werten für die Generalisierten Werte

#importiere Age. Die Datei Age.py liegt in dem Ordner columns

import pandas as pd
import numpy as np
from python_files.spalten.Spalten import Spalten
from python_files.spalten import EducationNum




class VorverarbeitungsDatensatz:
    def __init__(self, df):
        self.df = df


    def ersetze_durch_mittelwert(self, columns: list[Spalten]):
        self.df.reset_index(drop=True, inplace=True)
        for column in columns:
            for index, row in self.df.iterrows():
                if not row[column.value.name].isdigit():
                    intervall = column.value.get_value(row[column.value.name])
                    new_value = intervall[len(intervall)//2]
                    self.df.at[index, column.value.name] = new_value
            #self.df[column.value.name] = self.df[column.value.name].astype(int)

    def erstelle_neue_zeilen_v2(self, columns: list[Spalten]):
        for column in columns:
            new_rows = []

            condition = self.df[column.value.name].apply(column.value.is_generalized)
            rows_to_clone = self.df[condition].copy()
            self.df = self.df[~condition]
            self.df.reset_index(drop=True, inplace=True)
            rows_to_clone.reset_index(drop=True, inplace=True)

            for index, row in rows_to_clone.iterrows():
                intervall = column.value.get_value(row[column.value.name])
                new_rows.extend(self.create_rows_for_values(row, column.value.name, intervall))
                #ausgeben, die wievielte Spalte bearbeitet wird von wievielen gesamten Spalten
                
            self.df = pd.concat([self.df, pd.DataFrame(new_rows)], ignore_index=True)
            if column.value.name == Spalten.EDUCATION.value.name:
                #Füge Spalte education-num hinzu. Die Werte von education-num sind die Integer Values von education_num_mapping für die Werte von education.
                self.df["education-num"] = self.df["education"].apply(lambda x: EducationNum.education_num_mapping[x])



    def erstelle_neue_zeilen(self, columns: list[Spalten]):
        for column in columns:
            new_rows = []
            for index, row in self.df.iterrows():
                if column.value.is_generalized(row[column.value.name]):
                    intervall = column.value.get_value(row[column.value.name])
                    new_rows.extend(self.create_rows_for_values(row, column.value.name, intervall))
                    self.df.drop(index, inplace=True)
            self.df = pd.concat([self.df, pd.DataFrame(new_rows)], ignore_index=True)
            #self.df[column.value.name] = self.df[column.value.name].astype(int)


    def get_data_and_weights(self, drop_record_id=True):
        if drop_record_id:
            return self.df.drop(columns=["weight", "record_id"]), self.df["weight"]
        else:
            return self.df.drop(columns=["weight"]), self.df["weight"]
    
     
    @staticmethod
    def create_rows_for_values(row, attributName, values):
        new_rows = []
        for value in values:
            new_row = row.copy()
            new_row[attributName] = value
            new_rows.append(new_row)

        return new_rows
    
    def set_columns_type(self, original_df):
        for column in original_df.columns:
            print(column)
            #Wenn diese Spalte auch in self.df ist
            if column in self.df.columns:
                if original_df[column].dtype == "object" and column != "income":
                    original_df[column] = original_df[column].astype('category')
                    self.df[column] = self.df[column].astype('category').cat.set_categories(original_df[column].cat.categories)
                elif original_df[column].dtype == "category":
                    self.df[column] = self.df[column].astype('category').cat.set_categories(original_df[column].cat.categories)
                else:
                    try:
                        self.df[column] = self.df[column].astype('int64')
                    except ValueError:
                        print(f"Spalte {column} konnte nicht in int64 konvertiert werden.")
                        raise ValueError

    def predict_with_model(self, model):
        predicted_values_dict = {}
        #TODO: Gruppieren nach record_id. 
        # Alle Datensätze eine jeder record_id predicten und den Mittelwert bilden.
        # Ein Dictionary erstellen, in dem jede record_id auf den Mittelwert mappt. 
        # Dictionary nach den record_ids aufsteigend sortieren.
        # Die Werte des Dictionaries in eine Liste schreiben.
        record_ids_grouped = self.df.groupby("record_id")
        for record_id, group in record_ids_grouped:
            predicted_values = model.predict_proba(group.drop(columns=["record_id", "weight"]))[:, 1]
            predicted_values_dict[record_id] = np.mean(predicted_values)
        sorted_dict = dict(sorted(predicted_values_dict.items()))
        return list(sorted_dict.values())

    def write_to_csv(self, filename):
        self.df.to_csv(filename, index=False)