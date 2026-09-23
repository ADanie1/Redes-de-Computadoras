from flask import Flask, request, jsonify
import requests
import threading

app = Flask(__name__)

ejecucion_iniciada = False

# Configuramos los nodos (para cada uno sera diferente, cambiar puerto y nombre)
MI_PUERTO = 5000
MI_NOMBRE = "Diego"
# Igual que aqui, ponemos la URL del siguiente nodo (PC 2, PC 3...)
SIGUIENTE_NODO = "https://annoying-federal-relocate.ngrok-free.dev/recibir"


def enviar_al_siguiente(payload):
    try:
        requests.post(SIGUIENTE_NODO, json=payload)
    except Exception as e:
        print(f"Error conectando al siguiente nodo: {e}")


@app.route('/recibir', methods=['POST'])
def recibir():
    data = request.get_json()

    # Tenemos que saber quien gana
    if "ganador_final" in data:
        print(f"\nEl algoritmo termino. Ganó: {data['ganador_final']} ---\n")

        # Si no fuimos pasamos al siguiente
        if data.get("notificador") != MI_NOMBRE:
            threading.Thread(target=enviar_al_siguiente, args=(data,)).start()
        return jsonify({"status": "notificado"}), 200

    # 2. Contamos a 50
    valor = data.get("valor", 0)
    print(f"[{MI_NOMBRE}] Mensaje recibido. Valor actual: {valor}")

    if valor >= 50:
        print(f"Hasta aqui. El ganador es: {data.get('name')}")

        notificacion = {"ganador_final": data.get('name'), "notificador": MI_NOMBRE}
        threading.Thread(target=enviar_al_siguiente, args=(notificacion,)).start()

        return jsonify({"status": "finalizado", "ganador": data.get('name')}), 200

    # Incrementamos y pasamos
    nuevo_valor = valor + 1
    nuevo_payload = {"valor": nuevo_valor, "name": MI_NOMBRE}
    threading.Thread(target=enviar_al_siguiente, args=(nuevo_payload,)).start()

    return jsonify({"status": "procesando"}), 200


@app.route('/iniciar', methods=['GET'])
def iniciar():
    global ejecucion_iniciada

    if ejecucion_iniciada:
        return jsonify({
            "status": "El algoritmo ya fue inicializado"
        }), 200

    ejecucion_iniciada = True

    payload_inicial = {
        "valor": 0,
        "name": MI_NOMBRE
    }

    threading.Thread(
        target=enviar_al_siguiente,
        args=(payload_inicial,)
    ).start()

    return jsonify({
        "status": "Algoritmo inicializado"
    }), 200


if __name__ == '__main__':
    app.run(port=MI_PUERTO)