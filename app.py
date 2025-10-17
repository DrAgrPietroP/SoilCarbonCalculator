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

# -------------------------------
# Controlla se ci sono terreni
if st.session_state['terreni']:
    # Menu terreni esistenti
    terreno_selezionato = st.selectbox("Terreno", list(st.session_state['terreni'].keys()))
    
    # -------------------------------
    # 2️⃣ Selezione anno
    st.header("2️⃣ Seleziona anno")
    annate_terreno = st.session_state['terreni'][terreno_selezionato]["annate"]
    anni_disponibili = list(annate_terreno.keys())
    
    anno_nuovo = st.number_input("Nuovo anno", min_value=2000, max_value=2100, value=2025, step=1)

    if st.button("Aggiungi anno"):
        if anno_nuovo in annate_terreno:
            st.warning("Anno già presente!")
        else:
            annate_terreno[anno_nuovo] = []
            st.success(f"Anno {anno_nuovo} aggiunto al terreno '{terreno_selezionato}'.")

    # Selezione anno esistente o nuovo
    if anni_disponibili:
        anno_selezionato = st.selectbox("Anno da modificare", anni_disponibili)
    else:
        anno_selezionato = anno_nuovo

    # -------------------------------
    # 3️⃣ Inserimento colture per l'anno
    st.header(f"3️⃣ Inserisci colture per l'anno {anno_selezionato}")

    coltura = st.selectbox("Coltura", ["Mais granella", "Frumento", "Orzo", "Fieno/erba", "Soia"])
    resa = st.number_input("Resa raccolta (t/ha)", min_value=0.1, max_value=50.0, value=10.0, step=0.1)
    tessitura = st.selectbox("Tessitura del suolo", ["Sabbioso", "Franco sabbioso", "Franco limoso", "Franco argilloso", "Argilloso"])

    if st.button("Aggiungi coltura"):
        entry = {"coltura": coltura, "resa": resa, "tessitura": tessitura}
        st.session_state['terreni'][terreno_selezionato]["annate"][anno_selezionato].append(entry)
        st.success(f"Coltura '{coltura}' aggiunta all'anno {anno_selezionato}.")

    # -------------------------------
    # 4️⃣ Tabelle standard HI e %C
    hi_table = {
        "Mais granella": 0.50,
        "Frumento": 0.45,
        "Orzo": 0.45,
        "Fieno/erba": 0.50,
        "Soia": 0.40
    }

    c_percent_table = {
        "Mais granella": 0.45,
        "Frumento": 0.45,
        "Orzo": 0.45,
        "Fieno/erba": 0.40,
        "Soia": 0.45
    }

    decay_table = {
        "Sabbioso": 0.30,
        "Franco sabbioso": 0.25,
        "Franco limoso": 0.20,
        "Franco argilloso": 0.15,
        "Argilloso": 0.10
    }

    # -------------------------------
    # 5️⃣ Calcolo incrementi SOC e CO2 per anno
    st.header(f"4️⃣ Risultati stoccaggio annuo per {anno_selezionato}")
    colture_anno = st.session_state['terreni'][terreno_selezionato]["annate"][anno_selezionato]
    if colture_anno:
        superficie_terreno = st.session_state['terreni'][terreno_selezionato]["superficie"]
        delta_soc_tot = 0
        delta_co2_tot = 0
        for c in colture_anno:
            hi = hi_table[c["coltura"]]
            c_percent = c_percent_table[c["coltura"]]
            decay = decay_table[c["tessitura"]]
            biomassa_totale = c["resa"] / hi
            residui = biomassa_totale - c["resa"]
            c_residui = residui * c_percent
            delta_soc = c_residui * (1 - decay)
            delta_co2 = delta_soc * (44/12)
            delta_soc_tot += delta_soc
            delta_co2_tot += delta_co2
            st.write(f"**{c['coltura']}:** ΔSOC={delta_soc:.2f} t C/ha, ΔCO₂={delta_co2:.2f} t CO₂/ha")
        st.write(f"**Totale incremento per il terreno ({superficie_terreno:.2f} ha):** {delta_co2_tot*superficie_terreno:.2f} t CO₂")
    else:
        st.info("Nessuna coltura inserita per questo anno.")
else:
    st.info("Aggiungi prima almeno un terreno per continuare.")
