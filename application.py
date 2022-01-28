# Este código tem alterações na forma de consulta SQL em relação ao documento application_pyodbc.ipynb
# Pode ser rodado no ambiente CS50 IDE, ambiente virtual cloud Linux Ubuntu AWS disponibilizado por Harvard no curso de introdução à ciência de computação CS50

from cs50 import SQL
from flask import Flask, render_template, request, session, redirect
from flask_session import Session

app = Flask(__name__)
# configuro a session para lembrar o nome que foi inserido
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///poker.db")

# a funçao index checa se tem algum nome na session, se sim, leva a pagina inicial, se não, leva ao login
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

# logout apaga o nome registrado na session
@app.route("/logout", methods = ["POST", "GET"])
def logout():
    session["name"] = None
    return redirect("/")

# a função participantes pega o nome da session para ser usado como o participante um, e tambem retorna número de participantes e quantia inicial dos participantes
@app.route("/participantes", methods=["POST", "GET"])
def participantes():
    nome_p1 = session["name"]
    nro_participantes = int(request.form.get("nro_participantes"))
    quantia_inicial = int(request.form.get("quantia_inicial"))
    return render_template("participantes.html", nro_participantes=nro_participantes, quantia_inicial=quantia_inicial, nome_p1=nome_p1)

# poker carrega a primeira pagina do jogo com as instruções
@app.route("/poker", methods=["POST","GET"])
def poker():
    nro_participantes = int(request.form.get("nro_part"))
    quantia_inicial = request.form.get("qt_inicial")
    # aqui deletamos todos os dados prévios registrados nas duas tabelas
    db.execute("DELETE FROM participantes")
    db.execute("DELETE FROM transacoes")
    # aqui pegamos o nome de cada participante e inserimos na tabela com a quantia inicial
    for i, item in enumerate(range(nro_participantes)):
        part = request.form.get("p"+str(i+1))
        db.execute("INSERT INTO participantes(nome, quantia) VALUES(?, ?)", part, quantia_inicial)
    # depois inserimos a ultima linha com o Pote de Apostas com valor igual a zero
    db.execute("INSERT INTO participantes(nome, quantia) VALUES(?, 0)", "Pote")
    participantes = db.execute("SELECT * FROM participantes")
    transacoes = db.execute("SELECT * FROM transacoes")
    return render_template("poker.html", participantes=participantes, nro_participantes=nro_participantes, quantia_inicial=quantia_inicial, transacoes=transacoes)

# poker 2 é a página do restante do jogo
@app.route("/poker2", methods=["POST", "GET"])
def poker2():
    # pegamos as variaveis nro_participante e quantia_inicial atraves de uma tag input escondida na pagina poker
    nro_participantes = int(request.form.get("nro_part"))
    quantia_inicial = int(request.form.get("qt_inicial"))
    # pegamos o numero da conta de debito, credito e o valor da transferencia
    debito = int(request.form.get("debito"))
    credito = int(request.form.get("credito"))
    valor = int(request.form.get("valor"))
    # chacamos se o valor da conta de credito e debito nao sao as mesmas, se forem as mesmas a pagina recarrega e nada acontece
    if credito != debito:
        # aqui pegamos o saldo das contas
        conta_cred = db.execute("SELECT quantia FROM participantes WHERE id = ?", credito)
        conta_deb = db.execute("SELECT quantia FROM participantes WHERE id = ?", debito)
        # em seguida o nome dos participantes com as contas
        nome_cred = db.execute("SELECT nome FROM participantes WHERE id = ?", credito)
        nome_deb = db.execute("SELECT nome FROM participantes WHERE id = ?", debito)
        # verificamos se o valor é 0, se for, fazemos como dito nas intruções do jogo 
        # e transferimos todo o valor de uma conta para outra, facilitanto a usabilidade durante o jogo
        if valor != 0:
            saldo_cred = int(float(conta_cred[0]['quantia'])) + valor
            db.execute("UPDATE participantes SET quantia = ? WHERE id = ?", saldo_cred, credito)
            saldo_deb = int(float(conta_deb[0]['quantia'])) - valor
            db.execute("UPDATE participantes SET quantia = ? WHERE id = ?", saldo_deb, debito)
        else:
            valor = int(float(conta_deb[0]['quantia']))
            saldo_cred = int(float(conta_cred[0]['quantia'])) + valor
            db.execute("UPDATE participantes SET quantia = ? WHERE id = ?", saldo_cred, credito)
            saldo_deb = 0
            db.execute("UPDATE participantes SET quantia = ? WHERE id = ?", saldo_deb, debito)
        # inserimos na tabela de transacoes o nome de quem recebeu e quem pagou além do valor da transferencia
        db.execute("INSERT INTO transacoes(de, para, quantia) VALUES(?, ?, ?)", nome_deb[0]["nome"], nome_cred[0]["nome"], valor)
        # para definirmos qual conta ficara como padrão na proxima transação, 
        # temos que checar se a ultima conta de transferencia/ debito é maior que o número de participantes. 
        # Nesse caso a conta padrão volta a ser 1, facilitando as transações que ocorrem de forma sequencial no poker
        if debito < nro_participantes:
            debito_default = debito + 1
        else:
            debito_default = 1
    # caso a conta de debito e credito sejam a mesma, temos que definir uma conta padrao para o proxima transferencia, 
    # uma vez que precisamos passar essa variavel logo abaixo no return
    else:
        debito_default = 1
    # aqui fazemos as consultas de participantes e transações para aparecer na página
    participantes = db.execute("SELECT * FROM participantes")
    # ordenamos as transações com id decrescente para que as ultimas transações fiquem no topo, facilitando a leitura e usabilidade
    transacoes = db.execute("SELECT * FROM transacoes ORDER BY id DESC")
    return render_template("poker2.html", debito_default=debito_default, participantes=participantes, debito=debito, credito=credito, valor=valor, nro_participantes=nro_participantes, quantia_inicial=quantia_inicial, transacoes=transacoes )
