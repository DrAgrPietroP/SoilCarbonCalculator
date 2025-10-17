import streamlit as st

st.set_page_config(page_title="SoilCarbonCalculator Terreni", page_icon="🌱", layout="wide")
st.title("🌱 SoilCarbonCalculator - Gestione terreni e stoccaggio annuo")

# -------------------------------
# Inizializzazione session_state
if "terreni" not in st.session_state:
    st.session_state['terreni'] = {}

# -------------------------------
# 1️⃣ Selezione o aggiunta terreno
st.header("1️⃣ Seleziona o aggiungi terreno")
nuovo_terreno = st.text_input("Nome nuovo terreno")
superficie = st.number_input("Superficie (ha)", min_value=0.1, max_value=1000.0, value=1.0, step=0.1)

if st.button("Aggiungi terreno"):
    if nuovo_terreno in st.session_state['terreni']:
        st.warning("Il terreno esiste già!")
    else:
        st.session_state['terreni'][nuovo_terreno] = {"superficie": superficie, "annate": {}}
        st.success(f"Terreno '{nuovo_terreno}' aggiunto.")

# Menu terreni esistenti
terreno_selezionato = st.selectbox("Terreno", list(st.session_state['terreni'].keys()))

# -------------------------------
# 2️⃣ Selezione anno
st.header("2️⃣ Seleziona anno")
anni_disponibili = list(st.session_state['terreni'][terreno_selezionato]["annate"].keys())
anno_nuovo = st.number_input("Nuovo anno", min_value=2000, max_value=2100, value=2025, step=1)

if st.button("Aggiungi anno"):
    if anno_nuovo in st.session_state['terreni'][terreno_selezionato]["annate"]:
        st.warning("Anno già presente!")
    else:
        st.session_state['terreni'][terreno_selezionato]["annate"][anno_nuovo] = []
        st.success(f"Anno {anno_nuovo} aggiunto al terreno '{terreno_selezionato}'.")

# Selezione anno esistente
anno_selezionato = st.selectbox(
    "Anno da modificare",
    list(st.session_state['terreni'][terreno_selezionato]["annate"].keys())
)

# -------------------------------
# 3️⃣ Inserimento colture per l'anno
st.header(f"3️⃣ Inserisci colture per l'anno {anno_selezionato}")

coltura = st.selectbox("Coltura", ["Mais granella", "Frumento", "Orzo", "Fieno/erba", "Soia"])
resa = st.number_input("Resa raccolta_

