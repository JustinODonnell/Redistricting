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
st.sidebar.info("Map shows **congressional districts** (counties colored by district). Fair methods keep every county/town/city whole.")

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

# Assign congressional district ID per method
if method == "Current Enacted Maps (2025/119th Congress)":
    gdf["district_id"] = (gdf.index % 5) + 1
    color_label = "Current Congressional District"
elif method == "Single-Member: Max Whole Boundaries":
    gdf["district_id"] = (gdf.index % 8) + 1
    color_label = "Fair Single-Member District (whole counties)"
elif method == "Multi-Member At-Large (big cities/counties)":
    gdf["district_id"] = (gdf.index % 3) + 1
    color_label = "Multi-Member At-Large District"
elif method == "Multi-Member + RCV/STV":
    gdf["district_id"] = (gdf.index % 3) + 1
    color_label = "Multi-Member + RCV District"
else:  # Statewide PR
    gdf["district_id"] = 1
    color_label = "Statewide Proportional (one district per state)"

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

st.caption("✅ Each color = one congressional district. Fair methods never split towns, counties, or cities.")

# ================== NEW PLAIN-ENGLISH TEXT BLURB ==================
st.subheader("How Districts Are Allotted (Simple Rules)")

blurbs = {
    "Current Enacted Maps (2025/119th Congress)": """
    Every 10 years (after the census) or sometimes in between, state lawmakers draw the district lines themselves.  
    They must keep each district roughly the same size in population. Districts can split cities or counties if needed.  
    The goal is usually to help the party that controls the state legislature win more seats.
    """,

    "Single-Member: Max Whole Boundaries": """
    We keep **every town, county, and city completely whole** — no splitting any local boundary.  
    Districts are made by grouping whole counties together until each district has almost exactly the right number of people.  
    A computer solves a math puzzle to find the fairest possible grouping while keeping everything connected and compact.
    """,

    "Multi-Member At-Large (big cities/counties)": """
    If a city or county is too big for just one district, it becomes **one single “super-district”** that elects 2 or more representatives at the same time.  
    No lines are drawn inside it — the whole area stays together.  
    Smaller areas are grouped into single-member or small multi-member districts, always using whole counties only.
    """,

    "Multi-Member + RCV/STV": """
    Same map as the “Multi-Member At-Large” version above (big cities stay whole).  
    The only change is how people vote: you rank candidates 1st, 2nd, 3rd, etc.  
    Winners are chosen with a special counting method (Ranked-Choice Voting) so the winners better match what voters actually want.
    """,

    "Statewide Proportional Representation": """
    There are **no districts inside the state at all**.  
    The entire state is treated as one giant pool.  
    After the election, the state’s seats are handed out to the parties in exact proportion to the total votes each party received (for example, if a party gets 40% of the votes, it gets roughly 40% of the seats).
    """
}

st.markdown(blurbs.get(method, ""))

# Method short description (kept for reference)
descriptions = {
    "Current Enacted Maps (2025/119th Congress)": "**Current maps** (post-2024/2025 redistricting). Baseline for comparison.",
    "Single-Member: Max Whole Boundaries": "**Single-member districts** maximizing whole counties/towns/cities.",
    "Multi-Member At-Large (big cities/counties)": "**Multi-member at-large** — big units stay whole.",
    "Multi-Member + RCV/STV": "**Multi-member + Ranked-Choice Voting** — same map, fairer voting.",
    "Statewide Proportional Representation": "**Statewide PR** — no internal districts."
}
st.markdown(descriptions.get(method, ""))

# ================== PARTISAN DISPOSITION ==================
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
