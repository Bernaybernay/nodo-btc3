import hashlib
import json
import os
import time
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = '30052823Aa$'  # Clave maestra de administrador

CONFIG_FILE = 'wallet_btc3_segura.json'
LIMITE_MAXIMO_DEFAULT = 25_000_000_000  
RECOMPENSA_BLOQUE = 10          
TIEMPO_ESPERA_BLOQUE = 600      # 10 minutos exactos

def cargar_datos():
    if not os.path.exists(CONFIG_FILE):
        datos_iniciales = {
            "blockchain": [], 
            "billeteras": {},  
            "transacciones": [],
            "ultimo_tiempo_bloque": 0,
            "aportes_pool": {},
            "limite_maximo": LIMITE_MAXIMO_DEFAULT,
            "monedas_extra_admin": 0.0
        }
        guardar_datos(datos_iniciales)
        return datos_iniciales
    try:
        with open(CONFIG_FILE, 'r') as f:
            datos = json.load(f)
            if "limite_maximo" not in datos:
                datos["limite_maximo"] = LIMITE_MAXIMO_DEFAULT
            if "monedas_extra_admin" not in datos:
                datos["monedas_extra_admin"] = 0.0
            return datos
    except json.JSONDecodeError:
        return {
            "blockchain": [], "billeteras": {}, "transacciones": [], 
            "ultimo_tiempo_bloque": 0, "aportes_pool": {}, 
            "limite_maximo": LIMITE_MAXIMO_DEFAULT, "monedas_extra_admin": 0.0
        }

