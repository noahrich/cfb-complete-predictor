import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression

st.set_page_config(page_title="CFB Upset Predictor", layout="wide")

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
def fetch_mock_games():
    return pd.DataFrame([
        {"Matchup": "Florida @ LSU", "Spread": -6.5},
        {"Matchup": "UTSA @ Texas", "Spread": -8.0},
        {"Matchup": "Miami @ Georgia Tech", "Spread": 2.5},
        {"Matchup": "Nebraska @ Colorado", "Spread": -1.5},
        {"Matchup": "Oregon @ Washington", "Spread": 3.0},
    ])

st.title("🏈 CFB Weekly Upset Predictions Dashboard")
st.markdown("Compare predictions between simulation and logistic regression models.")

df = fetch_mock_games()
df['Sim Upset %'] = df['Spread'].apply(simulate_model) * 100
df['Logistic Upset %'] = logistic_model(df['Spread']) * 100
df['Difference'] = df['Logistic Upset %'] - df['Sim Upset %']

st.subheader("🔢 Predictions Comparison")
st.dataframe(df.style.format({
    'Spread': '{:.1f}',
    'Sim Upset %': '{:.1f}%',
    'Logistic Upset %': '{:.1f}%',
    'Difference': '{:+.1f}%'
}))

st.subheader("📈 Model Comparison Chart")
st.bar_chart(df.set_index('Matchup')[['Sim Upset %', 'Logistic Upset %']])