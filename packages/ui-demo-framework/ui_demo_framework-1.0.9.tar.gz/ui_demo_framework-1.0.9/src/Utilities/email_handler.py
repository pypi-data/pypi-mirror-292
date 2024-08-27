import email
import imaplib
import os
import re
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Utilities.log_handler import Logger
from Utilities.read_properties import ReadConfig


class EmailHandler:
    def __init__(self):
        self.log = Logger.setup_logging()
        self.read_config = ReadConfig()
        self.email_details = self.read_config.get_email_details()
        self.bluemail_details = self.read_config.get_bluemail_details()
        self.email_host = self.email_details['host']
        self.email_username = self.email_details['username']
        self.email_password = self.email_details['password']
        self.bluemail_host = self.bluemail_details['host']
        self.bluemail_username = self.bluemail_details['username']
        self.bluemail_password = self.bluemail_details['password']

    def fetch_unseen_emails(self, folder="Automation"):
        return self._fetch_unseen_emails(self.email_host, self.email_username, self.email_password, folder)

    def fetch_bluemail_unseen_emails(self, folder="INBOX"):
        return self._fetch_unseen_emails(self.bluemail_host, self.bluemail_username, self.bluemail_password, folder)

    def _fetch_unseen_emails(self, host, username, password, folder):
        try:
            mail = imaplib.IMAP4_SSL(host)
            mail.login(username, password)
            mail.select(folder)
            result, data = mail.search(None, 'UNSEEN')
            if result != "OK" or not data or not data[0]:
                self.log.error(f"No unseen emails found in folder '{folder}'. Result: {result}, Data: {data}")
                return []

            unread_messages = []
            for num in data[0].split():
                result, data = mail.fetch(num, '(RFC822)')
                if result != "OK" or not data or not data[0]:
                    self.log.error(f"Error fetching email with ID {num}. Result: {result}, Data: {data}")
                    continue

                email_message = email.message_from_bytes(data[0][1])
                message_data = {
                    'subject': email_message['subject'],
                    'to': email_message['to'],
                    'from': email_message['from'],
                    'date': email_message['date'],
                    'body': None,
                    'html_body': None
                }
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain" and not message_data['body']:
                        message_data['body'] = part.get_payload(decode=True).decode()
                    elif content_type == "text/html" and not message_data['html_body']:
                        message_data['html_body'] = part.get_payload(decode=True).decode()

                unread_messages.append(message_data)

            mail.close()
            mail.logout()
            return unread_messages

        except Exception as e:
            self.log.error("Error fetching unseen emails: %s", e)
            return []

    def mark_all_as_seen(self, folder="Automation"):
        return self._mark_all_as_seen(self.email_host, self.email_username, self.email_password, folder)

    def mark_all_bluemail_as_seen(self, folder="INBOX"):
        return self._mark_all_as_seen(self.bluemail_host, self.bluemail_username, self.bluemail_password, folder)

    def _mark_all_as_seen(self, host, username, password, folder):
        try:
            mail = imaplib.IMAP4_SSL(host)
            mail.login(username, password)
            mail.select(folder)
            result, data = mail.search(None, 'UNSEEN')
            if result != "OK" or not data:
                self.log.error(f"No unseen emails to mark as seen in folder '{folder}'. Result: {result}, Data: {data}")
                return

            for num in data[0].split():
                mail.store(num, '+FLAGS', '\\SEEN')
            mail.close()
            mail.logout()
            self.log.info("All unseen emails marked as seen.")
        except Exception as e:
            self.log.error("Error marking emails as seen: %s", e)

    def send_email(self, subject, message_text, recipients, attachment_file=None):
        return self._send_email(self.email_host, self.email_username, self.email_password, subject, message_text,
                                recipients, attachment_file)

    def send_bluemail(self, subject, message_text, recipients, attachment_file=None):
        return self._send_email(self.bluemail_host, self.bluemail_username, self.bluemail_password, subject,
                                message_text, recipients, attachment_file)

    def _send_email(self, host, username, password, subject, message_text, recipients, attachment_file=None):
        try:
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject

            body = MIMEText(message_text, 'plain')
            msg.attach(body)

            if attachment_file:
                with open(attachment_file, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(attachment_file)}')
                    msg.attach(part)

            if host == self.email_details['host']:
                server = smtplib.SMTP('smtp.gmail.com', 587)
            elif host == self.bluemail_details['host']:
                server = smtplib.SMTP(self.bluemail_details['smtp_host'], 587)
            else:
                self.log.error("Unsupported email host.")
                return

            server.starttls()
            server.login(username, password)
            server.sendmail(username, recipients, msg.as_string())
            server.quit()
            self.log.info("Email sent successfully.")
        except Exception as e:
            self.log.error("Error sending email: %s", e)

    def find_verification_link(self, message):
        try:
            verification_link = re.search(r'href="(.*?)"', message['html_body']).group(1)
            self.log.info("Verification link found: %s", verification_link)
            return verification_link
        except Exception as e:
            self.log.error("Error finding verification link: %s", e)
            return None

    @staticmethod
    def send_email_by_gmail():
        email_handler = EmailHandler()
        subject = "Pytest Report"
        message_text = "This is an automated email with the pytest report attached."
        recipients = email_handler.read_config.get_to_email_contacts().split(',')
        email_handler.send_email(subject, message_text, recipients)
