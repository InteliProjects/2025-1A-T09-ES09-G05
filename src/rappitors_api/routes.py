from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from services.accept_order import responder_pedido
from services.location import atualizar_localizacao, obter_coordenadas
from services.alocation import (
    obter_endereco_mockado,
    calcular_distancia,
    buscar_entregadores_disponiveis,
)
from services.status import iniciar_simulacao_para_entregadores
import firebase_admin
from firebase_admin import credentials, db
import os
import logging
from fastapi import APIRouter, Query
from services.weather import obter_clima
from services.git_stats import git_stats
import random
import time
from services.system_metrics import simulate_health_check

cred_path = os.getenv(
    "FIREBASE_CREDENTIALS", "../config/alocacao-entregadores-firebase-credenciais.json"
)

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(
        cred,
        {"databaseURL": "https://alocacao-entregadores-default-rtdb.firebaseio.com/"},
    )

db_ref = db.reference("entregadores")
app = FastAPI(version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

clima_instavel = False



@app.get("/entregadores/status")
async def get_all_status(background_tasks: BackgroundTasks):
    try:
        entregadores_ref = db.reference('entregadores')
        entregadores_dados = entregadores_ref.get()

        if not entregadores_dados:
            return JSONResponse(status_code=404, content={"detail": "Nenhum entregador encontrado"})

        entregadores_ids = [0, 1, 2, 3]
        resultado = []

        for id_entregador, entregador in entregadores_dados.items():
            try:
                id_entregador_int = int(id_entregador)
                if id_entregador_int in entregadores_ids:
                    estado = entregador.get("estado", "indefinido").strip('"')
                    ultima_atualizacao = entregador.get("ultima_atualizacao", "indefinido")

                    resultado.append({
                        "id": id_entregador_int,
                        "estado": estado,
                        "ultima_atualizacao": ultima_atualizacao,
                        "historico_estados": entregador.get("historico_estados", [])
                    })
            except ValueError:
                continue

        background_tasks.add_task(iniciar_simulacao_para_entregadores, entregadores_ids)
        return JSONResponse(content=resultado)
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.get("/entregadores/{entregador_id}")
async def get_entregador(entregador_id: int):
    # Obtém os dados do Firebase
    entregadores = db_ref.get()

    if not entregadores:
        raise HTTPException(status_code=404, detail="Nenhum entregador encontrado")

    # Converter o dicionário do Firebase para uma lista de dicionários
    if isinstance(entregadores, dict):  # Se for um dicionário, transformamos em lista
        entregadores_list = list(entregadores.values())
    elif isinstance(entregadores, list):  # Se já for uma lista, mantemos
        entregadores_list = entregadores
    else:
        raise HTTPException(
            status_code=500, detail="Erro ao processar os dados do Firebase"
        )

    # Busca o entregador pelo ID
    entregador = next((e for e in entregadores_list if e["id"] == entregador_id), None)

    if not entregador:
        raise HTTPException(status_code=404, detail="Entregador não encontrado")

    return entregador


@app.get("/pedidos/{pedido_id}/taxa")
async def get_taxa_pedido(pedido_id: int):
    try:
        pedido = db.reference(f"pedidos/{pedido_id}").get()

        if not pedido:
            raise HTTPException(
                status_code=404,
                detail=f"Pedido {pedido_id} não encontrado no banco de dados.",
            )

        taxa = pedido.get("taxa_do_entregador")

        if taxa is None:
            raise HTTPException(
                status_code=404,
                detail=f"O pedido {pedido_id} não contém taxa definida.",
            )

        return {"pedido_id": pedido_id, "taxa_do_entregador": taxa}
    except Exception as e:
        logging.error(f"Erro ao buscar taxa do pedido {pedido_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Erro interno ao processar a requisição."
        )


@app.post("/responder_pedido")
async def responder_pedido(pedido_id: int, entregador_id: int):
    ref_pedido = db.reference(f"pedidos/{pedido_id}")
    pedido = ref_pedido.get()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    candidatos = pedido.get("candidatos", [])
    if entregador_id not in candidatos:
        raise HTTPException(
            status_code=400, detail="Entregador não está na lista de candidatos"
        )
    ref_pedido.update({"entregador_atribuido": entregador_id})
    return {
        "message": "Pedido aceito pelo entregador",
        "pedido_id": pedido_id,
        "entregador_id": entregador_id,
    }

@app.get("/alocar_entregador")
def alocar_entregador():
    """
    Rota para alocar o entregador mais próximo disponível,
    expandindo o raio de busca se necessário
    """
    start_request_time = time.time()  # Tempo de início da requisição
    entregadores = buscar_entregadores_disponiveis()

    if not entregadores:
        return JSONResponse(status_code=404, content={"error": "Nenhum entregador disponível"})

    endereco_pedido = obter_endereco_mockado()
    raio_atual = 30.0  # Raio inicial 
    tempo_total_espera = 0  # Tempo total esperando um entregador
    tentativas = 0  # Contador de tentativas de alocação
    tempo_max_espera = 2*60
    clima_instavel = random.choices([True, False], weights=[0.3, 0.7])[0]

    print(f"Endereço pedido: {endereco_pedido}")

    print(f"Entregadores: {entregadores}")
    
    while True:
        entregadores_disponiveis = []
        for dados in entregadores:
            disponivel = dados.get("disponivel", True)

            proximidade_pedido = calcular_distancia(endereco_pedido, dados["localizacao"])

            print(f"Proximidade pedido: {proximidade_pedido}")

            if disponivel and proximidade_pedido <= raio_atual:
                entregadores_disponiveis.append(dados)

        print(f"Entregadores disponíveis: {entregadores_disponiveis}")

        if entregadores_disponiveis:
            # Ordena pelo mais próximo
            entregadores_disponiveis.sort(
                key=lambda e: calcular_distancia(endereco_pedido, e["localizacao"])
            )

            for entregador in entregadores_disponiveis:
                distancia = calcular_distancia(
                    endereco_pedido, entregador["localizacao"]
                )

                print(f"Calculando distância para entregador {entregador}: {endereco_pedido} e {distancia} km")

                # Simula tempo de resposta e aceitação aleatória
                time.sleep(random.uniform(0.8, 2.0))  # Garante tempo não-instantâneo
                aceitou_pedido = random.choices([True, False], weights=[0.7, 0.3])[0]

                if aceitou_pedido:
                    tempo_execucao = round(time.time() - start_request_time, 2)
                    tempo_total_espera = tempo_execucao  
                    clima_instavel = random.choice([True, False])
                    return {
                        "entregador_id": entregador["id"],
                        "aceitou_pedido": True,
                        "tempo_execucao": tempo_execucao,
                        "tempo_espera_total": tempo_total_espera,
                        "distancia_km": distancia,
                        "clima_instavel": clima_instavel,
                    }
                
        tempo_total_espera = round(time.time() - start_request_time, 2)
        if tempo_total_espera > tempo_max_espera or tentativas >= 3:
            return {
                "error": "Nenhum entregador aceitou o pedido após 10 minutos ou 3 tentativas"
            }, 408

        raio_atual += 0.5
        tentativas += 1
        print(f"Aumentando raio para {raio_atual} km... Tentativa #{tentativas}")
        time.sleep(1)


@app.post("/localizacao")
async def api_atualizar_localizacao(
    entregador_id: int,
    latitude: float = None,
    longitude: float = None,
    endereco: str = None,
):
    """Atualiza a localização do entregador, aceitando coordenadas ou endereço."""

    if endereco:
        coordenadas = obter_coordenadas(endereco)
        if "error" in coordenadas:
            raise HTTPException(status_code=400, detail=coordenadas["error"])
        latitude, longitude = coordenadas["latitude"], coordenadas["longitude"]

    if latitude is None or longitude is None:
        raise HTTPException(
            status_code=400,
            detail="É necessário fornecer coordenadas válidas ou um endereço.",
        )

    ref = db.reference(f"entregadores/{entregador_id}")
    if not ref.get():
        raise HTTPException(status_code=404, detail="Entregador não encontrado")

    ref.update({"latitude": latitude, "longitude": longitude})

    return {
        "message": "Localização atualizada",
        "entregador_id": entregador_id,
        "latitude": latitude,
        "longitude": longitude,
    }


@app.put("/pedidos/{pedido_id}/atualizar_estado")
async def api_atualizar_estado_pedido(pedido_id: int, estado: str):
    """Atualiza o estado de um pedido."""

    ref_pedido = db.reference(f"pedidos/{pedido_id}")
    pedido = ref_pedido.get()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    ref_pedido.update({"status": estado})

    return {
        "message": "Estado do pedido atualizado",
        "pedido_id": pedido_id,
        "novo_estado": estado,
    }


@app.put("/entregadores/{entregador_id}/atualizar_estado")
async def api_atualizacao_manual_entregador(entregador_id: int, estado: str):
    ref_entregadores = db.reference("entregadores")
    entregadores = ref_entregadores.get()

    if not entregadores or not isinstance(entregadores, list):
        raise HTTPException(status_code=404, detail="Nenhum entregador encontrado")

    # Buscar o índice do entregador na lista
    entregador_index = next(
        (i for i, e in enumerate(entregadores) if e["id"] == entregador_id), None
    )

    if entregador_index is None:
        raise HTTPException(status_code=404, detail="Entregador não encontrado")

    # Atualizar o estado do entregador
    entregadores[entregador_index]["estado"] = estado

    # Atualizar a lista completa no Firebase
    ref_entregadores.set(entregadores)

    return {
        "message": "Estado do entregador atualizado",
        "entregador_id": entregador_id,
        "novo_estado": estado,
    }


@app.get("/protocolo")
async def get_protocolo():
    return {"status": "ok", "versão": app.version}


@app.get("/clima")
async def clima(
    cidade: str = Query(
        default="auto", description="Nome da cidade ou 'auto' para detecção automática"
    )
):
    return await obter_clima(cidade)

@app.get("/git")
async def get_git_stats():
    git_info = git_stats()
    print(git_info)
    return git_info

@app.get("/health")
async def health():
    result, status_code = simulate_health_check()
    return JSONResponse(content=result, status_code=status_code)