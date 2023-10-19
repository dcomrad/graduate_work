########
import logging
import smtplib
from email.message import EmailMessage

from utils.dto import Settings


def send_email(email: EmailMessage):
    smtp_settings = Settings()

    EMAIL = smtp_settings.smtp_login

    server = smtplib.SMTP_SSL(smtp_settings.smtp_host,smtp_settings.smtp_port)
    server.login(smtp_settings.smtp_login,smtp_settings.smtp_password)

    message = email

    
    try:
        server.sendmail(EMAIL, [EMAIL], message.as_string())
    except smtplib.SMTPException as exc:
        reason = f'{type(exc).__name__}: {exc}'
        logging.exception(f'Не удалось отправить письмо. {reason}')
    else:
        logging.info('Письмо отправлено!')
    finally:
        server.close()

