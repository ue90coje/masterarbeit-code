#Klasse deren Konstruktor ein Dataframe entgegennimmt und die Methoden zur Vorverarbeitung des Dataframes enthält
#Die Methoden sind:
#-ersetze_durch_mittelwert: ersetzt generalisierte Werte eines Intervalls durch den mittleren Wert des Intervalls
#-erstelle_neue_zeilen: erstellt neue Zeilen mit konkreten Werten für die Generalisierten Werte

import pandas as pd
from python_files.spalten.Spalten import Spalten
import os




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

    def erstelle_neue_zeilen(self, columns: list[Spalten]):
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


    @staticmethod
    def create_rows_for_values(row, attributName, values):
        new_rows = []
        for value in values:
            new_row = row.copy()
            new_row[attributName] = value
            new_rows.append(new_row)

        return new_rows
    

    def write_to_csv(self, path:str):
        #split path in directory and filename
        outdir = os.path.dirname(path)
        if not os.path.exists(outdir):
            os.mkdir(outdir)
            
        self.df.to_csv(path, index=False)