import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
from folium import plugins

# -------------------------------
# SoilCarbonCalculator v4
# Web app con mappa satellitare e stima da SoilGrids
# -------------------------------

st.set_page_config(page_title="SoilCarbonCalculator v4", page_icon="🌱", layout="wide")
st.title("🌱 SoilCarbonCalculator v4")
st.markdown(
    "Seleziona il tuo campo sulla mappa e inserisci la tessitura del suolo. "
    "I valori di carbonio e densità apparente saranno stimati automaticamente da SoilGrids."
)

# -------------------------------
# Mappa iniziale centrata su Italia
m = folium.Map(location=[42.5, 12.5], zoom_start=6)

# Layer satellitare ESRI
folium.TileLayer('Esri.WorldImagery', name='Satellite').add_to(m)
# Layer di base OpenStreetMap
folium.TileLayer('OpenStreetMap', name='Mappa stradale').add_to(m)

# Abilita controllo layer
folium.LayerControl().add_to(m)

# Strumenti di disegno (poligono)
draw = features.Draw(export=True)
draw.add_to(m)

# Mostra mappa in Streamlit
map_data = st_folium(m, width=800, height=500, returned_objects=["all_drawings", "last_clicked"])

# -------------------------------
# Ottieni coordinate
field_area_ha = 1.0
if map_data:
    # Verifica se l'utente ha disegnato un poligono
    polygons = map_data.get("all_drawings", [])
    if polygons:
        st.success("📍 Poligono del campo selezionato.")
        # calcolo del centroide (per la stima su SoilGrids)
        coords = polygons[0]['geometry']['coordinates'][0]
        lat = sum([pt[1] for pt in coords]) / len(coords)
        lon = sum([pt[0] for pt in coords]) / len(coords)
        # stima area se vuoi calcolare automaticamente
        field_area_ha = polygons[0]['properties'].get('area_ha', 1.0)
    elif map_data.get("last_clicked"):
        # punto singolo
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        st.success(f"📍 Punto selezionato: lat {lat:.5f}, lon {lon:.5f}")
    else:
        lat = lon = None

    if lat and lon:
        st.header("2️⃣ Inserisci la tessitura del suolo")
        tessitura = st.selectbox(
            "Tessitura del suolo",
            ["Sabbioso", "Franco sabbioso", "Franco limoso", "Franco argilloso", "Argilloso"]
        )

        st.header("3️⃣ Inserisci l'area del campo (ha)")
        area = st.number_input("Area (ha)", min_value=0.1, max_value=1000.0, value=field_area_ha, step=0.1)

        # -------------------------------
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
            st.write(f"**Densità apparente stimata:** {bd:.2f} g/cm³")

            # Calcolo stock C e CO2
            depth = 30  # cm
            stock_C = (c_percent / 100) * bd * depth * 10  # t C/ha
            stock_CO2 = stock_C * (44 / 12)  # t CO2eq/ha
            total_CO2 = stock_CO2 * area

            st.divider()
            st.subheader("📊 Risultati")
            st.write(f"**Stock di carbonio (C):** {stock_C:.2f} t C/ha")
            st.write(f"**Stock di CO₂ equivalente:** {stock_CO2:.2f} t CO₂/ha")
            st.write(f"**Totale per l'area:** {total_CO2:.2f} t CO₂")

            st.info("💡 Puoi modificare i valori stimati manualmente se hai dati reali.")
        except Exception as e:
            st.error(f"Errore nel recupero dati SoilGrids: {e}")
else:
    st.info("Clicca sulla mappa o disegna il campo per iniziare.")

st.markdown("---")
st.caption("Versione 4.0 - Mappa satellitare ESRI, disegno del campo, stima automatica da SoilGrids, tessitura inserita manualmente.")
