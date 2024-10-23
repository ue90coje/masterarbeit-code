from python_files.Data_Loader import Data_Loader
from python_files.spalten.Spalten import Spalten
from python_files.Modellauswertung_Dask import Modellauswertung_Dask
from dask.distributed import Client, LocalCluster
#from dask_jobqueue import SLURMCluster
from python_files.ResultsIOHandler import ResultsIOHandler
from itertools import combinations
import logging
from python_files.UserGroups  import Anonymization
from python_files.Vorverarbeitung import Szenario

def configure_logger(i):
    # Pfad zur .out-Datei (dieser muss an deine Konfiguration angepasst werden)
    out_file = "slurm_job_" + str(i) + ".out"

    # Logger konfigurieren
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(out_file),
            logging.StreamHandler()
        ]
    )

    # Beispiel-Logger verwenden
    logger = logging.getLogger(__name__)

    # Logging-Informationen schreiben
    logger.info("Dies ist eine Info-Nachricht.")
    logger.error("Dies ist eine Fehler-Nachricht.")
    return logger

""" def config_slurm_cluster():
    cluster = SLURMCluster(
        job_cpu=1,               # CPUs pro Job
        job_mem='200G',           # Speicher pro Job
        cores=1,                 # Gesamtanzahl der Kerne
        memory='200GB',           # Gesamtanzahl des Speichers
        walltime='40:00:00',     # Maximale Laufzeit
        queue='clara',         # Partition/Queue Name
    )
    cluster.scale(jobs=8)
    return cluster """

def config_local_cluster():
    return LocalCluster(n_workers=1, threads_per_worker=1, memory_limit='16GB')




def evaluate_for_szenario_1(manipulate_test_data: bool = False,absolute_results: bool = False):
    cluster = config_local_cluster()
    client = Client(cluster)
    results_io_handler = ResultsIOHandler(Szenario.Szenario1, manipulate_test_data)
    #logger = configure_logger(1)
    for user_group in Anonymization:
        data_loader = Data_Loader(Szenario.Szenario1)
        print("lade daten")
        data_loader.preprocess_scenario_1_and_2(user_group.value, manipulate_test_data)
        evaluate_model_and_save_results(data_loader, user_group, results_io_handler, client, absolute_results=absolute_results)
    client.close()
    cluster.close()



def evaluate_for_szenario_3(manipulate_test_data: bool = False):
    cluster = config_local_cluster()
    client = Client(cluster)
    results_io_handler = ResultsIOHandler(Szenario.Szenario3, manipulate_test_data)
    
    for user_group in Anonymization:
        data_loader = Data_Loader(Szenario.Szenario3)
        print("lade daten")
        data_loader.preprocess_scenario_3(user_group, manipulate_test_data)
        evaluate_model_and_save_results(data_loader, user_group, results_io_handler, client)


def evaluate_for_szenario_5(manipulate_test_data: bool = False):
    cluster = config_local_cluster()
    client = Client(cluster)
    results_io_handler = ResultsIOHandler(Szenario.Szenario5, manipulate_test_data)

    for anonymization in Anonymization:
        data_loader = Data_Loader(Szenario.Szenario5)
        data_loader.preprocess_scenario_5(anonymization, manipulate_test_data)
        evaluate_model_and_save_results(data_loader, anonymization, results_io_handler, client)
        
    
def evaluate_for_szenario_6(manipulate_test_data: bool = False):
    cluster = config_local_cluster()
    client = Client(cluster)
    results_io_handler = ResultsIOHandler(Szenario.Szenario6, manipulate_test_data)

    for anonymization in Anonymization:
        data_loader = Data_Loader(Szenario.Szenario6)
        data_loader.preprocess_scenario_6(anonymization, manipulate_test_data)
        evaluate_model_and_save_results(data_loader, anonymization, results_io_handler, client, weighted=True)
    
def get_num_of_rows(szenario: Szenario):
    for anonymization in Anonymization:
        data_loader = Data_Loader(szenario)
        if szenario == Szenario.Szenario1 or szenario == Szenario.Szenario2:
            data_loader.preprocess_scenario_1_and_2(anonymization.value, True)
        elif szenario == Szenario.Szenario3:
            data_loader.preprocess_scenario_3(anonymization, True)
        elif szenario == Szenario.Szenario5:
            data_loader.preprocess_scenario_5(anonymization, True)
        elif szenario == Szenario.Szenario6:
            data_loader.preprocess_scenario_6(anonymization, True)

        data_train, data_test = data_loader.get_data()
        train_count = data_train.shape[0].compute()
        test_count = data_test.shape[0].compute()
        write_to_txt_file("Anonymisierung: " + anonymization.name + " | Train: " + str(train_count) + " | Test: " + str(test_count), szenario.name + "_rows.txt")


def write_to_txt_file(text:str, name:str):
    with open(name, "a") as file:
        file.write(text + "\n")


def evaluate_model_and_save_results(data_loader: Data_Loader, user_group: Anonymization, results_io_handler: ResultsIOHandler, client, weighted: bool = False, absolute_results: bool = False):
    data_train, data_test = data_loader.get_data()
    X_train = data_train.drop(columns=["income"])
    Y_train = data_train["income"]
    X_test = data_test.drop(columns=["income"])
    #Nur die Spalten record_id und income werden benötigt
    y_test_with_record_ids = data_test[["record_id", "income"]]
    modell_auswertung = Modellauswertung_Dask(X_train, X_test, Y_train, y_test_with_record_ids, client)
    accuracy, f1_score_0, f1_score_1 = modell_auswertung.train_model(X_train, X_test, weighted, absolute_results)
    true_labels, pred_proba = modell_auswertung.get_true_values_and_pred_proba()
    results_io_handler.save_model_results(user_group, pred_proba, true_labels, accuracy, f1_score_0, f1_score_1)



