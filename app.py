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
    if not nuovo_terreno.strip():
        st.error("Errore: inserisci un nome valido per il terreno.")
    elif nuovo_terreno in st.session_state['terreni']:
        st.warning("Il terreno esiste già!")
    else:
        st.session_state['terreni'][nuovo_terreno] = {"superficie": superficie, "annate": {}}
        st.success(f"Terreno '{nuovo_terreno}' aggiunto.")

# Controlla se ci sono terreni
if st.session_state['terreni']:
    # Menu terreni esistenti
    terreno_selezionato = st.selectbox("Terreno", list(st.session_state['terreni'].keys()))
    annate_terreno = st.session_state['terreni'][terreno_selezionato]["annate"]

    # -------------------------------
    # 2️⃣ Selezione anno
    st.header("2️⃣ Seleziona anno")
    anni_disponibili = list(annate_terreno.keys())
    anno_nuovo = st.number_input("Nuovo anno", min_value=2000, max_value=2100, value=2025, step=1)

    if st.button("Aggiungi anno"):
        if anno_nuovo in annate_terreno:
            st.warning("Anno già presente!")
        else:
            annate_terreno[anno_nuovo] = []
            st.success(f"Anno {anno_nuovo} aggiunto al terreno '{terreno_selezionato}'.")

    # Selezione anno esistente o nuovo
    anni_totali = anni_disponibili + ([anno_nuovo] if anno_nuovo not in anni_disponibili else [])
    if anni_totali:
        anno_selezionato = st.selectbox("Anno da modificare", anni_totali)
        # Assicuriamoci che l’anno esista nel dizionario
        if anno_selezionato not in annate_terreno:
            annate_terreno[anno_selezionato] = []
    else:
        st.info("Aggiungi almeno un anno per continuare.")
        anno_selezionato = None

    # -------------------------------
    # 3️⃣ Inserimento colture per l'anno
    if anno_selezionato is not None:
        st.header(f"3️⃣ Inserisci colture per l'anno {anno_selezionato}")
        coltura = st.selectbox("Coltura", ["Mais granella", "Frumento", "Orzo", "Fieno/erba", "Soia"])
        resa = st.number_input("Resa raccolta (t/ha)", min_value=0.0, max_value=50.0, value=10.0, step=0.1)
        tessitura = st.selectbox("Tessitura del suolo", ["Sabbioso", "Franco sabbioso", "Franco limoso", "Franco argilloso", "Argilloso"])

        if st.button("Aggiungi coltura"):
            if resa <= 0:
                st.error("Errore: la resa deve essere maggiore di zero.")
            else:
                entry = {"coltura": coltura, "resa": resa, "tessitura": tessitura}
                annate_terreno[anno_selezionato].append(entry)
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
        colture_anno = annate_terreno[anno_selezionato]

        if not colture_anno:
            st.info(f"Nessuna coltura inserita per l'anno {anno_selezionato}. Inserisci almeno una coltura.")
        else:
            superficie_terreno = st.session_state['terreni'][terreno_selezionato]["superficie"]
            delta_soc_tot = 0
            delta_co2_tot = 0
            for c in colture_anno:
                if c["resa"] <= 0:
                    st.warning(f"Coltura {c['coltura']} ha resa nulla o negativa. Ignorata nel calcolo.")
                    continue
                hi = hi_table[c["coltura"]]
                c_percent = c_percent_table[c["coltura"]]
                decay = decay_table[c["tessitura"]]
                biomassa_totale = c["resa"] / hi
                residui = biomassa_totale - c["resa"]
                c_residui = residui * c_percent
                delta_soc = c_residui * (1 - decay)
                delta_co2 = delta_soc * (44 / 12)
                delta_soc_tot += delta_soc
                delta_co2_tot += delta_co2
                st.write(f"**{c['coltura']}:** ΔSOC={delta_soc:.2f} t C/ha, ΔCO₂={delta_co2:.2f} t CO₂/ha")
            st.write(f"**Totale incremento per il terreno ({superficie_terreno:.2f} ha):** {delta_co2_tot * superficie_terreno:.2f} t CO₂")
else:
    st.info("Aggiungi prima almeno un terreno per continuare.")
