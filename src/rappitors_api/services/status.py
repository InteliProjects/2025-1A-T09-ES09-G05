import random
import time
from firebase_admin import db
from threading import Thread

# Mapeamento de transições possíveis entre estados
TRANSICOES_ESTADOS = {
    "disponível": ["aceitou pedido"],
    "aceitou pedido": ["a caminho da loja"],
    "a caminho da loja": ["aguardando na loja", "a caminho da entrega"],
    "aguardando na loja": ["a caminho da entrega"],
    "a caminho da entrega": ["aguardando cliente", "entregue"],
    "aguardando cliente": ["entregue"],
    "entregue": ["disponível"]
}

ESTADOS_OBRIGATORIOS = ["disponível", "aceitou pedido", "a caminho da loja", "a caminho da entrega", "entregue"]

def gerar_tempo_no_estado():
    """ Gera um tempo aleatório entre 5 e 600 segundos para cada estado. """
    return random.randint(5, 600)

def gerar_historico_entregador():
    """ Simula um ciclo completo do entregador, garantindo que ele passe por todos os estados obrigatórios. """
    historico = []
    timestamp_inicial = time.time() - (len(ESTADOS_OBRIGATORIOS) * 600)  # Simula tempos no passado
    estado_atual = "disponível"
    
    while estado_atual != "entregue":
        tempo_no_estado = gerar_tempo_no_estado()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp_inicial))
        
        historico.append({
            "estado": estado_atual,
            "tempo_no_estado_s": tempo_no_estado,
            "timestamp": timestamp
        })
        
        timestamp_inicial += tempo_no_estado
        estado_atual = random.choice(TRANSICOES_ESTADOS[estado_atual])
    
    # Garante que o último estado seja "entregue"
    historico.append({
        "estado": "entregue",
        "tempo_no_estado_s": gerar_tempo_no_estado(),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp_inicial))
    })
    
    return historico

def simular_entregador(entregador_id: int):
    """ Simula e armazena um ciclo completo para um entregador. """
    entregador_ref = db.reference(f"entregadores/{entregador_id}")
    historico = gerar_historico_entregador()
    entregador_ref.update({
        "historico_estados": historico,
        "estado": "entregue",
        "ultima_atualizacao": historico[-1]["timestamp"]
    })

def iniciar_simulacao_para_entregadores(entregadores_ids):
    """ Inicia a simulação para vários entregadores em paralelo. """
    for entregador_id in entregadores_ids:
        Thread(target=simular_entregador, args=(entregador_id,), daemon=True).start()
