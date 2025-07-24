[![Weekly Email](https://github.com/your-username/CFB_Live_Full_App/actions/workflows/cfb_email.yaml/badge.svg)](https://github.com/your-username/CFB_Live_Full_App/actions)

https://cfb-complete-predictor-4bufsc5yv2snuddhiqwnds.streamlit.app/

# 🏈 CFB Live Predictor

This project predicts college football upsets, covers, and confidence picks using logistic regression and simulation models, powered by live data from CollegeFootballData and TheOddsAPI.

## 🚀 Features

- Live game schedule and spreads
- Upset probabilities (simulated & logistic)
- Cover probability estimates
- Confidence index and suggested picks
- Injury reports per matchup
- Automated weekly email alerts (via GitHub Actions or Render)
- Streamlit dashboard for exploration

## 📦 Files

| File        | Purpose                                        |
|-------------|------------------------------------------------|
| `app.py`    | Streamlit dashboard                           |
| `main.py`   | Email sender with weekly predictions          |
| `.env.template` | Template for secrets and API keys         |
| `requirements.txt` | Python dependencies                    |

## 🛠 Setup

1. Clone or upload contents to GitHub.
2. Create `.env` based on `.env.template` and populate with your keys.
3. Deploy:
   - `app.py` on [Streamlit Cloud](https://streamlit.io/cloud)
   - `main.py` on [Render.com](https://render.com) or GitHub Actions as Cron

## 🔐 Required Environment Variables

```env
CFBD_API_KEY=your_cfbd_api_key
ODDS_API_KEY=your_odds_api_key
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_TO=your_email@example.com
```

## 🕒 GitHub Actions Automation

This repo includes a GitHub Actions workflow to auto-email weekly predictions:

- Trigger: Every Thursday at 9 AM UTC
- File: `.github/workflows/cfb_email.yaml`

Be sure to set these secrets in GitHub:

- `CFBD_API_KEY`
- `ODDS_API_KEY`
- `EMAIL_PASSWORD`
- `EMAIL_TO`

## ✅ License

MIT License
