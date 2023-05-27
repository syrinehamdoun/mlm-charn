import joblib
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, json, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import pickle
import re
import os
import csv
from io import TextIOWrapper
import pandas as pd
import streamlit as st

from jinja2 import defaults

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'banque'

# Intialize MySQL
mysql = MySQL(app)


@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('index.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['ID']
            session['username'] = account['login']
            session['email'] = account['email']
            session['role'] = account['role']
            # Redirect to home page
            return redirect(url_for('dashboard'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'email ou mote de passe incorrecte!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    msg = ''
    a = 0
    if request.method == 'POST':
        # Create variables for easy access
        id = request.form['id']
        nom = request.form['nom']
        Nb_fils_direct = request.form['Nb_fils_direct']
        pays = request.form.get('pays')
        genre = request.form['genre']
        Nb_fils = request.form['Nb_fils']
        Grade = request.form.get('Grade')
        NB_cheque = request.form['NB_cheque']
        Prime_animation = request.form.get('Prime_animation')
        Prime_parrainage = request.form.get('Prime_parrainage')
        Date_naissance = request.form.get('Date_naissance')
        Date_inscription = request.form.get('Date_inscription')
        Nb_fois_actif = request.form.get('Nb_fois_actif')



        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM conseillers WHERE IdConseiller = %s', (id,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Customer already exists!'
            a = 1

        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO conseillers VALUES (NULL, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                           (id, nom, Nb_fils_direct, pays, genre, Nb_fils, Grade, NB_cheque, Prime_animation, Prime_parrainage, Date_naissance, Date_inscription,Nb_fois_actif, quitter,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            a = 2

    return render_template('add_customer.html', username=session['username'], msg=msg, a=a)


@app.route('/get_customer/<IdConseiller>', methods=['GET', 'POST'])
def get_customer(IdConseiller):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM conseillers WHERE IdConseiller = %s', (IdConseiller,))
    data = cursor.fetchall()
    cursor.close()
    print(data[0])

    return render_template('update_customer.html', username=session['username'], data=data[0])


@app.route('/update_customer/<IdConseiller>', methods=['GET', 'POST'])
def update_customer(IdConseiller):
    msg = ''
    if request.method == 'POST':
        # Create variables for easy access
        id = request.form['id']
        nom = request.form['nom']
        Nb_fils_direct = request.form['Nb_fils_direct']
        pays = request.form.get('pays')
        genre = request.form['genre']
        Nb_fils = request.form['Nb_fils']
        Grade = request.form.get('Grade')
        NB_cheque = request.form['NB_cheque']
        Prime_animation = request.form.get('Prime_animation')
        Prime_parrainage = request.form.get('Prime_parrainage')
        Date_naissance = request.form.get('Date_naissance')
        Date_inscription = request.form.get('Date_inscription')
        Nb_fois_actif = request.form.get('Nb_fois_actif')
        quitter = 1



        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE conseillers set Nom=%s,Nb_fils_direct=%s,Pays=%s,Genre=%s,Grade=%s,NB_cheque=%s,'
                       'Prime_animation=%s,Prime_parrainage=%s,Date_naissance=%s,Date_inscription=%s,Nb_fois_actif=%s,Nb_fils=%s,Quitte=%s where IdConseiller=%s',
                       (nom, Nb_fils_direct, pays, genre, Grade, NB_cheque,Prime_animation, Prime_parrainage, Date_naissance, Date_inscription, Nb_fois_actif,Nb_fils, quitter, id))
        mysql.connection.commit()
        msg = 'You have successfully updated!'
        account = cursor.fetchone()

    return redirect(url_for('historique'))


@app.route('/delete_customer/<string:IdConseiller>', methods=['POST', 'GET'])
def delete_customer(IdConseiller):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM  conseillers WHERE IdConseiller = {0}'.format(IdConseiller))
    mysql.connection.commit()

    exist=cursor.execute('Select IdConseiller from conseillers_prediction WHERE IdConseiller = {0}'.format(IdConseiller))
    if exist:
        cursor.execute('DELETE FROM  conseillers_prediction WHERE IdConseiller = {0}'.format(IdConseiller))
        mysql.connection.commit()



    return redirect(url_for('historique'))


@app.route('/delete_customer_analyse/<string:IdConseiller>', methods=['POST', 'GET'])
def delete_customer_analyse(IdConseiller):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM  conseillers_prediction WHERE IdConseiller = {0}'.format(IdConseiller))
    mysql.connection.commit()
    return redirect(url_for('analyse'))


# Listes des conseillerss
@app.route('/historique', methods=['POST', 'GET'])
def historique():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM conseillers where ligne>9970')
    conseillers = cursor.fetchall()

    return render_template('historique.html', username=session['username'], conseillers=conseillers)


# Listes des conseillerss aprés prédiction
@app.route('/analyse', methods=['POST', 'GET'])
def analyse():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM conseillers_prediction where Ligne>9990')
    conseillers = cursor.fetchall()

    return render_template('analyse_customer.html', username=session['username'], conseillers=conseillers)


# upload csv
@app.route("/upload", methods=['GET', 'POST'])
def uploadFiles():
    if request.method == 'POST':
        csv_file = request.files['file']
        csv_file = TextIOWrapper(csv_file, encoding='utf-8', errors='ignore')
        csv_reader = csv.reader(csv_file, delimiter=';')

        try:
            if csv_reader.__next__():
                csv_reader = csv_reader
                for row in csv_reader:
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    exist = cursor.execute('select IdConseiller from conseillers where IdConseiller=%s', (row[1],))

                    if not exist:
                        sql = "INSERT INTO conseillers (IdConseiller,nom, Nb_fils_direct, pays, genre, Grade, NB_cheque,Prime_animation, Prime_parrainage, Date_naissance, Date_inscription, Nb_fois_actif,Nb_fils, quitter, id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        value = (
                            row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                            row[12],
                            row[13],)
                        cursor.execute(sql, value)
                        mysql.connection.commit()

                    else:
                        sql = "UPDATE conseillers set Nom=%s,CreditScore=%s,Pays=%s,Genre=%s,Age=%s,Tenure=%s,Solde=%s,NbreDeProduits=%s,AvoirCarteCr=%s,MembreActif=%s,SalaireEstime=%s,Quitte=%s where IdConseiller=%s"
                        value = (
                            row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12],
                            row[13],
                            row[1],)
                        cursor.execute(sql, value)
                        mysql.connection.commit()
                return redirect(url_for('historique'))
            else:
                raise (StopIteration, UnicodeEncodeError, csv.Error, IndexError)


        except (StopIteration, UnicodeEncodeError, csv.Error, IndexError):
            flash('Il y a un problème dans le fichier')
            return redirect(url_for('historique'))

        return render_template('historique.html', username=session['username'])


@app.route('/user_list')
def user_list():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user  ')
    user = cursor.fetchall()

    return render_template('user_list.html', username=session['username'], user=user)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    msg = ''
    if request.method == 'POST':

        login = request.form['login']
        password = request.form['password']
        email = request.form['email']
        if request.form.get('role'):
            role = "Super Admin"
        else:
            role = "Utilisateur"

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO user VALUES (NULL, %s,%s,%s,%s)', (login, password, email, role,))
        msg = 'user added successfully'
        mysql.connection.commit()
        cursor.close()
    return render_template('add_user.html', username=session['username'], msg=msg)


@app.route('/get_user/<ID>', methods=['GET', 'POST'])
def get_user(ID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user WHERE ID = %s', (ID,))
    data = cursor.fetchall()
    cursor.close()
    print(data[0])

    return render_template('update_user.html', username=session['username'], data=data[0])


@app.route('/update_user/<ID>', methods=['GET', 'POST'])
def update_user(ID):
    msg = ''
    if request.method == 'POST':
        # Create variables for easy access
        login = request.form['login']
        password = request.form['password']
        email = request.form['email']

        if request.form.get('role'):
            role = "Super Admin"
        else:
            role = "Utilisateur"

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE user set login=%s,password=%s,email=%s,role=%s where ID=%s',
                       (login, password, email, role, ID,))
        mysql.connection.commit()
        msg = 'You have successfully updated!'
        account = cursor.fetchone()

    return redirect(url_for('user_list'))


@app.route('/delete_user/<string:ID>', methods=['POST', 'GET'])
def delete_user(ID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM  user WHERE ID = {0}'.format(ID))
    mysql.connection.commit()
    return redirect(url_for('user_list'))


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', username=session['username'])


@app.route('/get_predict_customer/', defaults={'IdConseiller': 0})
@app.route('/get_predict_customer/<IdConseiller>', methods=['GET', 'POST'])
def get_predict_customer(IdConseiller):
    message = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM conseillers WHERE IdConseiller = %s', (IdConseiller,))
    data = cursor.fetchone()
    if data:
        cursor.close()

    else:
        message = "Le conseillers n'existe pas"

    return render_template('predictionCustomer.html', username=session['username'], data=data, message=message)


# # Load model
# with open('LightGBM.pkl', 'rb') as file:
#     model = pickle.load(file)
#
# # Load scaler
# with open('Scaler.pkl', 'rb') as file:
#     sc = pickle.load(file)

clf = joblib.load('classifier.pkl')
sca = joblib.load('scale.pkl')


@app.route('/prediction/<IdConseiller>', methods=['GET', 'POST'])
def predictionCustomer(IdConseiller):
    if request.method == 'POST':
        CreditScore = int(request.form['score'])
        Age = int(request.form['age'])
        Tenure = int(request.form['tenure'])
        Solde = float(request.form['solde'])
        NbreDeProduits = int(request.form['nb_prod'])
        SalaireEstime = float(request.form['salaire'])

        Pays_Germany = request.form['pays']
        if (Pays_Germany == 'Germany'):
            Pays_Germany = 1
            Pays_Spain = 0
            Pays_France = 0
            pays = 'Germany'

        elif (Pays_Germany == 'Spain'):
            Pays_Germany = 0
            Pays_Spain = 1
            Pays_France = 0
            pays = 'Spain'

        else:
            Pays_Germany = 0
            Pays_Spain = 0
            Pays_France = 1
            pays = 'France'

        Genre_Homme = request.form['genre']
        if (Genre_Homme == 'Homme'):
            Genre_Homme = 1
            Genre_Femme = 0
            genre = 'Homme'
        else:
            Genre_Homme = 0
            Genre_Femme = 1
            genre = 'Femme'

        if request.form.get('etat'):
            MembreActif = 1
        else:
            MembreActif = 0

        if request.form.get('carte'):
            AvoirCarteCr = 1
        else:
            AvoirCarteCr = 0

        input_data = [[CreditScore, Age, Tenure, Solde, NbreDeProduits, MembreActif, Pays_Germany, Genre_Femme]]
        input_data = pd.DataFrame(input_data)

        input_data.columns = ['CreditScore', 'Age', 'Tenure', 'Solde', 'NbreDeProduits', 'MembreActif', 'Pays_Germany',
                              'Genre_Femme']
        c = ['CreditScore', 'Age', 'Tenure', 'Solde', 'NbreDeProduits']
        # sc = StandardScaler()
        input_data[c] = sca.transform(input_data[c])

        # X_test_data=sca.transform(input_data)

        prediction = clf.predict(input_data)
        prediction_proba = clf.predict_proba(input_data)
        prediction_proba = prediction_proba[:, 1]
        prediction_proba = (prediction_proba * 100).round(2)
        prediction_proba = prediction_proba.item(0)

        if prediction == 1:
            quitte = 1
        else:
            quitte = 0

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        exist = cursor.execute('select * from conseillers_prediction where IdConseiller=%s', (IdConseiller,))

        if not exist:
            cursor.execute('select * from conseillers where IdConseiller=%s', (IdConseiller,))
            data = cursor.fetchone()
            print(data)
            Nom = data["Nom"]

            sql = "INSERT INTO conseillers_prediction (IdConseiller, Nom, CreditScore, Pays, Genre,Age,Tenure,Solde,NbreDeProduits,AvoirCarteCr,MembreActif,SalaireEstime,Quitte,Probabilite_quitte) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)"
            value = (
                IdConseiller, Nom, CreditScore, pays, genre, Age, Tenure, Solde, NbreDeProduits, AvoirCarteCr, MembreActif,
                SalaireEstime, quitte, prediction_proba,)
            cursor.execute(sql, value)
            mysql.connection.commit()

        else:
            sql = "UPDATE conseillers_prediction set CreditScore=%s,Pays=%s,Genre=%s,Age=%s,Tenure=%s,Solde=%s,NbreDeProduits=%s,AvoirCarteCr=%s,MembreActif=%s,SalaireEstime=%s,Quitte=%s,Probabilite_quitte=%s where IdConseiller=%s"
            value = (
                CreditScore, pays, genre, Age, Tenure, Solde, NbreDeProduits, AvoirCarteCr, MembreActif,
                SalaireEstime, quitte, prediction_proba, IdConseiller)
            cursor.execute(sql, value)
            mysql.connection.commit()

        req=cursor.execute('select * from conseillers_prediction where IdConseiller=%s', (IdConseiller,))
        d=cursor.fetchone()

        return render_template('prediction.html', prediction=prediction, prediction_proba=prediction_proba,d=d)




@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    return render_template('prediction.html', username=session['username'])


@app.route('/prediction_much_customer', methods=['GET', 'POST'])
def prediction_much_customer():
    if request.method == 'POST':

        df = pd.read_csv(request.files.get('file'), error_bad_lines=False, sep=';', encoding='unicode_escape')

        df2 = df
        df2 = df2.drop(columns=['Ligne'])
        df2 = df2.drop(columns=['Quitte'])

        df = df.drop(columns=['Ligne'])

        IdConseiller = df['IdConseiller']
        Nom = df['Nom']
        CreditScore = df['CreditScore']
        Pays = df['Pays']
        Genre = df['Genre']
        Age = df['Age']
        Tenure = df['Tenure']
        Solde = df['Solde']
        NbreDeProduits = df['NbreDeProduits']
        AvoirCarteCr = df['AvoirCarteCr']
        MembreActif = df['MembreActif']
        SalaireEstime = df['SalaireEstime']

        df = df[['CreditScore', 'Pays', 'Genre', 'Age', 'Tenure', 'Solde', 'NbreDeProduits', 'MembreActif', 'Quitte']]
        df = pd.get_dummies(df)
        df = df[['CreditScore', 'Age', 'Tenure', 'Solde', 'NbreDeProduits', 'MembreActif', 'Quitte',
                 'Pays_Germany', 'Genre_Femme']]
        X = df.iloc[:, [0, 1, 2, 3, 4, 5, 7, 8]]
        y = df.iloc[:, 6].values
        y = pd.DataFrame(y)

        c = ['CreditScore', 'Age', 'Tenure', 'Solde', 'NbreDeProduits']

        X[c] = sca.transform(X[c])

        prediction = clf.predict(X)
        prediction_proba = clf.predict_proba(X)
        prediction_proba = prediction_proba[:, 1]
        prediction_proba = (prediction_proba * 100).round(2)

        result = df2
        result['Quitte'] = prediction
        result['Probabilite_quitte'] = prediction_proba

        for index, row in result.iterrows():

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            exist = cursor.execute('select * from conseillers_prediction where IdConseiller=%s', (row.IdConseiller,))

            if not exist:

                sql = "INSERT INTO conseillers_prediction (IdConseiller, Nom, CreditScore, Pays, Genre,Age,Tenure,Solde,NbreDeProduits,AvoirCarteCr,MembreActif,SalaireEstime,Quitte,Probabilite_quitte) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)"
                value = (
                    row.IdConseiller, row.Nom, row.CreditScore, row.Pays, row.Genre, row.Age, row.Tenure, row.Solde,
                    row.NbreDeProduits, row.AvoirCarteCr, row.MembreActif,
                    row.SalaireEstime, row.Quitte, row.Probabilite_quitte,)
                cursor.execute(sql, value)
                mysql.connection.commit()

            else:
                sql = "UPDATE conseillers_prediction set CreditScore=%s,Pays=%s,Genre=%s,Age=%s,Tenure=%s,Solde=%s,NbreDeProduits=%s,AvoirCarteCr=%s,MembreActif=%s,SalaireEstime=%s,Quitte=%s,Probabilite_quitte=%s where IdConseiller=%s"
                value = (
                    row.CreditScore, row.Pays, row.Genre, row.Age, row.Tenure, row.Solde,
                    row.NbreDeProduits, row.AvoirCarteCr, row.MembreActif,
                    row.SalaireEstime, row.Quitte, row.Probabilite_quitte, row.IdConseiller)
                cursor.execute(sql, value)
                mysql.connection.commit()

        return redirect(url_for('analyse'))


@app.route('/get_customerPred/<IdConseiller>', methods=['GET', 'POST'])
def get_customerPred(IdConseiller):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM conseillers WHERE IdConseiller = %s', (IdConseiller,))
    data = cursor.fetchone()

    return render_template('getCustomerPred.html', username=session['username'], data=data)


@app.route('/predictionSingle/<IdConseiller>', methods=['GET', 'POST'])
def predictionSingle(IdConseiller):
    if request.method == 'POST':
        CreditScore = int(request.form['score'])
        Age = int(request.form['age'])
        Tenure = int(request.form['tenure'])
        Solde = float(request.form['solde'])
        NbreDeProduits = int(request.form['nb_prod'])
        SalaireEstime = float(request.form['salaire'])

        Pays_Germany = request.form['pays']
        if (Pays_Germany == 'Germany'):
            Pays_Germany = 1
            Pays_Spain = 0
            Pays_France = 0
            pays = 'Germany'

        elif (Pays_Germany == 'Spain'):
            Pays_Germany = 0
            Pays_Spain = 1
            Pays_France = 0
            pays = 'Spain'

        else:
            Pays_Germany = 0
            Pays_Spain = 0
            Pays_France = 1
            pays = 'France'

        Genre_Homme = request.form['genre']
        if (Genre_Homme == 'Homme'):
            Genre_Homme = 1
            Genre_Femme = 0
            genre = 'Homme'
        else:
            Genre_Homme = 0
            Genre_Femme = 1
            genre = 'Femme'

        if request.form.get('etat'):
            MembreActif = 1
        else:
            MembreActif = 0

        if request.form.get('carte'):
            AvoirCarteCr = 1
        else:
            AvoirCarteCr = 0

        input_data = [[CreditScore, Age, Tenure, Solde, NbreDeProduits, MembreActif, Pays_Germany, Genre_Femme]]
        input_data = pd.DataFrame(input_data)

        input_data.columns = ['CreditScore', 'Age', 'Tenure', 'Solde', 'NbreDeProduits', 'MembreActif', 'Pays_Germany',
                              'Genre_Femme']
        c = ['CreditScore', 'Age', 'Tenure', 'Solde', 'NbreDeProduits']
        # sc = StandardScaler()
        input_data[c] = sca.transform(input_data[c])

        # X_test_data=sca.transform(input_data)

        prediction = clf.predict(input_data)
        prediction_proba = clf.predict_proba(input_data)
        prediction_proba = prediction_proba[:, 1]
        prediction_proba = (prediction_proba * 100).round(2)
        prediction_proba = prediction_proba.item(0)

        if prediction == 1:
            quitte = 1
        else:
            quitte = 0

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        exist = cursor.execute('select * from conseillers_prediction where IdConseiller=%s', (IdConseiller,))
        d = cursor.fetchone()

        if not exist:
            cursor.execute('select * from conseillers where IdConseiller=%s', (IdConseiller,))
            data = cursor.fetchone()
            print(data)
            Nom = data["Nom"]

            sql = "INSERT INTO conseillers_prediction (IdConseiller, Nom, CreditScore, Pays, Genre,Age,Tenure,Solde,NbreDeProduits,AvoirCarteCr,MembreActif,SalaireEstime,Quitte,Probabilite_quitte) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)"
            value = (
                IdConseiller, Nom, CreditScore, pays, genre, Age, Tenure, Solde, NbreDeProduits, AvoirCarteCr, MembreActif,
                SalaireEstime, quitte, prediction_proba,)
            cursor.execute(sql, value)
            mysql.connection.commit()

        else:
            sql = "UPDATE conseillers_prediction set CreditScore=%s,Pays=%s,Genre=%s,Age=%s,Tenure=%s,Solde=%s,NbreDeProduits=%s,AvoirCarteCr=%s,MembreActif=%s,SalaireEstime=%s,Quitte=%s,Probabilite_quitte=%s where IdConseiller=%s"
            value = (
                CreditScore, pays, genre, Age, Tenure, Solde, NbreDeProduits, AvoirCarteCr, MembreActif,
                SalaireEstime, quitte, prediction_proba, IdConseiller)
            cursor.execute(sql, value)
            mysql.connection.commit()

    req = cursor.execute('select * from conseillers_prediction where IdConseiller=%s', (IdConseiller,))
    d = cursor.fetchone()

    if prediction == 1:
        return render_template('ResultatPred.html', prediction=prediction, prediction_proba=prediction_proba, d=d)
    else:
        return render_template('ResultatPred.html', prediction=prediction, prediction_proba=prediction_proba, d=d)


@app.route('/prediction2', methods=['GET', 'POST'])
def prediction2():
    return render_template('ResultatPred.html', username=session['username'])


# @app.route('/h')
# def historique1():
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute('SELECT * FROM conseillers   ')
#     conseillers = cursor.fetchall()
#
#     data = []
#     c = {}
#
#     for i in conseillers:
#         c = {'IdConseiller': i['IdConseiller'], 'Nom': i['Nom'], 'CreditScore': i['CreditScore'], 'Pays': i['Pays'],
#              'Genre': i['Genre'], 'Age': i['Age'], 'Tenure': i['Tenure'], 'Solde': i['Solde'],
#              'NbreDeProduits': i['NbreDeProduits'], 'AvoirCarteCr': i['AvoirCarteCr'],
#              'MembreActif': i['MembreActif'], 'SalaireEstime': i['SalaireEstime'], 'Quitte': i['Quitte']}
#
#         data.append(c)
#         c = {}
#
#     return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
