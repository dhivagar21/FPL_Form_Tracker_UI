import requests
import pandas as pd
import streamlit as st

# Load FPL data
url = "https://fantasy.premierleague.com/api/bootstrap-static/"
response = requests.get(url)
data = response.json()
players = data["elements"]
clubs = data["teams"]

# Build club name mapping
club_map = {club['id']: club['name'] for club in clubs}

# Map element_type to position
position_map = {1: "Goalkeeper", 2: "Defender", 3: "Midfielder", 4: "Forward"}

# Map status codes to readable labels
status_map = {
    "a": "Active",
    "i": "Injured",
    "d": "Doubtful",
    "s": "Suspended"
}

# Create DataFrame
df = pd.DataFrame(players)
df["position"] = df["element_type"].map(position_map)
df["form"] = df["form"]
df["price_float"] = (df["now_cost"] / 10).round(1)  # for filtering
df["price"] = "£" + df["price_float"].astype(str)   # for display
df["club"] = df["team"].map(club_map)
df["status"] = df["status"].map(status_map)
df["news"] = df["news"]
df["transfers_in_event"] = df["transfers_in_event"]  # transfers in this GW
df["transfers_out_event"] = df["transfers_out_event"]  # transfers out this GW

# Select relevant columns
df_form = df[[
    "web_name", "position", "club", "form", "price", "price_float",
    "goals_scored", "assists", "minutes", "transfers_in_event", "transfers_out_event", "status", "news"
]].sort_values(by="form", ascending=False)

# Streamlit UI
st.title("🔥 Dee's FPL Form Tracker")
st.markdown("One place to get the details of Premier League players based "
            "on Current Form, xGoals, xAssists, Transfers In/Out, Price (£) and more...")

# Filters
position_filter = st.selectbox("Filter by Position", ["All"] + list(position_map.values()))
club_filter = st.selectbox("Filter by Club", ["All"] + sorted(club_map.values()))
price_filter = st.slider("Max Price (£m)", 4.0, 15.0, 15.0)

# Apply filters
filtered_df = df_form.copy()
if position_filter != "All":
    filtered_df = filtered_df[filtered_df["position"] == position_filter]
if club_filter != "All":
    filtered_df = filtered_df[filtered_df["club"] == club_filter]
filtered_df = filtered_df[filtered_df["price_float"] <= price_filter]

# Drop helper column before display
filtered_df = filtered_df.drop(columns=["price_float"])

# Add row numbers
filtered_df = filtered_df.head(150).reset_index(drop=True)
filtered_df.insert(0, "No.", filtered_df.index + 1)

# Rename columns for clean headers
filtered_df.rename(columns={
    "web_name": "Player",
    "position": "Position",
    "club": "Club",
    "form": "Form",
    "price": "Price (£m)",
    "goals_scored": "Goals Scored",
    "assists": "Assists",
    "minutes": "Minutes Played",
    "transfers_in_event": "Transfers In (GW)",
    "transfers_out_event": "Transfers Out (GW)",
    "status": "Status",
    "news": "Injury News"
}, inplace=True)

# Highlight flagged players
def highlight_row(row):
    if row["Status"] == "Injured":
        return ['background-color: #FFCCCC'] * len(row)
    elif row["Status"] == "Doubtful":
        return ['background-color: #FFE5B4'] * len(row)
    elif row["Status"] == "Suspended":
        return ['background-color: #D3D3D3'] * len(row)
    else:
        return [''] * len(row)

# Display styled table
st.subheader("Top Players by Form")
styled_df = filtered_df.style.apply(highlight_row, axis=1)
st.dataframe(styled_df, use_container_width=True)