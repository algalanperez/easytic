"""
Envío de notificaciones por email.

Usa smtplib (stdlib) con STARTTLS. Configura en .env:
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, NOTIFY_TO
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import config


def _send(subject: str, html: str, plain: str) -> bool:
    """Envía un email. Devuelve True si tuvo éxito, False si falta config o falla."""
    if not all([config.SMTP_HOST, config.SMTP_USER, config.SMTP_PASS, config.NOTIFY_TO]):
        return False

    recipients = [r.strip() for r in config.NOTIFY_TO.split(",") if r.strip()]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = config.SMTP_FROM or config.SMTP_USER
    msg["To"]      = ", ".join(recipients)
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=15) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(config.SMTP_USER, config.SMTP_PASS)
            smtp.sendmail(msg["From"], recipients, msg.as_string())
        return True
    except Exception as exc:
        print(f"[notifier] Error enviando email: {exc}")
        return False


# ── Templates de mensajes ─────────────────────────────────────────────────────

def notify_deadline_alert(deadlines: list[dict]) -> bool:
    """Alerta de vencimientos fiscales próximos."""
    if not deadlines:
        return False

    rows_html = "".join(
        f"<tr><td>{d['vencimiento']}</td><td>Modelo {d['modelo']}</td>"
        f"<td>{d['descripcion']}</td><td><strong>{d['dias_restantes']} días</strong></td></tr>"
        for d in deadlines
    )
    rows_plain = "\n".join(
        f"  {d['vencimiento']}  Mod.{d['modelo']}  {d['descripcion']}  ({d['dias_restantes']} días)"
        for d in deadlines
    )

    html = f"""
<html><body style="font-family:sans-serif;color:#1e293b">
<h2 style="color:#1a1d23">⚠ Vencimientos fiscales próximos — {config.EMPRESA_NOMBRE}</h2>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%">
  <thead style="background:#1a1d23;color:#fff">
    <tr><th>Fecha</th><th>Modelo</th><th>Descripción</th><th>Días restantes</th></tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>
<p style="color:#64748b;font-size:12px">
  Generado automáticamente por Agente Contable EasyTic · NIF: {config.EMPRESA_NIF}
</p>
</body></html>"""

    plain = (
        f"VENCIMIENTOS FISCALES PRÓXIMOS — {config.EMPRESA_NOMBRE}\n"
        f"{'─'*60}\n{rows_plain}\n{'─'*60}\n"
        f"NIF: {config.EMPRESA_NIF}"
    )

    subject = f"[EasyTic Contable] {len(deadlines)} vencimiento(s) próximo(s)"
    return _send(subject, html, plain)


def notify_quarterly_report(ejercicio: int, periodo: str, m303: dict, m111: dict, sii: dict) -> bool:
    """Resumen de cierre trimestral: 303, 111 y estado SII."""
    c303 = m303.get("casillas", {})
    c111 = m111.get("casillas", {})
    sii_res = sii.get("resumen", {})

    res303 = c303.get("64_resultado", 0)
    signo303 = "A INGRESAR" if res303 >= 0 else "A COMPENSAR"
    total111 = c111.get("28_total_ingresar", 0)
    pct_sii = sii_res.get("porcentaje_cumplimiento", 0)
    color_sii = "#10b981" if pct_sii == 100 else ("#f59e0b" if pct_sii >= 80 else "#ef4444")

    html = f"""
<html><body style="font-family:sans-serif;color:#1e293b">
<h2 style="color:#1a1d23">Resumen trimestral {periodo}/{ejercicio} — {config.EMPRESA_NOMBRE}</h2>

<table cellpadding="12" style="width:100%;border-collapse:collapse">
  <tr style="background:#f8f9fa">
    <td><strong>Modelo 303 (IVA)</strong></td>
    <td>Resultado: <strong>{res303:,.2f} € — {signo303}</strong></td>
  </tr>
  <tr>
    <td><strong>Modelo 111 (IRPF)</strong></td>
    <td>A ingresar: <strong>{total111:,.2f} €</strong></td>
  </tr>
  <tr style="background:#f8f9fa">
    <td><strong>SII / Verifactu</strong></td>
    <td>Cumplimiento: <strong style="color:{color_sii}">{pct_sii}%</strong>
      ({sii_res.get('facturas_con_errores', 0)} factura(s) con incidencias)</td>
  </tr>
</table>

<p>Los borradores han sido guardados en la base de datos y están listos para revisar.</p>
<p style="color:#64748b;font-size:12px">
  Generado automáticamente · Agente Contable EasyTic · NIF: {config.EMPRESA_NIF}
</p>
</body></html>"""

    plain = (
        f"RESUMEN TRIMESTRAL {periodo}/{ejercicio} — {config.EMPRESA_NOMBRE}\n"
        f"{'─'*60}\n"
        f"Modelo 303 (IVA):   {res303:,.2f} € — {signo303}\n"
        f"Modelo 111 (IRPF):  {total111:,.2f} € a ingresar\n"
        f"SII/Verifactu:      {pct_sii}% cumplimiento\n"
        f"{'─'*60}\n"
        f"NIF: {config.EMPRESA_NIF}"
    )

    subject = f"[EasyTic Contable] Cierre {periodo}/{ejercicio} calculado"
    return _send(subject, html, plain)


def notify_sii_errors(periodo: str, errores: list[dict]) -> bool:
    """Alerta cuando el check SII detecta facturas con incidencias."""
    if not errores:
        return False

    rows_html = "".join(
        f"<tr><td>{f['tipo']}</td><td>{f['numero']}</td><td>{f['fecha']}</td>"
        f"<td>{f['emisor']}</td><td>{'<br>'.join(f['errores'])}</td></tr>"
        for f in errores[:20]   # máximo 20 en el email
    )

    html = f"""
<html><body style="font-family:sans-serif;color:#1e293b">
<h2 style="color:#ef4444">⚠ Incidencias SII detectadas — {periodo} — {config.EMPRESA_NOMBRE}</h2>
<p>{len(errores)} factura(s) con incidencias. Corrígelas antes de presentar.</p>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%">
  <thead style="background:#ef4444;color:#fff">
    <tr><th>Tipo</th><th>Número</th><th>Fecha</th><th>Emisor</th><th>Errores</th></tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>
<p style="color:#64748b;font-size:12px">
  Agente Contable EasyTic · NIF: {config.EMPRESA_NIF}
</p>
</body></html>"""

    plain = "\n".join(
        f"  [{f['tipo']}] {f['numero']}  {f['fecha']}  {f['emisor']}\n"
        + "\n".join(f"    → {e}" for e in f["errores"])
        for f in errores[:20]
    )

    subject = f"[EasyTic Contable] {len(errores)} incidencia(s) SII en {periodo}"
    return _send(subject, html, plain)
