from pydantic import BaseModel

class RequisicaoRecomendacao(BaseModel):
    track_id: str
    audio_features: dict   
    filtrar_genero: bool = True
    motor_classificacao: str = 'lightgbm'