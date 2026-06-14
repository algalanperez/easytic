import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

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
