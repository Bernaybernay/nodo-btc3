import hashlib
import time
import secrets
import json
import os
from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
WALLET_FILE = "wallet.json"
PASSWORD_SECRETA = "30052823Aa$"

class Wallet:
    def __init__(self):
        if os.path.exists(WALLET_FILE):
            with open(WALLET_FILE, "r") as f:
                data = json.load(f)
                self.private_key = data["private_key"]
                self.address = data["address"]
        else:
            self.private_key = secrets.token_hex(32)
            self.address = "btc3_" + hashlib.sha256(self.private_key.encode()).hexdigest()[:16]
            with open(WALLET_FILE, "w") as f:
                json.dump({"private_key": self.private_key, "address": self.address}, f)

class Bloque:
    def __init__(self, indice, transacciones, hash_anterior, dificultad):
        self.indice = indice
        self.timestamp = time.time()
        self.transacciones = transacciones
        self.hash_anterior = hash_anterior
        self.dificultad = dificultad
        self.nonce = 0
        self.hash = self.minar()

    def calcular_hash(self):
        texto = f"{self.indice}{self.timestamp}{str(self.transacciones)}{self.hash_anterior}{self.nonce}"
        return hashlib.sha256(texto.encode('utf-8')).hexdigest()

    def minar(self):
        objetivo = '0' * self.dificultad
        while True:
            hash_actual = self.calcular_hash()
            if hash_actual.startswith(objetivo):
                return hash_actual
            self.nonce += 1

class NodoBtc3:
    def __init__(self, dificultad=3):
        self.dificultad = dificultad
        self.cadena = []

    def crear_bloque_genesis(self, direccion_creador):
        oferta_inicial = 999_999_999_999_999_999
        transaccion_genesis = {
            "emisor": "GENESIS_NETWORK", 
            "receptor": direccion_creador, 
            "monto": oferta_inicial
        }
        bloque_gen = Bloque(0, [transaccion_genesis], "0", self.dificultad)
        self.cadena.append(bloque_gen)

    def consultar_saldo(self, dir):
        return sum(
            tx["monto"] for b in self.cadena for tx in b.transacciones if tx["receptor"] == dir
        ) - sum(
            tx["monto"] for b in self.cadena for tx in b.transacciones if tx["emisor"] == dir
        )

    def agregar_transaccion(self, emisor, receptor, monto):
        if self.consultar_saldo(emisor) < monto:
            return False, "Fondos insuficientes"
        transaccion = {"emisor": emisor, "receptor": receptor, "monto": monto}
        ultimo_bloque = self.cadena[-1]
        nuevo_bloque = Bloque(
            len(self.cadena),
            [transaccion],
            ultimo_bloque.hash,
            self.dificultad
        )
        self.cadena.append(nuevo_bloque)
        return True, "¡Transacción enviada con éxito!"

nodo = NodoBtc3(dificultad=3)
mi_wallet = Wallet()
nodo.crear_bloque_genesis(mi_wallet.address)

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Acceso Seguro - Btc3</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 50px; }
        .card { background: #1e293b; border-radius: 12px; padding: 30px; max-width: 400px; margin: auto; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        h2 { color: #f59e0b; }
        input, button { width: 100%; padding: 12px; margin-top: 12px; border-radius: 6px; border: none; box-sizing: border-box; }
        input { background: #334155; color: white; text-align: center; font-size: 16px; }
        button { background: #f59e0b; color: #0f172a; font-weight: bold; cursor: pointer; }
        .error { color: #f43f5e; margin-top: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🔒 Nodo Protegido</h2>
        <p>Introduce tu clave de acceso para continuar:</p>
        <form method="POST">
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit">Ingresar</button>
        </form>
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Nodo Web - Btc3</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 20px; }
        .card { background: #1e293b; border-radius: 12px; padding: 20px; max-width: 500px; margin: 20px auto; box-shadow: 0 4px 10px rgba(0,0,0,0.3); text-align: left; }
        h1 { color: #f59e0b; text-align: center; }
        h3 { color: #38bdf8; font-size: 16px; margin-top: 15px; }
        .saldo { font-size: 22px; font-weight: bold; color: #10b981; margin: 10px 0; text-align: center; word-break: break-all; }
        .address { font-size: 13px; background: #334155; padding: 8px; border-radius: 6px; word-break: break-all; font-family: monospace; }
        input, button { width: 100%; padding: 10px; margin-top: 8px; border-radius: 6px; border: none; box-sizing: border-box; }
        input { background: #334155; color: white; }
        button { background: #f59e0b; color: #0f172a; font-weight: bold; cursor: pointer; margin-top: 15px; }
        .msg { color: #f43f5e; text-align: center; margin-top: 10px; font-weight: bold; }
        .success { color: #10b981; text-align: center; margin-top: 10px; font-weight: bold; }
        .logout { display: block; text-align: center; margin-top: 20px; color: #f43f5e; text-decoration: none; font-size: 14px; }
    </style>
</head>
<body>
    <h1>🚀 Nodo Oficial de Btc3</h1>
    <div class="card">
        <h3>Tu Dirección (Creador)</h3>
        <div class="address">{{ address }}</div>
        
        <h3>Tu Saldo Disponible</h3>
        <div class="saldo">{{ saldo }} BTC3</div>

        <hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;">

        <h3>Enviar BTC3 a otra persona</h3>
        <form method="POST" action="/enviar">
            <label>Dirección de destino:</label>
            <input type="text" name="receptor" placeholder="Ej: btc3_xxxx..." required>
            
            <label>Cantidad a enviar:</label>
            <input type="number" name="monto" placeholder="Ej: 1000" required>
            
            <button type="submit">Realizar Transferencia</button>
        </form>

        {% if mensaje %}
            <div class="{{ tipo_msg }}">{{ mensaje }}</div>
        {% endif %}

        <a class="logout" href="/logout">Cerrar sesión</a>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD_SECRETA:
            session['autenticado'] = True
            return redirect(url_for('home'))
        else:
            error = "Contraseña incorrecta"

    if not session.get('autenticado'):
        return render_template_string(LOGIN_TEMPLATE, error=error)

    saldo = nodo.consultar_saldo(mi_wallet.address)
    return render_template_string(HTML_TEMPLATE, address=mi_wallet.address, saldo=f"{saldo:,}", mensaje=None)

@app.route('/enviar', methods=['POST'])
def enviar():
    if not session.get('autenticado'):
        return redirect(url_for('home'))

    receptor = request.form.get('receptor')
    try:
        monto = int(request.form.get('monto'))
    except ValueError:
        monto = 0

    exito, mensaje = nodo.agregar_transaccion(mi_wallet.address, receptor, monto)
    saldo = nodo.consultar_saldo(mi_wallet.address)
    
    tipo_msg = "success" if exito else "msg"
    return render_template_string(HTML_TEMPLATE, address=mi_wallet.address, saldo=f"{saldo:,}", mensaje=mensaje, tipo_msg=tipo_msg)

@app.route('/logout')
def logout():
    session.pop('autenticado', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
