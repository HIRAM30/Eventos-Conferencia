# config.py
from flask_mail import Mail

# Configuración de Flask-Mail
mail = Mail()
import os

class Config:
    # Configuración de correo con Gmail SMTP
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587  # Usamos TLS, por lo tanto, puerto 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False  # No usar SSL si usas TLS
    MAIL_USERNAME = 'toral.carrera.yair@gmail.com'  # Tu correo de Gmail
    MAIL_PASSWORD = 'urjz gweo uach kymn'  # Contraseña de tu cuenta de Gmail o contraseña de aplicación si tienes 2FA
    MAIL_DEFAULT_SENDER = 'toral.carrera.yair@gmail.com'
