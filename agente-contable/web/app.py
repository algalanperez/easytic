"""
Panel web del Agente Contable EasyTic.
FastAPI + Jinja2. Arranca con: python main.py --serve
"""
from __future__ import annotations

import io
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import config
from database import db
from database.db import get_conn
from tools.db_tools import tool_resumen_periodo
from tools.export_aeat import export_model, export_facturas_csv
from tools.modelo_200 import calculate_200
from tools.sii_check import check_sii_compliance
from tools.tax_calendar import (
    get_upcoming_deadlines, quarter_date_range, quarter_of_date,
)
from tools.tax_models import (
    calculate_303, calculate_111, generate_model_draft, list_liquidaciones,
)
import scheduler as sched_mod

BASE_DIR = Path(__file__).parent


# ── Lifespan: inicia BD + scheduler ──────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_conn()
    Path(config.EXPORT_DIR).mkdir(exist_ok=True)
    sched_mod.start()
    yield
    sched_mod.stop()


app = FastAPI(title="Agente Contable EasyTic", docs_url=None, redoc_url=None, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ── Contexto base ─────────────────────────────────────────────────────────────

def _ctx(request: Request, active: str = "", **extra) -> dict:
    # Starlette 1.x: request es el primer arg de TemplateResponse, no va en el contexto
    return {
        "active":         active,
        "empresa_nombre": config.EMPRESA_NOMBRE,
        "empresa_nif":    config.EMPRESA_NIF,
        "ejercicio":      config.EMPRESA_EJERCICIO,
        "today":          date.today().isoformat(),
        "flash":          request.query_params.get("flash"),
        "flash_level":    request.query_params.get("flash_level", "info"),
        **extra,
    }


def _redirect(path: str, flash: str, level: str = "success") -> RedirectResponse:
    from urllib.parse import quote
    return RedirectResponse(
        f"{path}?flash={quote(flash)}&flash_level={level}", status_code=303
    )


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    today = date.today()
    current_q = quarter_of_date(today.isoformat())
    fd, fh = quarter_date_range(config.EMPRESA_EJERCICIO, current_q)

    return templates.TemplateResponse(request, "dashboard.html", _ctx(
        request, "dashboard",
        deadlines      = get_upcoming_deadlines(45, config.EMPRESA_EJERCICIO),
        current_q      = current_q,
        resumen_q      = tool_resumen_periodo(fd, fh),
        resumen_anual  = tool_resumen_periodo(
            f"{config.EMPRESA_EJERCICIO}-01-01",
            f"{config.EMPRESA_EJERCICIO}-12-31",
        ),
        liquidaciones  = list_liquidaciones(config.EMPRESA_EJERCICIO),
        sii_resumen    = check_sii_compliance(
            fecha_desde=f"{config.EMPRESA_EJERCICIO}-01-01",
            fecha_hasta=today.isoformat(),
        )["resumen"],
    ))


# ── Facturas ──────────────────────────────────────────────────────────────────

@app.get("/facturas", response_class=HTMLResponse)
async def facturas_list(
    request: Request,
    tipo: str = "", desde: str = "", hasta: str = "", page: int = 1,
):
    PAGE = 25
    offset = (page - 1) * PAGE
    conds = ["1=1"]
    if tipo:  conds.append(f"tipo = '{tipo}'")
    if desde: conds.append(f"fecha >= '{desde}'")
    if hasta: conds.append(f"fecha <= '{hasta}'")
    where = " AND ".join(conds)

    total    = db.raw_query(f"SELECT COUNT(*) AS n FROM facturas WHERE {where}")[0]["n"]
    facturas = db.raw_query(
        f"SELECT * FROM facturas WHERE {where} ORDER BY fecha DESC LIMIT {PAGE} OFFSET {offset}"
    )
    return templates.TemplateResponse(request, "facturas.html", _ctx(
        request, "facturas",
        facturas    = facturas,
        total       = total,
        page        = page,
        page_size   = PAGE,
        total_pages = (total + PAGE - 1) // PAGE,
        filtros     = {"tipo": tipo, "desde": desde, "hasta": hasta},
    ))


@app.post("/facturas/exportar")
async def facturas_exportar(
    desde: str = Form(""), hasta: str = Form(""), tipo: str = Form(""),
):
    if not (desde and hasta):
        return _redirect("/facturas", "Especifica rango de fechas para exportar.", "warning")
    csv_data = export_facturas_csv(desde, hasta, tipo or None)
    filename = f"facturas_{desde}_{hasta}.csv"
    return StreamingResponse(
        io.BytesIO(csv_data.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Modelos / Liquidaciones ───────────────────────────────────────────────────

@app.get("/modelos", response_class=HTMLResponse)
async def modelos_list(request: Request):
    return templates.TemplateResponse(request, "modelos.html", _ctx(
        request, "modelos",
        liquidaciones = list_liquidaciones(),
        periodos      = ["Q1", "Q2", "Q3", "Q4"],
        current_q     = quarter_of_date(date.today().isoformat()),
    ))


@app.post("/modelos/calcular")
async def modelos_calcular(
    modelo: str = Form(...), periodo: str = Form(...), ejercicio: int = Form(...),
):
    try:
        generate_model_draft(modelo.upper(), ejercicio, periodo.upper())
        return _redirect("/modelos", f"Borrador Mod.{modelo} {periodo}/{ejercicio} guardado.")
    except Exception as e:
        return _redirect("/modelos", f"Error: {e}", "error")


@app.post("/modelos/exportar")
async def modelos_exportar_post(
    modelo: str = Form(...), periodo: str = Form(...), ejercicio: int = Form(...),
):
    try:
        outdir = Path(config.EXPORT_DIR)
        outdir.mkdir(exist_ok=True)
        result = export_model(
            modelo=modelo.upper(), ejercicio=ejercicio, periodo=periodo.upper(),
            output_path=str(outdir / f"modelo_{modelo.lower()}_{ejercicio}_{periodo.lower()}.{'xml' if modelo in ('303','111') else 'json'}"),
        )
        return _redirect("/modelos", f"Exportado: {result['fichero']} ({result['bytes']} bytes)")
    except Exception as e:
        return _redirect("/modelos", f"Error al exportar: {e}", "error")


@app.get("/modelos/download/{modelo}/{ejercicio}/{periodo}")
async def modelos_download(modelo: str, ejercicio: int, periodo: str):
    """Genera y descarga el modelo directamente sin guardar en disco."""
    modelo = modelo.upper()
    periodo = periodo.upper()
    try:
        result = export_model(
            modelo=modelo, ejercicio=ejercicio, periodo=periodo,
            output_path=f"/tmp/dl_{modelo}_{ejercicio}_{periodo}.tmp",
        )
        ext = result["formato"]
        media = "application/xml" if ext == "xml" else (
            "application/json" if ext == "json" else "text/csv"
        )
        filename = f"modelo_{modelo.lower()}_{ejercicio}_{periodo.lower()}.{ext}"
        content = Path(f"/tmp/dl_{modelo}_{ejercicio}_{periodo}.tmp").read_bytes()
        return StreamingResponse(
            io.BytesIO(content),
            media_type=media,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        return _redirect("/modelos", f"Error al generar descarga: {e}", "error")


# ── SII Check ─────────────────────────────────────────────────────────────────

@app.get("/sii", response_class=HTMLResponse)
async def sii_page(request: Request, desde: str = "", hasta: str = "", tipo: str = ""):
    resultado = None
    if desde or hasta:
        resultado = check_sii_compliance(
            fecha_desde=desde or None,
            fecha_hasta=hasta or None,
            tipo=tipo or None,
        )
    return templates.TemplateResponse(request, "sii.html", _ctx(
        request, "sii",
        filtros   = {"desde": desde, "hasta": hasta, "tipo": tipo},
        resultado = resultado,
    ))


@app.post("/sii/verificar")
async def sii_verificar(
    desde: str = Form(""), hasta: str = Form(""), tipo: str = Form(""),
):
    from urllib.parse import urlencode
    params = {k: v for k, v in {"desde": desde, "hasta": hasta, "tipo": tipo}.items() if v}
    return RedirectResponse(f"/sii?{urlencode(params)}", status_code=303)


# ── Scheduler ─────────────────────────────────────────────────────────────────

@app.get("/scheduler", response_class=HTMLResponse)
async def scheduler_page(request: Request):
    return templates.TemplateResponse(request, "scheduler.html", _ctx(
        request, "scheduler",
        scheduler_running  = sched_mod.get_scheduler().running,
        jobs               = sched_mod.list_jobs(),
        notify_configured  = bool(config.SMTP_HOST and config.NOTIFY_TO),
        notify_to          = config.NOTIFY_TO,
        smtp_host          = config.SMTP_HOST,
        smtp_port          = config.SMTP_PORT,
        smtp_user          = config.SMTP_USER,
        current_q          = quarter_of_date(date.today().isoformat()),
    ))


@app.post("/scheduler/run/deadline_alert")
async def scheduler_run_deadline(request: Request):
    try:
        sched_mod.job_deadline_alert()
        return _redirect("/scheduler", "Verificación de vencimientos ejecutada correctamente.")
    except Exception as e:
        return _redirect("/scheduler", f"Error: {e}", "error")


@app.post("/scheduler/run/quarterly")
async def scheduler_run_quarterly(quarter: str = Form(...)):
    try:
        sched_mod.job_quarterly_close(quarter.upper(), config.EMPRESA_EJERCICIO)
        return _redirect("/scheduler", f"Cierre {quarter}/{config.EMPRESA_EJERCICIO} ejecutado.")
    except Exception as e:
        return _redirect("/scheduler", f"Error: {e}", "error")
