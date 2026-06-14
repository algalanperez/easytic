"""
Gestión del flujo OAuth2 para Google Drive y Gmail.

Primera ejecución: abre el navegador para autorizar.
Ejecuciones posteriores: reutiliza token.json.
"""
import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import config

_creds: Credentials | None = None


def get_credentials() -> Credentials:
    global _creds
    if _creds and _creds.valid:
        return _creds

    token_path = Path(config.GOOGLE_TOKEN_FILE)
    if token_path.exists():
        _creds = Credentials.from_authorized_user_file(str(token_path), config.GOOGLE_SCOPES)

    if not _creds or not _creds.valid:
        if _creds and _creds.expired and _creds.refresh_token:
            _creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.GOOGLE_CREDENTIALS_FILE, config.GOOGLE_SCOPES
            )
            _creds = flow.run_local_server(port=0)
        token_path.write_text(_creds.to_json())

    return _creds


def drive_service():
    return build("drive", "v3", credentials=get_credentials())


def gmail_service():
    return build("gmail", "v1", credentials=get_credentials())
