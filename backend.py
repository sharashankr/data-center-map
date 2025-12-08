from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime
import pytz
import csv
import os
import pandas as pd

from numbers_parser import Document

# --- FILE CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MONITOR_CSV = os.path.abspath('OZ_PM_AQI.csv')
DC_CSV = os.path.abspath('data/Data_Centers_Database - Data Centers.csv')
WATER_CSV = os.path.abspath('final_footprint_dataset (2).csv')
CARBON_CSV = os.path.abspath('final_footprint_dataset (2).csv')
IMPACT_CSV = os.path.abspath('data/dc_impact_summary.csv')

# --- Global variables ---
MONITOR_DATA = []
WATER_DATA = []
CARBON_DATA = []
POWER_DATA = []
SCENARIO_DATA = []

# --- Initialize Flask ---
app = Flask(__name__)
CORS(app)

def get_aqi_and_color(concentration, pollutant):
    if pollutant.lower() == 'ozone':
        # Ozone formula (ppm)
        if concentration <= 0.054:
            aqi = int(concentration / 0.054 * 50)
            color = "green"
        elif concentration <= 0.070:
            aqi = 51 + int((concentration - 0.055) / (0.070 - 0.055) * 49)
            color = "yellow"
        elif concentration <= 0.085:
            aqi = 101 + int((concentration - 0.071) / (0.085 - 0.071) * 49)
            color = "orange"
        elif concentration <= 0.105:
            aqi = 151 + int((concentration - 0.086) / (0.105 - 0.086) * 49)
            color = "red"
        else:
            aqi = 201 + int((concentration - 0.106) / 0.01 * 10)
            color = "purple"

    elif pollutant.lower() == 'pm2.5 - local conditions':
        # PM2.5 formula (µg/m³)
        if concentration <= 12.0:
            aqi = int(concentration / 12.0 * 50)
            color = "green"
        elif concentration <= 35.4:
            aqi = 51 + int((concentration - 12.1) / (35.4 - 12.1) * 49)
            color = "yellow"
        elif concentration <= 55.4:
            aqi = 101 + int((concentration - 35.5) / (55.4 - 35.5) * 49)
            color = "orange"
        elif concentration <= 150.4:
            aqi = 151 + int((concentration - 55.5) / (150.4 - 55.5) * 49)
            color = "red"
        elif concentration <= 250.4:
            aqi = 201 + int((concentration - 150.5) / (250.4 - 150.5) * 99)
            color = "purple"
        else:
            aqi = 301 + int((concentration - 250.5) / (500 - 250.5) * 199)
            color = "maroon"
    else:
        aqi, color = None, None

    return max(1, aqi), color


