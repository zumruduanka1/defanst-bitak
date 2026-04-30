import smtplib
import os
from email.mime.text import MIMEText

def send_mail(to, result):
    try:
        msg = MIMEText(f"Analiz sonucu:\nRisk: {result['risk']}\nDurum: {result['label']}")
        msg["Subject"] = "DEFANS ANALİZ SONUCU"
        msg["From"] = os.getenv("EMAIL_USER")
        msg["To"] = to

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        server.send_message(msg)
        server.quit()
    except:
        pass