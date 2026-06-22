import os
import joblib
import torch
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Importações dos seus novos arquivos modulares!
from schemas import RequisicaoRecomendacao
from redes_siamesas import MapeadorSiames
from services_ml import processar_recomendacoes, buscar_sugestoes_por_texto, buscar_audio_features

modelos_ram = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Constantes
    EMBEDDING_DIM = 32
    HIDDEN_SIZE = 64
    INPUT_SIZE = 9

    DIRETORIO_MODELS = "models"
    DIRETORIO_MODELS_LIGHTGBM = "models/lightgbm"
    DIRETORIO_MODELS_LR = "models/lr"

    print("Iniciando o Back-end e carregando a inteligência na memória RAM...")

    # Classificador - LightGBM
    caminhoClasificadorLightGbmCluster = os.path.join(DIRETORIO_MODELS_LIGHTGBM, "lightgbm_roteador.pkl")
    modelos_ram["ClasificadorLightGbmCluster"] = joblib.load(caminhoClasificadorLightGbmCluster)
    print("  -> Classificador Light GBM para Clusters carregado.")
    
    # Classificadores Especialistas - LightGBM
    modelos_ram["especialistasLgbm"] = {}
    for arquivo in os.listdir(DIRETORIO_MODELS_LIGHTGBM):
        if arquivo.startswith("lightgbm_especialista_cluster_") and arquivo.endswith(".pkl"):

            cluster_id = int(arquivo.split("_")[-1].split(".")[0])
            caminho_esp = os.path.join(DIRETORIO_MODELS_LIGHTGBM, arquivo)
            
            modelos_ram["especialistasLgbm"][cluster_id] = joblib.load(caminho_esp)
            
    print(f"  -> {len(modelos_ram['especialistasLgbm'])} Classificadores Especialistas LightGBM carregados.")
    
    # Classificador - LR
    caminhoClassificadorLRCluster = os.path.join(DIRETORIO_MODELS_LR, "lr_macrogenero.pkl")
    caminhoScalerLRCluster = os.path.join(DIRETORIO_MODELS_LR, "scaler_global.pkl")
    
    modelos_ram["ClassificadorLRCluster"] = joblib.load(caminhoClassificadorLRCluster)
    modelos_ram["ScalerLRCluster"] = joblib.load(caminhoScalerLRCluster)
    print("  -> Classificador LR e Scaler de Cluster carregados.")
    
    # Classificadores Especialistas - LR
    modelos_ram["especialistasLr"] = {}
    for arquivo in os.listdir(DIRETORIO_MODELS_LR):
        if arquivo.startswith("lr_especialista_") and arquivo.endswith(".pkl"):
            vibe = arquivo[16:-4] 
            caminho_esp_lr = os.path.join(DIRETORIO_MODELS_LR, arquivo)
            
            # Como salvamos um dicionário, ele já vem completo para a RAM
            modelos_ram["especialistasLr"][vibe] = joblib.load(caminho_esp_lr)
            
    print(f"  -> {len(modelos_ram['especialistasLr'])} Especialistas LR carregados.")

    # Rede Siamesa
    redeSiamesa = MapeadorSiames(
        input_size=INPUT_SIZE, 
        embedding_dim=EMBEDDING_DIM, 
        hidden_size=HIDDEN_SIZE) 
    caminhoSiamesa = os.path.join(DIRETORIO_MODELS, "rede_siamesa.pth")
    redeSiamesa.load_state_dict(torch.load(
        caminhoSiamesa, 
        map_location=torch.device('cpu'),
        weights_only=True))
    redeSiamesa.eval()
    modelos_ram["redeSiamesa"] = redeSiamesa
    print("  -> Pesos da Rede Siamesa injetados.")

    # Scaler rede siamesa
    caminhoScalerSiamesa = os.path.join(DIRETORIO_MODELS, "scaler_siamesa.pkl")
    modelos_ram["scalerSiamesa"] = joblib.load(caminhoScalerSiamesa)
    print("  -> Scaler Siamesa carregado.")
    
    # Embeddings
    print("  -> Carregando matriz dos embeddings...")
    modelos_ram["embeddings"] = np.load(os.path.join(DIRETORIO_MODELS, "todos_os_embeddings.npy"))
    
    # Buscador
    buscador = joblib.load(os.path.join(DIRETORIO_MODELS, "buscador_knn.pkl"))
    buscador.fit(modelos_ram["embeddings"])
    modelos_ram["buscador"] = buscador
    print("  -> Buscador NearestNeighbors re-indexado com sucesso.")

    # Generos e IDS
    modelos_ram["generosMusicas"] = joblib.load(os.path.join(DIRETORIO_MODELS, "todos_os_generos.pkl"))
    modelos_ram["listaIdsMusicas"] = joblib.load(os.path.join(DIRETORIO_MODELS, "lista_track_ids.pkl"))
    print("  -> Listas de IDs e gêneros carregadas (Prontas para o Filtro Rígido).")

    # Dicionário de audio features das músicas
    caminhoMusicasLocais = os.path.join(DIRETORIO_MODELS, "dicionario_busca_musicas.pkl")
    modelos_ram["DatasetMusicasLocais"] = joblib.load(caminhoMusicasLocais)
    print("  -> Dicionário de Busca Offline carregado.")
    
    print("Todos os modelos estão na memória! Pronto para receber conexões.")
    yield
    print("Desligando o servidor e liberando memória...")
    modelos_ram.clear()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def raiz():
    return {"status": "Back-end rodando com sucesso!", "modelos_carregados": list(modelos_ram.keys())}

@app.post("/recomendar")
def obterRecomendacoes(dados: RequisicaoRecomendacao):
    return processar_recomendacoes(dados, modelos_ram)

@app.get("/buscar-sugestoes")
def getSugestoes(texto_busca: str):
    return buscar_sugestoes_por_texto(texto_busca, modelos_ram)

@app.get("/buscar-audio-features")
def getAudioFeatures(track_id: str):
    resultado = buscar_audio_features(track_id, modelos_ram)
    if not resultado:
        raise HTTPException(status_code=404, detail="Música não encontrada na base local.")
    return resultado