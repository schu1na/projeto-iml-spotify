import os
import joblib
import torch
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Importações dos seus novos arquivos modulares!
from schemas import RequisicaoRecomendacao
from redes_siamesas import MapeadorSiames
from services_ml import processar_recomendacoes

modelos_ram = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando o Back-end e carregando a inteligência na memória RAM...")
    DIRETORIO_MODELS = "models"

    # Constantes
    EMBEDDING_DIM = 32
    HIDDEN_SIZE = 64
    INPUT_SIZE = 8

    # Roteador
    caminho_roteador = os.path.join(DIRETORIO_MODELS, "lightgbm_roteador.pkl")
    modelos_ram["roteador"] = joblib.load(caminho_roteador)
    print("  -> Roteador LightGBM carregado.")
    
    # Especialistas
    modelos_ram["especialistas"] = {}
    for arquivo in os.listdir(DIRETORIO_MODELS):
        if arquivo.startswith("lightgbm_especialista_cluster_") and arquivo.endswith(".pkl"):

            cluster_id = int(arquivo.split("_")[-1].split(".")[0])
            caminho_esp = os.path.join(DIRETORIO_MODELS, arquivo)
            
            modelos_ram["especialistas"][cluster_id] = joblib.load(caminho_esp)
            
    print(f"  -> {len(modelos_ram['especialistas'])} Modelos Especialistas carregados.")
    

    # Rede Siamesa
    rede_siamesa = MapeadorSiames(input_size=INPUT_SIZE, embedding_dim=EMBEDDING_DIM, hidden_size=HIDDEN_SIZE) 
    caminho_siamesa = os.path.join(DIRETORIO_MODELS, "rede_siamesa.pth")
    rede_siamesa.load_state_dict(torch.load(caminho_siamesa, map_location=torch.device('cpu')))
    rede_siamesa.eval()
    modelos_ram["siamesa"] = rede_siamesa
    print("  -> Pesos da Rede Siamesa injetados.")
    

    # Buscador e Matrizes
    modelos_ram["buscador"] = joblib.load(os.path.join(DIRETORIO_MODELS, "buscador_knn.pkl"))
    print("  -> Buscador NearestNeighbors indexado.")

    modelos_ram["todos_os_embeddings"] = np.load(os.path.join(DIRETORIO_MODELS, "todos_os_embeddings.npy"))
    modelos_ram["todos_os_generos"] = joblib.load(os.path.join(DIRETORIO_MODELS, "todos_os_generos.pkl"))
    modelos_ram["lista_ids"] = joblib.load(os.path.join(DIRETORIO_MODELS, "lista_track_ids.pkl"))
    print("  -> Matriz global e lista de gêneros carregadas (Prontas para o Filtro Rígido).")
    
    print("Todos os modelos estão na memória! Pronto para receber conexões.")
    yield
    print("Desligando o servidor e liberando memória...")
    modelos_ram.clear()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def raiz():
    return {"status": "Back-end rodando com sucesso!", "modelos_carregados": list(modelos_ram.keys())}

@app.post("/recomendar")
def obter_recomendacoes(dados: RequisicaoRecomendacao):
    return processar_recomendacoes(dados, modelos_ram)

@app.get("/buscar-sugestoes")
def buscar_sugestoes_por_texto(texto_busca: str):
    return buscar_features_por_texto(texto_busca)

@app.get("/buscar-audio-features")
def buscar_audio_features_endpoint(track_id: str):
    return buscar_audio_features(track_id)