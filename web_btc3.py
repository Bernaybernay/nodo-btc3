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
        {"nombre": "Alejandro", "balance": 999999999999999.0, "usdt": 0.0, "claveSecreta": "tu_clave"}
    ],
    "minerosActivos": {},
    "ordenesMercado": [],
    "walletOficialUSDT": "0x9b4fecb9684f8949925b836fb0863e9249a29fc0"
}

CLAVE_ADMIN = "30052823"
NUMERO_WHATSAPP = "65993417539"

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
    <title>Red Oficial Btc3 - Exchange y Minería</title>
    <style>
        body { background: #131722; color: #fff; font-family: Arial, sans-serif; padding: 20px; margin: 0; }
        nav { background: #1e222d; padding: 10px; border-radius: 8px; margin-bottom: 20px; display: flex; gap: 10px; flex-wrap: wrap; }
        nav button { background: #2a2e39; color: #fff; border: none; padding: 10px 15px; cursor: pointer; border-radius: 4px; font-weight: bold; }
        nav button.active { background: #ff9800; }
        .pantalla { display: none; background: #1e222d; padding: 20px; border-radius: 8px; }
        .pantalla.active { display: block; }
        button.accion { background: #ff9800; color: white; border: none; padding: 8px 12px; cursor: pointer; border-radius: 4px; font-weight: bold; }
        button.detener { background: #f44336; color: white; border: none; padding: 8px 12px; cursor: pointer; border-radius: 4px; }
        button.whatsapp { background: #25D366; color: white; border: none; padding: 10px 15px; cursor: pointer; border-radius: 4px; font-weight: bold; width: 100%; margin-top: 10px; display: flex; align-items: center; justify-content: center; gap: 8px; text-decoration: none; box-sizing: border-box;}
        input, select { padding: 8px; margin: 5px 0; background: #2a2e39; color: #fff; border: 1px solid #444; width: 100%; box-sizing: border-box; }
        .log { background: #111; padding: 10px; margin-top: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; max-height: 150px; overflow-y: auto; }
        .saldo-box { background: #131722; padding: 15px; border-radius: 6px; margin-top: 15px; border: 1px solid #ff9800; display: flex; justify-content: space-around; }
        .mineros-grid { display: flex; gap: 20px; flex-wrap: wrap; margin-top: 15px; }
        .columna-minado { flex: 2; min-width: 300px; }
        .columna-pool { flex: 1; min-width: 250px; background: #131722; padding: 15px; border-radius: 6px; border: 1px solid #333; }
        .minero-item { background: #1e222d; padding: 8px 12px; margin-bottom: 8px; border-radius: 4px; border-left: 4px solid #4CAF50; display: flex; justify-content: space-between; align-items: center; font-size: 14px; }
        .orden-card { background: #131722; padding: 10px; margin-bottom: 8px; border-radius: 4px; border: 1px solid #444; display: flex; justify-content: space-between; align-items: center; }
        .banner-anuncio { background: linear-gradient(135deg, #ff9800, #ff5722); color: #fff; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    </style>
</head>
<body>

    <h1>Red Oficial Btc3 & Market</h1>

    <nav>
        <button id="btn-minar" class="active" onclick="cambiarPantalla('minar')">⛏️ Minado</button>
        <button id="btn-billetera" onclick="cambiarPantalla('billetera')">💼 Billetera</button>
        <button id="btn-exchange" onclick="cambiarPantalla('exchange')">💱 Exchange USDT</button>
        <button id="btn-admin" onclick="cambiarPantalla('admin')">⚙️ Admin</button>
    </nav>

    <!-- PANTALLA MINADO -->
    <div id="pantalla-minar" class="pantalla active">
        <h2>Zona de Minado Global</h2>
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
                <h3 style="margin-top:0; color: #ff9800;">🌐 Mineros Activos</h3>
                <div id="listaMinerosRed" style="max-height: 220px; overflow-y: auto;">
                    <p style="color: #888; font-size: 13px;">No hay mineros activos...</p>
                </div>
            </div>
        </div>
    </div>

    <!-- PANTALLA BILLETERA -->
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
                <h3>Consultar Saldos</h3>
                <input type="text" id="saldoNombre" placeholder="Tu Billetera">
                <input type="password" id="saldoClave" placeholder="Tu Clave Secreta">
                <button class="accion" onclick="consultarSaldo()">Ver Saldos</button>
                <div id="saldoResultado" class="saldo-box" style="display:none;">
                    <div><small style="color: #888;">Btc3:</small><h3 id="valorSaldoBtc3" style="color: #4CAF50; margin:0;">0.0</h3></div>
                    <div><small style="color: #888;">USDT:</small><h3 id="valorSaldoUsdt" style="color: #ff9800; margin:0;">0.0</h3></div>
                </div>
            </div>
            <div style="flex: 1; min-width: 250px; background: #131722; padding: 15px; border-radius: 6px;">
                <h3>Transferir Btc3</h3>
                <input type="text" id="transOrigen" placeholder="Tu Billetera Origen">
                <input type="password" id="transClave" placeholder="Clave Secreta">
                <input type="text" id="transDestino" placeholder="Billetera Destino">
                <input type="number" id="transMonto" placeholder="Monto Btc3">
                <button class="accion" onclick="enviarFondos()">Enviar</button>
            </div>
        </div>
        <div id="billeteraLog" class="log" style="margin-top: 15px;"></div>
    </div>

    <!-- PANTALLA EXCHANGE (COMPRA CON USDT REAL) -->
    <div id="pantalla-exchange" class="pantalla">
        
        <!-- ANUNCIO PUBLICITARIO -->
        <div class="banner-anuncio">
            <h2 style="margin: 0 0 5px 0;">🚀 ¡También puedes comprar tus monedas de pre-lanzamiento!</h2>
            <p style="margin: 0; font-size: 14px;">Asegura tu futuro y adquiere Btc3 antes de su expansión global.</p>
        </div>

        <h2>Exchange P2P & Depósito USDT</h2>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            
            <!-- Columna de Depósito Real con Botón de WhatsApp -->
            <div style="flex: 1; min-width: 280px; background: #131722; padding: 15px; border-radius: 6px; border: 1px solid #ff9800;">
                <h3 style="color: #ff9800; margin-top:0;">1. Depositar USDT (Red ETH/ERC20)</h3>
                <p style="font-size: 13px; color: #ccc;">Envía tus USDT a la siguiente dirección oficial de depósito:</p>
                <div style="background: #111; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 11px; word-break: break-all; color: #4CAF50;" id="walletOficial">
                    0x9b4fecb9684f8949925b836fb0863e9249a29fc0
                </div>
                <p style="font-size: 12px; color: #888; margin-top: 10px;">Una vez realizado el depósito, confirma enviando tu comprobante por WhatsApp:</p>
                <a href="https://wa.me/59165993417539?text=Hola,%20adjunto%20mi%20comprobante%20de%20depósito%20USDT%20para%20la%20acreditación%20de%20saldo%20en%20Btc3." class="whatsapp" target="_blank">
                    💬 Confirmar por WhatsApp (65993417539)
                </a>
            </div>

            <!-- Columna de Publicar Orden de Venta de Btc3 -->
            <div style="flex: 1; min-width: 280px; background: #131722; padding: 15px; border-radius: 6px;">
                <h3 style="margin-top:0;">2. Vender Btc3 por USDT</h3>
                <input type="text" id="vendeNombre" placeholder="Tu Billetera" oninput="verificarSaldoVenta()">
                <input type="password" id="vendeClave" placeholder="Tu Clave Secreta" oninput="verificarSaldoVenta()">
                
                <!-- Indicador de saldo disponible en tiempo real -->
                <div id="avisoSaldoVenta" style="font-size: 13px; color: #4CAF50; margin: 5px 0; min-height: 18px;"></div>

                <input type="number" id="vendeCantidad" placeholder="Cantidad de Btc3 a Vender">
                <input type="number" id="vendePrecio" placeholder="Precio en USDT por cada Btc3">
                <button class="accion" onclick="crearOrdenVenta()">Publicar Oferta</button>
            </div>

        </div>

        <h3 style="margin-top: 25px;">Mercado Activo (Libro de Órdenes)</h3>
        <div id="libroOrdenes" style="background: #131722; padding: 15px; border-radius: 6px; max-height: 250px; overflow-y: auto;">
            <p style="color: #888;">No hay órdenes en el mercado...</p>
        </div>
        <div id="exchangeLog" class="log"></div>
    </div>

    <!-- PANTALLA ADMIN -->
    <div id="pantalla-admin" class="pantalla">
        <h2>Panel de Administración</h2>
        <input type="password" id="claveAdminInput" placeholder="Contraseña de Administrador">
        <button class="accion" onclick="ingresarAdmin()">Entrar</button>
        
        <div id="panelAdminOculto" style="display:none; margin-top: 15px;">
            <p style="color: #4CAF50;">¡Acceso concedido!</p>
            <hr style="border-color: #333; margin: 15px 0;">
            
            <h3>Acreditar USDT (Tras recibir depósito real)</h3>
            <input type="text" id="adminUserUsdt" placeholder="Billetera del Usuario">
            <input type="number" id="adminMontoUsdt" placeholder="Cantidad de USDT a Acreditar">
            <button class="accion" style="background: #ff9800;" onclick="adminAcreditarUsdt()">Acreditar USDT</button>
            
            <h3 style="margin-top: 20px;">Emisión de Btc3 (Desde Alejandro)</h3>
            <input type="text" id="adminDestino" placeholder="Billetera Destino">
            <input type="number" id="adminMonto" placeholder="Cantidad de Btc3">
            <button class="accion" style="background: #4CAF50;" onclick="adminEnviarFondos()">Enviar Btc3</button>
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
    if(nombre === 'exchange') cargarLibroOrdenes();
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
    if (!res.ok) { alert(data.error); return; }

    localStorage.setItem('btc3_minero', minero);
    localStorage.setItem('btc3_clave', clave);
    activarBucleMinado(minero);
}

function activarBucleMinado(minero) {
    minandoActivo = true;
    let logBox = document.getElementById('minadoLog');
    logBox.innerHTML = `[+] Minero ${minero} conectado. Buscando bloques...<br>`;
    if (intervaloHash) clearInterval(intervaloHash);
    intervaloHash = setInterval(() => {
        if (!minandoActivo) return;
        let nonce = Math.floor(Math.random() * 90000000 + 10000000);
        logBox.innerHTML += `[Hashrate] Nonce: ${nonce} | Intentando resolver...<br>`;
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
        }).then(res => { if (res.ok) activarBucleMinado(guardadoMinero); });
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
        document.getElementById('valorSaldoBtc3').innerText = data.balance;
        document.getElementById('valorSaldoUsdt').innerText = data.usdt;
        document.getElementById('saldoResultado').style.display = 'flex';
    } else {
        alert(data.error);
        document.getElementById('saldoResultado').style.display = 'none';
    }
}

async function verificarSaldoVenta() {
    let nombre = document.getElementById('vendeNombre').value;
    let clave = document.getElementById('vendeClave').value;
    let aviso = document.getElementById('avisoSaldoVenta');
    
    if (!nombre || !clave) {
        aviso.innerText = "";
        return;
    }

    try {
        let res = await fetch('/api/billetera/saldo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre, clave })
        });
        let data = await res.json();
        if (res.ok) {
            aviso.innerHTML = `✅ Disponible para vender: <strong>${data.balance} Btc3</strong>`;
        } else {
            aviso.innerHTML = `<span style="color: #f44336;">⚠️ Credenciales incorrectas</span>`;
        }
    } catch(e) {
        aviso.innerText = "";
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

async function crearOrdenVenta() {
    let vendedor = document.getElementById('vendeNombre').value;
    let clave = document.getElementById('vendeClave').value;
    let cantidad = parseFloat(document.getElementById('vendeCantidad').value);
    let precio = parseFloat(document.getElementById('vendePrecio').value);

    let res = await fetch('/api/exchange/vender', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vendedor, clave, cantidad, precio })
    });
    let data = await res.json();
    document.getElementById('exchangeLog').innerText = data.mensaje || data.error;
    verificarSaldoVenta();
    cargarLibroOrdenes();
}

async function cargarLibroOrdenes() {
    let res = await fetch('/api/exchange/ordenes');
    let data = await res.json();
    let contenedor = document.getElementById('libroOrdenes');
    if(data.ordenes.length === 0) {
        contenedor.innerHTML = '<p style="color: #888;">No hay órdenes en el mercado...</p>';
        return;
    }
    let html = '';
    data.ordenes.forEach(o => {
        html += `<div class="orden-card">
            <div>
                <strong>${o.vendedor}</strong> vende <strong>${o.cantidad} Btc3</strong> a <span style="color:#ff9800;">${o.precio} USDT</span> c/u
            </div>
            <button class="accion" onclick="comprarOrden(${o.id})">Comprar</button>
        </div>`;
    });
    contenedor.innerHTML = html;
}

async function comprarOrden(ordenId) {
    let comprador = prompt("Ingresa el nombre de tu billetera:");
    let clave = prompt("Ingresa tu clave secreta:");
    let res = await fetch('/api/exchange/comprar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ordenId, comprador, clave })
    });
    let data = await res.json();
    alert(data.mensaje || data.error);
    cargarLibroOrdenes();
}

function ingresarAdmin() {
    let clave = document.getElementById('claveAdminInput').value;
    if (clave === "30052823") {
        document.getElementById('panelAdminOculto').style.display = 'block';
        alert("¡Acceso concedido!");
    } else {
        alert("Contraseña incorrecta.");
    }
}

async function adminAcreditarUsdt() {
    let claveAdmin = document.getElementById('claveAdminInput').value;
    let destino = document.getElementById('adminUserUsdt').value;
    let monto = parseFloat(document.getElementById('adminMontoUsdt').value);
    let res = await fetch('/api/admin/acreditar_usdt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ claveAdmin, destino, monto })
    });
    let data = await res.json();
    document.getElementById('adminLog').innerText = data.mensaje || data.error;
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
    if (res.ok) { sincronizar(); alert("Bloque forzado."); } else { alert(data.error); }
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
    if not nombre or not clave: return jsonify({"error": "Faltan datos"}), 400
    for b in estado_red["billeteras"]:
        if b["nombre"] == nombre: return jsonify({"error": "La billetera ya existe"}), 400
    estado_red["billeteras"].append({"nombre": nombre, "balance": 0.0, "usdt": 0.0, "claveSecreta": clave})
    return jsonify({"mensaje": f"Billetera '{nombre}' registrada con éxito."})

@app.route('/api/billetera/saldo', methods=['POST'])
def obtener_saldo():
    data = request.get_json()
    w = next((b for b in estado_red["billeteras"] if b["nombre"] == data.get("nombre") and b["claveSecreta"] == data.get("clave")), None)
    if not w: return jsonify({"error": "Billetera o clave incorrecta"}), 400
    return jsonify({"balance": w["balance"], "usdt": w["usdt"]})

@app.route('/api/transferir', methods=['POST'])
def transferir():
    data = request.get_json()
    w_origen = next((b for b in estado_red["billeteras"] if b["nombre"] == data.get("origen") and b["claveSecreta"] == data.get("clave")), None)
    w_destino = next((b for b in estado_red["billeteras"] if b["nombre"] == data.get("destino")), None)
    if not w_origen or not w_destino: return jsonify({"error": "Billeteras o clave incorrectas"}), 400
    monto = data.get("monto")
    if w_origen["balance"] < monto: return jsonify({"error": "Fondos insuficientes"}), 400
    w_origen["balance"] -= monto
    w_destino["balance"] += monto
    return jsonify({"mensaje": f"¡Transferencia exitosa de {monto} Btc3!"})

@app.route('/api/exchange/vender', methods=['POST'])
def exchange_vender():
    data = request.get_json()
    vendedor = data.get("vendedor")
    clave = data.get("clave")
    cantidad = data.get("cantidad")
    precio = data.get("precio")
    
    w = next((b for b in estado_red["billeteras"] if b["nombre"] == vendedor and b["claveSecreta"] == clave), None)
    if not w: return jsonify({"error": "Credenciales incorrectas"}), 400
    if w["balance"] < cantidad: return jsonify({"error": "No tienes suficientes Btc3 para vender"}), 400
    
    w["balance"] -= cantidad
    nueva_orden = {
        "id": len(estado_red["ordenesMercado"]) + 1,
        "vendedor": vendedor,
        "cantidad": cantidad,
        "precio": precio
    }
    estado_red["ordenesMercado"].append(nueva_orden)
    return jsonify({"mensaje": "Oferta publicada en el mercado con éxito."})

@app.route('/api/exchange/ordenes')
def exchange_ordenes():
    return jsonify({"ordenes": estado_red["ordenesMercado"]})

@app.route('/api/exchange/comprar', methods=['POST'])
def exchange_comprar():
    data = request.get_json()
    orden_id = data.get("ordenId")
    comprador_nombre = data.get("comprador")
    clave = data.get("clave")
    
    comprador = next((b for b in estado_red["billeteras"] if b["nombre"] == comprador_nombre and b["claveSecreta"] == clave), None)
    if not comprador: return jsonify({"error": "Comprador o clave incorrecta"}), 400
    
    orden = next((o for o in estado_red["ordenesMercado"] if o["id"] == orden_id), None)
    if not orden: return jsonify({"error": "La orden ya no está disponible"}), 400
    
    costo_total = orden["cantidad"] * orden["precio"]
    if comprador["usdt"] < costo_total:
        return jsonify({"error": f"No tienes suficiente USDT. Necesitas {costo_total} USDT."})
    
    vendedor = next((b for b in estado_red["billeteras"] if b["nombre"] == orden["vendedor"]), None)
    
    comprador["usdt"] -= costo_total
    if vendedor: vendedor["usdt"] += costo_total
    comprador["balance"] += orden["cantidad"]
    
    estado_red["ordenesMercado"].remove(orden)
    return jsonify({"mensaje": f"¡Compra exitosa de {orden['cantidad']} Btc3!"})

@app.route('/api/minar/iniciar', methods=['POST'])
def iniciar_minar():
    data = request.get_json()
    w = next((b for b in estado_red["billeteras"] if b["nombre"] == data.get("minero") and b["claveSecreta"] == data.get("clave")), None)
    if not w: return jsonify({"error": "Billetera no registrada o clave incorrecta"}), 400
    estado_red["minerosActivos"][data.get("minero")] = 30.0
    return jsonify({"mensaje": "Minero conectado"})

@app.route('/api/minar/detener', methods=['POST'])
def detener_minar():
    data = request.get_json()
    if data.get("minero") in estado_red["minerosActivos"]:
        del estado_red["minerosActivos"][data.get("minero")]
    return jsonify({"mensaje": "Minero desconectado"})

@app.route('/api/admin/acreditar_usdt', methods=['POST'])
def admin_acreditar_usdt():
    data = request.get_json()
    if not data or data.get("claveAdmin") != CLAVE_ADMIN: return jsonify({"error": "No autorizado"}), 403
    destino = next((b for b in estado_red["billeteras"] if b["nombre"] == data.get("destino")), None)
    if not destino: return jsonify({"error": "Billetera destino no encontrada"}), 400
    monto = data.get("monto")
    destino["usdt"] += monto
    return jsonify({"mensaje": f"¡Acreditados {monto} USDT a {destino['nombre']} con éxito!"})

@app.route('/api/admin/enviar', methods=['POST'])
def admin_enviar():
    data = request.get_json()
    if not data or data.get("claveAdmin") != CLAVE_ADMIN: return jsonify({"error": "No autorizado"}), 403
    destino = next((b for b in estado_red["billeteras"] if b["nombre"] == data.get("destino")), None)
    alejandro = next((b for b in estado_red["billeteras"] if b["nombre"] == "Alejandro"), None)
    if not destino: return jsonify({"error": "Destino no existe"}), 400
    monto = data.get("monto")
    alejandro["balance"] -= monto
    destino["balance"] += monto
    return jsonify({"mensaje": f"¡Enviados {monto} Btc3 desde Alejandro!"})

@app.route('/api/admin/reset', methods=['POST'])
def admin_reset():
    data = request.get_json()
    if not data or data.get("claveAdmin") != CLAVE_ADMIN: return jsonify({"error": "No autorizado"}), 403
    estado_red["tiempoRestante"] = 0
    return jsonify({"mensaje": "Bloque forzado"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
