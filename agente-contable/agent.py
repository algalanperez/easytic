"""
Agente contable de EasyTic.

Orquesta las tools mediante el API de Claude con tool_use.
El bucle principal procesa mensajes hasta que Claude devuelve stop_reason='end_turn'.
"""
import base64
import hashlib
import io
import json
from typing import Any

import anthropic

import config
from connectors import drive, gmail
from database import db
from tools import db_tools, parse_invoice, tax_calendar

# ── Definición de tools para la API de Claude ─────────────────────────────────

TOOLS: list[dict] = [
    {
        "name": "drive_list_files",
        "description": "Lista archivos de facturas en Google Drive para un período.",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder_id": {"type": "string", "description": "ID de carpeta en Drive (opcional)"},
                "date_from":  {"type": "string", "description": "Fecha inicio YYYY-MM-DD"},
                "date_to":    {"type": "string", "description": "Fecha fin YYYY-MM-DD"},
            },
        },
    },
    {
        "name": "drive_parse_invoice",
        "description": "Descarga un archivo de Drive y extrae sus datos de factura.",
        "input_schema": {
            "type": "object",
            "required": ["file_id", "mime_type", "tipo"],
            "properties": {
                "file_id":   {"type": "string"},
                "mime_type": {"type": "string"},
                "tipo":      {"type": "string", "enum": ["emitida", "recibida"]},
                "file_name": {"type": "string"},
            },
        },
    },
    {
        "name": "gmail_search_invoices",
        "description": "Busca emails con adjuntos de facturas en Gmail.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date_from":   {"type": "string", "description": "YYYY-MM-DD"},
                "date_to":     {"type": "string", "description": "YYYY-MM-DD"},
                "max_results": {"type": "integer", "default": 50},
            },
        },
    },
    {
        "name": "gmail_parse_attachment",
        "description": "Descarga un adjunto de Gmail y extrae sus datos de factura.",
        "input_schema": {
            "type": "object",
            "required": ["message_id", "attachment_id", "mime_type"],
            "properties": {
                "message_id":    {"type": "string"},
                "attachment_id": {"type": "string"},
                "mime_type":     {"type": "string"},
                "filename":      {"type": "string"},
            },
        },
    },
    {
        "name": "upsert_factura",
        "description": "Guarda o actualiza una factura en el libro contable.",
        "input_schema": {
            "type": "object",
            "required": ["tipo", "fecha", "base_imponible", "cuota_iva", "total", "fuente"],
            "properties": {
                "tipo":            {"type": "string", "enum": ["emitida", "recibida"]},
                "numero":          {"type": "string"},
                "fecha":           {"type": "string"},
                "nif_emisor":      {"type": "string"},
                "nombre_emisor":   {"type": "string"},
                "nif_receptor":    {"type": "string"},
                "nombre_receptor": {"type": "string"},
                "base_imponible":  {"type": "number"},
                "tipo_iva":        {"type": "number"},
                "cuota_iva":       {"type": "number"},
                "tipo_retencion":  {"type": "number"},
                "cuota_retencion": {"type": "number"},
                "total":           {"type": "number"},
                "concepto":        {"type": "string"},
                "fuente":          {"type": "string"},
                "fuente_id":       {"type": "string"},
            },
        },
    },
    {
        "name": "query_facturas",
        "description": "Consulta facturas almacenadas con filtros opcionales.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tipo":        {"type": "string", "enum": ["emitida", "recibida"]},
                "fecha_desde": {"type": "string"},
                "fecha_hasta": {"type": "string"},
                "fuente":      {"type": "string"},
            },
        },
    },
    {
        "name": "resumen_periodo",
        "description": "Devuelve resumen contable de un período: bases, IVA devengado/soportado, resultado.",
        "input_schema": {
            "type": "object",
            "required": ["fecha_desde", "fecha_hasta"],
            "properties": {
                "fecha_desde": {"type": "string"},
                "fecha_hasta": {"type": "string"},
            },
        },
    },
    {
        "name": "raw_query",
        "description": "Ejecuta una consulta SQL SELECT sobre la base de datos contable.",
        "input_schema": {
            "type": "object",
            "required": ["sql"],
            "properties": {"sql": {"type": "string"}},
        },
    },
    {
        "name": "get_tax_calendar",
        "description": "Devuelve el calendario de vencimientos fiscales de un ejercicio.",
        "input_schema": {
            "type": "object",
            "properties": {"ejercicio": {"type": "integer"}},
        },
    },
    {
        "name": "get_upcoming_deadlines",
        "description": "Devuelve los vencimientos fiscales que caen en los próximos N días.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days_ahead": {"type": "integer", "default": 30},
                "ejercicio":  {"type": "integer"},
            },
        },
    },
]

