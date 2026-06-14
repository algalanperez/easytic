"""
Conector Gmail: busca correos con adjuntos de facturas.
Devuelve los adjuntos PDF/imagen listos para parsear.
"""
import base64
import re
from typing import Iterator

import config
from connectors.google_auth import gmail_service

ATTACHMENT_MIMES = {"application/pdf", "image/png", "image/jpeg"}


def search_invoice_emails(
    date_from: str | None = None,   # "YYYY/MM/DD"
    date_to: str | None = None,
    label: str | None = None,
    max_results: int = 100,
) -> list[dict]:
    """
    Devuelve lista de mensajes con adjuntos que pueden ser facturas.
    Cada elemento incluye: message_id, subject, date, attachments[].
    """
    svc = gmail_service()
    query_parts = ["has:attachment"]
    if label or config.GMAIL_LABEL:
        lbl = label or config.GMAIL_LABEL
        query_parts.append(f"label:{lbl}")
    if date_from:
        query_parts.append(f"after:{date_from.replace('-', '/')}")
    if date_to:
        query_parts.append(f"before:{date_to.replace('-', '/')}")

    query = " ".join(query_parts)
    resp = svc.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()
    messages = resp.get("messages", [])

    results = []
    for msg_stub in messages:
        msg = svc.users().messages().get(
            userId="me", id=msg_stub["id"], format="full"
        ).execute()
        info = _extract_message_info(msg)
        if info["attachments"]:
            results.append(info)

    return results


def download_attachment(message_id: str, attachment_id: str) -> bytes:
    svc = gmail_service()
    att = svc.users().messages().attachments().get(
        userId="me", messageId=message_id, id=attachment_id
    ).execute()
    return base64.urlsafe_b64decode(att["data"])


# ── helpers ───────────────────────────────────────────────────────────────────

def _extract_message_info(msg: dict) -> dict:
    headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
    attachments = []
    _walk_parts(msg["payload"], msg["id"], attachments)
    return {
        "message_id": msg["id"],
        "subject": headers.get("Subject", ""),
        "from": headers.get("From", ""),
        "date": headers.get("Date", ""),
        "attachments": attachments,
    }


def _walk_parts(part: dict, message_id: str, acc: list) -> None:
    mime = part.get("mimeType", "")
    body = part.get("body", {})
    if mime in ATTACHMENT_MIMES and body.get("attachmentId"):
        acc.append({
            "message_id": message_id,
            "filename": part.get("filename", "adjunto"),
            "mime_type": mime,
            "attachment_id": body["attachmentId"],
            "size": body.get("size", 0),
        })
    for subpart in part.get("parts", []):
        _walk_parts(subpart, message_id, acc)
