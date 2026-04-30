import smtplib, os
from email.mime.text import MIMEText

def send_mail(result):
    try:
        msg = MIMEText(f"""
Risk: {result['risk']}
Durum: {result['label']}
Açıklama: {result['reason']}
""")

        msg["Subject"] = "DEFANS ANALİZ"
        msg["From"] = os.getenv("EMAIL_USER")

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))

        server.sendmail(
            os.getenv("EMAIL_USER"),
            [os.getenv("MAIL_TO1"), os.getenv("MAIL_TO2")],
            msg.as_string()
        )
        server.quit()
    except:
        pass