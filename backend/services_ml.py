import torch
import numpy as np
import spotipy
import os
import traceback
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.neighbors import NearestNeighbors
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))

def processar_recomendacoes(dados, modelos_ram):
    """
    Função principal do back-end que executa a pipeline de Machine Learning.
    Recebe os dados da música do usuário e retorna 5 recomendações.
    
    Parâmetros:
    - dados: Objeto contendo 'audio_features' (dicionário numérico) e 'filtrar_genero' (booleano).
    - modelos_ram: Dicionário contendo os modelos pré-carregados (Siamesa, LGBM, NearestNeighbors, etc).
    """
    try:
        featuresDict = dados.audio_features
        deveFiltrar = dados.filtrar_genero
        motor_classificacao = getattr(dados, "motor_classificacao", "lightgbm")
        
        # Definição das colunas exatas que cada modelo espera.
        featuresLgbm = [
            'danceability', 'energy', 'loudness', 
            'speechiness', 'acousticness', 'instrumentalness', 
            'liveness', 'valence', 'explicit', 'tempo'
        ]
        
        featuresSiamesa = [
            'danceability', 'energy', 'loudness', 
            'speechiness', 'acousticness', 'instrumentalness', 
            'liveness', 'valence', 'tempo'
        ]

        vetor_lgbm = np.array([[featuresDict[f] for f in featuresLgbm]], dtype=np.float32)
        
        id_musica_buscada = dados.track_id 
        print("ID da música buscada:", id_musica_buscada)
        
        if id_musica_buscada in modelos_ram["listaIdsMusicas"]:
            print("Música conhecida! Pegando o vetor diretamente da matriz (Igual ao Notebook).")
            indice_musica = modelos_ram["listaIdsMusicas"].index(id_musica_buscada)
            embedding_busca = np.array([modelos_ram["embeddings"][indice_musica]])
            print("Embedding da música buscada:", embedding_busca[:5])
        else:
            print("Música nova! Usando a Rede Siamesa para inferir o vetor...")
            df_siamesa = pd.DataFrame([[featuresDict[f] for f in featuresSiamesa]], columns=featuresSiamesa)
            vetor_siamesa_normalizado = modelos_ram["scalerSiamesa"].transform(df_siamesa)
            tensor_entrada = torch.tensor(vetor_siamesa_normalizado, dtype=torch.float32)
            
            with torch.no_grad():
                embedding_busca = modelos_ram["redeSiamesa"](tensor_entrada).numpy()

        # Classificação de gênero — sempre executada, independentemente do filtro
        if motor_classificacao == "linear":
            print("Classificando gênero via Regressão Logística (Linear)...")
            vetor_lr_scaled = modelos_ram["ScalerLRCluster"].transform(vetor_lgbm)
            vibe_prevista = str(modelos_ram["ClassificadorLRCluster"].predict(vetor_lr_scaled)[0])
            genero_previsto = str(modelos_ram["especialistasLr"][vibe_prevista]["modelo"].predict(
                modelos_ram["especialistasLr"][vibe_prevista]["scaler"].transform(vetor_lgbm)
            )[0])
        else:
            print("Classificando gênero via LightGBM...")
            cluster_previsto = int(modelos_ram["ClasificadorLightGbmCluster"].predict(vetor_lgbm)[0])
            genero_previsto = str(modelos_ram["especialistasLgbm"][cluster_previsto].predict(vetor_lgbm)[0])

        genero_final = genero_previsto
        print(f"Gênero classificado: {genero_final} | Filtrar: {deveFiltrar} | Motor: {motor_classificacao}")

        # Seleção dos embeddings/IDs — com ou sem filtro de gênero
        embeddings_candidatos = modelos_ram["embeddings"]
        ids_candidatos = np.array(modelos_ram["listaIdsMusicas"])

        if deveFiltrar:
            print("Aplicando filtro de gênero...")
            todos_generos = np.array(modelos_ram["generosMusicas"])
            mascara_genero = (todos_generos == genero_previsto)
            embeddings_candidatos = embeddings_candidatos[mascara_genero]
            ids_candidatos = ids_candidatos[mascara_genero]

        # Busca pelos vizinhos mais próximos (brute-force cosine)
        n_vizinhos = min(6, len(ids_candidatos))
        buscador_nicho = NearestNeighbors(n_neighbors=n_vizinhos, metric='cosine', algorithm='brute')
        buscador_nicho.fit(embeddings_candidatos)
        distancias, indices = buscador_nicho.kneighbors(embedding_busca)
        ids_recomendados = [ids_candidatos[idx] for idx in indices[0]]
        modo_final = f"{motor_classificacao}_genre_filter" if deveFiltrar else f"{motor_classificacao}_global"

        # Tratamento final e retorno
        # Remove a própria música buscada da lista de recomendações (se presente) e pega as 5 primeiras
        lista_completa_limpa = [str(id_musica).strip().replace("'", "").replace('"', '') for id_musica in ids_recomendados]
        lista_sem_buscada = [id_ for id_ in lista_completa_limpa if id_ != id_musica_buscada]

        recomendacoes_estruturadas = montar_informacoes_recomendacoes(lista_sem_buscada[:5], modelos_ram)

        # Busca os dados completos da música buscada para exibir no frontend
        dados_musica_buscada = montar_informacoes_recomendacoes([id_musica_buscada], modelos_ram)
        musica_buscada = dados_musica_buscada[0] if dados_musica_buscada else None

        return {
            "modo": modo_final,
            "genero_detectado": genero_final,
            "musica_buscada": musica_buscada,
            "recomendacoes": recomendacoes_estruturadas
        }

    except Exception as e:
        print("\n" + "="*50)
        print("ERRO GRAVE NA PIPELINE DE ML:")
        traceback.print_exc() 
        print("="*50 + "\n")
        raise HTTPException(status_code=500, detail=f"Erro na pipeline de ML: {str(e)}")



