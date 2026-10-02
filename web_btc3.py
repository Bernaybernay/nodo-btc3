from flask import Flask, render_template_string, jsonify, request
import time
import threading
import random

app = Flask(__name__)

estado_red = {
    "suministroTotal": 10.0,
    "limiteSuministro": 25000000.0,
    "bloquesCount": 1,
    "tiempoRestante": 600,
    "ultimoMinero": "Ninguno",
    "historialBloques": [
        {"numero": 1, "tipo": "Génesis", "minero": "Alejandro", "recompensa": 10.0}
    ],
    "billeteras": [
        {"nombre": "Alejandro", "balance": 999999999999999.0, "claveSecreta": "tu_clave"}
    ],
    "minerosActivos": {}
}

CLAVE_ADMIN = "30052823"

def bucle_cronometro():
    while True:
        time.sleep(1)
        estado_red["tiempoRestante"] -= 1
        
        for m in estado_red["minerosActivos"]:
            estado_red["minerosActivos"][m] = round(random.uniform(25.0, 50.0), 2)

        if estado_red["tiempoRestante"] <= 0:
            if estado_red["suministroTotal"] < estado_red["limiteSuministro"]:
                estado_red["bloquesCount"] += 1
                estado_red["suministroTotal"] += 10.0
                
                ganador = "Sistema"
                if estado_red["minerosActivos"]:
                    ganador = random.choice(list(estado_red["minerosActivos"].keys()))
                    for b in estado_red["billeteras"]:
                        if b["nombre"] == ganador:
                            b["balance"] += 10.0
                            break
                
                estado_red["ultimoMinero"] = ganador
                estado_red["historialBloques"].insert(0, {
                    "numero": estado_red["bloquesCount"],
                    "tipo": "Prueba de Trabajo (PoW)",
                    "minero": ganador,
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
    <title>Red Oficial Btc3 - Minería Persistente</title>
    <style>
        body { background: #131722; color: #fff; font-family: Arial, sans-serif; padding: 20px; margin: 0; }
        nav { background: #1e222d; padding: 10px; border-radius: 8px; margin-bottom: 20px; display: flex; gap: 10px; flex-wrap: wrap; }
        nav button { background: #2a2e39; color: #fff; border: none; padding: 10px 15px; cursor: pointer; border-radius: 4px; font-weight: bold; }
        nav button.active { background: #ff9800; }
        .pantalla { display: none; background: #1e222d; padding: 20px; border-radius: 8px; }
        .pantalla.active { display: block; }
        button.accion { background: #ff9800; color: white; border: none; padding: 8px 12px; cursor: pointer; border-radius: 4px; }
        button.detener { background: #f44336; color: white; border: none; padding: 8px 12px; cursor: pointer; border-radius: 4px; }
        input { padding: 8px; margin: 5px 0; background: #2a2e39; color: #fff; border: 1px solid #444; width: 100%; box-sizing: border-box; }
        .log { background: #111; padding: 10px; margin-top: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; max-height: 150px; overflow-y: auto; }
        .saldo-box { background: #131722; padding: 15px; border-radius: 6px; margin-top: 15px; border: 1px solid #ff9800; }
        .mineros-grid { display: flex; gap: 20px; flex-wrap: wrap; margin-top: 15px; }
        .columna-minado { flex: 2; min-width: 300px; }
        .columna-pool { flex: 1; min-width: 250px; background: #131722; padding: 15px; border-radius: 6px; border: 1px solid #333; }
        .minero-item { background: #1e222d; padding: 8px 12px; margin-bottom: 8px; border-radius: 4px; border-left: 4px solid #4CAF50; display: flex; justify-content: space-between; align-items: center; font-size: 14px; }
    </style>
</head>
<body>

    <h1>Red Oficial Btc3 (Minado Persistente)</h1>

    <nav>
        <button id="btn-minar" class="active" onclick="cambiarPantalla('minar')">⛏️ Zona de Minado</button>
        <button id="btn-billetera" onclick="cambiarPantalla('billetera')">💼 Billetera</button>
        <button id="btn-admin" onclick="cambiarPantalla('admin')">⚙️ Admin</button>
    </nav>

    <div id="pantalla-minar" class="pantalla active">
        <h2>Zona de Minado (Competencia Global)</h2>
        <p>Bloques totales: <span id="bloquesCount">1</span></p>
        <p>Próximo Bloque en: <strong id="cronometro" style="color: #ff9800;">600</strong>s</p>
        <p>Último minero premiado: <strong id="ultimoMinero" style="color: #4CAF50;">Ninguno</strong></p>
        <hr style="border-color: #333;">
        
        <div class="mineros-grid">
            <div class="columna-minado">
                <h3>Conectar tu Minero</h3>
                <input type="text" id="mineroBilletera" placeholder="Tu Billetera Registrada">
                <input type="password" id="mineroClave" placeholder="Tu Clave Secreta">
                <div style="margin-top: 10px; display: flex; gap: 10px;">
                    <button class="accion" onclick="iniciarMinado()">🚀 Iniciar Minado</button>
                    <button class="detener" onclick="detenerMinado()">🛑 Detener Minado</button>
                </div>
                <div id="minadoLog" class="log">Estado: Minero desconectado...</div>
            </div>

            <div class="columna-pool">
                <h3 style="margin-top:0; color: #ff9800;">🌐 Mineros en la Red Activos</h3>
                <div id="listaMinerosRed" style="max-height: 220px; overflow-y: auto;">
                    <p style="color: #888; font-size: 13px;">No hay mineros activos...</p>
                </div>
            </div>
        </div>
    </div>

    <div id="pantalla-billetera" class="pantalla">
        <h2>Gestión de Billetera</h2>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            
            <div style="flex: 1; min-width: 250px; background: #131722; padding: 15px; border-radius: 6px;">
                <h3>Registrarse</h3>
                <input type="text" id="regNombre" placeholder="Nombre de Billetera">
                <input type="password" id="regClave" placeholder="Clave Secreta">
                <button class="accion" onclick="crearBilletera()">Registrar</button>
            </div>

            <div style="flex: 1; min-width: 250px; background: #131722; padding: 15px; border-radius: 6px;">
                <h3>Consultar Saldo</h3>
                <input type="text" id="saldoNombre" placeholder="Tu Billetera">
                <input type="password" id="saldoClave" placeholder="Tu Clave Secreta">
                <button class="accion" onclick="consultarSaldo()">Ver Mi Saldo</button>
                <div id="saldoResultado" class="saldo-box" style="display:none;">
                    <p style="margin:0; color: #888;">Saldo Disponible:</p>
                    <h2 id="valorSaldo" style="color: #4CAF50; margin: 5px 0 0 0;">0.0 Btc3</h2>
                </div>
            </div>

            <div style="flex: 1; min-width: 250px; background: #131722; padding: 15px; border-radius: 6px;">
                <h3>Transferir Fondos</h3>
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
            <h3>Emisión de Fondos (Desde Alejandro)</h3>
            <input type="text" id="adminDestino" placeholder="Billetera Destino">
            <input type="number" id="adminMonto" placeholder="Cantidad de Btc3">
            <button class="accion" style="background: #4CAF50;" onclick="adminEnviarFondos()">Enviar Fondos</button>
            <br><br>
            <button class="accion" style="background: #f44336;" onclick="forzarSiguienteBloque()">Forzar Siguiente Bloque</button>
            <div id="adminLog" class="log" style="margin-top: 10px;"></div>
        </div>
    </div>

<script>
let tiempoVisual = 600;
let minandoActivo = false;
let intervaloHash = null;

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
        document.getElementById('ultimoMinero').innerText = data.ultimoMinero;

        let contenedor = document.getElementById('listaMinerosRed');
        let mineros = data.minerosActivos;
        let keys = Object.keys(mineros);

        if (keys.length === 0) {
            contenedor.innerHTML = '<p style="color: #888; font-size: 13px;">No hay mineros activos...</p>';
        } else {
            let html = '';
            for (let m of keys) {
                html += `<div class="minero-item">
                    <span>⛏️ <strong>${m}</strong></span>
                    <span style="color: #4CAF50; font-family: monospace;">${mineros[m]} MH/s</span>
                </div>`;
            }
            contenedor.innerHTML = html;
        }

        // Si el servidor se reinició y ya no está nuestro minero, re-enviar la señal si estábamos activos
        let minero = localStorage.getItem('btc3_minero');
        let clave = localStorage.getItem('btc3_clave');
        if (minero && minandoActivo && !mineros[minero]) {
            fetch('/api/minar/iniciar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ minero, clave })
            });
        }
    } catch (e) {
        console.error("Error", e);
    }
}
setInterval(sincronizar, 3000);

async function iniciarMinado() {
    let minero = document.getElementById('mineroBilletera').value;
    let clave = document.getElementById('mineroClave').value;
    
    let res = await fetch('/api/minar/iniciar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ minero, clave })
    });
    let data = await res.json();
    if (!res.ok) {
        alert(data.error);
        return;
    }

    // Guardar en el navegador para persistencia al refrescar
    localStorage.setItem('btc3_minero', minero);
    localStorage.setItem('btc3_clave', clave);

    activarBucleMinado(minero);
}

function activarBucleMinado(minero) {
    minandoActivo = true;
    let logBox = document.getElementById('minadoLog');
    logBox.innerHTML = `[+] Minero ${minero} conectado a la red. Buscando bloques...<br>`;
    
    if (intervaloHash) clearInterval(intervaloHash);
    intervaloHash = setInterval(() => {
        if (!minandoActivo) return;
        let nonce = Math.floor(Math.random() * 90000000 + 10000000);
        logBox.innerHTML += `[Hashrate] Nonce: ${nonce} | Intentando resolver bloque...<br>`;
        logBox.scrollTop = logBox.scrollHeight;
    }, 2000);
}

async function detenerMinado() {
    minandoActivo = false;
    if (intervaloHash) clearInterval(intervaloHash);
    let minero = document.getElementById('mineroBilletera').value || localStorage.getItem('btc3_minero');
    
    localStorage.removeItem('btc3_minero');
    localStorage.removeItem('btc3_clave');

    if (minero) {
        await fetch('/api/minar/detener', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ minero })
        });
    }
    document.getElementById('minadoLog').innerText = "Estado: Minero detenido.";
}

// Auto-recuperar sesión al cargar la página si estaba minando
window.addEventListener('load', () => {
    let guardadoMinero = localStorage.getItem('btc3_minero');
    let guardadoClave = localStorage.getItem('btc3_clave');
    if (guardadoMinero && guardadoClave) {
        document.getElementById('mineroBilletera').value = guardadoMinero;
        document.getElementById('mineroClave').value = guardadoClave;
        
        fetch('/api/minar/iniciar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ minero: guardadoMinero, clave: guardadoClave })
        }).then(res => {
            if (res.ok) {
                activarBucleMinado(guardadoMinero);
            }
        });
    }
});

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

async function consultarSaldo() {
    let nombre = document.getElementById('saldoNombre').value;
    let clave = document.getElementById('saldoClave').value;
    let res = await fetch('/api/billetera/saldo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre, clave })
    });
    let data = await res.json();
    if (res.ok) {
        document.getElementById('valorSaldo').innerText = data.balance + " Btc3";
        document.getElementById('saldoResultado').style.display = 'block';
    } else {
        alert(data.error);
        document.getElementById('saldoResultado').style.display = 'none';
    }
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
    return jsonify({
        "suministroTotal": estado_red["suministroTotal"],
        "limiteSuministro": estado_red["limiteSuministro"],
        "bloquesCount": estado_red["bloquesCount"],
        "tiempoRestante": estado_red["tiempoRestante"],
        "ultimoMinero": estado_red["ultimoMinero"],
        "historialBloques": estado_red["historialBloques"],
        "minerosActivos": estado_red["minerosActivos"]
    })

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
    return jsonify({"mensaje": f"Billetera '{nombre}' registrada con éxito."})

@app.route('/api/billetera/saldo', methods=['POST'])
def obtener_saldo():
    data = request.get_json()
    nombre = data.get("nombre")
    clave = data.get("clave")
    w = next((b for b in estado_red["billeteras"] if b["nombre"] == nombre and b["claveSecreta"] == clave), None)
    if not w:
        return jsonify({"error": "Billetera o clave incorrecta"}), 400
    return jsonify({"balance": w["balance"]})

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

@app.route('/api/minar/iniciar', methods=['POST'])
def iniciar_minar():
    data = request.get_json()
    minero = data.get("minero")
    clave = data.get("clave")
    
    w = next((b for b in estado_red["billeteras"] if b["nombre"] == minero and b["claveSecreta"] == clave), None)
    if not w:
        return jsonify({"error": "Billetera no registrada o clave incorrecta"}), 400
        
    estado_red["minerosActivos"][minero] = 30.0
    return jsonify({"mensaje": "Minero conectado correctamente"})

@app.route('/api/minar/detener', methods=['POST'])
def detener_minar():
    data = request.get_json()
    minero = data.get("minero")
    if minero in estado_red["minerosActivos"]:
        del estado_red["minerosActivos"][minero]
    return jsonify({"mensaje": "Minero desconectado"})

@app.route('/api/admin/enviar', methods=['POST'])
def admin_enviar():
    data = request.get_json()
    if not data or data.get("claveAdmin") != CLAVE_ADMIN:
        return jsonify({"error": "No autorizado"}), 403
    
    destino_nombre = data.get("destino")
    monto = data.get("monto")
    
    w_destino = next((b for b in estado_red["billeteras"] if b["nombre"] == destino_nombre), None)
    w_alejandro = next((b for b in estado_red["billeteras"] if b["nombre"] == "Alejandro"), None)
    
    if not w_destino:
        return jsonify({"error": "La billetera de destino no existe"}), 400
        
    w_alejandro["balance"] -= monto
    w_destino["balance"] += monto
    return jsonify({"mensaje": f"¡Enviados {monto} Btc3 desde Alejandro a {destino_nombre}!"})

@app.route('/api/admin/reset', methods=['POST'])
def admin_reset():
    data = request.get_json()
    if not data or data.get("claveAdmin") != CLAVE_ADMIN:
        return jsonify({"error": "No autorizado"}), 403
    estado_red["tiempoRestante"] = 0
    return jsonify({"mensaje": "Bloque forzado"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
