import pandas as pd
import qrcode
import os

csvFlag = 1

while csvFlag:
    file_pathy = input("please enter your csv file: ")
    if file_pathy.lower().endswith('.csv'):
        if os.path.exists(file_pathy):
            csvFlag= False
        else:
            print("That file doesn't exist")
    else:
        print("You didn't choose the right format!")


df = pd.read_csv(f"{file_pathy}")

emailFlag = 1
while emailFlag:
    emailCol = input("What is the name of the emails' column?")
    if emailCol in df.columns:
        emailFlag = False
    else:
        print("There's no such column with that name")


columnFlag = 1
while columnFlag:
    colCode = input("What is the name of the codes' column?")
    if colCode in df.columns:
        if os.path.exists(os.path.join(os.path.dirname(file_pathy),"qr_codes")):
            pass
        else:
            os.makedirs(os.path.join(os.path.dirname(file_pathy),"qr_codes"))
            for index, row in df.iterrows():
                student_code = str(row[colCode]) 
                qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
                qr.add_data(student_code)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                qrPath = os.path.join(os.path.dirname(file_pathy),"qr_codes", student_code + ".png")
                img.save(qrPath)
                df.at[index, 'QR_Code_Path'] = qrPath
        columnFlag = False
    else:
        print ("column name doesn't exist")


df.to_csv(os.path.join(os.path.dirname(file_pathy),"studQr.csv"), index=False)

import re
import smtplib
import ssl
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders


emailsDf = pd.read_csv(os.path.join(os.path.dirname(file_pathy),"studQr.csv"))
subject =  input("What is your email subject?   ")
body =  input("What is your email body?   ")


# Define email sender and receiver
emailFlag = 1
email_password = ""

def is_valid_gmail(email):
    global email_password
    global emailFlag
    # Regular expression pattern for a valid Gmail address
    gmail_pattern = f'^[a-zA-Z0-9._%+-]+@gmail.com$'
    
    # Check if the email matches the pattern
    if re.match(gmail_pattern, email):
        email_password =  input("What is your email password?    ")
        emailFlag = False

    else:
        pass





# Add SSL (layer of security)
loginFlag = 1  
context = ssl.create_default_context()
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    while loginFlag:
        emailFlag = 1
        while emailFlag:
            email_sender = input("What is your email?     ")
            is_valid_gmail(email_sender)
        try:    
            smtp.login(email_sender, email_password)
            loginFlag= False
        except:
            print("You provided wrong email and password")

    for index, row in emailsDf.iterrows():

        email_receiver = row[emailCol]

        em = EmailMessage()
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)


        with open(row["QR_Code_Path"], 'rb') as attachment_file:
            file_data = attachment_file.read()
            file_name = attachment_file.name.split("\\")[-1]

        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(file_data)
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
        em.add_attachment(attachment)

        em['From'] = email_sender
        
        smtp.sendmail(email_sender, email_receiver, em.as_string())
        print (f"Email {index+1} is sent.")
    