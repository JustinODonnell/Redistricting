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
    "New Mexico": "35", "New York": "36", "North
