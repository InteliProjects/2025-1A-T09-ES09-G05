import time
import redis.asyncio as aioredis 
import firebase_admin
from firebase_admin import credentials, db
from fastapi import FastAPI, HTTPException
import structlog

# Caminho para o arquivo de credenciais do Firebase
cred_path = r"../../config/alocacao-entregadores-firebase-credenciais.json"

# Inicializar Firebase se ainda não estiver inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://alocacao-entregadores-default-rtdb.firebaseio.com/"
    })

# Conectar ao Firebase
db_ref = db.reference("entregadores")

# Conectar ao Redis
redis = None
async def get_redis():
    global redis
    if not redis:
        redis = aioredis.Redis.from_url("redis://localhost")  
    return redis

app = FastAPI()

CACHE_EXPIRATION = 300  
API_TIMEOUT_THRESHOLD = 3


# Configurar logs estruturados
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ]
)
log = structlog.get_logger()

@app.get("/entregadores/{entregador_id}/saldo_final")
async def get_saldo_final(entregador_id: str):
    redis_conn = await get_redis()
    cache_key = f"saldo_final:{entregador_id}"

    # Verifica se há cache disponível
    cached_saldo_final = await redis_conn.get(cache_key)
    if cached_saldo_final:
        log.info("Cache hit", entregador_id=entregador_id, cache=True)
        return {"id": entregador_id, "saldo_final": float(cached_saldo_final), "cache": True}

    try:
        start_time = time.time()
        saldo_final = db_ref.child(entregador_id).child("saldo_final").get()
        response_time = time.time() - start_time

        # Log do tempo de resposta
        log.info("API Response Time", entregador_id=entregador_id, response_time=response_time)

        if response_time > API_TIMEOUT_THRESHOLD:
            log.warning("API lenta", entregador_id=entregador_id, response_time=response_time)

        if saldo_final is None:
            raise HTTPException(status_code=404, detail="saldo_final não encontrados")

        # Armazena no cache
        await redis_conn.setex(cache_key, CACHE_EXPIRATION, saldo_final)

        return {"id": entregador_id, "saldo_final": saldo_final, "cache": False}

    except Exception as e:
        log.error("Erro ao buscar saldo_final", entregador_id=entregador_id, error=str(e))
        if cached_saldo_final:
            return {"id": entregador_id, "saldo_final": float(cached_saldo_final), "cache": True, "warning": "Dados desatualizados"}
        raise HTTPException(status_code=500, detail=f"Erro ao buscar saldo_final: {str(e)}")
