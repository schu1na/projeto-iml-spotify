"""
Sistema de Recomendação Musical - Streamlit App
Trabalho final - Introdução ao Aprendizado de Máquina
"""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# =============================================================================
# CONFIG GERAL
# =============================================================================
st.set_page_config(
    page_title="MoodTune • Recomendador Musical",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# TEMA / CSS (Dark Mode inspirado no Spotify)
# =============================================================================
SPOTIFY_GREEN = "#1DB954"
BG = "#121212"
CARD_BG = "#181818"
CARD_HOVER = "#282828"
TEXT_MUTED = "#B3B3B3"

st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {BG};
            color: #FFFFFF;
        }}
        section[data-testid="stSidebar"] {{ background-color: #000000; }}
        header[data-testid="stHeader"] {{ background: transparent; }}
        #MainMenu, footer {{ visibility: hidden; }}

        h1, h2, h3, h4 {{ color: #FFFFFF; font-family: 'Helvetica Neue', sans-serif; }}
        .subtle {{ color: {TEXT_MUTED}; font-size: 0.9rem; }}

        /* ===== HEADER ===== */
        .app-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 28px;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(12px);
            border-radius: 14px;
            border: 1px solid #1f1f1f;
            margin-bottom: 28px;
        }}
        .app-header .brand {{
            display: flex; align-items: center; gap: 10px;
            font-weight: 800; font-size: 1.15rem; color: #fff;
            letter-spacing: 0.5px;
        }}
        .app-header .brand-dot {{
            width: 10px; height: 10px; border-radius: 50%;
            background: {SPOTIFY_GREEN};
            box-shadow: 0 0 12px {SPOTIFY_GREEN};
        }}

        /* nav: estiliza st.page_link como pílulas */
        div[data-testid="stPageLink"] a {{
            color: {TEXT_MUTED} !important;
            font-weight: 600;
            padding: 8px 18px !important;
            border-radius: 999px;
            transition: all 0.2s ease;
            text-decoration: none !important;
        }}
        div[data-testid="stPageLink"] a:hover {{
            color: #fff !important;
            background: {CARD_HOVER};
        }}

        /* ===== SEARCH (centralizada) ===== */
        .search-wrap {{
            max-width: 620px;
            margin: 40px auto 28px auto;
            text-align: center;
        }}
        .search-icon {{
            font-size: 2.4rem;
            color: {SPOTIFY_GREEN};
            margin-bottom: 10px;
            display: block;
        }}
        .search-title {{
            font-size: 1.6rem; font-weight: 700;
            color: #fff; margin: 0 0 6px 0;
        }}
        .search-sub {{
            color: {TEXT_MUTED}; font-size: 0.95rem;
            margin-bottom: 22px;
        }}
        /* selectbox arredondado */
        div[data-baseweb="select"] > div {{
            background: {CARD_BG} !important;
            border: 1px solid #2a2a2a !important;
            border-radius: 999px !important;
            padding: 4px 12px !important;
        }}

        /* ===== Cards ===== */
        .track-card {{
            background: {CARD_BG};
            padding: 16px;
            border-radius: 12px;
            transition: background 0.2s ease;
            height: 100%;
        }}
        .track-card:hover {{ background: {CARD_HOVER}; }}
        .track-card img {{
            width: 100%; border-radius: 8px; margin-bottom: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }}
        .track-title {{
            font-weight: 700; font-size: 1rem; color: #FFF; margin: 0;
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
        }}
        .track-artist {{ color: {TEXT_MUTED}; font-size: 0.85rem; margin-top: 4px; }}

        /* Botões */
        .stButton > button {{
            background: transparent; color: #FFF;
            border: 1px solid #404040; border-radius: 999px;
            padding: 6px 16px; font-weight: 600;
            transition: all 0.2s ease;
        }}
        .stButton > button:hover {{
            border-color: #FFF; transform: scale(1.03);
        }}
        .stButton > button[kind="primary"] {{
            background: {SPOTIFY_GREEN}; border-color: {SPOTIFY_GREEN}; color: #000;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# DADOS MOCK (substituir por chamadas ao FastAPI / modelo)
# =============================================================================
@st.cache_data
def load_mock_catalog() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 300
    artists = ["The Weeknd", "Tame Impala", "Daft Punk", "Arctic Monkeys",
               "Billie Eilish", "Kendrick Lamar", "Radiohead", "Dua Lipa",
               "Frank Ocean", "Tyler, The Creator", "FKA twigs", "Anitta",
               "Caetano Veloso", "Jorge Ben Jor", "Marisa Monte"]
    songs = ["Blinding Lights", "The Less I Know", "Get Lucky", "Do I Wanna Know",
             "Bad Guy", "HUMBLE.", "Creep", "Levitating", "Pink + White",
             "EARFQUAKE", "Two Weeks", "Envolver", "Sozinho", "Mas Que Nada",
             "Beija Eu", "Midnight City", "Redbone", "After Hours", "Borderline",
             "Solar Power", "Heat Waves", "Glimpse of Us", "Vampire", "Anti-Hero"]
    data = {
        "track": rng.choice(songs, n),
        "artist": rng.choice(artists, n),
        "energy": rng.random(n),
        "danceability": rng.random(n),
        "valence": rng.random(n),
        "tempo": rng.uniform(60, 200, n),
        "cluster": rng.integers(0, 5, n),
    }
    df = pd.DataFrame(data)
    df["track"] = df["track"] + " #" + df.index.astype(str)
    return df


def get_recommendations(seed_track: str, df: pd.DataFrame, k: int = 5) -> pd.DataFrame:
    """PLACEHOLDER: substituir por modelo Siamês / Annoy / FastAPI."""
    seed = df[df["track"] == seed_track].iloc[0]
    features = ["energy", "danceability", "valence"]
    dist = np.linalg.norm(df[features].values - seed[features].values, axis=1)
    df = df.assign(_dist=dist).sort_values("_dist")
    return df[df["track"] != seed_track].head(k).reset_index(drop=True)


def album_cover_url(seed: str) -> str:
    h = abs(hash(seed)) % 10_000
    return f"https://picsum.photos/seed/{h}/300/300"


# =============================================================================
# STATE
# =============================================================================
if "feedback" not in st.session_state:
    st.session_state.feedback = {}
if "page" not in st.session_state:
    st.session_state.page = "search"

df = load_mock_catalog()

# =============================================================================
# HEADER (brand + navegação)
# =============================================================================
st.markdown(
    f"""
    <div class="app-header">
        <div class="brand"><span class="brand-dot"></span> MoodTune</div>
        <div id="nav-anchor"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Navegação via botões (mantém estado em uma única página)
nav_l, nav_c, nav_r = st.columns([1, 2, 1])
with nav_c:
    n1, n2 = st.columns(2)
    with n1:
        if st.button("🔎  Pesquisa",
                     use_container_width=True,
                     type="primary" if st.session_state.page == "search" else "secondary"):
            st.session_state.page = "search"
            st.rerun()
    with n2:
        if st.button("📈  Métricas",
                     use_container_width=True,
                     type="primary" if st.session_state.page == "metrics" else "secondary"):
            st.session_state.page = "metrics"
            st.rerun()

st.markdown("<br/>", unsafe_allow_html=True)

# =============================================================================
# PÁGINA: PESQUISA
# =============================================================================
def render_search_page():
    # Bloco de busca centralizado
    st.markdown(
        """
        <div class="search-wrap">
            <span class="search-icon">🔍</span>
            <h2 class="search-title">O que você quer ouvir hoje?</h2>
            <p class="search-sub">Escolha uma música base e receba recomendações personalizadas.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Selectbox centralizado
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        options = sorted(df["track"].unique().tolist())
        seed_track = st.selectbox(
            "música base",
            options=options,
            index=0,
            label_visibility="collapsed",
            placeholder="Buscar música...",
        )
        st.button("✨ Recomendar", use_container_width=True, type="primary")

    st.markdown("---")

    # Resultados
    st.subheader("🎵 Top 5 recomendações para você")
    if not seed_track:
        return

    recs = get_recommendations(seed_track, df, k=5)
    cols = st.columns(5, gap="medium")

    for i, (col, row) in enumerate(zip(cols, recs.itertuples())):
        with col:
            cover = album_cover_url(f"{row.track}-{row.artist}")
            st.markdown(
                f"""
                <div class="track-card">
                    <img src="{cover}" alt="cover" />
                    <p class="track-title" title="{row.track}">{row.track}</p>
                    <p class="track-artist">{row.artist}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            current = st.session_state.feedback.get(row.track)
            fb1, fb2 = st.columns(2)
            with fb1:
                label = "👍 Gostei" if current != "like" else "✅ Gostei"
                if st.button(label, key=f"like_{i}", use_container_width=True):
                    st.session_state.feedback[row.track] = "like"
                    st.rerun()
            with fb2:
                label = "👎 Não" if current != "dislike" else "❌ Não"
                if st.button(label, key=f"dislike_{i}", use_container_width=True):
                    st.session_state.feedback[row.track] = "dislike"
                    st.rerun()

    with st.expander("🧠 Feedback coletado (entrada para o modelo supervisionado)"):
        if st.session_state.feedback:
            fb_df = pd.DataFrame(
                [{"track": k, "feedback": v} for k, v in st.session_state.feedback.items()]
            )
            st.dataframe(fb_df, use_container_width=True, hide_index=True)
            st.caption("Pode ser enviado via `POST /feedback` ao back-end FastAPI.")
        else:
            st.info("Nenhum feedback registrado ainda.")


# =============================================================================
# PÁGINA: MÉTRICAS
# =============================================================================
def render_metrics_page():
    st.subheader("📈 Métricas do Modelo")
    st.markdown(
        f"<p class='subtle'>Indicadores de avaliação dos modelos de "
        f"agrupamento (K-Means) e similaridade (Rede Siamesa).</p>",
        unsafe_allow_html=True,
    )

    # KPIs (placeholders — conectar ao back-end)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Silhouette (K-Means)", "0.62", "+0.04")
    k2.metric("Inertia", "1284.5", "-12.1")
    k3.metric("Precision@5 (Siamês)", "0.81", "+0.03")
    k4.metric("Feedbacks coletados", str(len(st.session_state.feedback)))

    st.markdown("---")

    # Mapa de Clusters
    st.subheader("🗺️ Mapa de Clusters — 'vibe' das músicas")
    fig = px.scatter_3d(
        df, x="energy", y="danceability", z="valence",
        color=df["cluster"].astype(str),
        hover_data={"track": True, "artist": True, "cluster": True,
                    "energy": ":.2f", "danceability": ":.2f", "valence": ":.2f"},
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={"color": "Cluster"},
    )
    fig.update_traces(marker=dict(size=4, opacity=0.85))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG, font_color="#FFF",
        height=560, margin=dict(l=0, r=0, t=10, b=0),
        scene=dict(
            xaxis=dict(backgroundcolor=BG, gridcolor="#333", color="#FFF"),
            yaxis=dict(backgroundcolor=BG, gridcolor="#333", color="#FFF"),
            zaxis=dict(backgroundcolor=BG, gridcolor="#333", color="#FFF"),
        ),
        legend=dict(bgcolor=CARD_BG, bordercolor="#333"),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Distribuição por cluster")
        st.bar_chart(df["cluster"].value_counts().sort_index())
    with c2:
        st.markdown("#### Features médias por cluster")
        st.dataframe(
            df.groupby("cluster")[["energy", "danceability", "valence", "tempo"]]
              .mean().round(3),
            use_container_width=True,
        )


# =============================================================================
# ROUTER
# =============================================================================
if st.session_state.page == "search":
    render_search_page()
else:
    render_metrics_page()

# =============================================================================
# RODAPÉ
# =============================================================================
st.markdown("---")
st.markdown(
    "<p class='subtle' style='text-align:center'>"
    "MoodTune © Trabalho final • Introdução ao Aprendizado de Máquina"
    "</p>",
    unsafe_allow_html=True,
)