def guardar_datos(datos):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(datos, f, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == '30052823Aa$':
            session['autenticado'] = True
            return redirect(url_for('index'))
        else:
            return render_template_string(LOGIN_HTML, error="Contraseña incorrecta")

    if not session.get('autenticado'):
        return render_template_string(LOGIN_HTML, error=None)

    datos = cargar_datos()
    limite = datos.get('limite_maximo', LIMITE_MAXIMO_DEFAULT)
    suministro_actual = len(datos['blockchain']) * RECOMPENSA_BLOQUE
    monedas_extra = datos.get('monedas_extra_admin', 0.0)
    suministro_total = suministro_actual + monedas_extra

    tiempo_actual = time.time()
    tiempo_transcurrido = tiempo_actual - datos['ultimo_tiempo_bloque']
    tiempo_restante = max(0, int(TIEMPO_ESPERA_BLOQUE - tiempo_transcurrido))

    return render_template_string(PANEL_HTML, 
                                  blockchain=datos['blockchain'], 
                                  billeteras=datos['billeteras'], 
                                  transacciones=datos['transacciones'],
                                  suministro=suministro_total, 
                                  limite=limite,
                                  tiempo_restante=tiempo_restante)

@app.route('/crear_billetera', methods=['POST'])
def crear_billetera():
    if not session.get('autenticado'):
        return redirect(url_for('index'))

    nombre = request.form.get('nombre_billetera').strip()
    clave = request.form.get('clave_personal').strip()

    if not nombre or not clave:
        return "Error: Debes ingresar un nombre y una clave personal."

    datos = cargar_datos()
    if nombre in datos['billeteras']:
        return "Error: Esta billetera ya existe. Si es tuya, usa tu clave para iniciar sesión o minar."

    datos['billeteras'][nombre] = {
        "password": hashlib.sha256(clave.encode()).hexdigest(),
        "balance": 0.0
    }
    guardar_datos(datos)
    return redirect(url_for('index'))

@app.route('/mine_solo', methods=['POST'])
def minar_solo():
    if not session.get('autenticado'):
        return redirect(url_for('index'))

    billetera = request.form.get('billetera').strip()
    clave = request.form.get('clave').strip()
    nonce_cliente = request.form.get('nonce')

    datos = cargar_datos()
    billeteras = datos['billeteras']

    if billetera not in billeteras:
        return "Error: La billetera no está registrada."
    
    clave_hash = hashlib.sha256(clave.encode()).hexdigest()
    if billeteras[billetera]['password'] != clave_hash:
        return "Error: Clave personal incorrecta."

    tiempo_actual = time.time()
    if datos['ultimo_tiempo_bloque'] > 0:
        if (tiempo_actual - datos['ultimo_tiempo_bloque']) < TIEMPO_ESPERA_BLOQUE:
            return "Espera: Solo se permite un bloque global cada 10 minutos."

    suministro_actual = (len(datos['blockchain']) * RECOMPENSA_BLOQUE) + datos.get('monedas_extra_admin', 0.0)
    limite = datos.get('limite_maximo', LIMITE_MAXIMO_DEFAULT)
    if suministro_actual >= limite:
        return "Límite máximo global alcanzado."

    ultimo_nonce = datos['blockchain'][-1]['nonce'] if datos['blockchain'] else 1
    if hashlib.sha256(f'{ultimo_nonce}{nonce_cliente}'.encode()).hexdigest()[:3] != "000":
        return "Error: Prueba de trabajo inválida."

    billeteras[billetera]['balance'] += RECOMPENSA_BLOQUE

    nuevo_bloque = {
        "index": len(datos['blockchain']) + 1,
        "tipo": "Solitario",
        "nonce": nonce_cliente,
        "minero": billetera,
        "recompensa": RECOMPENSA_BLOQUE
    }
    datos['blockchain'].append(nuevo_bloque)
    datos['ultimo_tiempo_bloque'] = tiempo_actual
    datos['aportes_pool'] = {}

    guardar_datos(datos)
    return redirect(url_for('index'))

@app.route('/aporte_pool', methods=['POST'])
def aporte_pool():
    if not session.get('autenticado'):
        return {"status": "error", "msg": "No autorizado"}

    billetera = request.form.get('billetera').strip()
    clave = request.form.get('clave').strip()
    hashes_aportados = int(request.form.get('hashes', 0))

    datos = cargar_datos()
    billeteras = datos['billeteras']

    if billetera not in billeteras or billeteras[billetera]['password'] != hashlib.sha256(clave.encode()).hexdigest():
        return {"status": "error", "msg": "Billetera o clave incorrecta"}

    tiempo_actual = time.time()
    tiempo_transcurrido = tiempo_actual - datos['ultimo_tiempo_bloque']

    if datos['ultimo_tiempo_bloque'] > 0 and tiempo_transcurrido >= TIEMPO_ESPERA_BLOQUE:
        blockchain = datos['blockchain']
        aportes = datos['aportes_pool']
        suministro_actual = (len(blockchain) * RECOMPENSA_BLOQUE) + datos.get('monedas_extra_admin', 0.0)
        limite = datos.get('limite_maximo', LIMITE_MAXIMO_DEFAULT)

        if suministro_actual < limite and len(aportes) > 0:
            total_hashes = sum(aportes.values())
            if total_hashes > 0:
                repartos = {}
                for w, h in aportes.items():
                    if w in billeteras:
                        premio = RECOMPENSA_BLOQUE * (h / total_hashes)
                        billeteras[w]['balance'] += premio
                        repartos[w] = round(premio, 4)

                blockchain.append({
                    "index": len(blockchain) + 1,
                    "tipo": "Compartido (Pool)",
                    "nonce": "pool_repartida",
                    "minero": "Comunidad Pool",
                    "recompensa": RECOMPENSA_BLOQUE,
                    "reparto": repartos
                })
                datos['ultimo_tiempo_bloque'] = tiempo_actual
                datos['aportes_pool'] = {}
                guardar_datos(datos)
                return {"status": "bloque_encontrado_pool"}

    if billetera not in datos['aportes_pool']:
        datos['aportes_pool'][billetera] = 0
    datos['aportes_pool'][billetera] += hashes_aportados

    guardar_datos(datos)
    return {"status": "ok"}

@app.route('/transferir', methods=['POST'])
def transferir():
    if not session.get('autenticado'):
        return redirect(url_for('index'))

    origen = request.form.get('origen').strip()
    clave = request.form.get('clave').strip()
    destino = request.form.get('destino').strip()
    try:
        cantidad = float(request.form.get('cantidad', 0))
    except ValueError:
        return "Cantidad inválida."

    datos = cargar_datos()
    billeteras = datos['billeteras']

    if origen not in billeteras or billeteras[origen]['password'] != hashlib.sha256(clave.encode()).hexdigest():
        return "Error: Billetera de origen o clave personal incorrecta."
    if destino not in billeteras:
        return "Error: La billetera de destino no existe."
    if cantidad <= 0 or origen == destino:
        return "Datos de transferencia incorrectos."

    if billeteras[origen]['balance'] < cantidad:
        return "Fondos insuficientes."

    billeteras[origen]['balance'] -= cantidad
    billeteras[destino]['balance'] += cantidad

    datos['transacciones'].append({"de": origen, "para": destino, "monto": cantidad, "timestamp": time.time()})
    guardar_datos(datos)
    return redirect(url_for('index'))

@app.route('/admin_monedas', methods=['POST'])
def admin_monedas():
    if not session.get('autenticado'):
        return redirect(url_for('index'))

    try:
        nuevas_monedas = float(request.form.get('cantidad_extra', 0) or 0)
        nuevo_limite_input = request.form.get('nuevo_limite', '').strip()
    except ValueError:
        return "Valores inválidos."

    datos = cargar_datos()
    if "monedas_extra_admin" not in datos:
        datos["monedas_extra_admin"] = 0.0

    if nuevas_monedas > 0:
        datos["monedas_extra_admin"] += nuevas_monedas
        destino_admin = request.form.get('billetera_admin', '').strip()
        if destino_admin and destino_admin in datos['billeteras']:
            datos['billeteras'][destino_admin]['balance'] += nuevas_monedas

    if nuevo_limite_input:
        try:
            datos['limite_maximo'] = float(nuevo_limite_input)
        except ValueError:
            pass

    guardar_datos(datos)
    return redirect(url_for('index'))

@app.route('/api/info', methods=['GET'])
def api_info():
    datos = cargar_datos()
    suministro_actual = (len(datos['blockchain']) * RECOMPENSA_BLOQUE) + datos.get('monedas_extra_admin', 0.0)
    balances_simples = {w: info['balance'] for w, info in datos['billeteras'].items()}
    return {
        "moneda": "Btc3",
        "suministro_actual": suministro_actual,
        "limite_maximo": datos.get('limite_maximo', LIMITE_MAXIMO_DEFAULT),
        "saldos": balances_simples
    }

@app.route('/logout')
def logout():
    session.pop('autenticado', None)
    return redirect(url_for('index'))

# --- HTML / INTERFAZ ---
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Acceso</title>
<style>
body { background: #0b0f19; color: #fff; font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; margin:0;}
.card { background: #161b22; padding: 30px; border-radius: 12px; width: 300px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
input { width: 90%; padding: 10px; margin: 15px 0; background: #0d1117; border: 1px solid #30363d; color: #fff; border-radius: 6px; }
button { background: #f7931a; color: #fff; border: none; padding: 10px; font-weight: bold; border-radius: 6px; cursor: pointer; width: 100%; }
</style></head>
<body>
<div class="card">
<h2>🔒 Nodo Btc3</h2>
<form method="POST"><input type="password" name="password" placeholder="Contraseña de Nodo" required><button type="submit">Ingresar</button></form>
</div></body></html>
"""

PANEL_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><title>Red Btc3</title>
<style>
body { background: #0b0f19; color: #c9d1d9; font-family: Arial; margin: 0; padding: 20px; }
.container { max-width: 950px; margin: auto; background: #161b22; padding: 25px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
h1, h2 { color: #f7931a; }
.stats { display: flex; justify-content: space-between; background: #0d1117; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #30363d; flex-wrap: wrap; gap: 10px; }
input, button { padding: 10px; border-radius: 6px; font-size: 14px; margin: 5px 0; }
input { background: #0d1117; border: 1px solid #30363d; color: #fff; width: 100%; box-sizing: border-box; }
button { background: #f7931a; color: #fff; border: none; font-weight: bold; cursor: pointer; width: 100%; }
button:hover { background: #e08212; }
table { width: 100%; border-collapse: collapse; margin-top: 15px; }
th, td { padding: 10px; border-bottom: 1px solid #30363d; text-align: left; }
th { color: #f7931a; }
.logout { float: right; background: #f85149; color: #fff; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 13px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 15px; }
.box { background: #0d1117; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
.admin-box { border: 1px solid #f7931a; background: #121620; margin-top: 20px; }
</style>
</head>
<body>
<div class="container">
<a href="/logout" class="logout">Salir</a>
<h1>🌐 Red Oficial Btc3</h1>
<p>Sistema seguro: Billeteras con clave personal y persistencia de datos.</p>

<div class="stats">
<div><strong>Suministro Total:</strong> {{ suministro }} / {{ limite }} Btc3</div>
<div><strong>Bloques:</strong> {{ blockchain | length }}</div>
<div><strong>Próximo Bloque en:</strong> <span id="timer" style="color:#f7931a;">{{ tiempo_restante }}</span>s</div>
</div>

<div class="grid">
<!-- CREAR BILLETERA -->
<div class="box">
<h2>🔑 Crear Billetera</h2>
<form action="/crear_billetera" method="POST">
<input type="text" name="nombre_billetera" placeholder="Nombre de Billetera" required>
<input type="password" name="clave_personal" placeholder="Tu Clave Secreta" required>
<button type="submit">Registrar Billetera</button>
</form>
</div>

<!-- MINERIA SOLITARIO -->
<div class="box">
<h2>⛏️ Minería Solitario</h2>
<input type="text" id="wSolo" placeholder="Tu Billetera" required>
<input type="password" id="kSolo" placeholder="Tu Clave Secreta" required>
<button type="button" onclick="minarSolo()" id="btnSolo">Minar Bloque</button>
<p id="stSolo" style="font-size:12px; color:#8b949e;"></p>
</div>

<!-- MINERIA POOL -->
<div class="box">
<h2>👥 Minería Pool</h2>
<input type="text" id="wPool" placeholder="Tu Billetera" required>
<input type="password" id="kPool" placeholder="Tu Clave Secreta" required>
<button type="button" onclick="togglePool()" id="btnPool">Unirse a Pool</button>
<p id="stPool" style="font-size:12px; color:#8b949e;">Desconectado</p>
</div>

<!-- TRANSFERENCIAS -->
<div class="box">
<h2>💸 Transferir</h2>
<form action="/transferir" method="POST">
<input type="text" name="origen" placeholder="Tu Billetera Origen" required>
<input type="password" name="clave" placeholder="Tu Clave Secreta" required>
<input type="text" name="destino" placeholder="Billetera Destino" required>
<input type="number" step="any" name="cantidad" placeholder="Monto Btc3" required>
<button type="submit">Enviar Fondos</button>
</form>
</div>
</div>

<!-- PANEL DE ADMINISTRADOR: AÑADIR MONEDAS -->
<div class="box admin-box">
<h2>⚙️ Panel Admin: Emitir / Añadir Monedas</h2>
<form action="/admin_monedas" method="POST">
<input type="number" step="any" name="cantidad_extra" placeholder="Cantidad de monedas a crear extra">
<input type="text" name="billetera_admin" placeholder="Asignar a esta billetera (Opcional)">
<input type="number" step="any" name="nuevo_limite" placeholder="Nuevo Límite Máximo Global (Opcional)">
<button type="submit" style="background:#238636;">Actualizar Monedas / Límite</button>
</form>
</div>

<h2>💼 Billeteras Registradas</h2>
<table>
<tr><th>Billetera</th><th>Balance</th></tr>
{% for w, info in billeteras.items() %}
<tr><td>{{ w }}</td><td>{{ info.balance }} Btc3</td></tr>
{% else %}
<tr><td colspan="2">No hay billeteras creadas.</td></tr>
{% endfor %}
</table>

<h2>⛓️ Historial de Bloques</h2>
<table>
<tr><th>Nº</th><th>Tipo</th><th>Minero</th><th>Recompensa</th></tr>
{% for b in blockchain | reverse %}
<tr><td>#{{ b.index }}</td><td>{{ b.tipo }}</td><td>{{ b.minero }}</td><td>{{ b.recompensa }} Btc3</td></tr>
{% else %}
<tr><td colspan="4">Sin bloques.</td></tr>
{% endfor %}
</table>
</div>

<script>
let tiempoRestante = {{ tiempo_restante }};
const timerEl = document.getElementById('timer');
if (tiempoRestante > 0) {
    setInterval(() => {
        if (tiempoRestante > 0) tiempoRestante--;
        timerEl.innerText = tiempoRestante > 0 ? tiempoRestante : "¡Listo!";
    }, 1000);
}

async function sha256(msg) {
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(msg));
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function minarSolo() {
    let w = document.getElementById('wSolo').value;
    let k = document.getElementById('kSolo').value;
    let st = document.getElementById('stSolo');
    if(!w || !k) { alert("Ingresa billetera y clave"); return; }
    if(tiempoRestante > 0) { alert("Espera a que pasen los 10 minutos."); return; }

    st.innerText = "Buscando bloque...";
    let nonce = 0, encontrado = false;
    while(!encontrado && nonce < 300000) {
        if((await sha256("1" + nonce)).startsWith("000")) { encontrado = true; break; }
        nonce++;
    }

    if(encontrado) {
        let f = document.createElement('form'); f.method='POST'; f.action='/mine_solo';
        f.innerHTML = `<input name="billetera" value="${w}"><input name="clave" value="${k}"><input name="nonce" value="${nonce}">`;
        document.body.appendChild(f); f.submit();
    } else { st.innerText = "No encontrado, intenta de nuevo."; }
}

let poolInt = null;
function togglePool() {
    let w = document.getElementById('wPool').value;
    let k = document.getElementById('kPool').value;
    let btn = document.getElementById('btnPool');
    let st = document.getElementById('stPool');
    if(!w || !k) { alert("Ingresa billetera y clave"); return; }

    if(poolInt) {
        clearInterval(poolInt); poolInt = null;
        btn.innerText = "Unirse a Pool"; st.innerText = "Desconectado";
        btn.style.background = "#f7931a";
    } else {
        btn.innerText = "Salir de Pool"; st.innerText = "Minando en grupo...";
        btn.style.background = "#f85149";
        poolInt = setInterval(async () => {
            let data = new URLSearchParams();
            data.append('billetera', w); data.append('clave', k); data.append('hashes', 10000);
            let res = await fetch('/aporte_pool', {method:'POST', body: data});
            let json = await res.json();
            if(json.status === "bloque_encontrado_pool") { alert("¡Bloque de pool completado!"); location.reload(); }
        }, 3000);
    }
}
</script>
</body>
</html>
"""

# Arranque seguro para Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
