import smtplib, ssl
import read_config

configs = read_config.read_config("C:/Users/roseh/PycharmProjects/AutomatedStockTrading/config.yml")

port = 465
password = configs["notify"]["pw"]
email = configs["notify"]["email"]
context = ssl.create_default_context()
subject = """\
Subject: STOCK COPY CAT RAN


"""


def send_email(message):
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(email, password)

        message = subject + message
        server.sendmail(email, email, message)