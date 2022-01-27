# Este código tem alterações na forma de consulta SQL em relação ao documento application.ipynb
# Pode ser rodado no ambiente CS50 IDE, ambiente virtual Linux Ubuntu AWS disponibilizado por Harvard no curso de introdução à ciência de computação CS50

from cs50 import SQL
from flask import Flask, render_template, request, session, redirect
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///poker.db")

@app.route("/")
def index():
    if not session.get("name"):
        return redirect("/login")
    return render_template("inicio.html")

@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        session["name"] = request.form.get("name")
        return redirect("/")
    return render_template("login.html")

@app.route("/logout", methods = ["POST", "GET"])
def logout():
    session["name"] = None
    return redirect("/")

@app.route("/participantes", methods=["POST", "GET"])
def participantes():
    nome_p1 = session["name"]
    nro_participantes = int(request.form.get("nro_participantes"))
    quantia_inicial = int(request.form.get("quantia_inicial"))
    return render_template("participantes.html", nro_participantes=nro_participantes, quantia_inicial=quantia_inicial, nome_p1=nome_p1)

@app.route("/poker", methods=["POST","GET"])
def poker():
    nro_participantes = int(request.form.get("nro_part"))
    quantia_inicial = request.form.get("qt_inicial")
    part = []
    for i, item in enumerate(range(nro_participantes)):
        part.append(request.form.get("p"+str(i+1)))
    db.execute("DELETE FROM participantes")
    db.execute("DELETE FROM transacoes")
    for i, participante in enumerate(range(nro_participantes)):
        db.execute("INSERT INTO participantes(nome, quantia) VALUES(?, ?)", part[i], quantia_inicial)
    pote = "Pote"
    db.execute("INSERT INTO participantes(nome, quantia) VALUES(?, ?)", pote, 0)
    participantes = db.execute("SELECT * FROM participantes")
    transacoes = db.execute("SELECT * FROM transacoes")
    return render_template("poker.html", participantes=participantes, nro_participantes=nro_participantes, quantia_inicial=quantia_inicial, transacoes=transacoes)

@app.route("/poker2", methods=["POST", "GET"])
def poker2():
    nro_participantes = int(request.form.get("nro_part"))
    quantia_inicial = int(request.form.get("qt_inicial"))
    debito = request.form.get("debito")
    credito = request.form.get("credito")
    valor_s = request.form.get("valor")
    valor = int(valor_s)
    conta_cred = db.execute("SELECT quantia FROM participantes WHERE id = ?", credito)
    conta_deb = db.execute("SELECT quantia FROM participantes WHERE id = ?", debito)
    nome_cred = db.execute("SELECT nome FROM participantes WHERE id = ?", credito)
    nome_deb = db.execute("SELECT nome FROM participantes WHERE id = ?", debito)
    saldo_cred = int(float(conta_cred[0]['quantia'])) + valor
    db.execute("UPDATE participantes SET quantia = ? WHERE id = ?", saldo_cred, credito)
    saldo_deb = int(float(conta_deb[0]['quantia'])) - valor
    db.execute("UPDATE participantes SET quantia = ? WHERE id = ?", saldo_deb, debito)
    db.execute("INSERT INTO transacoes(de, para, quantia) VALUES(?, ?, ?)", nome_deb[0]["nome"], nome_cred[0]["nome"], valor)
    participantes = db.execute("SELECT * FROM participantes")
    transacoes = db.execute("SELECT * FROM transacoes ORDER BY id DESC")
    return render_template("poker2.html", participantes=participantes, debito=debito, credito=credito, valor=valor, conta_deb=conta_deb, conta_cred=conta_cred, nro_participantes=nro_participantes, quantia_inicial=quantia_inicial, transacoes=transacoes )
