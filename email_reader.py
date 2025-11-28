import imaplib
import email
import os
from email.header import decode_header
from dotenv import load_dotenv
load_dotenv()

IMAP_SERVER = "pop.gmail.com"
EMAIL_ADDRESS = os.getenv("g_email")
EMAIL_PASSWORD = os.getenv("g_app_password")

def connect_imap():
    print("Connected to inbox successfully via IMAP")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    return mail

def fetch_unread_emails(max_count=20):
    print("Reading emails")
    mail = connect_imap()
    mail.select("inbox")

    print(mail.search(None, '(UNSEEN)'))
    status, data = mail.search(None, '(UNSEEN)')
    if status != "OK":
        return []
    print("emaildata: ",data)
    email_ids = data[0].split()
    email_ids = email_ids[-max_count:]  # last max_count emails

    emails = []

    for eid in email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1])
        # msg_id_header = msg.get("Message-ID", "")
        subject = decode_mime_header(msg.get("Subject"))
        # print(" email msg: ", msg)
        # print('got subject !')
        from_ = msg.get("From")
        # print('got from !')
        body = extract_body(msg)
        print(f'''got subject,from & body from email {eid}!''')

        emails.append({
            "id": eid.decode(),
            "subject": subject,
            "from": from_,
            "body": body,
            # "message_id": msg_id_header,
        })

    mail.close()
    mail.logout()
    return emails

def decode_mime_header(val):
    # print('called decode_mime_header')
    if not val:
        return ""
    decoded_parts = decode_header(val)
    parts = []
    for text, enc in decoded_parts:
        if isinstance(text, bytes):
            parts.append(text.decode(enc or "utf-8", errors="ignore"))
        else:
            parts.append(text)
    return "".join(parts)

def extract_body(msg):
    print('Extracting body')
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_dispo = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_dispo:
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode("utf-8", errors="ignore")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode("utf-8", errors="ignore")
    return ""