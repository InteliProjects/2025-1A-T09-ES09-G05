import random
from typing import Dict, List, Any
import geopy.distance
from firebase_admin import db
from apscheduler.schedulers.background import BackgroundScheduler

clima_instavel = False

def atualizar_clima():
    """
    Atualiza o clima a cada minuto de forma aleatória.
    """
    global clima_instavel
    clima_instavel = random.choices([False, True], weights=[0.6, 0.4])[0]


scheduler = BackgroundScheduler()
scheduler.add_job(atualizar_clima, "interval", minutes=1)
scheduler.start()

def obter_endereco_mockado() -> Dict:
    """
    Retorna um endereço aleatório dentro de São Paulo.
    """
    latitude = random.uniform(-23.42, -23.35)
    longitude = random.uniform(-46.72, -46.65)
    print(f"Endereço Mockado: Latitude = {latitude}, Longitude = {longitude}")
    return {"latitude": latitude, "longitude": longitude}

def calcular_distancia(coord1, coord2) -> float:
    """
    Calcula a distância entre dois pontos (latitude, longitude) em km.
    """
    try:
        lat1, lon1 = coord1["latitude"], coord1["longitude"]
        lat2, lon2 = coord2["latitude"], coord2["longitude"]

        # Verificar se as coordenadas são válidas
        if not (-90 <= lat1 <= 90 and -180 <= lon1 <= 180):
            raise ValueError(f"Coordenadas de ponto 1 inválidas: ({lat1}, {lon1})")
        if not (-90 <= lat2 <= 90 and -180 <= lon2 <= 180):
            raise ValueError(f"Coordenadas de ponto 2 inválidas: ({lat2}, {lon2})")
        
        print(f"Calculando distância entre coordenadas: ({lat1}, {lon1}) e ({lat2}, {lon2})")
            
        return round(
            geopy.distance.distance(
                (lat1, lon1),
                (lat2, lon2),
            ).km,
            2,
        )
    except ValueError as e:
        print(f"Erro de coordenada: {e}")
        return float('inf')

def buscar_entregadores_disponiveis() -> List[Dict[str, Any]]:
    """
    Busca entregadores disponíveis no banco de dados.
    """
    try:
        ref = db.reference("entregadores")
        entregadores = ref.get()
        
        if not entregadores:
            print("Nenhum entregador encontrado no banco de dados.")
            return []

        if isinstance(entregadores, dict):
            entregadores = list(entregadores.values())
        elif not isinstance(entregadores, list):
            print("Formato inesperado: esperada uma lista ou dicionário de entregadores.")
            return []

        entregadores_disponiveis = []

        for i, entregador in enumerate(entregadores):
            try:
                if (
                    entregador
                    and isinstance(entregador, dict)
                    and entregador.get("disponivel", False)
                ):
                    entregadores_disponiveis.append(entregador)
            except Exception as loop_error:
                print(f"Erro ao processar entregador na posição {i}: {loop_error}")
        
        return entregadores_disponiveis

    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        return []
    
# Exemplo de chamada
coordenada_ponto1 = obter_endereco_mockado()  # Chama a função para obter o endereço mockado
coordenada_ponto2 = obter_endereco_mockado()  # Outra coordenada mockada

# Chama a função de cálculo de distância com as coordenadas válidas
distancia = calcular_distancia(coordenada_ponto1, coordenada_ponto2)
print(f"Distância calculada: {distancia} km")