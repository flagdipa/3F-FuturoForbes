import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlmodel import Session, select
from ..core.database import engine
from ..models.models_config import Configuracion
import logging

def get_smtp_config():
    """Retrieves SMTP configuration from database."""
    config = {
        'host': '',
        'port': 587,
        'user': '',
        'password': '',
        'from': 'noreply@3f.com'
    }
    
    with Session(engine) as session:
        settings = session.exec(select(Configuracion).where(Configuracion.clave.like('SMTP_%'))).all()
        for s in settings:
            if s.clave == 'SMTP_host': config['host'] = s.valor
            if s.clave == 'SMTP_port': config['port'] = int(s.valor) if s.valor.isdigit() else 587
            if s.clave == 'SMTP_user': config['user'] = s.valor
            if s.clave == 'SMTP_password': config['password'] = s.valor
            if s.clave == 'SMTP_from': config['from'] = s.valor
            
    return config

def send_email(to_email: str, subject: str, html_content: str):
    """Sends an email using configured SMTP settings."""
    smtp_cfg = get_smtp_config()
    
    if not smtp_cfg['host']:
        logging.warning(f"SMTP NOT CONFIGURED. Email to {to_email} not sent. Content: {subject}")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_cfg['from']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # Connect and send
        server = smtplib.SMTP(smtp_cfg['host'], smtp_cfg['port'])
        server.starttls()
        if smtp_cfg['user'] and smtp_cfg['password']:
            server.login(smtp_cfg['user'], smtp_cfg['password'])
        
        server.send_message(msg)
        server.quit()
        
        logging.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {str(e)}")
        return False
