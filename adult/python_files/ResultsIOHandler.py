import h5py
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
import seaborn as sns
from python_files.Anonymization import Anonymization
from python_files.Vorverarbeitung import Preparing_Method
from python_files.Szenario import Szenario

class ResultsIOHandler:

    def __init__(self, method: Preparing_Method, szenario: Szenario):
        filename = ""
        if method == Preparing_Method.weighted_specialization:
            filename += "gewichtete_spezialisierung/"
        elif method == Preparing_Method.specialization:
            filename += "spezialisierung/"
        elif method == Preparing_Method.forced_generalization:
            filename += "zwangsgeneralisierung/"
        elif method == Preparing_Method.weighted_specialization_highest_confidence:
            filename += "spezialisierung_höchste_sicherheit/"
        elif method == Preparing_Method.no_preprocessing:
            filename += "keine_aufbereitung/"
        elif method == Preparing_Method.extended_weighted_specialization:
            filename += "erweiterte_gewichtete_spezialisierung/"
        elif method == Preparing_Method.complete_weighted_specialization:
            filename += "komplett_gewichtete_spezialisierung/"
        elif method == Preparing_Method.complete_forced_generalization:
            filename += "komplett_zwangsgeneralisierung/"
        elif method == Preparing_Method.complete_no_preprocessing:
            filename += "komplett_keine_aufbereitung/"
        
        filename += "results_" + szenario.name

        self.file_path_h5 = "ergebnisse/" + filename + '.h5'
        self.file_path_csv = "ergebnisse/" + filename + '.csv'
        self.last_id = self.get_last_id(self.file_path_csv)
        self.method = method
        self.szenario = szenario

    def get_last_id(self, file_path_csv):
        if os.path.exists(file_path_csv):
            results_df = pd.read_csv(file_path_csv, sep=';')
            return results_df['id'].max() + 1
        else:
            outdir = os.path.dirname(file_path_csv)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            
            return 0

    def save_model_results(self, anonymization: Anonymization, probas, true_labels, accuracy, f1_score_0, f1_score_1):
        column_combination = get_column_combination_string(anonymization)
        with h5py.File(self.file_path_h5, 'a') as file:
            group = file.create_group(str(self.last_id))
            group.create_dataset('probas', data=probas)
            group.create_dataset('true_labels', data=true_labels)
            group.create_dataset('column_combination', data=column_combination)

            result = {
            'id': str(self.last_id),
            'column_combination': column_combination,
            'accuracy': accuracy,
            'f1_score_class_0': f1_score_0,
            'f1_score_class_1': f1_score_1,
            'anonymization': anonymization.name
            }
            self.write_result_to_csv(result)
            
            self.last_id += 1

    def write_result_to_csv(self, result):
        if os.path.exists(self.file_path_csv):
            results_df = pd.read_csv(self.file_path_csv, sep=';')
            results_df = pd.concat([results_df, pd.DataFrame(result, index=[0])], ignore_index=True)
            results_df.to_csv(self.file_path_csv, index=False, sep=';')
        else:
            result_df = pd.DataFrame(result, index=[0])
            result_df.to_csv(self.file_path_csv, index=False, sep=';')


    def load(self, key):
        with h5py.File(self.file_path_h5, 'r') as file:
            group = file[key]
            probas = group['probas'][:]
            true_labels = group['true_labels'][:]
            return {'probas': probas, 'true_labels': true_labels}
        
    #Methode gibt ein Dictionary zurück, das die Metriken aus der csv sowie die Spaltenkombination sowie die Prognosen und die wahren Labels enthält aus der h5
    def get_results(self):
        results = pd.read_csv(self.file_path_csv, sep=';')
        results_dict = results.to_dict(orient='records')
        for result in results_dict:
            key = str(result['id'])
            result['probas'] = self.load(key)['probas']
            result['true_labels'] = self.load(key)['true_labels']
        return results_dict
    
    def show_roc_curve(self, title = None):
        results = self.get_results()

        for result in results:
            true_labels = result["true_labels"]
            probas = result["probas"]
            fpr, tpr, thresholds = roc_curve(true_labels, probas)
            plt.plot(fpr, tpr)

        plt.legend([result["anonymization"] for result in results])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        if title is None:
            title = self.get_roc_title()
        plt.title(title)
        plt.show()


    def get_roc_title(self):
        title = "ROC Curve for " + str(self.method.value) + " " + str(self.szenario.name)
        return title
        

    def show_probability_distribution(self):
        #Wahrscheinlichkeitsverteilung als Linienplot wie Gaußkurve
        results = self.get_results()
        for result in results:
            probas = result["probas"]
            sns.kdeplot(probas, label=result["anonymization"])
            
        plt.legend([result["anonymization"] for result in results])
        plt.xlabel("Probability")
        plt.ylabel("Density")
        plt.title("Probability Distribution")
        plt.show()


def compare_results_in_table(results_handlers: list[ResultsIOHandler], accuracy: bool = False):
    results = pd.DataFrame()
    results['anonymization'] = [anonymization.name for anonymization in Anonymization]

    for result_handler in results_handlers:
        column = []
        for anonymization in Anonymization:
            res = result_handler.get_results()
            #den Eintrag aus der Liste, bei dem 'user' gleich der aktuell betrachtete User ist
            user_result_dict = next((item for item in res if item["anonymization"] == anonymization.name), None)
            if user_result_dict is None:
                column.append("---")
                continue
            if accuracy:
                value = user_result_dict['accuracy']
            else:
                value = (user_result_dict['f1_score_class_0'] + user_result_dict['f1_score_class_1']) / 2

            #value mit zwei Nachkommastellen runden
            column.append(f"{value:.2f}")
        column_name = result_handler.method.value + "\n " + result_handler.szenario.name
        results[column_name] = column
    
    #plot table matplotlib
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('off')
    table = ax.table(cellText=results.values, colLabels=results.columns, cellLoc='center', loc='center', colWidths=[0.12] * len(results.columns))
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(2, 2)
    if accuracy:
        plt.title("Accuracy")
    else:
        plt.title("F1 Scores")
    #wrap text
    plt.show()




def get_column_combination_string(anonymization: Anonymization):
    column_combination_string = ""
    for column in anonymization.value:
        column_combination_string += column.value.name + "_manipuliert, "
    return column_combination_string[:-2]

