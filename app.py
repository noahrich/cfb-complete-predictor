import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LogisticRegression
import requests
from datetime import datetime

st.set_page_config(page_title="CFB Live Predictor", layout="wide")

def simulate_model(spread):
    return np.clip(0.5 - spread / 30.0, 0.05, 0.95)

def logistic_model(spreads):
    spreads = np.array(spreads).reshape(-1, 1)
    model = LogisticRegression()
    X = np.linspace(-30, 30, 200).reshape(-1, 1)
    y = [1 if x > 0 else 0 for x in X]
    model.fit(X, y)
    return model.predict_proba(spreads)[:,1]

@st.cache_data
def fetch_live_games():
    cfbd_key = os.getenv("CFBD_API_KEY")
    odds_key = os.getenv("ODDS_API_KEY")
    week = datetime.now().isocalendar().week
    year = datetime.now().year

    games_url = f"https://api.collegefootballdata.com/games?year={year}&week={week}&seasonType=regular"
    headers = {"Authorization": f"Bearer {cfbd_key}"}
    games_res = requests.get(games_url, headers=headers)

    odds_url = f"https://api.the-odds-api.com/v4/sports/americanfootball_ncaaf/odds?regions=us&markets=spreads&oddsFormat=decimal&apiKey={odds_key}"
    odds_res = requests.get(odds_url)

    games_df = pd.DataFrame(games_res.json())
    odds_df = pd.DataFrame(odds_res.json())

    rows = []
    for game in games_df.itertuples():
        team1 = game.home_team
        team2 = game.away_team
        matchup = f"{team2} @ {team1}"
        spread = np.nan
        for line in odds_df.get("bookmakers", []):
            if line.get("markets"):
                for market in line["markets"]:
                    for outcome in market["outcomes"]:
                        if outcome["name"] == team1:
                            spread = -outcome.get("point", 0)
        rows.append({"Matchup": matchup, "Spread": spread})
    return pd.DataFrame(rows).dropna()

@st.cache_data
def fetch_injuries(teams):
    key = os.getenv("CFBD_API_KEY")
    if not key:
        return pd.DataFrame()
    r = requests.get(
        "https://api.collegefootballdata.com/injuries",
        headers={"Authorization": f"Bearer {key}"}
    )
    if r.status_code != 200:
        return pd.DataFrame()
    df = pd.DataFrame(r.json())
    return df[df['team'].isin(teams)]

st.title("🏈 CFB Live Prediction Dashboard")

df = fetch_live_games()
if df.empty:
    st.warning("No live games or lines available.")
else:
    df['Sim Upset %'] = df['Spread'].apply(simulate_model) * 100
    df['Logistic Upset %'] = logistic_model(df['Spread']) * 100
    df['Difference'] = df['Logistic Upset %'] - df['Sim Upset %']
    df['Confidence'] = abs(df['Difference']).round(1)
    df['Sim Cover %'] = df['Spread'].apply(lambda x: 100 - simulate_model(x) * 100)

    st.subheader("📊 Predictions")
    st.dataframe(df.style.format({
        'Spread': '{:.1f}',
        'Sim Upset %': '{:.1f}%',
        'Logistic Upset %': '{:.1f}%',
        'Sim Cover %': '{:.1f}%',
        'Confidence': '{:.1f}%'
    }))

    st.subheader("✅ Suggested Picks")
    high_conf = df[df['Confidence'] > 15].copy()
    if high_conf.empty:
        st.write("No strong confidence picks this week.")
    else:
        st.table(high_conf[['Matchup', 'Spread', 'Sim Upset %', 'Logistic Upset %', 'Confidence']])

    st.subheader("🩼 Injury Report")
    teams = []
    for matchup in df["Matchup"]:
        for team in matchup.split(" @ "):
            teams.append(team.strip())
    injuries_df = fetch_injuries(teams)
    if injuries_df.empty:
        st.info("No injury data available or API key missing.")
    else:
        st.dataframe(injuries_df[['team', 'player', 'position', 'status']])