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
# db_connect = create_engine('mysql+mysqlconnector://root@localhost/banque')
db_connect = create_engine('mysql+mysqlconnector://root:pY1jcn5XdnFH1mFvNCtF@containers-us-west-188.railway.app:6949/banque')

df = pd.read_sql('select * from client', con=db_connect)

# df['Solde']=np.log10(df['Solde']+1)
# Including only Potential Predictors as independent varibles
df = df[['CreditScore', 'Pays', 'Genre', 'Age', 'Tenure', 'Solde', 'NbreDeProduits', 'MembreActif', 'Quitte']]
# Converting the categorical variables into numerical and avoiding Dummy Varibale Trap
df = pd.get_dummies(df)
df = df[
    ['CreditScore', 'Age', 'Tenure', 'Solde', 'NbreDeProduits', 'MembreActif', 'Quitte', 'Pays_Germany', 'Genre_Femme']]
# Splitting the Dataset into Dependent and Independent Variables
X = df.iloc[:, [0, 1, 2, 3, 4, 5, 7, 8]]
y = df.iloc[:, 6].values

# X = df.drop(labels=["Quitte"], axis=1)
# y = df["Quitte"]


# Splitting the dataset into Training and Testing Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# #mise à l'echelle
c = ['CreditScore', 'Age', 'Tenure', 'Solde', 'NbreDeProduits']
sc = StandardScaler()
X_train[c] = sc.fit_transform(X_train[c])
X_test[c] = sc.transform(X_test[c])

# sc = StandardScaler()
# X_train = sc.fit_transform(X_train)
# X_test= sc.transform(X_test)

# oversample train data
oversample = SMOTE(random_state=101, sampling_strategy='minority')
X_train, y_train = oversample.fit_resample(X_train, y_train)

# build catboost model

cat_model = CatBoostClassifier(learning_rate=0.004, depth=6, iterations=900, l2_leaf_reg=1e-20,
                               leaf_estimation_iterations=10, logging_level='Silent', loss_function='Logloss',
                               random_seed=42)
cat_model.fit(X_train, y_train)
y_pred = cat_model.predict(X_test)

joblib.dump(sc, 'scale.pkl')
joblib.dump(cat_model, 'classifier.pkl')

# sco = metrics.accuracy_score(y_test, y_pred)
# print("Accuracy: {0:.2f} %".format(100 * sco))
#
# f_sco = metrics.f1_score(y_test, y_pred)
# print("f: {0:.2f} %".format(100 * f_sco))
#
# recall = metrics.precision_score(y_test, y_pred)
# print("precision_score: {0:.2f} %".format(100 * recall))
#
# prec = metrics.recall_score(y_test, y_pred)
# print("recall_score: {0:.2f} %".format(100 * prec))
#
# print("f2_score:", fbeta_score(y_test, y_pred, beta=2))

# # Save scaler
# pkl_filename_scaler = "Scaler.pkl"
# with open(pkl_filename_scaler, 'wb') as file:
#     pickle.dump(sc, file)
#
# # Save model
# pkl_filename = "catboostModel.pkl"
# with open(pkl_filename, 'wb') as file:
#     pickle.dump(cat_model, file)

# # Load from file
# with open(pkl_filename, 'rb') as file:
#     pickle_model = pickle.load(file)
#
# # Calculate the accuracy score and predict target values
# score = pickle_model.score(X_test, y_test)
# print("Test score: {0:.2f} %".format(100 * score))
# Ypredict = pickle_model.predict(X_test)


# tuple_objects = (lgbm_model, X_test, y_test, score)

# # Save tuple
# pickle.dump(tuple_objects, open("tuple_model.pkl", 'wb'))
#
# # Restore tuple
# pickled_model, pickled_Xtrain, pickled_Ytrain, pickled_score = pickle.load(open("tuple_model.pkl", 'rb'))
#
# print(pickled_score)
