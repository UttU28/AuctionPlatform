# Email sending logic
# utils/email_utils.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def sendOtpEmail(recipientEmail, otp):
    senderEmail = 'your-email@example.com'
    senderPassword = 'your-email-password'
    
    subject = 'Your OTP for Password Reset'
    body = f'Your OTP for resetting your password is: {otp}'

    msg = MIMEMultipart()
    msg['From'] = senderEmail
    msg['To'] = recipientEmail
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login(senderEmail, senderPassword)
        server.sendmail(senderEmail, recipientEmail, msg.as_string())
        server.close()
        print('Email sent successfully!')
    except Exception as e:
        print(f"Failed to send email: {e}")
