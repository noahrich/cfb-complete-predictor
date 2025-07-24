import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def simulate_model(spread):
    return np.clip(0.5 - spread / 30.0, 0.05, 0.95)

def logistic_model(spreads):
    spreads = np.array(spreads).reshape(-1, 1)
    model = LogisticRegression()
    X = np.linspace(-30, 30, 200).reshape(-1, 1)
    y = [1 if x > 0 else 0 for x in X]
    model.fit(X, y)
    return model.predict_proba(spreads)[:,1]

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

    if games_res.status_code != 200 or odds_res.status_code != 200:
        return pd.DataFrame()

    games_df = pd.DataFrame(games_res.json())
    odds_data = odds_res.json()

    rows = []
    for game in games_df.itertuples():
        team1 = game.home_team
        team2 = game.away_team
        matchup = f"{team2} @ {team1}"
        spread = np.nan
        for event in odds_data:
            if event.get("home_team") == team1 and event.get("away_team") == team2:
                for bookmaker in event.get("bookmakers", []):
                    for market in bookmaker.get("markets", []):
                        for outcome in market.get("outcomes", []):
                            if outcome["name"] == team1:
                                spread = -outcome.get("point", 0)
        if not np.isnan(spread):
            rows.append({"matchup": matchup, "spread": spread})
    return pd.DataFrame(rows)

def fetch_injuries(teams):
    key = os.getenv("CFBD_API_KEY")
    if not key:
        return []
    r = requests.get(
        "https://api.collegefootballdata.com/injuries",
        headers={"Authorization": f"Bearer {key}"}
    )
    if r.status_code != 200:
        return []
    df = pd.DataFrame(r.json())
    filtered = df[df['team'].isin(teams)]
    return filtered[['team', 'player', 'position', 'status']].to_dict(orient='records')

def build_email_content(games_df):
    sim_probs = [simulate_model(sp) for sp in games_df['spread']]
    log_probs = logistic_model(games_df['spread'])
    teams = [team for matchup in games_df['matchup'] for team in matchup.split(" @ ")]
    injuries = fetch_injuries(teams)

    content = "🏈 Weekly CFB Predictions and Injuries\n\n"
    content += "📊 Match Predictions:\n"
    for i, row in games_df.iterrows():
        content += f"- {row['matchup']} (spread: {row['spread']})\n"
        content += f"   • Sim Upset Chance: {sim_probs[i]*100:.1f}%\n"
        content += f"   • Logistic Upset Chance: {log_probs[i]*100:.1f}%\n"
        content += f"   • Cover Probability: {100 - sim_probs[i]*100:.1f}%\n"

    if injuries:
        content += "\n🩼 Injury Report:\n"
        for inj in injuries:
            content += f"- {inj['team']}: {inj['player']} ({inj['position']}) – {inj['status']}\n"
    else:
        content += "\n🩼 No injury data available this week.\n"
    return content

def send_email(content):
    sender_email = os.getenv("EMAIL_FROM", os.getenv("EMAIL_TO"))
    receiver_email = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Weekly CFB Predictions + Injuries + Picks"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    part = MIMEText(content, "plain")
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

if __name__ == "__main__":
    df = fetch_live_games()
    if df.empty:
        print("No live game data available.")
    else:
        content = build_email_content(df)
        print(content)
        # Uncomment below to enable email sending
        # send_email(content)