from flask import Flask, render_template_string, jsonify, request
import time
import threading

app = Flask(__name__)

# Estado global de la red
estado_red = {
    "suministroTotal": 10.0,
    "limiteSuministro": 2500000000,
    "bloquesCount": 1,
    "tiempoRestante": 60,  # Duración del bloque en segundos
    "historialBloques": [
        {"numero": 1, "tipo": "Solitario", "minero": "Gabriel", "recompensa": 10.0}
    ],
    "billeteras": [
        {"nombre": "Gabriel", "balance": 10.0, "claveSecreta": "tu_clave"}
    ]
}

# Contraseña de administrador (cámbiala por la que prefieras)
CLAVE_ADMIN = "admin1234_cambiala"

# Hilo en segundo plano para que el cronómetro corra automáticamente sin parar
def bucle_cronometro():
    while True:
        time.sleep(1)
        estado_red["tiempoRestante"] -= 1
        if estado_red["tiempoRestante"] <= 0:
            # Al llegar a 0, avanza al siguiente bloque automáticamente
            estado_red["bloquesCount"] += 1
            estado_red["suministroTotal"] += 10.0
            
            estado_red["historialBloques"].insert(0, {
                "numero": estado_red["bloquesCount"],
                "tipo": "Automático / Red",
                "minero": "Sistema",
                "recompensa": 10.0
            })
            
            # Reiniciar el temporizador del bloque
            estado_red["tiempoRestante"] = 60

# Iniciar el hilo del reloj al arrancar Flask
hilo = threading.Thread(target=bucle_cronometro, daemon=True)
hilo.start()

# Interfaz HTML mejorada con el cronómetro en tiempo real y panel de administrador
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Red Oficial Btc3</title>
    <style>
        body { background: #131722; color: #fff; font-family: Arial, sans-serif; padding: 20px; }
        .panel { background: #1e222d; padding: 15px; margin-bottom: 15px; border-radius: 8px; }
        button { background: #ff9800; color: white; border: none; padding: 8px 12px; cursor: pointer; border-radius: 4px; }
        input { padding: 8px; margin-right: 5px; background: #2a2e39; color: #fff; border: 1px solid #444; }
    </style>
</head>
<body>

    <h1>Red Oficial Btc3</h1>
    
    <div class="panel">
        <h3>Estado del Bloque</h3>
        <p>Bloques: <span id="bloquesCount">1</span></p>
        <p>Próximo Bloque en: <span id="cronometro">60</span>s</p>
    </div>

    <!-- Panel de Administrador / Dueño -->
    <div class="panel" style="border: 1px solid #ff9800;">
        <h3>Panel de Dueño / Administrador</h3>
        <input type="password" id="claveAdminInput" placeholder="Contraseña de Administrador">
        <button onclick="ingresarAdmin()">Entrar</button>
        
        <div id="panelAdmin" style="display:none; margin-top: 15px;">
            <p style="color: #4CAF50; font-weight: bold;">¡Acceso de Administrador Concedido!</p>
            <button onclick="forzarSiguienteBloque()" style="background: #f44336;">Forzar Siguiente Bloque</button>
        </div>
    </div>

<script>
let tiempoVisual = 60;

// Descenso fluido del contador cada segundo en la pantalla
setInterval(() => {
    if (tiempoVisual > 0) {
        tiempoVisual--;
        document.getElementById('cronometro').innerText = tiempoVisual;
    }
}, 1000);

// Sincronizar con Flask cada 5 segundos para evitar desfases
async function sincronizar() {
    try {
        let res = await fetch('/api/estado');
        let data = await res.json();
        tiempoVisual = data.tiempoRestante;
        document.getElementById('cronometro').innerText = tiempoVisual;
        document.getElementById('bloquesCount').innerText = data.bloquesCount;
    } catch (e) {
        console.error("Error sincronizando", e);
    }
}
setInterval(sincronizar, 5000);

function ingresarAdmin() {
    let clave = document.getElementById('claveAdminInput').value;
    if (clave === "admin1234_cambiala") {
        document.getElementById('panelAdmin').style.display = 'block';
        alert("Bienvenido, dueño.");
    } else {
        alert("Contraseña incorrecta.");
    }
}

async function forzarSiguienteBloque() {
    let clave = document.getElementById('claveAdminInput').value;
    let res = await fetch('/api/admin/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ claveAdmin: clave })
    });
    let data = await res.json();
    if (res.ok) {
        alert("Bloque reiniciado con éxito.");
        sincronizar();
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

@app.route('/api/admin/reset', methods=['POST'])
def api_admin_reset():
    data = request.get_json()
    if not data or data.get("claveAdmin") != CLAVE_ADMIN:
        return jsonify({"error": "Contraseña de administrador incorrecta"}), 403
    
    estado_red["tiempoRestante"] = 60
    return jsonify({"mensaje": "Reiniciado correctamente", "estado": estado_red})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
