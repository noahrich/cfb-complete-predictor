# main.py: Weekly email sender with prop insights
import os
import smtplib
from email.mime.text import MIMEText

def fetch_prop_summary():
    return """Jayden Daniels (LSU, QB): PASS YDS
• Market: Over 295.5 | Model: 318.7 | Hit Rate: 68% | Edge: +23.2
"""

def send_email():
    sender = "your_email@gmail.com"
    recipient = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_PASSWORD")

    content = fetch_prop_summary()
    msg = MIMEText(content)
    msg["Subject"] = "📊 Weekly CFB Prop Picks"
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

if __name__ == "__main__":
    send_email()