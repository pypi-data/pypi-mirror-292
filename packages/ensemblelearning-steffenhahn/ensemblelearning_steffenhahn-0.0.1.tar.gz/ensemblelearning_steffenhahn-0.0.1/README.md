# Projekt Softwareentwicklung

## Setzt die Vorgaben in Python um und verpackt euren Code in einem Python-Package - Dokumentation ist optional (30%)

### Klasse umsetzen, mit deren Hilfe ein Multi-Model-Model Ensemble Regressor (Aggregiert die Schätzung von mehreren, unterschiedlichen Regressionsmodellen, z.B. Decision Tree und Lineare Regression) trainiert werden kann.

Ich habe eine Klasse entwickelt "EnsembleLearning", dass die Daten des Titanic Datensatzes von Kaggle verarbeitet. Diese werden zunächst pre-processed und dann dann an die Klasse übergeben. Über einen User-Input, kann das Ensemble Learning initiiert werden. Zur Verfügung stehende Regressors:
- least_squares 
- nearest_neighbor 
- xgboost
- sgd (stochastic gradient descent)

Die Klasse fitted und predicted anschließend die Zielvariablen und zurückgegeben wird die Accuracy für den Datensatz Titanic

Das Package habe ich unter ensemblelearning-steffenhahn veröffentlich auf PyPi


### Schreibt Unit-Tests (5 Stück reichen) um die Funktionalität der Regressor-Klasse zu testen (20%)

Die Unit Test sind im test_model file zu finden

### Entwickelt einen REST-Webservice der das von euch erstellte Paket nutzt und die passenden Endpoints anbietet (20%)

Ich habe ein Flask-App erstellt, welche den Titanic Datensatz lädt, und der User kann die Regressoren auswählen

<div align="center">
    <img src="/screenshots/screen1.png" width="400px"</img> 
</div>

Das trainierte Model wird abgespeichert (trained_model.joblib), und anschließend wird die Accuracy zurückgegeben:

<div align="center">
    <img src="/screenshots/screen2.png" width="400px" </img> 
</div>

Wird nur ein Regressor ausgewählt, wird eine Fehlermeldung zurückgegeben:

<div align="center">
    <img src="/screenshots/screen3.png" width="400px" </img> 
</div>


### Erstellt ein Docker-Image für den oben genannten Web-Service (10%)

Ist erstellt unter "Dockerfile" und sollte auch funktionieren, wenngleich das Image mit >2GB völlig überdimensioniert ist. Aber habe meine fehlendes Know-How mit Masse kompensiert, und es läuft zumindest;)

### Entwickelt eine GitLab-Pipeline um eure Tests und alle anderen automatisierbaren Schritte auszuführen (20%)

Ist ebenfalls unter .gitlab-ci.yml erstellt und getestet:

<div align="center">
    <img src="/screenshots/screen4.png" width="400px" </img> 
</div>

