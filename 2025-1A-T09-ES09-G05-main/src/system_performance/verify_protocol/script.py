from firebase_admin import credentials, db
import logging
import requests
import asyncio
import aiohttp
import firebase_admin
import os
import json

cred_path = os.getenv("FIREBASE_CREDENTIALS", "src/config/alocacao-entregadores-firebase-credenciais.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://alocacao-entregadores-default-rtdb.firebaseio.com/"
    })

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

urls = {"rappitors_api": "rappitors_api:8000"}

async def verify_protocols(): 
    print('Iniciando verificação de protocolos...')

    ref = db.reference("protocolos")
    db_protocolos = ref.get()
    
    if not db_protocolos:
        logger.info('Nenhum protocolo encontrado no banco.')
        return
    
    async with aiohttp.ClientSession() as session:
        for url_key, url_value in urls.items():
            try:
                if url_key not in db_protocolos:
                    logger.warning(f"Protocolo para {url_key} não encontrado no banco de dados.")
                    continue
                
                protocolo_esperado = db_protocolos[url_key]
                endpoint = f"http://{url_value}/protocolo"
                
                logger.info(f"Verificando protocolo para {url_key} no endpoint: {endpoint}")
                response = await session.get(endpoint)

                if response.status == 200:
                    try:
                        # Obtém o JSON da resposta corretamente
                        response_json = await response.json()
                        logger.info(f"Resposta recebida: {response_json}")
                        
                        # Verifica o campo 'status' no JSON
                        if response_json.get("status") == "ok":
                            protocolo_recebido = response_json.get("versão", "")
                            logger.info(f"Protocolo recebido: {protocolo_recebido}")

                            # Comparação do protocolo
                            if protocolo_recebido and protocolo_recebido == protocolo_esperado:
                                logger.info(f"Protocolo para {url_key} está válido!")
                            else:
                                logger.warning(f"Protocolo para {url_key} desatualizado. Esperado: {protocolo_esperado}, Atual: {protocolo_recebido}")
                        else:
                            logger.error(f"Resposta do {url_key} não tem status 'ok'. Resposta: {response_json}")
                    
                    except json.JSONDecodeError as e:
                        response_text = await response.text()
                        logger.error(f"Erro ao tentar parsear JSON para {url_key}: {str(e)}")
                        logger.error(f"Conteúdo da resposta: {response_text}")
                else:
                    logger.error(f"Falha ao verificar {url_key}. Status: {response.status}")
                    response_text = await response.text()
                    logger.error(f"Corpo da resposta: {response_text}")
            
            except aiohttp.ClientError as e:
                logger.error(f"Erro de conexão ao verificar protocolo para {url_key}: {str(e)}")
            except Exception as e:
                logger.error(f"Erro ao verificar protocolo para {url_key}: {str(e)}")


async def periodic_task():
    while True:
        try:
            await verify_protocols()
        except Exception as e:
            logger.error(f"Erro na execução da tarefa periódica: {str(e)}")
        finally:
            await asyncio.sleep(10)

    
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(periodic_task())
    except KeyboardInterrupt:
        logger.info("Serviço interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal no serviço: {str(e)}")