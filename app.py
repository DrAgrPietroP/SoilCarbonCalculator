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
# 2️⃣ Selezione terreno
st.header("2️⃣ Seleziona o aggiungi terreno")
terreni_anno = st.session_state["annate"][anno_selezionato]
nuovo_terreno = st.text_input("Nome nuovo terreno")
col1, col2 = st.columns([0.1, 0.9])
with col1:
    aggiungi_terreno = st.button("+")

if aggiungi_terreno:
    if not nuovo_terreno.strip():
        st.error("Errore: inserisci un nome valido per il terreno.")
    elif nuovo_terreno in terreni_anno:
        st.warning("⚠️ Il terreno esiste già!")
    else:
        terreni_anno[nuovo_terreno] = []
        st.success(f"✅ Terreno '{nuovo_terreno}' aggiunto.")

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
        nuove_colture = [c for c in st.session_state["colture_form"] if c["resa"] > 0 and c["coltura"] != "Nessuna"]
        if not nuove_colture:
            st.error("⚠️ Errore: inserisci almeno una coltura valida con resa > 0")
        else:
            terreni_anno[terreno_selezionato].extend(nuove_colture)
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
# 5️⃣ Calcolo SOC/CO2
st.header("4️⃣ Risultati stoccaggio CO₂")
if terreno_selezionato and terreni_anno[terreno_selezionato]:
    delta_soc_tot = 0
    delta_co2_tot = 0
    for c in terreni_anno[terreno_selezionato]:
        if c["coltura"] not in hi_table:
            st.warning(f"⚠️ Coltura '{c['coltura']}' non presente in tabella, saltata.")
            continue
        hi = hi_table[c["coltura"]]
        c_percent = c_percent_table[c["coltura"]]
        biomassa_totale = c["resa"] / hi if hi > 0 else 0
        residui = biomassa_totale - c["resa"]
        c_residui = residui * c_percent
        delta_soc = c_residui  # senza decay
        delta_co2 = delta_soc * (44 / 12)
        delta_soc_tot += delta_soc
        delta_co2_tot += delta_co2
        st.write(f"**{c['coltura']}:** ΔSOC={delta_soc:.2f} t C/ha, ΔCO₂={delta_co2:.2f} t CO₂/ha")
    st.write(f"### 🌾 Totale incremento per il terreno: **{delta_co2_tot:.2f} t CO₂/ha**")
else:
    st.info("ℹ️ Inserisci almeno una coltura per visualizzare i risultati.")

