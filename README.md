# 🏈 College Football Player Props Dashboard

This app is a live, data-driven dashboard for exploring NCAA college football player props. It combines real-time betting lines with historical performance stats to calculate edge, hit rates, and suggested bets.

---

## 🚀 Features

- 📊 **Player Prop Explorer**  
  - Pulls live player prop lines from [TheOddsAPI](https://the-odds-api.com/)
  - Enhances with player performance stats from [CollegeFootballData API (CFBD)](https://collegefootballdata.com/)
  - Filters: Team, Stat Type, Position (future)
  - Computes model projection (average last 5 games), hit %, and edge
  - Highlights top suggested bets (Edge > 10, Hit% > 60%)

- 📧 **Email Script (main.py)**  
  - Optional script to send top props to your inbox weekly
  - Securely pulls from `.env` or GitHub Secrets

---

## 📦 Project Structure

```
CFB_Live_Props_Stats_Integrated/
│
├── app.py               # Streamlit dashboard with live player props
├── main.py              # Email automation script (optional)
├── requirements.txt     # Python dependencies
├── .env.template        # Template for API keys and secrets
└── README.md            # This documentation
```

---

## 🔧 Setup Instructions

1. **Install Requirements**
```bash
pip install -r requirements.txt
```

2. **Add API Keys**  
   Create a `.env` file or set these as GitHub/Render secrets:
```
ODDS_API_KEY=your_odds_api_key
CFBD_API_KEY=your_cfbd_api_key
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_TO=recipient@example.com
```

3. **Run Locally**
```bash
streamlit run app.py
```

---

## 📤 Optional: Email Predictions

To automate sending weekly top props, configure `main.py` to run as a scheduled job (via Render or GitHub Actions).

---

## 🧠 Notes

- You must sign up for [TheOddsAPI](https://the-odds-api.com/) and [CFBD](https://collegefootballdata.com/) to get your keys.
- Some props may not match exactly by player name between systems. Future enhancements will support fuzzy matching and position detection.

---

## ✨ Example Output

| Player           | Team | Stat Type     | Prop Line | Model Proj | Hit % | Edge | Bookmaker |
|------------------|------|---------------|-----------|------------|-------|------|-----------|
| Jayden Daniels   | LSU  | Passing Yards | 295.5     | 318.7      | 0.68  | 23.2 | DraftKings|

---

Made with ❤️ for college football data enthusiasts.