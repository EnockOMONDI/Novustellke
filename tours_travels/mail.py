import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def verification_mail(link, user):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()

    ei = "djseanizellkenya@gmail.com"
    password = "zjxdqtqsgxjygdiu"

    # print(ei, password)

    s.login(ei, password)
    msg = MIMEMultipart()
    print(link, user.email, type(user.email))
    msg['From'] = "Jungle Dream Adventures"
    msg['To'] = user.email
    msg['Subject'] = "Welcome to Jungle Dreams Adventures"
    message = 'Hi ' + user.username + ' welcome to Jungle Dreams Adventures. To activate your account, click the link below:\n' + link

    msg.attach(MIMEText(message, 'html'))
    s.send_message(msg)
    s.quit()

