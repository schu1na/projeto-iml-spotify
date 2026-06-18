import torch
import numpy as np
import spotipy
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
    try:
        features_dict = dados.audio_features
        deve_filtrar = dados.filtrar_genero
        
        features_lgbm = [
            'danceability', 'energy', 'loudness', 'speechiness', 
            'acousticness', 'instrumentalness', 'liveness', 'valence', 'explicit'
        ]
        
        features_siamesa = [
            'danceability', 'energy', 'loudness', 'speechiness', 
            'acousticness', 'instrumentalness', 'liveness', 'valence'
        ]
        
        vetor_lgbm = np.array([[features_dict[f] for f in features_lgbm]], dtype=np.float32)
        vetor_siamesa = np.array([[features_dict[f] for f in features_siamesa]], dtype=np.float32)
        
        tensor_entrada = torch.tensor(vetor_siamesa, dtype=torch.float32)
        
        with torch.no_grad():
            embedding_busca = modelos_ram["siamesa"](tensor_entrada).numpy()

        if not deve_filtrar:
            print("Executando Modo: Espaço Latente Puro (Mais Próximos Globais)")
            distancias, indices = modelos_ram["buscador"].kneighbors(embedding_busca)
            ids_recomendados = [modelos_ram["lista_ids"][idx] for idx in indices[0]]
            modo_final = "pure_latent_space"
            genero_final = "N/A (Ignorado neste modo)"

        else:
            print("Executando Modo: Filtro de Contexto Rígido por Gênero")
            cluster_previsto = int(modelos_ram["roteador"].predict(vetor_lgbm)[0])
            genero_previsto = str(modelos_ram["especialistas"][cluster_previsto].predict(vetor_lgbm)[0])
                        
            todos_generos = np.array(modelos_ram["todos_os_generos"])
            mascara_genero = (todos_generos == genero_previsto)
            
            embeddings_filtrados = modelos_ram["todos_os_embeddings"][mascara_genero]
            ids_filtrados = np.array(modelos_ram["lista_ids"])[mascara_genero]
            
            buscador_nicho = NearestNeighbors(n_neighbors=min(6, len(ids_filtrados)), metric='cosine', algorithm='brute')
            buscador_nicho.fit(embeddings_filtrados)
            
            distancias, indices = buscador_nicho.kneighbors(embedding_busca)
            ids_recomendados = [ids_filtrados[idx] for idx in indices[0]]
            modo_final = "hard_genre_filter"
            genero_final = genero_previsto            

        lista_completa_limpa = [str(id_musica).strip().replace("'", "").replace('"', '') for id_musica in ids_recomendados]

        id_original = str(features_dict.get('track_id', '')).strip()

        if lista_completa_limpa[0] == id_original:
            ids_para_spotify = lista_completa_limpa[1:]
        else:
            ids_para_spotify = lista_completa_limpa[0:5]

        recomendacoes_estruturadas = montar_informacoes_recomendacoes(ids_para_spotify)

        return {
            "modo": modo_final,
            "genero_detectado": genero_final,
            "recomendacoes": recomendacoes_estruturadas
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na pipeline de ML: {str(e)}")



def montar_informacoes_recomendacoes(lista_ids):
    print("Buscando no Spotify os IDs exatos:", lista_ids)
    
    recomendacoes_estruturas = []
    
    # Fazemos a busca de UMA música por vez, exatamente como no seu teste isolado
    for id_musica in lista_ids:
        try:
            # Tenta buscar os dados apenas deste ID
            track = sp.track(id_musica)

            
            if track is not None:
                info_musica = {
                    "id": track.get('id', ''),
                    "nome": track.get('name', 'Desconhecido'),
                    "artista": track['artists'][0]['name'] if track.get('artists') else 'Desconhecido', 
                    "album": track['album']['name'] if track.get('album') else 'Desconhecido',
                    "imagem_url": track['album']['images'][0]['url'] if track.get('album') and track['album'].get('images') else "",
                    "link_spotify": track['external_urls']['spotify'] if track.get('external_urls') else ""
                }
                recomendacoes_estruturas.append(info_musica)
                
        except Exception as e:
            # Se ESSA música específica der o erro 403, o back-end NÃO explode.
            # Ele apenas avisa no terminal, ignora a música problemática e continua o loop.
            print(f"Aviso: O Spotify recusou o ID {id_musica}. Motivo: {e}")
            continue # Pula para o próximo ID
            
    return recomendacoes_estruturas


def buscar_sugestoes_por_texto(texto_busca: str):
    print(f"🔍 Buscando sugestões para: '{texto_busca}'...")
    
    # 1. Pede as 5 músicas mais relevantes para o texto digitado
    resultados = sp.search(q=texto_busca, type='track', limit=5)
    tracks_encontradas = resultados['tracks']['items']
    
    if not tracks_encontradas:
        return [] # Retorna lista vazia se não achar nada
               
    sugestoes_limpas = []
    
    # 4. Junta os dados visuais com os dados matemáticos
    for track, feats in zip(tracks_encontradas, features_brutas):
        if feats is None:
            continue # Pula a música se o Spotify não tiver as features dela
            
        sugestao = {
            "id": track['id'],
            "nome": track['name'],
            "artista": track['artists'][0]['name']
        }
        sugestoes_limpas.append(sugestao)
        
    return sugestoes_limpas


def buscar_audio_features(track_id: str):
    """
    Busca as features de áudio de uma música específica no Spotify usando o Track ID.
    Retorna um dicionário formatado para uso imediato pelo frontend.
    """
    try:
        # 1. Busca a música pelo ID exato
        track = sp.track(track_id)

        if track is None or not track.get('id'):
            print(f"Erro: Música com ID {track_id} não encontrada.")
            return None

        # 2. Busca as features de áudio para esse ID
        # O método audio_features aceita uma lista de IDs, mas como queremos só uma, passamos uma lista com um item
        features_list = sp.audio_features([track_id])
        
        # Se por acaso o Spotify não tiver as features, retorna None
        if features_list is None or len(features_list) == 0:
            print(f"Erro: Não foi possível obter features para o ID {track_id}.")
            return None

        feats = features_list[0]

        # 3. Monta o dicionário final exatamente no formato que o Frontend espera
        features_musica = {
            "track_id": track['id'],
            "danceability": feats['danceability'],
            "energy": feats['energy'],
            "loudness": feats['loudness'],
            "speechiness": feats['speechiness'],
            "acousticness": feats['acousticness'],
            "instrumentalness": feats['instrumentalness'],
            "liveness": feats['liveness'],
            "valence": feats['valence'],
            "explicit": 1 if track['explicit'] else 0
        }

        return features_musica

    except Exception as e:
        print(f"Erro ao buscar features para o ID {track_id}: {e}")
        return None