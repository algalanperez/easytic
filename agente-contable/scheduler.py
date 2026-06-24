"""
Cron automático del Agente Contable.

Jobs registrados:
  - Lunes 09:00  → alerta de vencimientos en los próximos 15 días
  - Día 1 de mes al cierre de cada trimestre, 08:00
      → calcula 303 + 111, verifica SII, guarda borradores, envía resumen

Diseñado para correr como BackgroundScheduler dentro del proceso uvicorn
(se inicia en el lifespan de la FastAPI app) o como proceso standalone
con --scheduler.
"""
import logging
from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import config
from database.db import get_conn
from tools.tax_calendar import get_upcoming_deadlines, quarter_date_range
from tools.tax_models import generate_model_draft
from tools.sii_check import check_sii_compliance
import notifier

log = logging.getLogger("scheduler")


# ── Jobs ──────────────────────────────────────────────────────────────────────

def job_deadline_alert() -> None:
    """Envía alerta si hay vencimientos en los próximos 15 días."""
    log.info("job_deadline_alert: comprobando vencimientos...")
    deadlines = get_upcoming_deadlines(days_ahead=15, ejercicio=config.EMPRESA_EJERCICIO)
    if deadlines:
        sent = notifier.notify_deadline_alert(deadlines)
        log.info("job_deadline_alert: %d vencimiento(s) — email=%s", len(deadlines), sent)
    else:
        log.info("job_deadline_alert: sin vencimientos próximos.")


def job_quarterly_close(quarter: str, ejercicio: int) -> None:
    """
    Al cerrar un trimestre:
    1. Calcula y guarda borradores 303 + 111.
    2. Verifica cumplimiento SII del trimestre.
    3. Envía resumen por email.
    4. Si hay errores SII, envía alerta adicional.
    """
    log.info("job_quarterly_close: iniciando %s/%s...", quarter, ejercicio)
    get_conn()  # asegura BD inicializada en este hilo

    try:
        m303 = generate_model_draft("303", ejercicio, quarter)
        m111 = generate_model_draft("111", ejercicio, quarter)
        log.info("job_quarterly_close: modelos calculados.")

        fd, fh = quarter_date_range(ejercicio, quarter)
        sii = check_sii_compliance(fecha_desde=fd, fecha_hasta=fh)
        log.info(
            "job_quarterly_close: SII %s/%s → %s%% cumplimiento",
            quarter, ejercicio, sii["resumen"]["porcentaje_cumplimiento"],
        )

        notifier.notify_quarterly_report(ejercicio, quarter, m303, m111, sii)

        if sii["facturas_error"]:
            notifier.notify_sii_errors(f"{quarter}/{ejercicio}", sii["facturas_error"])

    except Exception as exc:
        log.error("job_quarterly_close %s/%s FALLÓ: %s", quarter, ejercicio, exc, exc_info=True)


# ── Setup ─────────────────────────────────────────────────────────────────────

def build_scheduler() -> BackgroundScheduler:
    """
    Crea y configura el scheduler sin arrancarlo.
    Llama a .start() desde el código que lo usa.
    """
    scheduler = BackgroundScheduler(timezone="Europe/Madrid")

    # Alerta semanal de vencimientos — lunes a las 09:00
    scheduler.add_job(
        job_deadline_alert,
        CronTrigger(day_of_week="mon", hour=9, minute=0),
        id="weekly_deadlines",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    # Cierre trimestral:
    #   Q1 → 1 de abril a las 08:00
    #   Q2 → 1 de julio
    #   Q3 → 1 de octubre
    #   Q4 → 2 de enero del año siguiente (mes=1, día=2)
    quarterly_triggers = [
        ("Q1", 4, 1),
        ("Q2", 7, 1),
        ("Q3", 10, 1),
        ("Q4", 1, 2),   # enero del año siguiente
    ]
    for quarter, month, day in quarterly_triggers:
        # Para Q4 el ejercicio es el año anterior al del trigger
        scheduler.add_job(
            job_quarterly_close,
            CronTrigger(month=month, day=day, hour=8, minute=0),
            id=f"quarterly_{quarter}",
            kwargs={
                "quarter": quarter,
                "ejercicio": config.EMPRESA_EJERCICIO
                if quarter != "Q4"
                else config.EMPRESA_EJERCICIO,
            },
            replace_existing=True,
            misfire_grace_time=7200,
        )

    return scheduler


_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = build_scheduler()
    return _scheduler


def start() -> None:
    s = get_scheduler()
    if not s.running:
        s.start()
        log.info("Scheduler arrancado. Jobs: %s", [j.id for j in s.get_jobs()])


def stop() -> None:
    s = get_scheduler()
    if s.running:
        s.shutdown(wait=False)
        log.info("Scheduler detenido.")


def list_jobs() -> list[dict]:
    return [
        {
            "id": j.id,
            "next_run": j.next_run_time.isoformat() if j.next_run_time else None,
            "trigger": str(j.trigger),
        }
        for j in get_scheduler().get_jobs()
    ]