def montar_informacoes_recomendacoes(lista_ids, modelos_ram):
    """
    Monta a estrutura das recomendações que serão passadas para o frontend. Faz uso de um misto
    de informações locais da base de dados e informações obtidas a partir da API do Spotify
    
    Parâmetros:
    - lista_ids: Lista de IDs das músicas recomendadas.
    
    Retorno:
    - Lista de dicionários contendo as informações estruturadas das músicas recomendadas.
    """
    print("Buscando no Spotify os IDs exatos:", lista_ids)

    dicionario = modelos_ram.get("DatasetMusicasLocais", {})
    
    recomendacoes_estruturas = []
    
    for id_musica in lista_ids:
        try:
            track = sp.track(id_musica)

            if track is not None:
                info_musica = {
                    "id": track.get('id', ''),
                    "nome": track.get('name', 'Desconhecido'),
                    "artista": track['artists'][0]['name'] if track.get('artists') else 'Desconhecido', 
                    "duracao": track.get('duration_ms', ''),
                    "album": track['album']['name'] if track.get('album') else 'Desconhecido',
                    "imagem_url": track['album']['images'][0]['url'] if track.get('album') and track['album'].get('images') else "",
                    "link_spotify": track['external_urls']['spotify'] if track.get('external_urls') else "",
                    "genero": dicionario[id_musica].get('genero')
                }
                recomendacoes_estruturas.append(info_musica)
                
        except Exception as e:
            print(f"Aviso: O Spotify recusou o ID {id_musica}. Motivo: {e}")
            continue 
            
    return recomendacoes_estruturas


def buscar_sugestoes_por_texto(texto_busca: str, modelos_ram: dict):
    """
    Busca sugestões de músicas baseadas em um texto digitado pelo usuário.
    
    Parâmetros:
    - texto_busca: Texto digitado pelo usuário.

    Retorno:
    - Lista de dicionários contendo as informações estruturadas das músicas recomendadas.
    """
    print(f"Buscando sugestões para: '{texto_busca}'...")
    
    texto_busca = texto_busca.lower().strip()
    dicionario = modelos_ram.get("DatasetMusicasLocais", {})
    
    sugestoes_limpas = []
    
    for track_id, dados in dicionario.items():
        nome_musica = str(dados.get('nome', '')).lower()
        artista = str(dados.get('artista', '')).lower()
        
        # Se o que o usuário digitou faz parte do nome da música ou do artista
        if texto_busca in nome_musica or texto_busca in artista:
            sugestao = {
                "id": track_id,
                "nome": str(dados.get('nome', 'Desconhecido')).title(), 
                "artista": str(dados.get('artista', 'Desconhecido')).title()
            }
            sugestoes_limpas.append(sugestao)
            
            if len(sugestoes_limpas) == 5:
                break
                
    return sugestoes_limpas


def buscar_audio_features(track_id: str, modelos_ram: dict):
    """
    Busca as features de áudio de uma música específica usando o Track ID.
    Retorna um dicionário formatado para uso imediato pelo frontend.
    
    Parâmetros:
    - track_id: ID da música no Spotify.
    
    Retorno:
    - Dicionário contendo as features de áudio da música.
    """
    print(f"Buscando features locais para o ID: {track_id}")
    dicionario = modelos_ram.get("DatasetMusicasLocais", {})
    
    try:
        if track_id in dicionario:
            dados_musica = dicionario[track_id]
            return dados_musica.get("audio_features")
        else:
            print(f"Aviso: Música com ID {track_id} não encontrada na base local.")
            return None

    except Exception as e:
        print(f"Erro ao buscar features locais para o ID {track_id}: {e}")
        return None