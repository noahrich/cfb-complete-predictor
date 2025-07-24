import streamlit as st
import pandas as pd
import requests
import os
from cfbd import Configuration, ApiClient, StatsApi

# Load API keys
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
CFBD_API_KEY = os.getenv("CFBD_API_KEY")

# Configure CFBD API
configuration = Configuration()
configuration.api_key['Authorization'] = CFBD_API_KEY
configuration.api_key_prefix['Authorization'] = 'Bearer'

def fetch_player_props():
    url = "https://api.the-odds-api.com/v4/sports/americanfootball_ncaaf/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "player_pass_yds,player_rush_yds,player_rec_yds",
        "oddsFormat": "decimal"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        st.error(f"Error fetching props: {response.text}")
        return pd.DataFrame()

    data = response.json()
    records = []
    for game in data:
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    records.append({
                        "player": outcome["name"],
                        "team": game["home_team"] if outcome["name"] in game["home_team"] else game["away_team"],
                        "stat_type": market["key"],
                        "prop_line": outcome["point"],
                        "bookmaker": bookmaker["title"]
                    })
    return pd.DataFrame(records)

def enrich_with_stats(df):
    with ApiClient(configuration) as api_client:
        api_instance = StatsApi(api_client)
        df["model_proj"] = None
        df["hit_pct"] = None
        df["edge"] = None
        for idx, row in df.iterrows():
            try:
                player_name = row['player']
                team = row['team']
                stat_cat = "passing" if "pass" in row["stat_type"] else "rushing" if "rush" in row["stat_type"] else "receiving"
                stats = api_instance.get_player_game_stats(year=2023, team=team, category=stat_cat)
                games = [g for g in stats if g.player and g.player.name and player_name.lower() in g.player.name.lower()]
                if games:
                    values = [float(g.stat.yards) for g in games if g.stat and hasattr(g.stat, 'yards')]
                    if values:
                        model_proj = sum(values[-5:]) / min(len(values), 5)
                        hit_count = sum(1 for val in values[-5:] if val > row["prop_line"])
                        df.at[idx, "model_proj"] = round(model_proj, 2)
                        df.at[idx, "hit_pct"] = round(hit_count / min(len(values), 5), 2)
                        df.at[idx, "edge"] = round(model_proj - row["prop_line"], 2)
            except Exception as e:
                print(f"Error processing stats for {row['player']}: {e}")
    return df

st.set_page_config(page_title="CFB Live Props", layout="wide")
tabs = st.tabs(["🏈 Predictions", "📊 Player Props"])
with tabs[1]:
    st.header("📊 Player Props Explorer")

    props_df = fetch_player_props()
    if props_df.empty:
        st.warning("No props found or check API key.")
    else:
        props_df = enrich_with_stats(props_df)

        teams = st.multiselect("Filter by Team", options=props_df["team"].dropna().unique())
        stats = st.multiselect("Filter by Stat Type", options=props_df["stat_type"].dropna().unique())

        filtered = props_df.copy()
        if teams:
            filtered = filtered[filtered["team"].isin(teams)]
        if stats:
            filtered = filtered[filtered["stat_type"].isin(stats)]

        st.dataframe(filtered)

        st.subheader("🔍 Suggested Props (Edge > 10 and Hit% > 60%)")
        suggestions = filtered[(filtered["edge"].abs() > 10) & (filtered["hit_pct"] >= 0.6)]
        st.table(suggestions[["player", "team", "stat_type", "prop_line", "model_proj", "edge", "hit_pct", "bookmaker"]])