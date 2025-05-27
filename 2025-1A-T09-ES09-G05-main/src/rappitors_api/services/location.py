from firebase_admin import db
from geopy.geocoders import Nominatim

# Definir um user_agent único para evitar bloqueios
USER_AGENT = "location_service"

def obter_coordenadas(endereco: str):
    geolocator = Nominatim(user_agent=USER_AGENT)
    localizacao = geolocator.geocode(endereco)
    
    if localizacao:
        return {"latitude": localizacao.latitude, "longitude": localizacao.longitude}
    else:
        return {"error": "Endereço não encontrado"}

def obter_endereco(latitude: float, longitude: float):
    geolocator = Nominatim(user_agent=USER_AGENT)
    localizacao = geolocator.reverse((latitude, longitude), exactly_one=True)
    
    if localizacao:
        return {"endereco": localizacao.address}
    else:
        return {"error": "Coordenadas não encontradas"}

async def atualizar_localizacao(entregador_id: int, latitude: float = None, longitude: float = None, endereco: str = None):
    if endereco:
        coordenadas = obter_coordenadas(endereco)
        if "error" in coordenadas:
            return coordenadas  # Retorna erro se não encontrar o endereço
        latitude, longitude = coordenadas["latitude"], coordenadas["longitude"]

    if latitude is None or longitude is None:
        return {"error": "Coordenadas inválidas"}

    ref = db.reference(f"entregadores/{entregador_id}/localizacao")
    ref.set({"latitude": latitude, "longitude": longitude})
    return {"message": "Localização atualizada"}
