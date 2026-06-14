"""
Extrae datos estructurados de una factura usando Claude (visión o texto).

Soporta:
  - PDF  → extrae texto con pdfplumber; si está escaneado, manda imagen a Claude
  - PNG/JPEG → manda directamente a Claude vision
  - CSV  → parsea con pandas
"""
import base64
import csv
import hashlib
import io
import json
from typing import Any

import anthropic
import pdfplumber
from PIL import Image

import config

_client: anthropic.Anthropic | None = None

EXTRACTION_PROMPT = """Eres un sistema de extracción de datos de facturas españolas.

Analiza el documento y devuelve ÚNICAMENTE un objeto JSON con estos campos:
{
  "numero": "número de factura o null",
  "fecha": "YYYY-MM-DD o null",
  "nif_emisor": "NIF/CIF del emisor o null",
  "nombre_emisor": "nombre/razón social del emisor o null",
  "nif_receptor": "NIF/CIF del receptor o null",
  "nombre_receptor": "nombre/razón social del receptor o null",
  "base_imponible": número_decimal,
  "tipo_iva": porcentaje_decimal (ej. 21, 10, 4, 0),
  "cuota_iva": número_decimal,
  "tipo_retencion": porcentaje_decimal (ej. 15, 7, 0),
  "cuota_retencion": número_decimal,
  "total": número_decimal,
  "concepto": "descripción breve del servicio/producto"
}

Si un campo no aparece en el documento, usa null para texto o 0 para números.
No incluyas explicaciones, sólo el JSON."""


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


def _content_id(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()[:16]


def parse_pdf(content: bytes) -> dict:
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception:
        pass

    if len(text.strip()) > 50:
        return _extract_from_text(text)
    # PDF escaneado: convertir primera página a imagen
    return _extract_from_pdf_as_image(content)


def parse_image(content: bytes, mime_type: str = "image/jpeg") -> dict:
    b64 = base64.standard_b64encode(content).decode()
    msg = _get_client().messages.create(
        model=config.CLAUDE_MODEL_PARSER,
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": mime_type, "data": b64}},
                {"type": "text", "text": EXTRACTION_PROMPT},
            ],
        }],
    )
    return _parse_response(msg.content[0].text)


def parse_csv_row(row: dict) -> dict:
    """Mapea una fila de CSV/Excel ya leída a la estructura de factura."""
    def _num(v: Any) -> float:
        try:
            return float(str(v).replace(",", ".").replace("€", "").strip() or 0)
        except ValueError:
            return 0.0

    # Intenta mapear nombres de columnas comunes en español
    col = {k.lower().strip(): v for k, v in row.items()}
    base = _num(col.get("base imponible") or col.get("base") or col.get("importe") or 0)
    iva_pct = _num(col.get("% iva") or col.get("tipo iva") or col.get("iva%") or 21)
    cuota = _num(col.get("cuota iva") or col.get("iva") or 0)
    if not cuota and base:
        cuota = round(base * iva_pct / 100, 2)

    return {
        "numero":           col.get("nº factura") or col.get("numero") or col.get("factura"),
        "fecha":            _normalize_date(col.get("fecha") or col.get("date")),
        "nif_emisor":       col.get("nif emisor") or col.get("nif proveedor") or col.get("cif"),
        "nombre_emisor":    col.get("emisor") or col.get("proveedor") or col.get("empresa"),
        "nif_receptor":     col.get("nif receptor") or col.get("nif cliente"),
        "nombre_receptor":  col.get("receptor") or col.get("cliente"),
        "base_imponible":   base,
        "tipo_iva":         iva_pct,
        "cuota_iva":        cuota,
        "tipo_retencion":   _num(col.get("% ret") or col.get("retencion%") or 0),
        "cuota_retencion":  _num(col.get("retencion") or col.get("ret. irpf") or 0),
        "total":            _num(col.get("total") or col.get("importe total") or 0),
        "concepto":         col.get("concepto") or col.get("descripcion") or "",
    }


# ── helpers ───────────────────────────────────────────────────────────────────

def _extract_from_text(text: str) -> dict:
    msg = _get_client().messages.create(
        model=config.CLAUDE_MODEL_PARSER,
        max_tokens=512,
        messages=[{"role": "user", "content": f"{EXTRACTION_PROMPT}\n\nTEXTO:\n{text[:8000]}"}],
    )
    return _parse_response(msg.content[0].text)


def _extract_from_pdf_as_image(content: bytes) -> dict:
    """Convierte la primera página del PDF a PNG y la manda a visión."""
    try:
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(content, first_page=1, last_page=1, dpi=150)
        buf = io.BytesIO()
        images[0].save(buf, format="PNG")
        return parse_image(buf.getvalue(), "image/png")
    except Exception:
        return _empty_invoice()


def _parse_response(text: str) -> dict:
    text = text.strip()
    # Extrae el bloque JSON aunque venga envuelto en ```json ... ```
    if "```" in text:
        start = text.find("{")
        end = text.rfind("}") + 1
        text = text[start:end]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return _empty_invoice()
    return {k: data.get(k) for k in _empty_invoice()}


def _empty_invoice() -> dict:
    return {
        "numero": None, "fecha": None,
        "nif_emisor": None, "nombre_emisor": None,
        "nif_receptor": None, "nombre_receptor": None,
        "base_imponible": 0.0, "tipo_iva": 21.0, "cuota_iva": 0.0,
        "tipo_retencion": 0.0, "cuota_retencion": 0.0,
        "total": 0.0, "concepto": None,
    }


def _normalize_date(val: Any) -> str | None:
    if not val:
        return None
    s = str(val).strip()
    # DD/MM/YYYY → YYYY-MM-DD
    import re
    m = re.match(r"(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})", s)
    if m:
        return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    # Ya en formato ISO
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return s[:10]
    return s
