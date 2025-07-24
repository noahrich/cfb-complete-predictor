import os
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def simulate_model(spread):
    upset_prob = np.clip(0.5 - spread / 30.0, 0.05, 0.95)
    return upset_prob

def logistic_model(spreads):
    spreads = np.array(spreads).reshape(-1, 1)
    model = LogisticRegression()
    X = np.linspace(-30, 30, 200).reshape(-1, 1)
    y = [1 if x > 0 else 0 for x in X]
    model.fit(X, y)
    return model.predict_proba(spreads)[:,1]

def fetch_mock_games():
    return pd.DataFrame([
        {"matchup": "Florida @ LSU", "spread": -6.5},
        {"matchup": "UTSA @ Texas", "spread": -8.0},
        {"matchup": "Miami @ Georgia Tech", "spread": 2.5},
    ])

def build_email_content(games_df):
    sim_probs = [simulate_model(sp) for sp in games_df['spread']]
    log_probs = logistic_model(games_df['spread'])

    email_text = "🏈 Weekly CFB Upset Predictions\n\n"

    email_text += "📊 Simulation Model:\n"
    for i, row in games_df.iterrows():
        email_text += f"- {row['matchup']} (spread: {row['spread']}) → {sim_probs[i]*100:.1f}% upset chance\n"

    email_text += "\n🧠 Logistic Regression Model:\n"
    for i, row in games_df.iterrows():
        email_text += f"- {row['matchup']} (spread: {row['spread']}) → {log_probs[i]*100:.1f}% upset chance\n"

    return email_text

def send_email(content):
    sender_email = "nnrichardson1.14@gmail.com"
    receiver_email = "nnrichardson1.14@gmail.com"
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Weekly CFB Predictions"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    part = MIMEText(content, "plain")
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

if __name__ == "__main__":
    df = fetch_mock_games()
    content = build_email_content(df)
    print(content)
    # Uncomment to enable:
    # send_email(content)