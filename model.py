# Importing the essential Libraries
import pandas as pd
import numpy as np
import mysql.connector
from catboost import CatBoostClassifier
from sklearn.metrics import fbeta_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import metrics
import pickle
from imblearn.over_sampling import SMOTE
from lightgbm import LGBMClassifier
import joblib
from sqlalchemy import create_engine

# Establish a MySQL database connection
db_connect = create_engine('mysql+mysqlconnector://root@localhost/banque')
# db_connect = create_engine('mysql+mysqlconnector://root:pY1jcn5XdnFH1mFvNCtF@containers-us-west-188.railway.app:6949/banque')

df = pd.read_sql('select * from client', con=db_connect)


# Étape 3: Prétraitement des données
def preprocess_data(data):
    # Convertir la colonne 'Date_inscription' en valeurs datetime
    data['Date_inscription'] = pd.to_datetime(data['Date_inscription'], errors='coerce')

    # Calculer l'ancienneté en mois
    date_actuelle = pd.to_datetime(date.today().strftime('%Y-%m-%d'))
    data['Anciennete'] = ((date_actuelle.year - data['Date_inscription'].dt.year) * 12 + date_actuelle.month - data['Date_inscription'].dt.month).fillna(0).astype(int)
    
    # Supprimer les colonnes inutiles pour la prédiction de l'attrition
    columns_to_drop = ['ID_conseiller', 'Date_naissance','Date_inscription']
    data = data.drop(columns=columns_to_drop)
    
    # Encodage des variables catégorielles
    categorical_features = ['Pays', 'Genre', 'Grade']
    data = pd.get_dummies(data, columns=categorical_features, drop_first=True)
    
    # Encodage des variables numériques (si nécessaire)
    numeric_features = ['Anciennete', 'Nb_fois_actif', 'CP', 'CE', 'Nb_fils_direct', 'Nb_fils', 'NB_cheque', 'Prime_parrainage', 'Prime_animation']
    data[numeric_features] = data[numeric_features].apply(lambda x: (x - x.mean()) / x.std())
    
    # Remplacer les valeurs manquantes par la médiane
    data = data.fillna(data.median())
    
    return data



preprocessed_data = preprocess_data(df)
# Étape 4: Configuration de l'environnement PyCaret et création du modèle
#init
exp = setup(data=preprocessed_data, target='Quitter', remove_outliers=True, normalize=True, fix_imbalance=True,log_experiment = True, experiment_name = 'Churn')

#création du modèle
gbc=create_model('gbc')
#optimisation du modèle
tuned_gbc = tune_model(gbc)




joblib.dump(preprocess_data, 'scale.pkl')
joblib.dump(tuned_gbc, 'classifier.pkl')


