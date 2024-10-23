from python_files.Data_Loader import Data_Loader
from python_files.spalten.Spalten import Spalten
from python_files.Modellauswertung_Dask import Modellauswertung_Dask
from dask.distributed import Client, LocalCluster
#from dask_jobqueue import SLURMCluster
from python_files.ResultsIOHandler import ResultsIOHandler
from itertools import combinations
import logging
from python_files.Anonymization  import Anonymization
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




def evaluate_for_szenario_1(manipulate_test_data: bool = False):
    cluster = config_local_cluster()
    client = Client(cluster)
    results_io_handler = ResultsIOHandler(Szenario.Szenario1, manipulate_test_data)
    for user_group in Anonymization:
        data_loader = Data_Loader(Szenario.Szenario1)
        print("lade daten")
        data_loader.preprocess_scenario_1_and_2(user_group.value, manipulate_test_data)
        evaluate_model_and_save_results(data_loader, user_group, results_io_handler, client, weighted=True)
    client.close()
    cluster.close()


def evaluate_for_szenario_2(manipulate_test_data: bool = False):
    cluster = config_local_cluster()
    client = Client(cluster)
    results_io_handler = ResultsIOHandler(Szenario.Szenario2, manipulate_test_data)
    for user_group in Anonymization:
        data_loader = Data_Loader(Szenario.Szenario2)
        print("lade daten")
        data_loader.preprocess_scenario_1_and_2(user_group.value, manipulate_test_data)
        evaluate_model_and_save_results(data_loader, user_group, results_io_handler, client)
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
    client.close()
    cluster.close()


def evaluate_for_szenario_4():
    cluster = config_local_cluster()
    client = Client(cluster)
    results_io_handler = ResultsIOHandler(Szenario.Szenario4, True)
    for user_group in Anonymization:
        data_loader = Data_Loader(Szenario.Szenario4)
        print("lade daten")
        data_loader.preprocess_scenario_1_and_2(user_group.value, True)
        evaluate_model_and_save_results(data_loader, user_group, results_io_handler, client, weighted=True)
    client.close()
    cluster.close()



def evaluate_for_szenario_5(manipulate_test_data: bool = False):
    cluster = config_local_cluster()
    client = Client(cluster)
    results_io_handler = ResultsIOHandler(Szenario.Szenario5, manipulate_test_data)

    for anonymization in Anonymization:
        data_loader = Data_Loader(Szenario.Szenario5)
        data_loader.preprocess_scenario_5(anonymization, manipulate_test_data)
        evaluate_model_and_save_results(data_loader, anonymization, results_io_handler, client)
    client.close()
    cluster.close()
        
    
def evaluate_for_szenario_6(manipulate_test_data: bool = False):
    cluster = config_local_cluster()
    client = Client(cluster)
    results_io_handler = ResultsIOHandler(Szenario.Szenario6, manipulate_test_data)

    for anonymization in [Anonymization.moderate, Anonymization.strong, Anonymization.complete]:
        data_loader = Data_Loader(Szenario.Szenario6)
        data_loader.preprocess_scenario_6(anonymization, manipulate_test_data)
        evaluate_model_and_save_results(data_loader, anonymization, results_io_handler, client, weighted=True)
    client.close()
    cluster.close()
    


def evaluate_model_and_save_results(data_loader: Data_Loader, user_group: Anonymization, results_io_handler: ResultsIOHandler, client, weighted: bool = False, absolute_results: bool = False):
    data_train, data_test = data_loader.get_data()
    X_train = data_train.drop(columns=["Diabetes_binary"])
    Y_train = data_train["Diabetes_binary"]
    X_test = data_test.drop(columns=["Diabetes_binary"])
    #Nur die Spalten record_id und income werden benötigt
    y_test_with_record_ids = data_test[["record_id", "Diabetes_binary"]]
    modell_auswertung = Modellauswertung_Dask(X_train, X_test, Y_train, y_test_with_record_ids, client)
    accuracy, f1_score_0, f1_score_1 = modell_auswertung.train_model(X_train, X_test, weighted, absolute_results)
    true_labels, pred_proba = modell_auswertung.get_true_values_and_pred_proba()
    results_io_handler.save_model_results(user_group, pred_proba, true_labels, accuracy, f1_score_0, f1_score_1)



