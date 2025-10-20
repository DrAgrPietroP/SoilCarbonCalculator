# app.py
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="SoilCarbonCalculator - Tier2", page_icon="🌱", layout="wide")

# -------------------------------
# STILE PERSONALIZZATO
st.markdown("""
<style>
h1, h2, h3, h4, h5 {font-family: 'Arial';}
section[data-testid="stSidebar"] div {font-size: 0.9rem;}
div[data-testid="stMarkdownContainer"] p {font-size: 0.9rem;}
.stNumberInput label, .stSelectbox label, .stSlider label {font-size: 0.9rem;}
.stButton button {font-size: 0.9rem; padding: 0.3rem 0.8rem;}
.result-box {
    background-color: #f0fdf7;
    border: 2px solid #0a662a;
    padding: 15px;
    border-radius: 10px;
    margin-top: 20px;
}
.result-title {
    font-size: 1.4rem;
    color: #0a662a;
    font-weight: bold;
    margin-bottom: 0.4rem;
}
.result-sub {
    font-size: 1.1rem;
    color: #333;
}
</style>
""", unsafe_allow_html=True)

st.title("🌱 SoilCarbonCalculator - Tier-2")
st.caption("Versione con residui tabellari e calcolo automatico")

# -------------------------------
# INIZIALIZZAZIONE
if "annate" not in st.session_state:
    st.session_state["annate"] = {}
if "colture_form" not in st.session_state:
    st.session_state["colture_form"] = []
if "settings" not in st.session_state:
    st.session_state["settings"] = {
        "f_C_default": 0.45,
        "h_res_default": 0.20,
        "h_man_default": 0.35
    }

# -------------------------------
# FUNZIONI
def reset_colture_form():
    st.session_state["colture_form"] = [
        {"coltura": "Nessuna", "resa": 0.0, "tillage": "Convenzionale", "manure_t_ha": 0.0, "manure_c_pct": 0.25},
        {"coltura": "Nessuna", "resa": 0.0, "tillage": "Convenzionale", "manure_t_ha": 0.0, "manure_c_pct": 0.25}
    ]

def tillage_multiplier(till_type):
    mapping = {"No-till": 1.10, "Minima lavorazione": 1.05, "Convenzionale": 1.00}
    return mapping.get(till_type, 1.0)

# Tabelle HI, frazione C e residui lasciati
hi_table = {
    "Mais granella": 0.50, "Mais trinciato": 1.00, "Frumento": 0.45,
    "Frumento trinciato": 1.00, "Orzo": 0.45, "Sorgo da granella": 0.50,
    "Sorgo trinciato": 1.00, "Avena": 0.45, "Erba medica": 1.00,
    "Fieno/erba": 1.00, "Soia": 0.40, "Girasole": 0.45,
    "Colza": 0.45, "Triticale": 0.45
}
c_percent_table = {k: 0.45 for k in hi_table}
c_percent_table["Fieno/erba"] = 0.40

residui_tabellari = {
    "Mais granella": 0.50, "Mais trinciato": 1.00, "Frumento": 0.40,
    "Frumento trinciato": 1.00, "Orzo": 0.40, "Sorgo da granella": 0.50,
    "Sorgo trinciato": 1.00, "Avena": 0.40, "Erba medica": 1.00,
    "Fieno/erba": 1.00, "Soia": 0.40, "Girasole": 0.45,
    "Colza": 0.45, "Triticale": 0.45
}

colture_disponibili = ["Nessuna"] + list(hi_table.keys())

# -------------------------------
# INTERFACCIA PRINCIPALE
col_input, col_output = st.columns([1.2, 1])

