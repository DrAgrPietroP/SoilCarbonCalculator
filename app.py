# app.py
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="SoilCarbonCalculator - Tier2", page_icon="🌱", layout="wide")
st.title("🌱 SoilCarbonCalculator - Tier-2: Stoccaggio annuo di carbonio (ΔSOC)")

# -------------------------------
# Inizializzazione session_state
if "annate" not in st.session_state:
    st.session_state["annate"] = {}  # struttura: {anno: {terreno_name: {"superficie": x, "colture": [..]}}}

if "colture_form" not in st.session_state:
    st.session_state["colture_form"] = []

if "settings" not in st.session_state:
    # parametri modificabili dall'utente (defaults ragionevoli)
    st.session_state["settings"] = {
        "f_C_default": 0.45,        # frazione C residui
        "h_res_default": 0.20,     # humification residui
        "h_man_default": 0.35,     # humification letame/compost
        "decay_extra": 0.0         # perdita extra (t C/ha) opzionale
    }

# -------------------------------
# Funzioni ausiliarie
def reset_colture_form():
    st.session_state["colture_form"] = [
        {"coltura": "Nessuna", "resa": 0.0, "retention_pct": 100.0, "tillage": "Convenzionale", "manure_t_ha": 0.0, "manure_c_pct": 0.25},
        {"coltura": "Nessuna", "resa": 0.0, "retention_pct": 100.0, "tillage": "Convenzionale", "manure_t_ha": 0.0, "manure_c_pct": 0.25}
    ]

def tillage_multiplier(till_type):
    # fattore di aggiustamento humification in base al tipo di lavorazione
    mapping = {
        "No-till": 1.10,
        "Minima lavorazione": 1.05,
        "Convenzionale": 1.00
    }
    return mapping.get(till_type, 1.0)

# -------------------------------
# 0) Tabelle HI e %C (ampliate)
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

colture_disponibili = ["Nessuna"] + list(hi_table.keys())

# -------------------------------
# 1️⃣ SEZIONE: anno (1950 - current)
st.header("1️⃣ Seleziona anno")
anno_corrente = datetime.now().year
anni_possibili = list(range(1950, anno_corrente + 1))
anno_selezionato = st.selectbox("Anno", anni_possibili, index=len(anni_possibili) - 1)

# assicurati struttura per anno
if anno_selezionato not in st.session_state["annate"]:
    st.session_state["annate"][anno_selezionato] = {}

# -------------------------------
# 2️⃣ SEZIONE: terreni (nome + superficie) - per anno
st.header("2️⃣ Seleziona o aggiungi terreno")
terreni_anno = st.session_state["annate"][anno_selezionato]  # dict: nome -> {"superficie": x, "colture":[..]}

nuovo_terreno = st.text_input("Nome nuovo terreno (inserisci nome e poi premi +)")
superficie_input = st.number_input("Superficie del terreno (ha)", min_value=0.1, max_value=10000.0, value=1.0, step=0.1)

col1, col2 = st.columns([0.08, 0.92])
with col1:
    btn_add_terreno = st.button("+", key="add_terreno")

if btn_add_terreno:
    if not nuovo_terreno.strip():
        st.error("Errore: inserisci un nome valido per il terreno.")
    elif nuovo_terreno in terreni_anno:
        st.warning("Il terreno esiste già per questo anno.")
    else:
        terreni_anno[nuovo_terreno] = {"superficie": superficie_input, "colture": []}
        st.success(f"Terreno '{nuovo_terreno}' aggiunto per anno {anno_selezionato} con superficie {superficie_input:.2f} ha.")

terreno_selezionato = None
if terreni_anno:
    terreno_selezionato = st.selectbox("Terreno", list(terreni_anno.keys()))
else:
    st.info("Nessun terreno per questo anno. Aggiungi un nuovo terreno.")

