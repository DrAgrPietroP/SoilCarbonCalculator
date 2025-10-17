# 🌱 SoilCarbonCalculator

Una semplice web app per calcolare lo **stoccaggio di carbonio nel suolo agricolo** secondo la formula IPCC di base.

---

## ⚙️ Funzionalità
- Inserimento di:  
  - % Carbonio organico  
  - Densità apparente del suolo (g/cm³)  
  - Profondità (cm)  
  - Area (ha)
- Calcolo automatico di:
  - Stock di C (t/ha)
  - Stock di CO₂ equivalente (t CO₂/ha)
  - Totale per l’area (t CO₂)

---

## 🧮 Formula IPCC semplificata
\[
\text{Stock C (t/ha)} = \frac{C\%}{100} × \text{BD} × \text{Profondità (cm)} × 10
\]
\[
\text{Stock CO₂ (t/ha)} = \text{Stock C} × \frac{44}{12}
\]

---

## 🚀 Come pubblicare l'app
1. Vai su [https://github.com/new](https://github.com/new)
2. Crea un nuovo repository chiamato **SoilCarbonCalculator**
3. Carica in esso i file:
   - `app.py`
   - `requirements.txt`
   - `README.md`
4. Vai su [https://share.streamlit.io](https://share.streamlit.io)
5. Accedi con il tuo account GitHub
6. Seleziona il repository `SoilCarbonCalculator`
7. Clicca **Deploy**

Dopo circa 1 minuto la tua app sarà online (esempio:  
`https://soilcarboncalculator.streamlit.app`)

---

## 👨‍🌾 Autore
**Dr. Agr. Pietro P.**  
Progetto open-source per la stima del carbonio nel suolo agricolo.