SYSTEM_PROMPT = f"""Eres el asistente contable y fiscal de {config.EMPRESA_NOMBRE} (NIF: {config.EMPRESA_NIF}).

Tu misión:
1. Recopilar y centralizar facturas emitidas y recibidas desde Google Drive, Gmail y otros orígenes.
2. Mantener actualizado el libro contable en la base de datos SQLite.
3. Calcular la posición fiscal trimestral: IVA (Modelo 303), IRPF (Modelo 111).
4. Alertar sobre vencimientos fiscales próximos.
5. Responder preguntas sobre la situación contable y fiscal de la empresa.

Normas:
- Usa siempre fechas en formato ISO (YYYY-MM-DD).
- Cuando proceses facturas de Drive o Gmail, guárdalas con upsert_factura antes de responder.
- Para calcular el resultado de IVA de un trimestre: usa resumen_periodo con el rango de fechas del trimestre.
- El IVA general en España es 21%. Servicios digitales: 21%. Reducido: 10%. Superreducido: 4%.
- Retención IRPF profesionales: 15% general (7% primeros 3 años de actividad).
- Nunca inventes datos; si no tienes información, dilo y sugiere qué fuente consultar.

Ejercicio fiscal en curso: {config.EMPRESA_EJERCICIO}.
"""


# ── Ejecución de tools ─────────────────────────────────────────────────────────

def _run_tool(name: str, inputs: dict) -> Any:
    if name == "drive_list_files":
        return drive.list_invoice_files(
            folder_id=inputs.get("folder_id"),
            date_from=inputs.get("date_from"),
            date_to=inputs.get("date_to"),
        )

    elif name == "drive_parse_invoice":
        content = drive.download_file(inputs["file_id"], inputs["mime_type"])
        if inputs["mime_type"] == "application/pdf":
            data = parse_invoice.parse_pdf(content)
        else:
            data = parse_invoice.parse_image(content, inputs["mime_type"])
        data["fuente"] = "drive"
        data["fuente_id"] = inputs["file_id"]
        data["tipo"] = inputs["tipo"]
        if not data.get("concepto") and inputs.get("file_name"):
            data["concepto"] = inputs["file_name"]
        return data

    elif name == "gmail_search_invoices":
        return gmail.search_invoice_emails(
            date_from=inputs.get("date_from"),
            date_to=inputs.get("date_to"),
            max_results=inputs.get("max_results", 50),
        )

    elif name == "gmail_parse_attachment":
        content = gmail.download_attachment(inputs["message_id"], inputs["attachment_id"])
        if inputs["mime_type"] == "application/pdf":
            data = parse_invoice.parse_pdf(content)
        else:
            data = parse_invoice.parse_image(content, inputs["mime_type"])
        data["fuente"] = "gmail"
        data["fuente_id"] = f"{inputs['message_id']}:{inputs['attachment_id']}"
        data["tipo"] = "recibida"  # los adjuntos de Gmail son facturas de proveedores
        if not data.get("concepto") and inputs.get("filename"):
            data["concepto"] = inputs["filename"]
        return data

    elif name == "upsert_factura":
        return db_tools.tool_upsert_factura(inputs)

    elif name == "query_facturas":
        return db_tools.tool_query_facturas(
            tipo=inputs.get("tipo"),
            fecha_desde=inputs.get("fecha_desde"),
            fecha_hasta=inputs.get("fecha_hasta"),
            fuente=inputs.get("fuente"),
        )

    elif name == "resumen_periodo":
        return db_tools.tool_resumen_periodo(inputs["fecha_desde"], inputs["fecha_hasta"])

    elif name == "raw_query":
        return db_tools.tool_raw_query(inputs["sql"])

    elif name == "get_tax_calendar":
        return tax_calendar.get_tax_calendar(
            inputs.get("ejercicio", config.EMPRESA_EJERCICIO)
        )

    elif name == "get_upcoming_deadlines":
        return tax_calendar.get_upcoming_deadlines(
            days_ahead=inputs.get("days_ahead", 30),
            ejercicio=inputs.get("ejercicio"),
        )

    else:
        return {"error": f"Tool desconocida: {name}"}


# ── Bucle del agente ──────────────────────────────────────────────────────────

class ContableAgent:
    def __init__(self):
        self._client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self._messages: list[dict] = []

    def chat(self, user_message: str) -> str:
        """Envía un mensaje al agente y devuelve su respuesta final."""
        self._messages.append({"role": "user", "content": user_message})

        while True:
            response = self._client.messages.create(
                model=config.CLAUDE_MODEL_AGENT,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=self._messages,
            )

            # Acumula el turno del asistente
            self._messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                # Extrae el texto de la respuesta final
                text_blocks = [b.text for b in response.content if hasattr(b, "text")]
                return "\n".join(text_blocks)

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue
                    print(f"  → tool: {block.name}({json.dumps(block.input, ensure_ascii=False)[:120]})")
                    try:
                        result = _run_tool(block.name, block.input)
                    except Exception as exc:
                        result = {"error": str(exc)}
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    })
                self._messages.append({"role": "user", "content": tool_results})

            else:
                # stop_reason inesperado
                break

        return "[El agente terminó sin respuesta]"

    def reset(self) -> None:
        self._messages = []
