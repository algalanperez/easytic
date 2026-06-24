import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/gmail.readonly",
]

DRIVE_FOLDER_EMITIDAS = os.getenv("DRIVE_FOLDER_FACTURAS_EMITIDAS")
DRIVE_FOLDER_RECIBIDAS = os.getenv("DRIVE_FOLDER_FACTURAS_RECIBIDAS")
GMAIL_LABEL = os.getenv("GMAIL_LABEL_FACTURAS", "facturas")

EMPRESA_NIF = os.getenv("EMPRESA_NIF", "")
EMPRESA_NOMBRE = os.getenv("EMPRESA_NOMBRE", "")
EMPRESA_EJERCICIO = int(os.getenv("EMPRESA_EJERCICIO", "2025"))

DB_PATH = os.getenv("DB_PATH", "contabilidad.db")

# Modelo principal para razonamiento; haiku para parseo masivo de facturas
CLAUDE_MODEL_AGENT = "claude-sonnet-4-6"
CLAUDE_MODEL_PARSER = "claude-haiku-4-5-20251001"

# Panel web
WEB_HOST = os.getenv("WEB_HOST", "127.0.0.1")
WEB_PORT = int(os.getenv("WEB_PORT", "8080"))
WEB_USER = os.getenv("WEB_USER", "")  # vacío → sin autenticación (dev local)
WEB_PASS = os.getenv("WEB_PASS", "")
EXPORT_DIR = os.getenv("EXPORT_DIR", "exports")

# Notificaciones email (opcional)
SMTP_HOST     = os.getenv("SMTP_HOST", "")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASS     = os.getenv("SMTP_PASS", "")
SMTP_FROM     = os.getenv("SMTP_FROM", SMTP_USER)
NOTIFY_TO     = os.getenv("NOTIFY_TO", "")       # email(s) separados por coma
