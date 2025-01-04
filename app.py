from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required,current_user
from models import db, User
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'key_sessione_user' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db.init_app(app)
login_manager = LoginManager() 
login_manager.init_app(app) 
login_manager.login_view = 'login'
@login_manager.user_loader

def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()


    


# Calcolatore Codice Fiscale
def codice_cognome(cognome):
    consonanti = ''.join([c for c in cognome if c.isalpha() and c not in 'AEIOU'])
    vocali = ''.join([c for c in cognome if c.isalpha() and c in 'AEIOU'])
    codice = (consonanti + vocali + 'XXX')[:3].upper()
    return codice

def codice_nome(nome):
    consonanti = ''.join([c for c in nome if c.isalpha() and c not in 'AEIOU'])
    vocali = ''.join([c for c in nome if c.isalpha() and c in 'AEIOU'])
    if len(consonanti) >= 4:
        consonanti = consonanti[0] + consonanti[2] + consonanti[3]
        codice = (consonanti + vocali + 'XXX')[:3].upper()
    else:
        codice = (consonanti + vocali + 'XXX')[:3].upper()
    return codice

def codice_data_nascita(data_nascita, sesso):
    mese_codice = 'ABCDEHLMPRST'
 
    anno = str(data_nascita.year)[-2:]
    mese = mese_codice[data_nascita.month - 1]
    giorno = data_nascita.day + 40 if sesso == 'F' else data_nascita.day
    giorno = f'{giorno:02d}'
    return anno + mese + giorno

def codice_comune(comune_str):
    comune = {
        'ROMA': 'H501',
        'MILANO': 'F205',
        'NAPOLI': 'F839',
        'TORINO': 'L219',
        'FIRENZE': 'D612',
        'BOLOGNA': 'A944',
        'GENOVA': 'D969',
        'VENEZIA': 'L736',
        'PALERMO': 'G273',
        'CAGLIARI': 'B354',
    }
    # Ensure comune_str is valid and uppercase
    if isinstance(comune_str, str):
        return comune.get(comune_str.upper(), 'XXXX')  # Default to 'XXXX' if comune is unknown
    return 'XXXX'

def carattere_di_controllo(cf_parziale):
    valori = {
        **{chr(i): i - 48 for i in range(48, 58)},
        **{chr(i): i - 55 for i in range(65, 91)}
    }
    dispari = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
            1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 1, 0, 5, 7, 9, 13, 15, 17, 19, 21,
            1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 1, 0, 5, 7, 9, 13, 15, 17, 19, 21]
    pari = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
            1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 1, 0, 5, 7, 9, 13, 15, 17, 19, 21,
            1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 1, 0, 5, 7, 9, 13, 15, 17, 19, 21]

    somma = sum(dispari[valori[cf_parziale[i]]] if i % 2 == 0 else pari[valori[cf_parziale[i]]] for i in range(15))
    return chr((somma % 26) + 65)

def calcola_cf(nome, cognome, data_nascita, sesso, comune):
    cf = codice_cognome(cognome)
    cf += codice_nome(nome)
    cf += codice_data_nascita(data_nascita, sesso)
    cf += codice_comune(comune)
    cf += carattere_di_controllo(cf)
    return cf
#Register

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Prendere i dati dal database
        username = request.form['username'] 
        password = request.form['password']
        nome = request.form['nome']
        cognome = request.form['cognome']
        sesso = request.form['sesso']
        data_nascita = datetime.strptime(request.form['data_nascita'], '%Y-%m-%d')
        luogo_nascita = request.form['luogo_nascita']
        comune = request.form['comune']
        #Controllo per vedere se esiste già
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Questo username è già in uso.")
        #Invio dati al metodo calcola_cf
        codice_fiscale = calcola_cf(nome, cognome, data_nascita,sesso,comune)
        new_user = User(username=username, password=password, nome=nome,cognome=cognome,data_nascita= data_nascita,luogo_nascita = luogo_nascita,sesso=sesso,comune=comune, codice_fiscale = codice_fiscale)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html', error=None)

#Login

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #prende dati dal form
        username = request.form['username'] 
        password = request.form['password']
        #cerca user su db
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
        return render_template('login.html', error="Credenziali non valide.") 
    return render_template('login.html', error=None)

#Home

@app.route('/home')
@login_required
def home():
     return f"Benvenuto, {current_user.nome} {current_user.cognome}. Il tuo codice fiscale è {current_user.codice_fiscale}"

if __name__ == '__main__': 
    
    app.run(debug=True)