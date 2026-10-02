from flask import Flask, render_template_string, jsonify, request
import time
import threading

app = Flask(__name__)

estado_red = {
    "suministroTotal": 10.0,
    "limiteSuministro": 25000000.0,
    "bloquesCount": 1,
    "tiempoRestante": 600,
    "historialBloques": [
        {"numero": 1, "tipo": "Génesis", "minero": "Gabriel", "recompensa": 10.0}
    ],
    "billeteras": [
        {"nombre": "Gabriel", "balance": 999999999999999.0, "claveSecreta": "tu_clave"}
    ]
}

CLAVE_ADMIN = "30052823"

def bucle_cronometro():
    while True:
        time.sleep(1)
        estado_red["tiempoRestante"] -= 1
        if estado_red["tiempoRestante"] <= 0:
            if estado_red["suministroTotal"] < estado_red["limiteSuministro"]:
                estado_red["bloquesCount"] += 1
                estado_red["suministroTotal"] += 10.0
                estado_red["historialBloques"].insert(0, {
                    "numero": estado_red["bloquesCount"],
                    "tipo": "Automático / Red",
                    "minero": "Sistema",
                    "recompensa": 10.0
                })
            estado_red["tiempoRestante"] = 600

hilo = threading.Thread(target=bucle_cronometro, daemon=True)
hilo.start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Red Oficial Btc3 - Admin Ilimitado</title>
    <style>
        body { background: #131722; color: #fff; font-family: Arial, sans-serif; padding: 20px; margin: 0; }
        nav { background: #1e222d; padding: 10px; border-radius: 8px; margin-bottom: 20px; display: flex; gap: 10px; flex-wrap: wrap; }
        nav button { background: #2a2e39; color: #fff; border: none; padding: 10px 15px; cursor: pointer; border-radius: 4px; font-weight: bold; }
        nav button.active { background: #ff9800; }
        .pantalla { display: none; background: #1e222d; padding: 20px; border-radius: 8px; }
        .pantalla.active { display: block; }
        button.accion { background: #ff9800; color: white; border: none; padding: 8px 12px; cursor: pointer; border-radius: 4px; }
        input { padding: 8px; margin: 5px 0; background: #2a2e39; color: #fff; border: 1px solid #444; width: 100%; box-sizing: border-box; }
        .log { background: #111; padding: 10px; margin-top: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; }
    </style>
</head>
<body>

    <h1>Red Oficial Btc3 (Admin Ilimitado)</h1>

    <nav>
        <button id="btn-minar" class="active" onclick="cambiarPantalla('minar')">⛏️ Zona de Minado</button>
        <button id="btn-billetera" onclick="cambiarPantalla('billetera')">💼 Billetera</button>
        <button id="btn-admin" onclick="cambiarPantalla('admin')">⚙️ Admin</button>
    </nav>

    <div id="pantalla-minar" class="pantalla active">
        <h2>Zona de Minado (10 Btc3 / 10 Minutos)</h2>
        <p>Bloques totales: <span id="bloquesCount">1</span></p>
        <p>Próximo Bloque en: <strong id="cronometro" style="color: #ff9800;">600</strong>s</p>
        <hr style="border-color: #333;">
        <h3>Minar Bloque Solitario</h3>
        <input type="text" id="mineroBilletera" placeholder="Nombre de tu Billetera (ej: Gabriel)">
        <input type="password" id="mineroClave" placeholder="Clave Secreta">
        <button class="accion" onclick="minarBloque()">Minar Bloque (10 Btc3)</button>
        <div id="minadoLog" class="log">Estado: Esperando acción...</div>
    </div>

    <div id="pantalla-billetera" class="pantalla">
        <h2>Gestión de Billetera</h2>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 250px; background: #131722; padding: 15px; border-radius: 6px;">
                <h3>Registrar Billetera</h3>
                <input type="text" id="regNombre" placeholder="Nombre">
                <input type="password" id="regClave" placeholder="Clave Secreta">
                <button class="accion" onclick="crearBilletera()">Registrar</button>
            </div>
            <div style="flex: 1; min-width: 250px; background: #131722; padding: 15px; border-radius: 6px;">
                <h3>Transferencia Libre</h3>
                <input type="text" id="transOrigen" placeholder="Tu Billetera Origen">
                <input type="password" id="transClave" placeholder="Tu Clave Secreta">
                <input type="text" id="transDestino" placeholder="Billetera Destino">
                <input type="number" id="transMonto" placeholder="Monto Btc3">
                <button class="accion" onclick="enviarFondos()">Enviar</button>
            </div>
        </div>
        <div id="billeteraLog" class="log" style="margin-top: 15px;"></div>
    </div>

    <div id="pantalla-admin" class="pantalla">
        <h2>Panel de Dueño / Administrador</h2>
        <input type="password" id="claveAdminInput" placeholder="Contraseña de Administrador">
        <button class="accion" onclick="ingresarAdmin()">Entrar</button>
        
        <div id="panelAdminOculto" style="display:none; margin-top: 15px;">
            <p style="color: #4CAF50;">¡Acceso de administrador concedido!</p>
            <hr style="border-color: #333; margin: 15px 0;">
            <h3>Emisión Infinita (Enviar a cualquier billetera)</h3>
            <input type="text" id="adminDestino" placeholder="Billetera Destino">
            <input type="number" id="adminMonto" placeholder="Cantidad Masiva / Infinita">
            <button class="accion" style="background: #4CAF50;" onclick="adminEnviarFondos()">Enviar Fondos Infinitos</button>
            <br><br>
            <button class="accion" style="background: #f44336;" onclick="forzarSiguienteBloque()">Forzar Siguiente Bloque</button>
            <div id="adminLog" class="log" style="margin-top: 10px;"></div>
        </div>
    </div>

<script>
let tiempoVisual = 600;

function cambiarPantalla(nombre) {
    document.querySelectorAll('.pantalla').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
    document.getElementById('pantalla-' + nombre).classList.add('active');
    document.getElementById('btn-' + nombre).classList.add('active');
}

setInterval(() => {
    if (tiempoVisual > 0) {
        tiempoVisual--;
        let min = Math.floor(tiempoVisual / 60);
        let seg = tiempoVisual % 60;
        document.getElementById('cronometro').innerText = min + "m " + seg + "s";
    }
}, 1000);

async function sincronizar() {
    try {
        let res = await fetch('/api/estado');
        let data = await res.json();
        tiempoVisual = data.tiempoRestante;
        document.getElementById('bloquesCount').innerText = data.bloquesCount;
    } catch (e) {
        console.error("Error", e);
    }
}
setInterval(sincronizar, 5000);

async function minarBloque() {
    let minero = document.getElementById('mineroBilletera').value;
    let clave = document.getElementById('mineroClave').value;
    let res = await fetch('/api/minar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ minero, clave })
    });
    let data = await res.json();
    document.getElementById('minadoLog').innerText = data.mensaje || data.error;
    sincronizar();
}

async function crearBilletera() {
    let nombre = document.getElementById('regNombre').value;
    let clave = document.getElementById('regClave').value;
    let res = await fetch('/api/billetera/crear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre, clave })
    });
    let data = await res.json();
    document.getElementById('billeteraLog').innerText = data.mensaje || data.error;
}

async function enviarFondos() {
    let origen = document.getElementById('transOrigen').value;
    let clave = document.getElementById('transClave').value;
    let destino = document.getElementById('transDestino').value;
    let monto = parseFloat(document.getElementById('transMonto').value);
    
    let res = await fetch('/api/transferir', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ origen, clave, destino, monto })
    });
    let data = await res.json();
    document.getElementById('billeteraLog').innerText = data.mensaje || data.error;
}

function ingresarAdmin() {
    let clave = document.getElementById('claveAdminInput').value;
    if (clave === "30052823") {
        document.getElementById('panelAdminOculto').style.display = 'block';
        alert("¡Acceso concedido correctamente!");
    } else {
        alert("Contraseña incorrecta.");
    }
}

async function adminEnviarFondos() {
    let claveAdmin = document.getElementById('claveAdminInput').value;
    let destino = document.getElementById('adminDestino').value;
    let monto = parseFloat(document.getElementById('adminMonto').value);

    let res = await fetch('/api/admin/enviar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ claveAdmin, destino, monto })
    });
    let data = await res.json();
    document.getElementById('adminLog').innerText = data.mensaje || data.error;
}

async function forzarSiguienteBloque() {
    let claveAdmin = document.getElementById('claveAdminInput').value;
    let res = await fetch('/api/admin/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ claveAdmin })
    });
    let data = await res.json();
    if (res.ok) {
        sincronizar();
        alert("Bloque forzado con éxito.");
    } else {
        alert(data.error);
    }
}

sincronizar();
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/estado')
def api_estado():
    return jsonify(estado_red)

@app.route('/api/billetera/crear', methods=['POST'])
def crear_billetera():
    data = request.get_json()
    nombre = data.get("nombre")
    clave = data.get("clave")
    if not nombre or not clave:
        return jsonify({"error": "Faltan datos"}), 400
    for b in estado_red["billeteras"]:
        if b["nombre"] == nombre:
            return jsonify({"error": "La billetera ya existe"}), 400
    estado_red["billeteras"].append({"nombre": nombre, "balance": 0.0, "claveSecreta": clave})
    return jsonify({"mensaje": f"Billetera '{nombre}' creada con éxito."})

@app.route('/api/transferir', methods=['POST'])
def transferir():
    data = request.get_json()
    origen_nombre = data.get("origen")
    clave = data.get("clave")
    destino_nombre = data.get("destino")
    monto = data.get("monto")
    
    w_origen = next((b for b in estado_red["billeteras"] if b["nombre"] == origen_nombre and b["claveSecreta"] == clave), None)
    w_destino = next((b for b in estado_red["billeteras"] if b["nombre"] == destino_nombre), None)
    
    if not w_origen:
        return jsonify({"error": "Billetera de origen o clave incorrecta"}), 400
    if not w_destino:
        return jsonify({"error": "Billetera de destino no encontrada"}), 400
    if w_origen["balance"] < monto:
        return jsonify({"error": "Fondos insuficientes"}), 400
        
    w_origen["balance"] -= monto
    w_destino["balance"] += monto
    return jsonify({"mensaje": f"¡Transferencia exitosa de {monto} Btc3 a {destino_nombre}!"})

@app.route('/api/minar', methods=['POST'])
def minar():
    data = request.get_json()
    minero = data.get("minero")
    clave = data.get("clave")
    
    w = next((b for b in estado_red["billeteras"] if b["nombre"] == minero and b["claveSecreta"] == clave), None)
    if not w:
        return jsonify({"error": "Billetera o clave de minero inválida"}), 400
        
    if estado_red["suministroTotal"] + 10.0 > estado_red["limiteSuministro"]:
        return jsonify({"error": "Se ha alcanzado el límite de suministro de 25 millones."}), 400
        
    w["balance"] += 10.0
    estado_red["bloquesCount"] += 1
    estado_red["suministroTotal"] += 10.0
    estado_red["historialBloques"].insert(0, {
        "numero": estado_red["bloquesCount"],
        "tipo": "Solitario",
        "minero": minero,
        "recompensa": 10.0
    })
    estado_red["tiempoRestante"] = 600
    return jsonify({"mensaje": f"¡Bloque minado con éxito! +10 Btc3 añadidos a {minero}"})

@app.route('/api/admin/enviar', methods=['POST'])
def admin_enviar():
    data = request.get_json()
    if not data or data.get("claveAdmin") != CLAVE_ADMIN:
        return jsonify({"error": "No autorizado"}), 403
    
    destino_nombre = data.get("destino")
    monto = data.get("monto")
    
    w_destino = next((b for b in estado_red["billeteras"] if b["nombre"] == destino_nombre), None)
    if not w_destino:
        return jsonify({"error": "La billetera de destino no existe"}), 400
        
    w_destino["balance"] += monto
    return jsonify({"mensaje": f"¡Emitidos y enviados {monto} Btc3 con éxito a {destino_nombre}!"})

@app.route('/api/admin/reset', methods=['POST'])
def admin_reset():
    data = request.get_json()
    if not data or data.get("claveAdmin") != CLAVE_ADMIN:
        return jsonify({"error": "No autorizado"}), 403
    estado_red["tiempoRestante"] = 600
    return jsonify({"mensaje": "Reiniciado"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
