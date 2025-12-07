# Environmental Risk Around US Data Centers 

An interactive web application that visualizes the environmental impact of data centers across the United States.

The app combines **air quality**, **water footprint**, **power consumption**, and **carbon emissions** with **data center locations** to help users explore how digital infrastructure interacts with local environmental conditions. :contentReference[oaicite:0]{index=0}


## 🚀 Features

### 🌫️ Air Quality Layer (Air)
- Visualizes **Air Quality Index (AQI)** conditions across the United States using monitored pollutants:
  - Ozone  
  - PM2.5  
  - Combined “Ozone and PM2.5”
- **Two viewing modes**:
  - **Plot by Facility** – individual monitoring stations as colored points.
  - **Plot by State Average** – each state filled with its average AQI for quick regional comparison.
- **Interactions**:
  - Hover hotspots to see AQI values.
  - Use the **Monitor Layer** panel to switch between Ozone + PM2.5, Ozone only, and PM2.5 only.
  - Zoom and pan to inspect pollution around specific data centers.


### 💧 Water Footprint Layer (Water)
- Shows **water footprint (m³/MWh)** associated with the electricity and cooling requirements of data centers.
- Marker **color and size** represent the intensity of water usage.
- **View options (top-right filters)**:
  - **State** – focus on all states (default) or a selected state.
  - **Fuel** – filter by electricity source (e.g., natural gas, coal, hydro, solar).
  - **PCA** – group impacts by power control areas (regional electricity supply zones).
  - **Plot by Facility** – individual facilities sized/colored by impact.
  - **Plot by State Average** – states colored by average water footprint.
- **More Insights panel**:
  - **Best vs Worst Water Projections** – how future footprint changes under efficient vs inefficient practices.
  - **Fuel Type Breakdown** – which electricity sources drive the highest water consumption.


### ⚡ Power Consumption Layer (Power)
- Visualizes **total electricity consumption (MWh)** by power facilities feeding data centers.
- Color and circle size indicate magnitude of power usage.
- **View options** (same control scheme as Water):
  - State / Fuel / PCA filters.
  - Plot by Facility vs Plot by State Average.
- **Tooltips** on hover show:
  - Power consumption (MWh)
  - Primary fuel type
  - Regional sub-basin supplying electricity.


### 🌍 CO₂ Emissions Layer (CO2)
- Maps **carbon emissions (kg/MWh)** from electricity used by data centers.
- Uses a heat-style color scale (low → high CO₂ intensity).
- **View options**:
  - Filter by **State**, **Fuel**, and **PCA**.
  - Toggle between facility-level view and state-level averages.
- **Tooltips** on hover show:
  - Emissions intensity (kg/MWh)
  - Regional sub-basin
  - Primary generation fuel
- **More Insights panel**:
  - **Best vs Worst Carbon Projections** – scenario analysis of decarbonization vs business-as-usual.
  - **Fuel Type Contribution** – CO₂ emissions contribution by electricity source.


### 🏢 Data Centers Overlay & Summary
- White icons on the map mark **data center locations**; icon size reflects **facility size**.
- Clicking a data center reveals:
  - Name, operator
  - Size in acres
  - Power source
  - Cooling source
  - City, state
  - Project cost
  - Status (e.g., operational, planned) :contentReference[oaicite:1]{index=1}
- A separate **Data Centers Summary** view shows aggregated charts (status breakdown, states, operators, size buckets, etc.).


## 🧱 Tech Stack

**Frontend**
- Plain HTML, CSS, and JavaScript (single-page app in `app.html`) :contentReference[oaicite:2]{index=2}  
- [Leaflet](https://leafletjs.com/) for interactive mapping and layers  
- [Tailwind CSS](https://tailwindcss.com/) + [DaisyUI](https://daisyui.com/) for UI styling  
- [Chart.js](https://www.chartjs.org/) for summary and “More Insights” charts  

**Backend**
- [Flask](https://flask.palletsprojects.com/) web framework  
- [flask-cors](https://flask-cors.readthedocs.io/) for CORS handling  
- [gunicorn](https://gunicorn.org/) for production serving (via `Procfile`) :contentReference[oaicite:3]{index=3}  

**Data & Processing**
- CSV data files for monitors and environmental metrics (e.g. AQI, water footprint, power usage)
- [pandas](https://pandas.pydata.org/) and [NumPy](https://numpy.org/) for preprocessing and aggregation  
- Timezone handling via `pytz` :contentReference[oaicite:4]{index=4}  


## 📁 Project Structure

```text
data-center-map/
├── app.html                   # Main single-page frontend (Leaflet + Chart.js UI)
├── backend.py                 # Flask backend serving API endpoints
├── requirements.txt           # Python dependencies
├── Procfile                   # Process definition for gunicorn/Render/Heroku deployment
├── OZ_PM_AQI.csv              # AQI / monitor input data
├── annual_conc_by_monitor_2025.csv
├── final_footprint_dataset (2).csv
├── updated_data_file.csv
├── data/                      # (Optional) Additional data files / preprocessed datasets
└── templates/                 # (If used) HTML templates for Flask

## Getting Started (Local Development)

Clone the repository:
```bash
git clone https://github.com/sharashankr/data-center-map.git
cd data-center-map

Create and activate a virtual environment:
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

Install Dependencies:
pip install -r requirements.txt

Run the backend server:
python backend.py

Backend will start on http://127.0.0.1:5000

Open the frontend:

Option A – Served from Flask (if configured):
http://127.0.0.1:5000/

Option B – Serve app.html statically:
python -m http.server 8000

Then visit:
http://127.0.0.1:8000/app.html

Make sure the frontend API URLs match your backend environment.
