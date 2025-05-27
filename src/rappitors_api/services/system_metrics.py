import time
import random

# Controle de estado interno do sistema
last_failure_time = None
last_recovery_time = None
is_down = False

# Parâmetros de simulação (tempo em segundos)
MTTR_SIM_RANGE = (5, 20)     # tempo médio para recuperação
MTBF_SIM_RANGE = (60, 300)   # tempo médio entre falhas

def simulate_health_check():
    global last_failure_time, last_recovery_time, is_down

    current_time = time.time()

    if is_down:
        # Simula recuperação com base em tempo aleatório
        simulated_mttr = random.uniform(*MTTR_SIM_RANGE)
        if current_time - last_failure_time >= simulated_mttr:
            # Sistema voltou ao ar
            last_recovery_time = current_time
            is_down = False

            return {
                "status": "up",
                "timestamp": current_time,
                "last_failure": last_failure_time,
                "last_recovery": last_recovery_time,
                "mtbf": last_failure_time - last_recovery_time if last_recovery_time else 0,
                "mttr": simulated_mttr
            }, 200
        else:
            # Ainda está em recuperação
            return {
                "status": "down",
                "timestamp": current_time,
                "last_failure": last_failure_time,
                "last_recovery": last_recovery_time,
                "mtbf": last_failure_time - last_recovery_time if last_recovery_time else 0,
                "mttr": simulated_mttr
            }, 500

    else:
        # Simula chance de falha
        if random.random() < 0.1:
            # Sistema caiu agora
            simulated_mtbf = random.uniform(*MTBF_SIM_RANGE)
            last_failure_time = current_time
            is_down = True

            return {
                "status": "down",
                "timestamp": current_time,
                "last_failure": last_failure_time,
                "last_recovery": last_recovery_time,
                "mtbf": simulated_mtbf,
                "mttr": 0
            }, 500

    # Sistema continua no ar
    return {
        "status": "up",
        "timestamp": current_time,
        "last_failure": last_failure_time,
        "last_recovery": last_recovery_time,
        "mtbf": current_time - last_recovery_time if last_recovery_time else 0,
        "mttr": last_recovery_time - last_failure_time if last_failure_time and last_recovery_time else 0
    }, 200
