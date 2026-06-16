"""
Pobla la BD con facturas realistas del Q2 2025 para EasyTic Solutions SL.
"""
import os, sys
os.environ.setdefault("ANTHROPIC_API_KEY", "seed")
os.environ.setdefault("EMPRESA_NIF",    "B87654321")
os.environ.setdefault("EMPRESA_NOMBRE", "EasyTic Solutions SL")
os.environ.setdefault("EMPRESA_EJERCICIO", "2025")
os.environ.setdefault("DB_PATH", "contabilidad.db")

from database import db
from tools.db_tools import tool_upsert_factura

# ── Facturas emitidas Q2 2025 (servicios SaaS + consultoría) ─────────────────
EMITIDAS = [
    # Abril
    dict(tipo="emitida", numero="F2025-041", fecha="2025-04-01",
         nif_receptor="A28000001", nombre_receptor="Talleres Martínez SA",
         concepto="Suscripción EasyFix Pro — abril 2025",
         base_imponible=1200.00, tipo_iva=21, cuota_iva=252.00, total=1452.00,
         fuente="manual", fuente_id="F2025-041"),
    dict(tipo="emitida", numero="F2025-042", fecha="2025-04-07",
         nif_receptor="B08000022", nombre_receptor="Auto Reparaciones López SL",
         concepto="Suscripción EasyFix — abril 2025",
         base_imponible=400.00, tipo_iva=21, cuota_iva=84.00, total=484.00,
         fuente="manual", fuente_id="F2025-042"),
    dict(tipo="emitida", numero="F2025-043", fecha="2025-04-15",
         nif_receptor="A46000033", nombre_receptor="Mecánica Pérez e Hijos SA",
         concepto="Consultoría de implementación EasyFix (40h)",
         base_imponible=3500.00, tipo_iva=21, cuota_iva=735.00, total=4235.00,
         fuente="manual", fuente_id="F2025-043"),
    # Mayo
    dict(tipo="emitida", numero="F2025-051", fecha="2025-05-02",
         nif_receptor="A28000001", nombre_receptor="Talleres Martínez SA",
         concepto="Suscripción EasyFix Pro — mayo 2025",
         base_imponible=1200.00, tipo_iva=21, cuota_iva=252.00, total=1452.00,
         fuente="manual", fuente_id="F2025-051"),
    dict(tipo="emitida", numero="F2025-052", fecha="2025-05-05",
         nif_receptor="B08000022", nombre_receptor="Auto Reparaciones López SL",
         concepto="Suscripción EasyFix — mayo 2025",
         base_imponible=400.00, tipo_iva=21, cuota_iva=84.00, total=484.00,
         fuente="manual", fuente_id="F2025-052"),
    dict(tipo="emitida", numero="F2025-053", fecha="2025-05-20",
         nif_receptor="B41000044", nombre_receptor="Eurocar Andalucía SL",
         concepto="Suscripción EasyFix Pro — mayo 2025",
         base_imponible=1200.00, tipo_iva=21, cuota_iva=252.00, total=1452.00,
         fuente="manual", fuente_id="F2025-053"),
    # Junio
    dict(tipo="emitida", numero="F2025-061", fecha="2025-06-02",
         nif_receptor="A28000001", nombre_receptor="Talleres Martínez SA",
         concepto="Suscripción EasyFix Pro — junio 2025",
         base_imponible=1200.00, tipo_iva=21, cuota_iva=252.00, total=1452.00,
         fuente="manual", fuente_id="F2025-061"),
    dict(tipo="emitida", numero="F2025-062", fecha="2025-06-05",
         nif_receptor="B08000022", nombre_receptor="Auto Reparaciones López SL",
         concepto="Suscripción EasyFix — junio 2025",
         base_imponible=400.00, tipo_iva=21, cuota_iva=84.00, total=484.00,
         fuente="manual", fuente_id="F2025-062"),
    dict(tipo="emitida", numero="F2025-063", fecha="2025-06-10",
         nif_receptor="B41000044", nombre_receptor="Eurocar Andalucía SL",
         concepto="Suscripción EasyFix Pro — junio 2025",
         base_imponible=1200.00, tipo_iva=21, cuota_iva=252.00, total=1452.00,
         fuente="manual", fuente_id="F2025-063"),
    dict(tipo="emitida", numero="F2025-064", fecha="2025-06-25",
         nif_receptor="A28000001", nombre_receptor="Talleres Martínez SA",
         concepto="Soporte técnico premium — junio 2025",
         base_imponible=650.00, tipo_iva=21, cuota_iva=136.50, total=786.50,
         fuente="manual", fuente_id="F2025-064"),
]

