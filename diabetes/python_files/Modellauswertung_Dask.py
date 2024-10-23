from itertools import combinations
from xgboost.dask import DaskXGBClassifier
import xgboost as xgb
from sklearn.metrics import f1_score, accuracy_score
import numpy as np
from dask.distributed import Client
import dask.dataframe as dd

class Modellauswertung_Dask:
    
    def __init__(self, X_train, X_test, y_train, y_test_with_record_ids, client):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test_with_record_ids = y_test_with_record_ids.drop_duplicates()
        self.client = client



    #Funktion, die das Modell trainiert und die Genauigkeit, sowie den F1 Score für beide Klassen zurückgibt
    def train_model(self, X_train, X_test, weighted, absolute_results=False):
        X_train, weights = self.get_weights(X_train)
        cl = DaskXGBClassifier(n_estimators=40, max_depth=5, enable_categorical=True, verbosity=3)
        #cl.set_params(device='cuda')
        cl.client = self.client
        if weighted:
            cl.fit(X_train, self.y_train, sample_weight=weights)
        else:
            cl.fit(X_train, self.y_train)
        print('Model trained')
        y_test, y_pred_proba = self.get_y_test_and_y_pred_proba(cl, X_test, absolute_results)
        self.y_true = y_test
        self.pred_proba = y_pred_proba
        #wandel die dask.dataframe in pandas.dataframe um, um die Funktionen accuracy_score und f1_score nutzen zu können
        y_pred = y_pred_proba.apply(lambda x: 1 if x >= 0.5 else 0)
        accuracy = accuracy_score(y_test, y_pred)
        f1_score_0 = f1_score(y_test, y_pred, pos_label=0)
        f1_score_1 = f1_score(y_test, y_pred, pos_label=1)
        return accuracy, f1_score_0, f1_score_1
    
    def get_true_values_and_pred_proba(self):
        return self.y_true, self.pred_proba

    def get_weights(self, X_train):
        #record_counts = X_train.groupby('record_id').size().reset_index(name='count')
        record_counts = X_train.groupby('record_id').size().reset_index()
        record_counts.columns = ['record_id', 'count']
        X_train = X_train.merge(record_counts, on='record_id', how='left')
        X_train['weights'] = 1 / X_train['count']
        weights = X_train['weights']
        X_train = X_train.drop(columns=['record_id', 'count', 'weights'])
        return X_train, weights
    
    def get_y_test_and_y_pred_proba(self, model, X_test, absolute_results):
        predicted_values_by_record_id = self.get_predictions_by_record_ids(model, X_test, absolute_results)
        print("Spalten: " + str(predicted_values_by_record_id.columns))
        #g = predicted_values_by_record_id.compute()
        df_outcome = self.y_test_with_record_ids
        df_outcome = dd.merge(df_outcome, predicted_values_by_record_id, on='record_id')
        df_outcome = df_outcome.compute()
        y_test = df_outcome['Diabetes_binary']
        y_pred_proba = df_outcome['predicted_values']
        return y_test, y_pred_proba

    def get_predictions_by_record_ids(self, model, X_test, absolute_results):
        #if absolute_results:
            #y_predicted = model.predict(X_test.drop(columns=["record_id"]))
        #else:
        y_predicted = model.predict_proba(X_test.drop(columns=["record_id"]))[:, 1]
        X_test['predicted_values'] = y_predicted
        #nur die record_id und predicted_values Spalten behalten
        if absolute_results:
            #X_test['deviation'] = (X_test['predicted_values'] - 0.5).abs()
            #idx = X_test.groupby('record_id')['deviation'].max() == X_test['deviation']
            #y_predicted_with_record_id = X_test[idx]
            y_predicted_with_record_id = X_test[['record_id', 'predicted_values']].groupby(["record_id"])['predicted_values'].apply(lambda x: max(x, key=lambda v: abs(v - 0.5)))
        else:
            y_predicted_with_record_id = X_test[['record_id', 'predicted_values']].groupby(["record_id"])['predicted_values'].mean()
        y_predicted_with_record_id = y_predicted_with_record_id.reset_index()
        print("Spalten: " + str(y_predicted_with_record_id.columns))
        return y_predicted_with_record_id