"""
Conector Google Drive: lista y descarga archivos de facturas.
Soporta PDF, imágenes (PNG/JPG) y hojas de cálculo (exportadas a CSV).
"""
import io
import mimetypes
from typing import Iterator

from googleapiclient.http import MediaIoBaseDownload

import config
from connectors.google_auth import drive_service

MIME_PDF   = "application/pdf"
MIME_PNG   = "image/png"
MIME_JPEG  = "image/jpeg"
MIME_SHEET = "application/vnd.google-apps.spreadsheet"
MIME_CSV   = "text/csv"

SUPPORTED_MIMES = {MIME_PDF, MIME_PNG, MIME_JPEG, MIME_SHEET, MIME_CSV}


def list_invoice_files(
    folder_id: str | None = None,
    date_from: str | None = None,   # "YYYY-MM-DD"
    date_to: str | None = None,
    page_size: int = 200,
) -> list[dict]:
    """
    Devuelve metadatos de archivos en Drive que pueden ser facturas.
    Si no se especifica folder_id usa las carpetas configuradas en .env.
    """
    svc = drive_service()
    folders = []
    if folder_id:
        folders = [folder_id]
    else:
        for f in [config.DRIVE_FOLDER_EMITIDAS, config.DRIVE_FOLDER_RECIBIDAS]:
            if f:
                folders.append(f)

    mime_filter = " or ".join(f"mimeType='{m}'" for m in SUPPORTED_MIMES)
    date_filter = ""
    if date_from:
        date_filter += f" and modifiedTime >= '{date_from}T00:00:00'"
    if date_to:
        date_filter += f" and modifiedTime <= '{date_to}T23:59:59'"

    results: list[dict] = []
    for fid in (folders or [None]):
        parent_filter = f"'{fid}' in parents and " if fid else ""
        q = f"{parent_filter}({mime_filter}) and trashed=false{date_filter}"
        page_token = None
        while True:
            resp = svc.files().list(
                q=q,
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
                pageToken=page_token,
            ).execute()
            results.extend(resp.get("files", []))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

    return results


def download_file(file_id: str, mime_type: str) -> bytes:
    """
    Descarga el contenido de un archivo de Drive.
    Las hojas de cálculo se exportan como CSV.
    """
    svc = drive_service()
    buf = io.BytesIO()

    if mime_type == MIME_SHEET:
        req = svc.files().export_media(fileId=file_id, mimeType=MIME_CSV)
    else:
        req = svc.files().get_media(fileId=file_id)

    downloader = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    return buf.getvalue()