# ── Facturas recibidas Q2 2025 (proveedores) ──────────────────────────────────
RECIBIDAS = [
    # Abril
    dict(tipo="recibida", numero="AWS-2025-04", fecha="2025-04-01",
         nif_emisor="ESW0173851G", nombre_emisor="Amazon Web Services EMEA SARL",
         concepto="Hosting cloud AWS — abril 2025",
         base_imponible=380.00, tipo_iva=21, cuota_iva=79.80, total=459.80,
         fuente="manual", fuente_id="AWS-2025-04"),
    dict(tipo="recibida", numero="REC-041", fecha="2025-04-10",
         nif_emisor="34567890A", nombre_emisor="Carlos Ruiz Fernández (freelance dev)",
         concepto="Desarrollo módulo agenda EasyFix (20h)",
         base_imponible=2000.00, tipo_iva=21, cuota_iva=420.00,
         tipo_retencion=15, cuota_retencion=300.00, total=2120.00,
         fuente="manual", fuente_id="REC-041"),
    dict(tipo="recibida", numero="GOOG-2025-04", fecha="2025-04-15",
         nif_emisor="ESN0011361H", nombre_emisor="Google Ireland Limited",
         concepto="Google Workspace Business — abril 2025",
         base_imponible=120.00, tipo_iva=21, cuota_iva=25.20, total=145.20,
         fuente="manual", fuente_id="GOOG-2025-04"),
    dict(tipo="recibida", numero="REC-042", fecha="2025-04-28",
         nif_emisor="12345678B", nombre_emisor="Marta García Sánchez (diseño UX)",
         concepto="Diseño de interfaces v2.0 EasyFix",
         base_imponible=800.00, tipo_iva=21, cuota_iva=168.00,
         tipo_retencion=15, cuota_retencion=120.00, total=848.00,
         fuente="manual", fuente_id="REC-042"),
    # Mayo
    dict(tipo="recibida", numero="AWS-2025-05", fecha="2025-05-01",
         nif_emisor="ESW0173851G", nombre_emisor="Amazon Web Services EMEA SARL",
         concepto="Hosting cloud AWS — mayo 2025",
         base_imponible=415.00, tipo_iva=21, cuota_iva=87.15, total=502.15,
         fuente="manual", fuente_id="AWS-2025-05"),
    dict(tipo="recibida", numero="GOOG-2025-05", fecha="2025-05-15",
         nif_emisor="ESN0011361H", nombre_emisor="Google Ireland Limited",
         concepto="Google Workspace Business — mayo 2025",
         base_imponible=120.00, tipo_iva=21, cuota_iva=25.20, total=145.20,
         fuente="manual", fuente_id="GOOG-2025-05"),
    dict(tipo="recibida", numero="REC-051", fecha="2025-05-20",
         nif_emisor="34567890A", nombre_emisor="Carlos Ruiz Fernández (freelance dev)",
         concepto="Desarrollo módulo reportes EasyFix (15h)",
         base_imponible=1500.00, tipo_iva=21, cuota_iva=315.00,
         tipo_retencion=15, cuota_retencion=225.00, total=1590.00,
         fuente="manual", fuente_id="REC-051"),
    # Junio
    dict(tipo="recibida", numero="AWS-2025-06", fecha="2025-06-01",
         nif_emisor="ESW0173851G", nombre_emisor="Amazon Web Services EMEA SARL",
         concepto="Hosting cloud AWS — junio 2025",
         base_imponible=395.00, tipo_iva=21, cuota_iva=82.95, total=477.95,
         fuente="manual", fuente_id="AWS-2025-06"),
    dict(tipo="recibida", numero="GOOG-2025-06", fecha="2025-06-15",
         nif_emisor="ESN0011361H", nombre_emisor="Google Ireland Limited",
         concepto="Google Workspace Business — junio 2025",
         base_imponible=120.00, tipo_iva=21, cuota_iva=25.20, total=145.20,
         fuente="manual", fuente_id="GOOG-2025-06"),
    dict(tipo="recibida", numero="REC-061", fecha="2025-06-16",
         nif_emisor="87654321C", nombre_emisor="Asesoría Contable Gómez SL",
         concepto="Asesoría fiscal y contable — Q2 2025",
         base_imponible=350.00, tipo_iva=21, cuota_iva=73.50,
         tipo_retencion=15, cuota_retencion=52.50, total=371.00,
         fuente="manual", fuente_id="REC-061"),
    dict(tipo="recibida", numero="REC-062", fecha="2025-06-20",
         nif_emisor="B28100500", nombre_emisor="Leroy Merlin (material oficina)",
         concepto="Material de oficina",
         base_imponible=230.00, tipo_iva=21, cuota_iva=48.30, total=278.30,
         fuente="manual", fuente_id="REC-062"),
]


def main():
    db.get_conn()

    # Limpia datos previos de seed (solo fuente=manual) para idempotencia
    conn = db.get_conn()
    conn.execute("DELETE FROM facturas WHERE fuente = 'manual'")
    conn.execute("DELETE FROM liquidaciones")
    conn.commit()

    total = 0
    for f in EMITIDAS + RECIBIDAS:
        tool_upsert_factura(f)
        total += 1

    print(f"Insertadas {total} facturas ({len(EMITIDAS)} emitidas, {len(RECIBIDAS)} recibidas)")

    # Verificación rápida
    from tools.tax_models import calculate_303, calculate_111
    r303 = calculate_303(2025, "Q2")
    r111 = calculate_111(2025, "Q2")

    print()
    print("── Modelo 303 Q2/2025 ──────────────────────────────")
    c = r303["casillas"]
    print(f"  Base 21%:           {c['01_base_general']:>10,.2f} €")
    print(f"  IVA devengado:      {c['27_total_devengado']:>10,.2f} €")
    print(f"  IVA deducible:      {c['46_total_deducible']:>10,.2f} €")
    print(f"  Resultado (cas.64): {c['64_resultado']:>10,.2f} € → {r303['resumen']['signo'].upper()}")

    print()
    print("── Modelo 111 Q2/2025 ──────────────────────────────")
    c = r111["casillas"]
    print(f"  Perceptores:        {c['10_perceptores_prof']:>10}")
    print(f"  Base retención:     {c['11_base_prof']:>10,.2f} €")
    print(f"  Retenciones:        {c['12_retenciones_prof']:>10,.2f} € → A INGRESAR")


if __name__ == "__main__":
    main()
