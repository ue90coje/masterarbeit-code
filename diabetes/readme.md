## Allgemeines
Der Code umfasst 5 Schritte, die über die verschiedenen Notebooks ausgewählt und gestartet werden:
- Aufteilen des Datasets in Trainings- und Testdaten
- Anonymisieren
- Aufbereitung der Daten
- Training und Test des Modells
- Auswertung

Da diese Schritte aufeinander aufbauen, müssen die Notebooks in dieser Reihenfolge ausgeführt werden, die entsprechenden Datasets nicht bereits erzeugt wurden.

## Aufteilen des Datasets in Trainings- und Testdaten
Hierfür das Notebook split_dataset.ipynb verwenden. Das Dataset wird bereinigt und aufgeteilt in Trainings- und Testdaten.

## Anonymisieren
Hierfür das Notebook anonymisieren.ipynb verwenden. Mit der Funktion 
```
Generalisierung.generalize_uniform_train_and_test_data(with_level0=True)
```
werden wird das Trainings- und das Testdataset anonymisiert. Wird der Parameter "with_level0" auf False gesetzt, wird garantiert jeder Wert anonymisiert, sodass kein originaler Wert mehr enthalten ist. Ansonsten erfolgt eine zufällig gleichverteilte Generalisierung über alle Granularitätsstufen hinweg. Die Anonymisierten Datasets befinden sich im Ordner /dataset/anonymisiert bzw. /dataset/komplett_anonymisiert.

## Aufbereitung der Daten
Hierfür das Notebook vorverarbeiten.ipynb verwenden. Über dieses werden folgende drei Funktionen ausgeführt:
```
prepare_specialization(complete_anonymization=False)
prepare_forced_generalization(complete_anonymization=False)
prepare_extended_specialization(complete_anonymization=False)
```

Diese Funktionen bereiten die anonymisierten Datasets nach den entsprechenden Aufbereitungsmethoden auf. Über den Parameter "complete_anonymization" wird ausgewählt, ob die komplett anonymisierten Datasets aufbereitet werden sollen oder die standard-anonymisierten. Ist der wert True werden die Datasets aus dem Ordner /dataset/komplett_anonymisiert aufbereitet, andernfalls aus dem Ordner /dataset/anonymisiert. Der Output erfolgt in folgenden Ordnern:
- /dataset/spezialisiert
- /dataset/zwangsgeneralisiert
- /dataset/erweitert_spezialisiert
- /dataset/komplett_spezialisiert
- /dataset/komplett_zwangsgeneralisiert
- /dataset/komplett_erweitert_spezialisiert

## Training und Test des Modells
Hierfür das Notebook main.ipynb verwenden. Darin wird die Funktion
```
Main.run_evaluation(slurm_cluster: bool, method: Preparing_Method, szenario: Szenario)
```
aufgerufen. Über die Parameter lässt sich die Aufbereitungsmethode und das Szenario auwählen. Über den Parameter "slurm_cluster" wird ausgewählt, ob ein LocalCluster oder ein SlurmCluster genutzt wird. Die Resultate werden im Ordner /ergebnisse abgelegt. Für jede Methode und jedes Szenario wird eine .csv-Datei und eine .h5-Datei angelegt.

Da diese Funktion bei den Spezialisierungsmethoden sehr lange dauert, kann dieses Notebook auf einem Slurm Cluster gestartet werden. Dafür die Datei job.sh mittels "sbatch job.sh" starten.

## Auwertung
Hierfür das Notebook auswertung.ipynb verwenden. Darin werden die abgespeicherten Ergebnisse aus dem Ordner /ergebnisse eingelesen und die F1-Scores in einer Tabelle dargestellt.

## Analyse der ananymisierten Datan und Bestimmung der Anzahl der Records
Im Notebook divereses.ipynb kann die Funktion 
```
get_anonymized_data_analysis(anonymization: Anonymization):
```
ausgeführt werden. Diese Funktion gibt für eine bestimmte Anonymisierungsstufe an, wie viel Prozent der Daten original, generalisiert oder fehlend sind.

Die Funktion
```
def get_num_of_rows(method: Preparing_Method):
```
speichert die Anzahl der Records für eine bestimmte Aufbereitungsmethode in einer .txt Datei ab.