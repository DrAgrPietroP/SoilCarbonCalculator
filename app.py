import streamlit as st

# -------------------------------
# SoilCarbonCalculator v1.0
# Calcolo dello stoccaggio di carbonio nel suolo
# Autore: DrAgrPietroP
# -------------------------------

st.set_page_config(page_title="Soil Carbon Calculator", page_icon="🌱", layout="centered")

st.title("🌱 Soil Carbon Calculator")
st.markdown("Calcola lo stoccaggio di **carbonio organico (C)** e la sua equivalenza in **CO₂** nel suolo agricolo.")

st.divider()

st.header("🔹 Inserisci i dati del campo")

col1, col2 = st.columns(2)
with col1:
    c_percent = st.number_input("Carbonio organico (%)", min_value=0.0, max_value=20.0, value=1.2, step=0.1)
    bulk_density = st.number_input("Densità apparente (g/cm³)", min_value=0.5, max_value=2.0, value=1.3, step=0.1)
with col2:
    depth = st.number_input("Profondità considerata (cm)", min_value=1, max_value=100, value=30, step=1)
    area = st.number_input("Area del campo (ha)", min_value=0.1, max_value=1000.0, value=1.0, step=0.1)

st.divider()

if st.button("Calcola lo stoccaggio di carbonio"):
    # Calcolo dello stock di carbonio e CO2
    stock_C = (c_percent / 100) * bulk_density * depth * 10  # t C/ha
    stock_CO2 = stock_C * (44 / 12)  # t CO2eq/ha
    total_CO2 = stock_CO2 * area

    st.success("✅ Calcolo completato!")
    st.subheader("Risultati")
    st.write(f"**Stock di carbonio (C):** {stock_C:.2f} t C/ha")
    st.write(f"**Stock di CO₂ equivalente:** {stock_CO2:.2f} t CO₂/ha")
    st.write(f"**Totale per l'area:** {total_CO2:.2f} t CO₂")
    
    st.markdown("---")
    st.caption("Formula IPCC semplificata: Stock = (C%/100) × Densità × Profondità × 10 × (44/12)")

st.markdown("---")
st.info("💡 Puoi modificare i parametri e ricalcolare. Tutti i valori sono riferiti a suoli minerali senza scheletro grossolano.")