with col_input:
    st.subheader("1️⃣ Seleziona anno e terreno")

    anni_possibili = list(range(1950, datetime.now().year + 1))
    anno_selezionato = st.selectbox("Anno", anni_possibili, index=len(anni_possibili)-1)

    if anno_selezionato not in st.session_state["annate"]:
        st.session_state["annate"][anno_selezionato] = {}

    terreni_anno = st.session_state["annate"][anno_selezionato]

    nuovo_terreno = st.text_input("Nome nuovo terreno")
    superficie_input = st.number_input("Superficie (ha)", 0.1, 10000.0, 1.0, 0.1)
    if st.button("+ Aggiungi terreno"):
        if not nuovo_terreno.strip():
            st.error("Inserisci un nome valido per il terreno.")
        elif nuovo_terreno in terreni_anno:
            st.warning("Il terreno esiste già.")
        else:
            terreni_anno[nuovo_terreno] = {"superficie": superficie_input, "colture": []}
            st.success(f"Aggiunto '{nuovo_terreno}' ({superficie_input:.2f} ha)")

    terreno_selezionato = st.selectbox("Terreno", list(terreni_anno.keys())) if terreni_anno else None

    if terreno_selezionato:
        st.divider()
        st.subheader("2️⃣ Colture annuali")

        if not st.session_state["colture_form"]:
            reset_colture_form()

        for i, entry in enumerate(st.session_state["colture_form"]):
            st.markdown(f"**Coltura {i+1}**")
            entry["coltura"] = st.selectbox(f"Tipo coltura {i+1}", colture_disponibili, key=f"colt_{i}")
            entry["resa"] = st.number_input(f"Resa (t/ha) {i+1}", 0.0, 100.0, entry.get("resa", 0.0), step=0.1, key=f"resa_{i}")
            entry["tillage"] = st.selectbox(f"Lavorazione {i+1}", ["Convenzionale", "Minima lavorazione", "No-till"], key=f"till_{i}")
            entry["manure_t_ha"] = st.number_input(f"Letame/compost (t/ha) {i+1}", 0.0, 100.0, entry.get("manure_t_ha", 0.0), step=0.1, key=f"man_{i}")
            st.markdown("---")

        if st.button("➕ Aggiungi altra coltura"):
            st.session_state["colture_form"].append(
                {"coltura": "Nessuna", "resa": 0.0, "tillage": "Convenzionale", "manure_t_ha": 0.0, "manure_c_pct": 0.25}
            )

        if st.button("💾 Salva colture"):
            nuove = [c.copy() for c in st.session_state["colture_form"] if c["coltura"] != "Nessuna" and c["resa"] > 0]
            if nuove:
                terreni_anno[terreno_selezionato]["colture"].extend(nuove)
                st.success(f"{len(nuove)} colture salvate per '{terreno_selezionato}'.")
                reset_colture_form()
            else:
                st.warning("Inserisci almeno una coltura valida.")

with col_output:
    st.subheader("📊 Riepilogo terreni e CO₂")

    risultati = []
    totale_CO2_azienda = 0.0
    totale_ha = 0.0

    for terreno, dati in terreni_anno.items():
        if not dati["colture"]:
            continue

        superficie = dati["superficie"]
        totale_delta_co2_per_ha = 0.0

        for c in dati["colture"]:
            nome = c["coltura"]
            resa = c["resa"]
            if nome not in hi_table or resa <= 0:
                continue
            hi = hi_table[nome]
            f_C = c_percent_table.get(nome, st.session_state["settings"]["f_C_default"])
            retention = residui_tabellari.get(nome, 1.0)
            till = c["tillage"]
            man_t = c["manure_t_ha"]
            man_c_pct = c.get("manure_c_pct", 0.25)

            residui_t_ha = resa * ((1 - hi)/hi) * retention
            c_residui = residui_t_ha * f_C
            h_res = st.session_state["settings"]["h_res_default"] * tillage_multiplier(till)
            c_hum = c_residui * h_res
            c_man = man_t * man_c_pct * st.session_state["settings"]["h_man_default"]

            delta_soc = c_hum + c_man
            delta_co2 = delta_soc * (44.0 / 12.0)

            totale_delta_co2_per_ha += delta_co2

        totale_CO2_ha = totale_delta_co2_per_ha
        totale_CO2_terreno = totale_CO2_ha * superficie

        risultati.append({
            "Terreno": terreno,
            "Superficie (ha)": superficie,
            "ΔCO₂ (t/ha)": round(totale_CO2_ha, 3),
            "Totale CO₂ (t)": round(totale_CO2_terreno, 3)
        })

        totale_CO2_azienda += totale_CO2_terreno
        totale_ha += superficie

    if risultati:
        df = pd.DataFrame(risultati)
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.markdown(f"""
        <div class="result-box">
            <p class="result-title">Totale aziendale CO₂ stoccata</p>
            <p class="result-sub">Superficie totale: <b>{totale_ha:.2f} ha</b></p>
            <p class="result-sub">Totale CO₂: <b>{totale_CO2_azienda:.3f} t</b></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Inserisci almeno una coltura salvata per visualizzare la tabella dei risultati.")

