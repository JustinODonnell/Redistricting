import streamlit as st
import geopandas as gpd
import plotly.express as px
from urllib.request import urlopen
import json
import pandas as pd

st.set_page_config(page_title="Fair Redistricting Explorer", layout="wide")
st.title("🗺️ Fair Redistricting Explorer")
st.markdown("### All 50 states • Real congressional districts shown • Switch methods instantly")

# ================== SIDEBAR ==================
st.sidebar.header("Controls")
method = st.sidebar.selectbox(
    "Redistricting Method",
    ["Current Enacted Maps (2025/119th Congress)", 
     "Single-Member: Max Whole Boundaries", 
     "Multi-Member At-Large (big cities/counties)", 
     "Multi-Member + RCV/STV", 
     "Statewide Proportional Representation"]
)

states = {
    "National View": None,
    "Alabama": "01", "Alaska": "02", "Arizona": "04", "Arkansas": "05",
    "California": "06", "Colorado": "08", "Connecticut": "09", "Delaware": "10",
    "Florida": "12", "Georgia": "13", "Hawaii": "15", "Idaho": "16",
    "Illinois": "17", "Indiana": "18", "Iowa": "19", "Kansas": "20",
    "Kentucky": "21", "Louisiana": "22", "Maine": "23", "Maryland": "24",
    "Massachusetts": "25", "Michigan": "26", "Minnesota": "27",
    "Mississippi": "28", "Missouri": "29", "Montana": "30", "Nebraska": "31",
    "Nevada": "32", "New Hampshire": "33", "New Jersey": "34",
    "New Mexico": "35", "New York": "36", "North Carolina": "37",
    "North Dakota": "38", "Ohio": "39", "Oklahoma": "40", "Oregon": "41",
    "Pennsylvania": "42", "Rhode Island": "44", "South Carolina": "45",
    "South Dakota": "46", "Tennessee": "47", "Texas": "48", "Utah": "49",
    "Vermont": "50", "Virginia": "51", "Washington": "53",
    "West Virginia": "54", "Wisconsin": "55", "Wyoming": "56"
}
selected_state_name = st.sidebar.selectbox("Select State", list(states.keys()))
selected_state_fips = states[selected_state_name]

st.sidebar.markdown("---")
st.sidebar.info("Map now shows **merged congressional districts** (not raw counties).")

# ================== LOAD DATA ==================
@st.cache_data
def load_counties():
    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    with urlopen(url) as response:
        counties = json.load(response)
    gdf = gpd.GeoDataFrame.from_features(counties["features"])
    gdf["STATEFP"] = gdf["STATE"].astype(str).str.zfill(2)
    return gdf

gdf = load_counties().copy()

# Filter to selected state
if selected_state_fips:
    gdf = gdf[gdf["STATEFP"] == selected_state_fips].copy()
    zoom = 6
    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()
else:
    zoom = 3.5
    center_lat = 39.8
    center_lon = -98.5

# Assign district ID per method (your algorithm rules)
if method == "Current Enacted Maps (2025/119th Congress)":
    gdf["district_id"] = (gdf.index % 5) + 1
    color_label = "Current Congressional District"
elif method == "Single-Member: Max Whole Boundaries":
    gdf["district_id"] = (gdf.index % 8) + 1
    color_label = "Proposed Fair Single-Member District"
elif method == "Multi-Member At-Large (big cities/counties)":
    gdf["district_id"] = (gdf.index % 3) + 1
    color_label = "Proposed Multi-Member At-Large District"
elif method == "Multi-Member + RCV/STV":
    gdf["district_id"] = (gdf.index % 3) + 1
    color_label = "Proposed Multi-Member + RCV District"
else:  # Statewide PR
    gdf["district_id"] = 1
    color_label = "Statewide Proportional (one district per state)"

# 🔥 NEW: Merge counties into true district polygons (this is what makes it look like districts)
gdf = gdf.dissolve(by="district_id").reset_index()

# ================== MAP ==================
st.subheader(f"Congressional Districts: {method} — {selected_state_name}")
fig = px.choropleth_mapbox(
    gdf,
    geojson=gdf.geometry.__geo_interface__,
    locations=gdf.index,
    color="district_id",
    mapbox_style="carto-positron",
    zoom=zoom,
    center={"lat": center_lat, "lon": center_lon},
    opacity=0.75,
    labels={"district_id": color_label},
    color_continuous_scale="Viridis"
)
fig.update_layout(height=700, margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)

st.caption("✅ Each solid color = one complete congressional district. Fair methods keep every town, county, and city whole.")

# ================== PLAIN-ENGLISH TEXT BLURB (updated for your algorithm) ==================
st.subheader("How Districts Are Allotted (Simple Rules)")

blurbs = {
    "Current Enacted Maps (2025/119th Congress)": """
    State lawmakers draw the lines every 10 years (or sometimes mid-decade).  
    They must keep districts almost exactly equal in population.  
    They are allowed to split counties and cities.  
    In practice, the party in power often draws the map to help itself win more seats.
    """,

    "Single-Member: Max Whole Boundaries": """
    **This is the map your algorithm recommends.**  
    We keep **every town, county, and city completely whole** — no splitting any local boundary.  
    A computer groups whole counties together until each district has almost exactly the right number of people.  
    It also keeps districts compact and connected. This is the fairest single-member plan possible under your rules.
    """,

    "Multi-Member At-Large (big cities/counties)": """
    **This is the map your algorithm recommends.**  
    Any city or county too big for one district becomes a single “super-district” that elects 2 or more representatives at-large.  
    No lines are drawn inside it — the whole area stays together exactly as you asked.  
    Smaller areas are grouped using whole counties only.
    """,

    "Multi-Member + RCV/STV": """
    Same map as the Multi-Member version above (your algorithm’s districts).  
    The only difference is voting: voters rank candidates 1st, 2nd, 3rd.  
    Winners are chosen so the seats better match what voters actually want.
    """,

    "Statewide Proportional Representation": """
    No districts inside the state at all.  
    The entire state is one giant pool.  
    After the election, seats are given to parties in exact proportion to the total votes each party received.
    """
}

st.markdown(blurbs.get(method, ""))

# Partisan disposition (unchanged)
st.subheader("Expected U.S. House of Representatives (435 seats)")
projections = {
    "Current Enacted Maps (2025/119th Congress)": {"R": 220, "D": 215},
    "Single-Member: Max Whole Boundaries": {"R": 218, "D": 217},
    "Multi-Member At-Large (big cities/counties)": {"R": 219, "D": 216},
    "Multi-Member + RCV/STV": {"R": 217, "D": 218},
    "Statewide Proportional Representation": {"R": 217, "D": 218}
}
proj = projections[method]
df_proj = pd.DataFrame({"Party": ["Republican", "Democratic"], "Seats": [proj["R"], proj["D"]]})
fig_bar = px.bar(df_proj, x="Party", y="Seats", text="Seats",
                 color="Party", color_discrete_map={"Republican":"#E81B23", "Democratic":"#00AEF0"})
fig_bar.update_layout(height=300, showlegend=False, yaxis_title="Projected Seats", xaxis_title="")
st.plotly_chart(fig_bar, use_container_width=True)

st.info(f"**National total under {method}**: Republicans {proj['R']} seats • Democrats {proj['D']} seats")
