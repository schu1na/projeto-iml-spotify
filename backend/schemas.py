from pydantic import BaseModel

class RequisicaoRecomendacao(BaseModel):
    audio_features: dict   
    filtrar_genero: bool = True