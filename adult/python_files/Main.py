from python_files.Data_Loader import Data_Loader
from python_files.Modellauswertung_Dask import Modellauswertung_Dask
from dask.distributed import Client, LocalCluster
from dask_jobqueue import SLURMCluster
from python_files.ResultsIOHandler import ResultsIOHandler
from python_files.Anonymization  import Anonymization
from python_files.Vorverarbeitung import Preparing_Method
from python_files.Szenario import Szenario


def config_slurm_cluster():
    cluster = SLURMCluster(
        job_cpu=1,               # CPUs pro Job
        job_mem='400G',           # Speicher pro Job
        cores=1,                 # Gesamtanzahl der Kerne
        memory='400GB',           # Gesamtanzahl des Speichers
        walltime='40:00:00',     # Maximale Laufzeit
        queue='clara',         # Partition/Queue Name
    )
    cluster.scale(jobs=8)
    return cluster

def config_local_cluster():
    return LocalCluster(n_workers=1, threads_per_worker=1, memory_limit='16GB')


def run_evaluation(slurm_cluster: bool, method: Preparing_Method, szenario: Szenario):
    if slurm_cluster:
        cluster = config_slurm_cluster()
    else:
        cluster = config_local_cluster()
    client = Client(cluster)
    results_io_handler = ResultsIOHandler(method, szenario)

    weighted = method == Preparing_Method.weighted_specialization or method == Preparing_Method.extended_weighted_specialization or method == Preparing_Method.complete_weighted_specialization
    absolute_results = method == Preparing_Method.weighted_specialization_highest_confidence

    for anonymization in Anonymization:
        data_loader = Data_Loader(method, szenario)
        print("lade daten")
        data_loader.preprocess(anonymization.value)
        evaluate_model_and_save_results(data_loader, anonymization, results_io_handler, client, weighted=weighted, absolute_results=absolute_results)

    client.close()
    cluster.close()

    
def get_num_of_rows(method: Preparing_Method):
    for anonymization in Anonymization:
        data_loader = Data_Loader(method, Szenario.szenario2)
        data_loader.preprocess(anonymization.value)

        data_train, data_test = data_loader.get_data()
        train_count = data_train.shape[0].compute()
        test_count = data_test.shape[0].compute()
        write_to_txt_file("Anonymisierung: " + anonymization.name + " | Train: " + str(train_count) + " | Test: " + str(test_count), "ergebnisse/" + method.name + "_rows.txt")


def write_to_txt_file(text:str, name:str):
    with open(name, "a") as file:
        file.write(text + "\n")


def evaluate_model_and_save_results(data_loader: Data_Loader, anonymization: Anonymization, results_io_handler: ResultsIOHandler, client, weighted: bool, absolute_results: bool):
    data_train, data_test = data_loader.get_data()
    X_train = data_train.drop(columns=["income"])
    Y_train = data_train["income"]
    X_test = data_test.drop(columns=["income"])
    #Nur die Spalten record_id und income werden benötigt
    y_test_with_record_ids = data_test[["record_id", "income"]]
    modell_auswertung = Modellauswertung_Dask(X_train, X_test, Y_train, y_test_with_record_ids, client)
    accuracy, f1_score_0, f1_score_1 = modell_auswertung.train_model(X_train, X_test, weighted, absolute_results)
    true_labels, pred_proba = modell_auswertung.get_true_values_and_pred_proba()
    results_io_handler.save_model_results(anonymization, pred_proba, true_labels, accuracy, f1_score_0, f1_score_1)



