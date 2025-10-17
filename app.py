import streamlit as st
from datetime import datetime

st.set_page_config(page_title="SoilCarbonCalculator Terreni", page_icon="🌱", layout="wide")
st.title("🌱 SoilCarbonCalculator - Calcolo stoccaggio carbonio")

# -------------------------------
# Inizializzazione session_state
if "annate" not in st.session_state:
    st.session_state["annate"] = {}

if "colture_form" not in st.session_state:
    st.session_state["colture_form"] = []

# -------------------------------
# 1️⃣ Selezione anno
st.header("1️⃣ Seleziona anno")
anno_corrente = datetime.now().year
anni_possibili = list(range(1950, anno_corrente + 1))
anno_selezionato = st.selectbox("Anno", anni_possibili, index=len(anni_possibili) - 1)

if anno_selezionato not in st.session_state["annate"]:
    st.session_state["annate"][anno_selezionato] = {}

# -------------------------------
# 2️⃣ Selezione terreno (con superficie)
st.header("2️⃣ Seleziona o aggiungi terreno con superficie")
terreni_anno = st.session_state["annate"][anno_selezionato]

# Input nuovo terreno + superficie
nuovo_terreno = st.text_input("Nome nuovo terreno")
superficie_input = st.number_input("Superficie del terreno (ha)", min_value=0.1, max_value=10000.0, value=1.0, step=0.1)

col1, col2 = st.columns([0.1, 0.9])
with col1:
    aggiungi_terreno = st.button("+")

if aggiungi_terreno:
    if not nuovo_terreno.strip():
        st.error("Errore: inserisci un nome valido per il terreno.")
    elif nuovo_terreno in terreni_anno:
        st.warning("⚠️ Il terreno esiste già!")
    else:
        # Salva non solo il nome ma anche la superficie e una lista di colture
        terreni_anno[nuovo_terreno] = {"superficie": superficie_input, "colture": []}
        st.success(f"✅ Terreno '{nuovo_terreno}' aggiunto con superficie {superficie_input:.2f} ha.")

terreno_selezionato = None
if terreni_anno:
    terreno_selezionato = st.selectbox("Terreno", list(terreni_anno.keys()))

# -------------------------------
# 3️⃣ Inserimento colture
if terreno_selezionato:
    st.header(f"3️⃣ Inserisci colture per il terreno '{terreno_selezionato}'")

    # inizializza form se vuoto
    if len(st.session_state["colture_form"]) < 2:
        st.session_state["colture_form"] = [{"coltura": "Nessuna", "resa": 0.0} for _ in range(2)]

    # elenco colture disponibili
    elenco_colture = [
        "Nessuna",
        "Mais granella",
        "Mais trinciato",
        "Frumento",
        "Frumento trinciato",
        "Orzo",
        "Sorgo da granella",
        "Sorgo trinciato",
        "Avena",
        "Erba medica",
        "Fieno/erba",
        "Soia",
        "Girasole",
        "Colza",
        "Triticale"
    ]

    # visualizza form esistente
    for i, entry in enumerate(st.session_state["colture_form"]):
        st.subheader(f"Coltura {i+1}")
        entry["coltura"] = st.selectbox(
            f"Seleziona coltura {i+1}",
            elenco_colture,
            index=elenco_colture.index(entry["coltura"]) if entry["coltura"] in elenco_colture else 0,
            key=f"coltura_{i}"
        )
        entry["resa"] = st.number_input(
            f"Resa raccolta (t/ha) {i+1}",
            min_value=0.0,
            max_value=100.0,
            value=entry["resa"],
            step=0.1,
            key=f"resa_{i}"
        )

    # pulsante aggiungi nuova coltura
    if st.button("Aggiungi coltura"):
        st.session_state["colture_form"].append({"coltura": "Nessuna", "resa": 0.0})

    # pulsante salva
    if st.button("Salva colture"):
        nuove_colture = [c for c in st.session_state["colture_form"]
                         if c["resa"] > 0 and c["coltura"] != "Nessuna"]
        if not nuove_colture:
            st.error("⚠️ Errore: inserisci almeno una coltura valida con resa > 0")
        else:
            # Aggiungi alla lista delle colture nel terreno selezionato
            terreni_anno[terreno_selezionato]["colture"].extend(nuove_colture)
            st.success(f"✅ {len(nuove_colture)} colture salvate per il terreno '{terreno_selezionato}'")
            st.session_state["colture_form"] = []

# -------------------------------
# 4️⃣ Tabelle standard HI e %C
hi_table = {
    "Mais granella": 0.50,
    "Mais trinciato": 1.00,
    "Frumento": 0.45,
    "Frumento trinciato": 1.00,
    "Orzo": 0.45,
    "Sorgo da granella": 0.50,
    "Sorgo trinciato": 1.00,
    "Avena": 0.45,
    "Erba medica": 1.00,
    "Fieno/erba": 1.00,
    "Soia": 0.40,
    "Girasole": 0.45,
    "Colza": 0.45,
    "Triticale": 0.45
}

c_percent_table = {
    "Mais granella": 0.45,
    "Mais trinciato": 0.45,
    "Frumento": 0.45,
    "Frumento trinciato": 0.45,
    "Orzo": 0.45,
    "Sorgo da granella": 0.45,
    "Sorgo trinciato": 0.45,
    "Avena": 0.45,
    "Erba medica": 0.45,
    "Fieno/erba": 0.40,
    "Soia": 0.45,
    "Girasole": 0.45,
    "Colza": 0.45,
    "Triticale": 0.45
}

# -------------------------------
# 5️⃣ Calcolo SOC/CO2 e Totale per terreno
st.header("4️⃣ Risultati stoccaggio CO₂")
if terreno_selezionato and terreni_anno[terreno_selezionato].get("colture"):
    superficie = terreni_anno[terreno_selezionato]["superficie"]
    delta_soc_tot = 0
    delta_co2_tot = 0
    for c in terreni_anno[terreno_selezionato]["colture"]:
        if c["coltura"] not in hi_table:
            st.warning(f"⚠️ Coltura '{c['coltura']}' non presente in tabella, ignorata.")
            continue
        hi = hi_table[c["coltura"]]
        c_percent = c_percent_table[c["coltura"]]
        biomassa_totale = c["resa"] / hi if hi > 0 else 0
        residui = biomassa_totale - c["resa"]
        c_residui = residui * c_percent
        delta_soc = c_residui  # senza decadimento
        delta_co2 = delta_soc * (44 / 12)
        delta_soc_tot += delta_soc
        delta_co2_tot += delta_co2
        st.write(f"**{c['coltura']}:** ΔSOC={delta_soc:.2f} t C/ha, ΔCO₂={delta_co2:.2f} t CO₂/ha")
    # calcolo totale per il terreno
    totale_CO2_terreno = delta_co2_tot * superficie
    st.write(f"### 🌾 Totale incremento per il terreno ({superficie:.2f} ha): **{totale_CO2_terreno:.2f} t CO₂**")
else:
    st.info("ℹ️ Inserisci colture valide per visualizzare i risultati.")