# -------------------------------
# 3️⃣ SEZIONE: inserimento colture (2 righe iniziali + aggiungi)
if terreno_selezionato:
    st.header(f"3️⃣ Inserisci colture per terreno: {terreno_selezionato} (anno {anno_selezionato})")

    # inizializza form con 2 righe se vuota
    if not st.session_state["colture_form"]:
        reset_colture_form()

    # mostra i campi per ogni riga (dinamico)
    for i, entry in enumerate(st.session_state["colture_form"]):
        st.subheader(f"Coltura {i+1}")
        # select coltura
        entry["coltura"] = st.selectbox(
            f"Seleziona coltura {i+1}",
            colture_disponibili,
            index=colture_disponibili.index(entry["coltura"]) if entry["coltura"] in colture_disponibili else 0,
            key=f"colt_{i}"
        )
        # resa
        entry["resa"] = st.number_input(
            f"Resa raccolta (t/ha) {i+1}",
            min_value=0.0,
            max_value=100.0,
            value=entry.get("resa", 0.0),
            step=0.1,
            key=f"resa_{i}"
        )
        # retention residui (%)
        entry["retention_pct"] = st.slider(
            f"% residui lasciati {i+1}",
            min_value=0.0,
            max_value=100.0,
            value=int(entry.get("retention_pct", 100.0)),
            step=5,
            key=f"ret_{i}"
        )
        # tillage
        entry["tillage"] = st.selectbox(
            f"Tipo lavorazione {i+1}",
            ["Convenzionale", "Minima lavorazione", "No-till"],
            index=["Convenzionale", "Minima lavorazione", "No-till"].index(entry.get("tillage", "Convenzionale")),
            key=f"till_{i}"
        )
        # apporto organico opzionale
        entry["manure_t_ha"] = st.number_input(
            f"Letame/compost (t/ha) {i+1} - opzionale",
            min_value=0.0,
            max_value=100.0,
            value=entry.get("manure_t_ha", 0.0),
            step=0.1,
            key=f"man_{i}"
        )
        entry["manure_c_pct"] = st.number_input(
            f"%C nel letame/compost {i+1} (es. 0.25 = 25%)",
            min_value=0.0,
            max_value=1.0,
            value=entry.get("manure_c_pct", 0.25),
            step=0.01,
            key=f"man_c_{i}"
        )
        st.markdown("---")

    # aggiungi nuova riga coltura
    if st.button("Aggiungi altra coltura", key="add_col_row"):
        st.session_state["colture_form"].append(
            {"coltura": "Nessuna", "resa": 0.0, "retention_pct": 100.0, "tillage": "Convenzionale", "manure_t_ha": 0.0, "manure_c_pct": 0.25}
        )

    # salva le righe nella lista colture del terreno
    if st.button("Salva colture nel terreno", key="save_colture"):
        # filtra righe valide
        nuove = []
        for c in st.session_state["colture_form"]:
            if c["coltura"] != "Nessuna" and c["resa"] > 0:
                nuove.append(c.copy())
        if not nuove:
            st.error("Errore: inserisci almeno una coltura valida con resa > 0 e coltura selezionata.")
        else:
            terreni_anno[terreno_selezionato]["colture"].extend(nuove)
            st.success(f"{len(nuove)} colture salvate per terreno '{terreno_selezionato}'.")
            # reset form a 2 righe vuote
            reset_colture_form()

    # mostra elenco colture già presenti per il terreno (con possibilità di cancellare)
    st.subheader("Colture già registrate per questo terreno")
    existing = terreni_anno[terreno_selezionato]["colture"]
    if existing:
        for idx, c in enumerate(existing):
            st.write(f"{idx+1}. {c['coltura']} — resa {c['resa']:.2f} t/ha — residui% {c.get('retention_pct',100):.0f} — till: {c.get('tillage','Convenzionale')} — letame {c.get('manure_t_ha',0):.2f} t/ha")
        # option to remove last / specific
        if st.button("Rimuovi ultima coltura", key="remove_last"):
            removed = existing.pop()
            st.warning(f"Rimossa: {removed['coltura']}, resa {removed['resa']:.2f} t/ha")
    else:
        st.info("Nessuna coltura salvata ancora per questo terreno.")

