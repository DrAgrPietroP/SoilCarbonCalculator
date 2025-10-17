import streamlit as st

# -------------------------------
# SoilCarbonCalculator Annual ΔSOC
# -------------------------------

st.set_page_config(page_title="SoilCarbonCalculator ΔSOC", page_icon="🌱", layout="wide")
st.title("🌱 SoilCarbonCalculator - Stoccaggio annuo di carbonio")

st.markdown(
    "Inserisci la coltura, la resa raccolta, la tessitura del suolo e l'area del campo. "
    "L'app calcolerà automaticamente l'incremento annuo di carbonio e CO₂."
)

# -------------------------------
# Input utente
st.header("1️⃣ Inserisci i dati agronomici")
coltura = st.selectbox("Coltura", ["Mais granella", "Frumento", "Orzo", "Fieno/erba", "Soia"])
resa = st.number_input("Resa raccolta (t/ha)", min_value=0.1, max_value=50.0, value=10.0, step=0.1)
tessitura = st.selectbox("Tessitura del suolo", ["Sabbioso", "Franco sabbioso", "Franco limoso", "Franco argilloso", "Argilloso"])
area = st.number_input("Area del campo (ha)", min_value=0.1, max_value=1000.0, value=1.0, step=0.1)

# -------------------------------
# Tabelle standard HI e %C
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

# Frazione decomposta subito in base alla tessitura
decay_table = {
    "Sabbioso": 0.30,
    "Franco sabbioso": 0.25,
    "Franco limoso": 0.20,
    "Franco argilloso": 0.15,
    "Argilloso": 0.10
}

# -------------------------------
# Calcolo biomassa totale e residui
hi = hi_table[coltura]
c_percent = c_percent_table[coltura]
decay = decay_table[tessitura]

biomassa_totale = resa / hi  # t/ha
residui = biomassa_totale - resa
c_residui = residui * c_percent
delta_soc = c_residui * (1 - decay)
delta_co2 = delta_soc * (44 / 12)
total_co2 = delta_co2 * area

# -------------------------------
# Risultati
st.header("2️⃣ Risultati")
st.write(f"**Biomassa totale stimata:** {biomassa_totale:.2f} t/ha")
st.write(f"**Residui lasciati nel terreno:** {residui:.2f} t/ha")
st.write(f"**Carbonio nei residui:** {c_residui:.2f} t C/ha")
st.write(f"**Incremento annuo stimato SOC:** {delta_soc:.2f} t C/ha")
st.write(f"**Incremento annuo stimato CO₂:** {delta_co2:.2f} t CO₂/ha")
st.write(f"**Incremento annuo totale per l'area:** {total_co2:.2f} t CO₂")
