from itertools import combinations
import xgboost as xgb
from sklearn.metrics import f1_score

class Modellauswertung:
    def __init__(self, X_train, X_test, y_train, y_test):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test



    #Funktion, die das Modell trainiert und die Genauigkeit, sowie den F1 Score für beide Klassen zurückgibt
    def train_model(self, X_train, X_test):
        model = xgb.XGBClassifier(enable_categorical=True, n_estimators=40, max_depth=5)
        model.fit(X_train, self.y_train)
        y_pred = model.predict(X_test)
        accuracy = model.score(X_test, self.y_test)
        f1_score_0 = f1_score(self.y_test, y_pred, pos_label=0)
        f1_score_1 = f1_score(self.y_test, y_pred, pos_label=1)
        return accuracy, f1_score_0, f1_score_1
    
    #Funktion, die die train_model Funktion aufruft für jede mögliche Kombination der Features
    def evaluate_all_combinations(self):
        features = self.X_train.columns
        results = {}
        #Anzahl aller möglichen Kombinationen berechnen
        num_combinations = 2**len(features) - 1
        actual_combinations = 0
        for i in range(1, len(features)+1):
            for j in combinations(features, i):
                X_train = self.X_train[list(j)]
                X_test = self.X_test[list(j)]
                accuracy, f1_score_0, f1_score_1 = self.train_model(X_train, X_test)
                results[j] = [accuracy, f1_score_0, f1_score_1]
                actual_combinations += 1
                print('Progress: ' + str(actual_combinations) + '/' + str(num_combinations) + ' combinations evaluated')
        return results
    
    #Funktion, die die evaluate Funktion aufruft und die Ergebnisse tabellarisch in einer csv-Datei ausgibt
    def evaluate_all_combinations_to_csv(self, filename):
        results = self.evaluate_all_combinations()
        with open(filename + '.csv', 'w') as f:
            f.write('Features;Accuracy;F1 Score 0;F1 Score 1\n')
            for key, value in results.items():
                f.write(str(key) + ';' + str(value[0]) + ';' + str(value[1]) + ';' + str(value[2]) + '\n')
        return results