# -------------------------------
# 4️⃣ SETTINGS (opzionale pannello espandibile)
with st.expander("Impostazioni avanzate (parametri di default)"):
    s = st.session_state["settings"]
    s["f_C_default"] = st.number_input("Frazione C residui (f_C) - default", min_value=0.0, max_value=1.0, value=float(s["f_C_default"]), step=0.01)
    s["h_res_default"] = st.number_input("Humification residui (h_res) - default", min_value=0.0, max_value=1.0, value=float(s["h_res_default"]), step=0.01)
    s["h_man_default"] = st.number_input("Humification letame/compost (h_man) - default", min_value=0.0, max_value=1.0, value=float(s["h_man_default"]), step=0.01)
    s["decay_extra"] = st.number_input("Perdita extra annua (t C/ha) - opzionale", min_value=0.0, max_value=10.0, value=float(s["decay_extra"]), step=0.01)

# -------------------------------
# 5️⃣ CALCOLO ΔSOC e ΔCO2 (per terreno)
st.header("4️⃣ Risultati: ΔSOC e ΔCO₂")

if terreno_selezionato and terreni_anno.get(terreno_selezionato) and terreni_anno[terreno_selezionato].get("colture"):
    superficie = terreni_anno[terreno_selezionato]["superficie"]
    totale_delta_soc_per_ha = 0.0
    totale_delta_co2_per_ha = 0.0

    for c in terreni_anno[terreno_selezionato]["colture"]:
        nome = c["coltura"]
        resa = c["resa"]
        if nome not in hi_table or resa <= 0:
            st.warning(f"Ignorata coltura non valida o resa nulla: {nome} (resa={resa})")
            continue

        # parametri
        hi = hi_table[nome]
        f_C = c_percent_table.get(nome, st.session_state["settings"]["f_C_default"])
        retention = c.get("retention_pct", 100.0) / 100.0
        till = c.get("tillage", "Convenzionale")
        man_t = c.get("manure_t_ha", 0.0)
        man_c_pct = c.get("manure_c_pct", 0.25)

        # calcoli
        biomassa_totale = resa / hi if hi > 0 else 0.0
        residui_t_ha = max(0.0, biomassa_totale - resa)
        c_residui = residui_t_ha * f_C * retention

        # humification adjusted by tillage
        h_res = st.session_state["settings"]["h_res_default"] * tillage_multiplier(till)
        c_hum = c_residui * h_res

        # contributo letame/compost
        c_man = man_t * man_c_pct * st.session_state["settings"]["h_man_default"]

        # eventuale perdita extra (distribuita proporzionalmente per coltura)
        decay_extra = st.session_state["settings"]["decay_extra"]

        # delta SOC per ha (t C/ha)
        delta_soc = c_hum + c_man - decay_extra * 0  # decay_extra può essere distribuito globalmente se si vuole; per ora non sottraiamo a singola coltura

        # per chiarezza NON forziamo delta_soc < 0 qui; l'utente può vedere eventuali valori negativi
        delta_co2 = delta_soc * (44.0 / 12.0)

        totale_delta_soc_per_ha += delta_soc
        totale_delta_co2_per_ha += delta_co2

        st.write(f"**{nome}:** residui {residui_t_ha:.2f} t/ha → C_res {c_residui:.3f} t C/ha; C_hum {c_hum:.3f} t C/ha; C_man {c_man:.3f} t C/ha; ΔSOC={delta_soc:.3f} t C/ha; ΔCO₂={delta_co2:.3f} t CO₂/ha")

    # totale per ha e per superficie
    totale_CO2_ha = totale_delta_co2_per_ha
    totale_CO2_terreno = totale_CO2_ha * superficie

    st.markdown("----")
    st.write(f"### 🔢 Totale stimato per ettaro: **{totale_CO2_ha:.3f} t CO₂/ha**")
    st.write(f"### 🌾 Totale stimato per il terreno ({superficie:.2f} ha): **{totale_CO2_terreno:.3f} t CO₂**")
    st.info("Nota: i parametri (f_C, h_res, h_man, decay_extra) sono modificabili nell'area impostazioni avanzate.")
else:
    st.info("Inserisci almeno una coltura valida per il terreno selezionato per visualizzare i risultati.")
