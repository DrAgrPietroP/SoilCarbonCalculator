import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
from folium.raster_layers import ImageOverlay

# Impostazioni della pagina
st.set_page_config(page_title="SoilCarbonCalculator v4", page_icon="🌱", layout="wide")
st.title("🌱 SoilCarbonCalculator v4")
st.markdown("Seleziona il tuo campo sulla mappa e inserisci la tessitura del suolo. I valori di carbonio e densità apparente saranno stimati automaticamente da SoilGrids.")

# Mappa iniziale centrata su Italia
m = folium.Map(location=[42.5, 12.5], zoom_start=6)

# Aggiunta di un layer di immagini satellitari (esempio con un'immagine fittizia)
satellite_image_url = "https://example.com/satellite_image.png"  # Sostituisci con l'URL dell'immagine
image_bounds = [[42.3, 12.3], [42.7, 12.7]]  # Coordinate angolo inferiore sinistro e angolo superiore destro
ImageOverlay(image_url=satellite_image_url, bounds=image_bounds, opacity=0.6).add_to(m)

# Layer vuoto (utente può cliccare)
folium.Marker([42.5, 12.5], tooltip="Clicca per il centro del campo").add_to(m)

# Mostra mappa in Streamlit
map_data = st_folium(m, width=700, height=500)

# Ottieni coordinate (primo punto cliccato)
if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.success(f"📍 Coordinate selezionate: lat {lat:.5f}, lon {lon:.5f}")

    st.header("2️⃣ Inserisci la tessitura del suolo")
    tessitura = st.selectbox(
        "Tessitura del suolo",
        ["Sabbioso", "Franco sabbioso", "Franco limoso", "Franco argilloso", "Argilloso"]
    )

    st.header("3️⃣ Inserisci l'area del campo (ha)")
    area = st.number_input("Area (ha)", min_value=0.1, max_value=1000.0, value=1.0, step=0.1)

    # Richiesta dati da SoilGrids
    try:
        url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=ocd&property=bdod&depth=0-30cm"
        response = requests.get(url)
        data = response.json()

        # Carbonio organico (%)
        c_percent = data["properties"]["ocd"]["depths"][0]["values"]["mean"]
        # Bulk density (g/cm³)
        bd = data["properties"]["bdod"]["depths"][0]["values"]["mean"]

        st.subheader("Valori stimati automaticamente da SoilGrids (0-30 cm)")
        st.write(f"**Carbonio organico stimato:** {c_percent:.2f} %")
        st.w