# --- Load AQI monitor data ---
def load_monitor_data():
    global MONITOR_DATA
    MONITOR_DATA = []

    if not os.path.exists(MONITOR_CSV):
        print(f"Monitor CSV not found: {MONITOR_CSV}")
        return

    with open(MONITOR_CSV, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("Monitor CSV is empty.")
            return

        try:
            lat_idx = header.index('Latitude')
            lon_idx = header.index('Longitude')
            mean_idx = header.index('Arithmetic Mean')
            site_name_idx = header.index('Local Site Name')
            pollutant_idx = header.index('Parameter Name')
            # *** ADDED: Index for the 'State Name' column
            state_name_idx = header.index('State Name') 
        except ValueError as e:
            print(f"Missing column in monitor CSV: {e}")
            return

        count = 0
        for row in reader:
            try:
                lat = float(row[lat_idx])
                lon = float(row[lon_idx])
                conc = float(row[mean_idx])
                city = row[site_name_idx]
                pollutant = row[pollutant_idx].lower()
                # *** ADDED: Retrieve the state name
                state = row[state_name_idx] 
                aqi, color = get_aqi_and_color(conc, pollutant)
                
                MONITOR_DATA.append({
                    "lat": lat,
                    "lon": lon,
                    "aqi": aqi,
                    "city": city,
                    # *** UPDATED: Include the state data
                    "state": state, 
                    "color": color,
                    "pollutant": pollutant
                })
                count += 1
            except Exception:
                continue

    print(f"Loaded {count} monitor records.")

# --- Load water footprint data ---
def load_water_data():
    global WATER_DATA
    WATER_DATA = []

    if not os.path.exists(WATER_CSV):
        print(f"Water CSV not found: {WATER_CSV}")
        return

    with open(WATER_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                lat_str = row.get("lat", "").strip()
                lon_str = row.get("lon", "").strip()
                water_str = row.get("water_footprint", "").strip()

                if not lat_str or not lon_str or not water_str:
                    continue

                lat = float(lat_str)
                lon = float(lon_str)
                water_fp = float(water_str)

                WATER_DATA.append({
                    "lat": lat,
                    "lon": lon,
                    "water_footprint": water_fp,
                    "subbasin": row.get("subbasin", ""),
                    "state": row.get("plant_state", ""),
                    "primary_fuel": row.get("primary_fuel", "")
                    
                })
                count += 1
            except Exception:
                continue

    print(f"Loaded {count} water footprint records.")

def load_carbon_data():
    global CARBON_DATA
    CARBON_DATA = []

    if not os.path.exists(CARBON_CSV):
        print(f"Carbon CSV not found: {CARBON_CSV}")
        return

    with open(CARBON_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0

        for row in reader:
            try:
                lat_str = row.get("lat", "").strip()
                lon_str = row.get("lon", "").strip()
                cf_str = row.get("carbon_footprint", "").replace(",", "").strip()

                if lat_str == "" or lon_str == "" or cf_str == "":
                    continue

                lat = float(lat_str)
                lon = float(lon_str)
                carbon_fp = float(cf_str)

                if carbon_fp == 0:
                    continue

                CARBON_DATA.append({
                    "lat": lat,
                    "lon": lon,
                    "subbasin": row.get("subbasin", ""),
                    "state": row.get("plant_state", ""),
                    "primary_fuel": row.get("primary_fuel", ""),
                    "carbon_footprint": carbon_fp
                })
                count += 1
            except Exception as e:
                print("Skipping row due to error:", e)
                continue

    print(f"Loaded {count} carbon footprint records.")



def load_power_data():
    global POWER_DATA
    POWER_DATA = []

    if not os.path.exists(WATER_CSV):  # Using WATER_CSV now
        print(f"Power CSV not found: {WATER_CSV}")
        return

    with open(WATER_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                lat_str = row.get("lat", "").strip()
                lon_str = row.get("lon", "").strip()
                total_mwh_str = row.get("total_mwh", "").strip()

                if not lat_str or not lon_str or not total_mwh_str:
                    continue

                lat = float(lat_str)
                lon = float(lon_str)
                total_mwh = float(total_mwh_str)

                POWER_DATA.append({
                    "lat": lat,
                    "lon": lon,
                    "total_mwh": total_mwh,
                    "subbasin": row.get("subbasin", ""),
                    "state": row.get("plant_state", ""),
                    "primary_fuel": row.get("primary_fuel", "")
                })
                count += 1
            except Exception:
                continue

    print(f"Loaded {count} power consumption records.")

def load_scenario_data():
    global SCENARIO_DATA
    SCENARIO_DATA = []

    if not os.path.exists(IMPACT_CSV):
        print(f"Impact CSV not found: {IMPACT_CSV}")
        return

    with open(IMPACT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                year = int(row.get("year", "").strip())
                energy = float(row.get("energy_TWh", "0").strip())
                carbon = float(row.get("carbon_MtCO2", "0").strip())
                water = float(row.get("water_Mm3", "0").strip())
                scenario = row.get("scenario", "").strip()

                SCENARIO_DATA.append({
                    "year": year,
                    "energy_TWh": energy,
                    "carbon_MtCO2": carbon,
                    "water_Mm3": water,
                    "scenario": scenario
                })
                count += 1
            except Exception as e:
                print(f"Skipping row due to error: {e}")
                continue

    print(f"Loaded {count} scenario records.")

# --- Load all data at startup ---
print("Loading monitor and water data...")
load_monitor_data()
load_water_data()
load_carbon_data()
load_power_data()
load_scenario_data()
print("Data loading complete.")

# --- API endpoint: /api/monitors ---
@app.route('/api/monitors', methods=['GET'])
def get_monitors():
    pollutant = request.args.get("pollutant", "all").lower()

    # Filter monitors based on pollutant
    if pollutant == "ozone":
        monitors = [m for m in MONITOR_DATA if "ozone" in m["pollutant"]]
    elif pollutant == "pm":
        monitors = [m for m in MONITOR_DATA if "pm" in m["pollutant"]]
    else:
        monitors = MONITOR_DATA

    # Load data centers dynamically with extra fields
    data_centers = []
    if os.path.exists(DC_CSV):
        with open(DC_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    lat_str = row.get("Lat", "").strip()
                    lon_str = row.get("Long", "").strip()
                    if not lat_str or not lon_str:
                        continue
                    lat = float(lat_str)
                    lon = float(lon_str)

                    data_centers.append({
                        "Name": row.get("Name", "N/A"),
                        "City": row.get("City", ""),
                        "State": row.get("State", ""),
                        "Operator": row.get("Operator", ""),
                        "PowerSource": row.get("Power source", ""),
                        "CoolingSource": row.get("Cooling source", ""),
                        "PropertySizeAcres": row.get("Property Size (acres)", ""),
                        "ProjectCost": row.get("Project cost", ""),
                        "Status": row.get("Status", ""),
                        "lat": lat,
                        "lon": lon,
                        "SizeRank": row.get("SizeRank (numeric)", "")
                    })
                except Exception:
                    continue

    return jsonify({
        "timestamp": datetime.now(pytz.utc).isoformat(),
        "monitors": monitors,
        "data_centers": data_centers
    })


# --- API endpoint: /api/water ---
@app.route('/api/water', methods=['GET'])
def get_water():
    return jsonify({
        "timestamp": datetime.now(pytz.utc).isoformat(),
        "points": WATER_DATA
    })

# --- API endpoint: /api/water_fuel ---
@app.route('/api/water_fuel', methods=['GET'])
def get_water_fuel():
    if not os.path.exists(WATER_CSV):
        return jsonify({"error": "Water CSV not found"}), 404

    try:
        # Load CSV
        df = pd.read_csv(WATER_CSV)

        # Ensure water_footprint is numeric, coerce errors
        df['water_footprint'] = pd.to_numeric(df['water_footprint'], errors='coerce')

        # Drop rows with NaN or zero water footprint
        df = df[df['water_footprint'].notna() & (df['water_footprint'] > 0)]

        # Drop rows with NaN primary_fuel
        df = df[df['primary_fuel'].notna() & (df['primary_fuel'].str.strip() != "")]

        # Aggregate by primary_fuel and sort descending
        aggregation_result = df.groupby('primary_fuel')['water_footprint'].sum().sort_values(ascending=False)

        # Drop NaN primary_fuels just in case
        aggregation_result_cleaned = aggregation_result.dropna(axis=0)

        # Convert to list of dicts in the requested format
        fuel_data = [
            {"primary_fuel": fuel, "water_footprint": float(round(wf, 2))}
            for fuel, wf in aggregation_result_cleaned.items()
        ]

        return jsonify(fuel_data)

    except Exception as e:
        return jsonify({"error": f"Failed to aggregate water footprint: {str(e)}"}), 500

@app.route('/api/carbon_fuel', methods=['GET'])
def get_carbon_fuel():
    if not os.path.exists(CARBON_CSV):
        return jsonify({"error": "Carbon CSV not found"}), 404
    try:
        df = pd.read_csv(CARBON_CSV)
        df['carbon_footprint'] = pd.to_numeric(df['carbon_footprint'], errors='coerce')
        df = df[df['carbon_footprint'].notna() & (df['carbon_footprint'] > 0)]
        df = df[df['primary_fuel'].notna() & (df['primary_fuel'].str.strip() != "")]
        aggregation_result = df.groupby('primary_fuel')['carbon_footprint'].sum().sort_values(ascending=False)
        aggregation_result_cleaned = aggregation_result.dropna(axis=0)
        carbon_data = [
            {"primary_fuel": fuel, "carbon_footprint": float(round(cf, 2))}
            for fuel, cf in aggregation_result_cleaned.items()
        ]
        return jsonify(carbon_data)
    except Exception as e:
        return jsonify({"error": f"Failed to aggregate carbon footprint: {str(e)}"}), 500


# --- API endpoint: /api/carbon ---
@app.route('/api/carbon', methods=['GET'])
def get_carbon():
    return jsonify({
        "timestamp": datetime.now(pytz.utc).isoformat(),
        "points": CARBON_DATA
    })

# --- API endpoint: /api/power ---
@app.route('/api/power', methods=['GET'])
def get_power():
    return jsonify({
        "timestamp": datetime.now(pytz.utc).isoformat(),
        "points": POWER_DATA
    })

# --- API endpoint: /api/scenario ---
@app.route('/api/scenario', methods=['GET'])
def get_scenario():
    year_filter = request.args.get("year")
    filtered_data = SCENARIO_DATA

    if year_filter:
        try:
            year_int = int(year_filter)
            filtered_data = [d for d in SCENARIO_DATA if d["year"] == year_int]
        except ValueError:
            pass

    return jsonify({
        "timestamp": datetime.now(pytz.utc).isoformat(),
        "data": filtered_data
    })

# --- NEW: API endpoint for /api/water_scenario ---
@app.route('/api/water_scenario', methods=['GET'])
def get_water_scenario():
    return jsonify({
        "timestamp": datetime.now(pytz.utc).isoformat(),
        "points": SCENARIO_DATA
    })

# --- API endpoint: /api/carbon_scenario ---
@app.route('/api/carbon_scenario', methods=['GET'])
def get_carbon_scenario():
    year_filter = request.args.get("year")
    filtered_data = SCENARIO_DATA

    if year_filter:
        try:
            year_int = int(year_filter)
            filtered_data = [d for d in SCENARIO_DATA if d["year"] == year_int]
        except ValueError:
            pass

    # Only keep year and carbon values
    carbon_only = [{"year": d["year"], "carbon_MtCO2": d["carbon_MtCO2"], "scenario": d["scenario"]} for d in filtered_data]

    return jsonify({
        "timestamp": datetime.now(pytz.utc).isoformat(),
        "data": carbon_only
    })
# --- API endpoint: /api/water_carbon_data ---
@app.route('/api/water_carbon_data', methods=['GET'])
def water_carbon_data():
    import pandas as pd

    if not os.path.exists(WATER_CSV):
        return jsonify({"error": "Water CSV not found"}), 404

    df = pd.read_csv(WATER_CSV)

    # --- Clean and filter ---
    df = df[df["total_mwh"] > 0].copy()
    df = df[df["water_footprint"].notna() & (df["water_footprint"] > 0)].copy()
    df = df[df["carbon_intensity_tons_per_mwh"].notna()].copy()

    # Optionally scale bubble sizes (for frontend)
    max_water = df["water_footprint"].max()
    df["size"] = df["water_footprint"] / max_water * 300

    # Select only the columns you need
    result = df[["total_mwh", "scarcity_factor", "water_footprint", "carbon_intensity_tons_per_mwh", "size"]]

    return jsonify(result.to_dict(orient="records"))

# --- API endpoint: /api/data_center_summary ---
@app.route('/api/data_center_summary', methods=['GET'])
def data_center_summary():
    if not os.path.exists(DC_CSV):
        return jsonify({"error": "Data Center CSV not found"}), 404

    try:
        df = pd.read_csv(DC_CSV)

        # -------- CLEANING --------
        df['Facility size (sq ft) Clean'] = (
            df['Facility size (sq ft)']
            .astype(str)
            .str.replace(r'[",]', '', regex=True)
        )
        df['Facility size (sq ft) Clean'] = pd.to_numeric(
            df['Facility size (sq ft) Clean'], errors='coerce'
        )

        df_size_clean = df.dropna(subset=['Facility size (sq ft) Clean']).copy()
        df_size_clean['Size_Million_sq_ft'] = (
            df_size_clean['Facility size (sq ft) Clean'] / 1_000_000
        )

        # -------- TABLE 1: STATUS COUNTS --------
        status_counts = (
            df['Status']
            .value_counts()
            .reset_index()
            .rename(columns={'index': 'Status', 'Status': 'Count'})
            .fillna(0)
        )

        # -------- TABLE 2: TOP 10 STATES --------
        state_counts = (
            df['State']
            .value_counts()
            .nlargest(10)
            .reset_index()
            .rename(columns={'index': 'State', 'State': 'Count'})
            .fillna(0)
        )

        # -------- TABLE 3: TOP 10 OPERATORS --------
        # -------- TABLE 3: TOP 10 OPERATORS --------
        operator_counts = (
            df['Operator']
            .replace(["", " ", "None", "Unknown"], pd.NA)
            .dropna()
            .str.strip()                # remove leading/trailing spaces
            .str.lower()                # normalize casing
            .value_counts()
            .nlargest(10)
            .reset_index()
            .rename(columns={'index': 'Operator', 'Operator': 'Count'})
            .fillna(0)
        )


        # -------- TABLE 4: FACILITY SIZE DISTRIBUTION --------
        size_distribution = df_size_clean[['Name', 'State', 'Size_Million_sq_ft']].fillna(0)

        # Convert NaN to None for JSON compatibility
        def replace_nan_with_none(df):
            return df.where(pd.notnull(df), None)

        return jsonify({
            "timestamp": datetime.now(pytz.utc).isoformat(),
            "status_counts": replace_nan_with_none(status_counts).to_dict(orient='records'),
            "top_states": replace_nan_with_none(state_counts).to_dict(orient='records'),
            "top_operators": replace_nan_with_none(operator_counts).to_dict(orient='records'),
            "size_distribution": replace_nan_with_none(size_distribution).to_dict(orient='records'),
        })

    except Exception as e:
        return jsonify({"error": f"Failed to load summary tables: {str(e)}"}), 500

# --- Test endpoint ---
@app.route('/test', methods=['GET'])
def test():
    return "Flask is working!"

@app.route("/")
def index():
    return render_template("app.html")

# --- Main entry ---
if __name__ == '__main__':
    print(f"Starting Flask server on http://127.0.0.1:3000...")
    app.run(debug=True, port=3000, use_reloader=False)
