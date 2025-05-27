import httpx
from fastapi import HTTPException

async def obter_clima(cidade: str = "auto"):
    url = f"https://wttr.in/{cidade}?format=%C+%t"
    
    try:
        async with httpx.AsyncClient() as client:
            resposta = await client.get(url)
            resposta.raise_for_status()  # Garante que erros HTTP sejam levantados
            return {"cidade": cidade, "clima": resposta.text}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Erro ao obter clima: {str(e)}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Erro de requisição: {str(e)}")
