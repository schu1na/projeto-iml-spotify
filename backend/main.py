from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Suas outras importações (pandas, modelos, etc)

app = FastAPI()

# --- CONFIGURAÇÃO DO CORS (Obrigatório para o Angular funcionar) ---
origins = [
    "http://localhost:4200", # Endereço padrão do Angular
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, PUT, DELETE
    allow_headers=["*"],
)
# -------------------------------------------------------------------

# Exemplo de Endpoint que o Angular vai chamar
@app.get("/")
def read_root():
    return {"mensagem": "API do Spotify conectada!"}

@app.post("/recomendar")
def recomendar_musica(musica: dict):
    # Aqui entra a lógica da Rede Siamesa e do Annoy
    return {"recomendacoes": ["Musica 1", "Musica 2", "Musica 3"]}