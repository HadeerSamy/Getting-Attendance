import tkinter as tk
import pandas as pd
import qrcode
import os
from tkinter import filedialog
import re
import smtplib
import ssl
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders

root = tk.Tk()
root.title("QrCodes Generator")
root.configure(bg="#FACDE5")
root.geometry("800x650")
def browse_file():

    filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    CSVConfirm.config(text= filename)
    return filename

def generateQR():
    df = pd.read_csv(f"{CSVConfirm.cget('text')}")
    os.makedirs(os.path.join(os.path.dirname(CSVConfirm.cget("text")),"qr_codes"))
    for index, row in df.iterrows():
        student_code = str(row[CodeColumnAnswer.get()]) 
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(student_code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qrPath = os.path.join(os.path.dirname(CSVConfirm.cget("text")),"qr_codes", student_code + ".png")
        img.save(qrPath)
        df.at[index, 'QR_Code_Path'] = qrPath
    df.to_csv(os.path.join(os.path.dirname(CSVConfirm.cget("text")),"studQr.csv"), index=False)

custom_font = ("Bartex", 16)
bC = "#FACDE5"
fC = "#E0218A"
CSVBrowse = tk.Label(root, text="Choose your CSV File:", bg=bC, fg=fC, font=custom_font)
CSVBrowse.pack()

browse_button = tk.Button(root, text="Browse", command=browse_file,
                          borderwidth=5,  bg=fC, fg="white")
browse_button.pack(pady=20)

CSVConfirm = tk.Label(root,  bg=bC, fg="grey")
CSVConfirm.pack()


EmailColumnAsk = tk.Label(root, text="What is the name of the emails' column?", bg=bC, fg=fC,font=custom_font)
EmailColumnAsk.pack()

EmailColumnAnswer = tk.Entry(root)
EmailColumnAnswer.pack()

CodeColumnAsk = tk.Label(root, text="What is the name of the codes' column?",bg=bC, fg=fC, font=custom_font)
CodeColumnAsk.pack()

CodeColumnAnswer = tk.Entry(root)
CodeColumnAnswer.pack()



QrCodeGenerator_button = tk.Button(root, text="Generate Qr Codes", command=generateQR, bg=fC, fg="white")
QrCodeGenerator_button.pack(pady=20)


# style = tk.Style()
# style.map("C.TButton",
#     foreground=[('pressed', 'red'), ('active', 'blue')],
#     background=[('pressed', '!disabled', 'black'), ('active', 'white')]
#     )

########################################################################################

def sendEmails():
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:

        try:    
            smtp.login(EmailAddressAnswer.get(), EmailPasswordAnswer.get())
        except:
            print("You provided wrong email and password")

        emailsDf = pd.read_csv(os.path.join(os.path.dirname(CSVConfirm.cget("text")),"studQr.csv"))
        for index, row in emailsDf.iterrows():

            email_receiver = row[EmailColumnAnswer.get()]

            em = EmailMessage()
            em['To'] = email_receiver
            em['Subject'] = EmailSubjectAnswer.get()
            em.set_content(EmailBodyAnswer.get("1.0", "end-1c"))


            with open(row["QR_Code_Path"], 'rb') as attachment_file:
                file_data = attachment_file.read()
                file_name = attachment_file.name.split("\\")[-1]

            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(file_data)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
            em.add_attachment(attachment)

            em['From'] = EmailAddressAnswer.get()
            
            smtp.sendmail(EmailAddressAnswer.get(), email_receiver, em.as_string())
            print (f"Email {index+1} is sent.")
    





EmailSubjectAsk = tk.Label(root, text="What is your email subject?",bg=bC, fg=fC, font=custom_font)
EmailSubjectAsk.pack()

EmailSubjectAnswer = tk.Entry(root)
EmailSubjectAnswer.pack()


EmailBodyAsk = tk.Label(root, text="What is your email body?",bg=bC, fg=fC, font=custom_font)
EmailBodyAsk.pack()

EmailBodyAnswer = tk.Text(root, height=5, width=40)
EmailBodyAnswer.pack(pady=20)


EmailAddressAsk = tk.Label(root, text="What is your email address?",bg=bC, fg=fC, font=custom_font)
EmailAddressAsk.pack()

EmailAddressAnswer = tk.Entry(root)
EmailAddressAnswer.pack()



EmailpasswordAsk = tk.Label(root, text="What is your email password?",bg=bC, fg=fC, font=custom_font)
EmailpasswordAsk.pack()

EmailPasswordAnswer = tk.Entry(root)
EmailPasswordAnswer.pack()

SendEmails_button = tk.Button(root, text="Send Emails", command=sendEmails,bg=fC, fg="white")
SendEmails_button.pack(pady=20)

root.mainloop()




