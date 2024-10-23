import h5py
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve, confusion_matrix, classification_report
import seaborn as sns
from python_files.Anonymization import Anonymization
from python_files.Vorverarbeitung import Szenario

class ResultsIOHandler:

    def __init__(self, szenario: Szenario, manipulated_test_data: bool):
        filename = ""
        if szenario == Szenario.Szenario1:
            filename += "szenario1/"
        elif szenario == Szenario.Szenario2:
            filename += "szenario2/"
        elif szenario == Szenario.Szenario3:
            filename += "szenario3/"
        elif szenario == Szenario.Szenario4:
            filename += "szenario4/"
        elif szenario == Szenario.Szenario5:
            filename += "szenario5/"
        elif szenario == Szenario.Szenario6:
            filename += "szenario6/"
        
        if manipulated_test_data:
            filename += "results_training_and_test_data_manipulated"
        else:
            filename += "results_training_data_manipulated"

        self.file_path_h5 = "model_results/" + filename + '.h5'
        self.file_path_csv = "model_results/" + filename + '.csv'
        self.last_id = self.get_last_id(self.file_path_csv)
        self.szenario = szenario
        self.manipulated_test_data = manipulated_test_data
        self.create_directories()

    def create_directories(self):
        outdir = os.path.dirname(self.file_path_h5)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        

    def get_last_id(self, file_path_csv):
        if os.path.exists(file_path_csv):
            results_df = pd.read_csv(file_path_csv, sep=';')
            return results_df['id'].max() + 1
        else:
            return 0

    def save_model_results(self, user_group: Anonymization, probas, true_labels, accuracy, f1_score_0, f1_score_1):
        column_combination = get_column_combination_string(user_group)
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
            'anonymization': user_group.name
            }
            self.write_result_to_csv(result)
            
            self.last_id += 1

    def write_result_to_csv(self, result):
        if os.path.exists(self.file_path_csv):
            results_df = pd.read_csv(self.file_path_csv, sep=';')
            #results_df = results_df.append(result, ignore_index=True) Use pandas.concat instead
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
        title = "ROC Curve for " + str(self.szenario.value)
        if self.manipulated_test_data:
            title += " with preprocessed test data"
        else:
            title += " with original test data"
        

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
    results['anonymization'] = [user.name for user in Anonymization]

    for result_handler in results_handlers:
        column = []
        for user in Anonymization:
            res = result_handler.get_results()
            #den Eintrag aus der Liste, bei dem 'user' gleich der aktuell betrachtete User ist
            user_result_dict = next((item for item in res if item["anonymization"] == user.name), None)
            if user_result_dict is None:
                column.append("---")
                continue
            if accuracy:
                value = user_result_dict['accuracy']
            else:
                value = (user_result_dict['f1_score_class_0'] + user_result_dict['f1_score_class_1']) / 2

            #value mit zwei Nachkommastellen runden
            column.append(f"{value:.2f}")
        column_name = result_handler.szenario.value
        if result_handler.manipulated_test_data:
            column_name += "\n with preprocessed test data"
        results[column_name] = column
    
    #plot table matplotlib
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('off')
    table = ax.table(cellText=results.values, colLabels=results.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(2, 2)
    if accuracy:
        plt.title("Accuracy")
    else:
        plt.title("F1 Scores")
    #wrap text
    plt.show()




def get_column_combination_string(user_group: Anonymization):
    column_combination_string = ""
    for column in user_group.value:
        column_combination_string += column.value.name + "_manipuliert, "
    return column_combination_string[:-2]

