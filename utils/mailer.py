import smtplib, os
from dotenv import load_dotenv

load_dotenv()

def send(msg):
    try:
        s = smtplib.SMTP("smtp.gmail.com",587)
        s.starttls()
        s.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))

        s.sendmail(os.getenv("EMAIL_USER"), os.getenv("EMAIL_TO_1"), msg)
        s.sendmail(os.getenv("EMAIL_USER"), os.getenv("EMAIL_TO_2"), msg)

        s.quit()
    except:
        pass