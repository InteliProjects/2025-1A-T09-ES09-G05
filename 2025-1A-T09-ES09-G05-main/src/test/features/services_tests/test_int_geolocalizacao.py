import pytest
import firebase_admin
from firebase_admin import credentials, db
from rappitors_api.services.location import atualizar_localizacao, obter_coordenadas, obter_endereco


# Inicializando o Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("config/alocacao-entregadores-firebase-credenciais.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://alocacao-entregadores-default-rtdb.firebaseio.com/"  
    })

# Teste para a função obter_coordenadas
@pytest.mark.parametrize("endereco, esperado", [
    ("Avenida Paulista, São Paulo", True),
    ("Localização Inexistente XYZ", False)
])
def test_obter_coordenadas(endereco, esperado):
    resultado = obter_coordenadas(endereco)
    if esperado:
        assert "latitude" in resultado and "longitude" in resultado
    else:
        assert "error" in resultado

# Teste para a função obter_endereco
@pytest.mark.parametrize("latitude, longitude, esperado", [
    (-23.561, -46.656, True),
    (0, 0, False)
])
def test_obter_endereco(latitude, longitude, esperado):
    resultado = obter_endereco(latitude, longitude)
    if esperado:
        assert "endereco" in resultado
    else:
        assert "error" in resultado

# Teste para a função atualizar_localizacao no Firebase
@pytest.mark.asyncio
async def test_atualizar_localizacao():
    resposta = await atualizar_localizacao("entregador_123", -23.561, -46.656)
    assert resposta == {"message": "Localização atualizada"}