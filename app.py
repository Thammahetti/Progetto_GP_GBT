from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required,current_user
from models import db, User
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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
    consonanti = ''.join([c for c in cognome.upper() if c.isalpha() and c not in 'AEIOU'])
    vocali = ''.join([c for c in cognome.upper() if c.isalpha() and c in 'AEIOU'])
    codice = (consonanti + vocali + 'XXX')[:3]
    return codice

def codice_nome(nome):

    consonanti = ''.join([c for c in nome.upper() if c.isalpha() and c not in 'AEIOU'])
    vocali = ''.join([c for c in nome.upper() if c.isalpha() and c in 'AEIOU'])
    if len(consonanti) >= 4:
        codice = consonanti[0] + consonanti[2] + consonanti[3]
    else:
        codice = (consonanti + vocali + 'XXX')[:3]
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
    'MILANO': 'F205',
    'BRESCIA': 'B157',
    'COMO': 'C671',
    'VARESE': 'L744',
    'MONZA': 'F836',
    'PAVIA': 'G324',
    'LECCO': 'E762',
    'CREMONA': 'D817',
    'ALBAIRATE': 'A127',
    'MANTOVA': 'F452',
    'LODI': 'E371',
    'SONDRIO': 'L840',
    'SEREGNO': 'I800',
    'CERNUSCO SUL NAVIGLIO': 'C234',
    'LEGNANO': 'E142',
    'DESIO': 'D465',
    'SESTO SAN GIOVANNI': 'I690',
    'RHO': 'L294',
    'VIGEVANO': 'L869',
    'SAN DONATO MILANESE': 'I815',
    'CODOGNO': 'C735',
    'CARUGATE': 'B216',
    'CARATE BRIANZA': 'B171',
    'CAVENAGO DI BRIANZA': 'C204',
    'CAGLIARI': 'B354',
    'SARONNO': 'I464',
    'GORGONZOLA': 'D474',
    'BUSTO ARSIZIO': 'B659',
    'ROBBIATE': 'H332',
    'NERVIANO': 'E679',
    'TREVIGLIO': 'L898',
    'SEGRATE': 'I410',
    'BARLASSINA': 'B507',
    'ABBIATEGRASSO': 'A051',
    'COLOGNO MONZESE': 'C492',
    'GALLARATE': 'D857',
    'BERGAMO': 'B197',
    'ALBINO': 'A800',
    'CARAVAGGIO': 'C286',
    'ALME': 'A530',
    'CAPRIATE SAN GERVASIO': 'B416',
    'SORESINA': 'I860',
    'ROVATO': 'L804',
    'SOMMA LOMBARDO': 'I953',
    'ROSSANO': 'F913',
    'PADERNO DUGNANO': 'I801',
    'CASTELLANZA': 'C441',
    'OLGINATE': 'I124',
    'LISSONE': 'D624',
    'PIEVE EMANUELE': 'D692',
    'PIEDIMONTE SAN GERMANO': 'E396',
    'MERATE': 'E402',
    'FAGNANO OLONA': 'E387',
    'MAZZANO': 'B928',
    'SOMAGLIA': 'F776',
    'TRADATE': 'E725',
    'VILLA GUARDIA': 'F431',
    'VALGREGHENTINO': 'V845',
    'VALMASINO': 'V967',
    'CASALMAGGIORE': 'C469',
    'PONTE SAN PIETRO': 'P374',
    'PESCATE': 'F340',
    'PIANELLO DEL LARIO': 'P283',
    'SALÒ': 'S613',
    'SAN BARTOLOMEO AL MARE': 'F274',
    'LIVRAGA': 'F274',
    'CASSOLNOVO': 'C245',
    'CAMPOGALLIANO': 'C265',
    'CANZO': 'C601',
    'BELLINZAGO NOVARESE': 'B619',
    'SIRMIONE': 'S624',
    'GUSSAGO': 'G301',
    'SAN MARTINO SICCOMARIO': 'F896',
    'BELLUSCO': 'B524',
    'LAZZATE': 'L108',
    'GRASSOBBIO': 'G846',
    'RONCONE': 'F724',
    'GORDONA': 'G795',
    'CARPI': 'F442',
    'CASTIGLIONE ADDA': 'C340',
    'CISLAGO': 'C106',
    'GAMBOLO': 'G217',
    'ROMA': 'H501',
    'LIVIGNO': 'L317',
    'VIMERCATE': 'V649',
    'MONZAMBANO': 'M296',
    'SERRADIFALCO': 'S675',
    'BOLOGNA': 'A944',
    'VOGHERA': 'L896',
    'PIACENZA': 'D607',
    'CUNEO': 'C231',
    'GENOVA': 'D969',
    'VENEZIA': 'L736',

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
        password_hash = generate_password_hash(password)
        nome = request.form['nome']
        cognome = request.form['cognome']
        sesso = request.form['sesso']
        data_nascita = datetime.strptime(request.form['data_nascita'], '%Y-%m-%d')
        data_emissione = datetime.now()
        luogo_nascita = request.form['luogo_nascita']
        comune = request.form['comune']
        #Controllo per vedere se esiste già
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Questo username è già in uso.")
        #Invio dati al metodo calcola_cf
        codice_fiscale = calcola_cf(nome, cognome, data_nascita,sesso,comune)
        new_user = User(username=username, password=password_hash, nome=nome,cognome=cognome,data_nascita= data_nascita,luogo_nascita = luogo_nascita,sesso=sesso,comune=comune, codice_fiscale = codice_fiscale, data_emissione = data_emissione)
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
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        return render_template('login.html', error="Credenziali non valide.") 
    return render_template('login.html', error=None)

#Home

@app.route('/home')
@login_required
def home():
    giornoattuale = current_user.data_emissione.day 
    meseattuale = current_user.data_emissione.month
    annosei = current_user.data_emissione.year + 6
    data_scadenza = f"{annosei}-{meseattuale}-{giornoattuale}"
    return render_template('home.html', error=None, data_scadenza = data_scadenza)


if __name__ == '__main__': 
    
    app.run(debug=True)