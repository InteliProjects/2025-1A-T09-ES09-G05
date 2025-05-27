import time
import subprocess
import firebase_admin
from firebase_admin import credentials, db
import os

cred_path = os.getenv("FIREBASE_CREDENTIALS", "/app/config/alocacao-entregadores-firebase-credenciais.json")

# Inicializa o Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://alocacao-entregadores-default-rtdb.firebaseio.com/"
    })

# Referência para os logs do Locust no Firebase
logs_ref = db.reference("locust_logs")

def get_average_response_time():
    logs = logs_ref.get()  # Obtém todos os logs
    tempos = []
    if logs:
        for log in logs.values():
            if "response_time" in log and log["response_time"]:
                tempos.append(log["response_time"])
    return sum(tempos) / len(tempos) if tempos else 0

def get_existing_instances():
    """ Obtém os containers existentes do api-service e os nomes em uso. """
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "name=api-service", "--format", "{{.Names}}"],
        capture_output=True, text=True
    )
    output = result.stdout.strip()
    return output.split("\n") if output else []

def scale_up_server():
    print("🔄 Escalando nova instância da API...")

    # Obtém todas as instâncias existentes
    instances = get_existing_instances()
    
    # Identifica o próximo número disponível
    new_instance_number = 2
    while f"api-service-{new_instance_number}" in instances:
        new_instance_number += 1
    
    new_instance_name = f"api-service-{new_instance_number}"
    new_port = 8000 + new_instance_number  # Evitar conflitos

    print(f"🚀 Iniciando nova instância: {new_instance_name} na porta {new_port}")

    subprocess.run([
        "docker", "run", "-d",
        "-p", f"{new_port}:8000",
        "--name", new_instance_name,
        "-e", f"VIRTUAL_PORT={new_port}",
        "-e", "VIRTUAL_HOST=api.local",
        "api-service"
    ], check=True)

    print(f"✅ Nova instância {new_instance_name} rodando!")

def monitor_and_scale(threshold):
    while True:
        avg_time = get_average_response_time()
        print(f"📊 Tempo médio de resposta: {avg_time:.3f} s")
        if avg_time > threshold:
            print("⚠️ ALTA LATÊNCIA DETECTADA! Escalando servidor...")
            scale_up_server()
        else:
            print("✅ Latência normal. Nenhuma ação necessária.")
        time.sleep(30)  # Checa a cada 30 segundos

if __name__ == "__main__":
    monitor_and_scale(threshold=1.0)
