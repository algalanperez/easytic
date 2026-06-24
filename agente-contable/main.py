#!/usr/bin/env python3
"""
Punto de entrada del Agente Contable de EasyTic.

Modos:
  python main.py                          → chat interactivo (requiere ANTHROPIC_API_KEY)
  python main.py --serve                  → panel web en http://localhost:8080
  python main.py --scheduler              → scheduler standalone (sin web)
  python main.py --alertas                → vencimientos próximos (30 días)
  python main.py --calc 303 --periodo Q2  → calcula Modelo 303
  python main.py --calc 200               → calcula Impuesto de Sociedades
  python main.py --draft 303 --periodo Q2 → calcula y guarda borrador
  python main.py --sii-check              → verifica cumplimiento SII/Verifactu
  python main.py --export 303 --periodo Q2 → exporta a XML
  python main.py --export facturas --desde 2025-01-01 --hasta 2025-12-31 → CSV
  python main.py --liquidaciones          → lista borradores guardados
  python main.py --sync Q1               → importa facturas Drive+Gmail (requiere OAuth)
  python main.py --init-db               → crea/verifica esquema BD
"""
import argparse
import sys

from database.db import get_conn
from tools.tax_calendar import get_upcoming_deadlines, quarter_date_range
from tools.tax_models import calculate_303, calculate_111, generate_model_draft, list_liquidaciones
from tools.modelo_200 import calculate_200
from tools.sii_check import check_sii_compliance
from tools.export_aeat import export_model
import config
# ContableAgent se importa dentro de cmd_chat/cmd_sync para no requerir API key en modos CLI

_SEP = "─" * 58


def cmd_alertas() -> None:
    deadlines = get_upcoming_deadlines(days_ahead=30, ejercicio=config.EMPRESA_EJERCICIO)
    if not deadlines:
        print("No hay vencimientos fiscales en los próximos 30 días.")
        return
    print(f"\n{'─'*60}")
    print(f"  VENCIMIENTOS FISCALES — próximos 30 días")
    print(f"{'─'*60}")
    for d in deadlines:
        print(f"  [{d['dias_restantes']:>2} días]  {d['vencimiento']}  Mod.{d['modelo']} {d['periodo']:6}  {d['descripcion']}")
    print(f"{'─'*60}\n")


def _print_303(r: dict) -> None:
    c = r["casillas"]
    print(f"\n{_SEP}")
    print(f"  MODELO 303 — IVA {r['periodo']}/{r['ejercicio']}")
    print(f"  {r['empresa_nombre']}  NIF: {r['empresa_nif']}")
    print(f"  Período: {r['fecha_desde']} → {r['fecha_hasta']}")
    print(_SEP)
    print(f"  IVA DEVENGADO")
    print(f"    [01] Base imponible 21%:       {c['01_base_general']:>10,.2f} €")
    print(f"    [02] Cuota devengada 21%:      {c['02_cuota_general']:>10,.2f} €")
    print(f"    [03] Base imponible 10%:       {c['03_base_reducido']:>10,.2f} €")
    print(f"    [04] Cuota devengada 10%:      {c['04_cuota_reducido']:>10,.2f} €")
    print(f"    [05] Base imponible 4%:        {c['05_base_superreducido']:>10,.2f} €")
    print(f"    [06] Cuota devengada 4%:       {c['06_cuota_superreducido']:>10,.2f} €")
    print(f"    {'·'*44}")
    print(f"    [27] TOTAL DEVENGADO:          {c['27_total_devengado']:>10,.2f} €")
    print(f"  IVA DEDUCIBLE")
    print(f"    [29] Base soportada:           {c['29_bases_soportadas']:>10,.2f} €")
    print(f"    [28] Cuota soportada:          {c['28_cuotas_soportadas']:>10,.2f} €")
    print(f"    {'·'*44}")
    print(f"    [46] TOTAL DEDUCIBLE:          {c['46_total_deducible']:>10,.2f} €")
    signo = "A INGRESAR" if r["resumen"]["signo"] == "ingreso" else "A COMPENSAR"
    print(f"  {'═'*50}")
    print(f"  [64] RESULTADO: {c['64_resultado']:>10,.2f} €  →  {signo}")
    print(f"  {'═'*50}")
    print(f"  Plazo de presentación: 20 de julio {r['ejercicio']}\n")


def _print_111(r: dict) -> None:
    c = r["casillas"]
    print(f"\n{_SEP}")
    print(f"  MODELO 111 — RETENCIONES IRPF {r['periodo']}/{r['ejercicio']}")
    print(f"  {r['empresa_nombre']}  NIF: {r['empresa_nif']}")
    print(f"  Período: {r['fecha_desde']} → {r['fecha_hasta']}")
    print(_SEP)
    print(f"  ACTIVIDADES PROFESIONALES (autónomos / freelance)")
    print(f"    [10] Nº perceptores:           {c['10_perceptores_prof']:>10}")
    print(f"    [11] Base de retención:        {c['11_base_prof']:>10,.2f} €")
    print(f"    [12] Retenciones:              {c['12_retenciones_prof']:>10,.2f} €")
    print(f"  {'═'*50}")
    print(f"  [28] TOTAL A INGRESAR: {c['28_total_ingresar']:>10,.2f} €")
    print(f"  {'═'*50}")
    print(f"  Plazo de presentación: 20 de julio {r['ejercicio']}\n")


def cmd_calc(modelo: str, periodo: str, ejercicio: int) -> None:
    modelo = modelo.upper()
    periodo = periodo.upper() if periodo else "Q1"
    if modelo == "303":
        _print_303(calculate_303(ejercicio, periodo))
    elif modelo == "111":
        _print_111(calculate_111(ejercicio, periodo))
    elif modelo == "200":
        _print_200(calculate_200(ejercicio))
    else:
        print(f"Modelo no soportado: {modelo}. Use 303, 111 o 200.", file=sys.stderr)
        sys.exit(1)


def cmd_draft(modelo: str, periodo: str, ejercicio: int) -> None:
    modelo = modelo.upper()
    periodo = periodo.upper() if periodo else ("anual" if modelo == "200" else "Q1")
    r = generate_model_draft(modelo, ejercicio, periodo)
    if modelo == "303":
        _print_303(r)
    elif modelo == "111":
        _print_111(r)
    elif modelo == "200":
        _print_200(r)
    else:
        print(f"Modelo no soportado: {modelo}.", file=sys.stderr)
        sys.exit(1)
    print(f"  Borrador guardado en BD: {config.DB_PATH}\n")


def _print_200(r: dict) -> None:
    c = r["casillas"]
    print(f"\n{_SEP}")
    print(f"  MODELO 200 — IMPUESTO DE SOCIEDADES {r['ejercicio']}")
    print(f"  {r['empresa_nombre']}  NIF: {r['empresa_nif']}")
    print(f"  Período: {r['fecha_desde']} → {r['fecha_hasta']}")
    print(_SEP)
    inp = r["inputs"]
    print(f"  CUENTA DE RESULTADOS (simplificada)")
    print(f"    Ingresos (fact. emitidas):     {inp['ingresos']:>12,.2f} €")
    print(f"    Gastos   (fact. recibidas):    {inp['gastos']:>12,.2f} €")
    print(f"    {'·'*48}")
    print(f"    [01] Resultado contable:       {c['01_resultado_contable']:>12,.2f} €")
    print(f"  LIQUIDACIÓN")
    print(f"    Ajustes fiscales:              {inp['ajustes_fiscales']:>12,.2f} €")
    print(f"    [550] Base imponible previa:   {c['550_base_imponible_previa']:>12,.2f} €")
    print(f"    BINs a compensar:              {inp['bins_anteriores']:>12,.2f} €")
    print(f"    [552] Base imponible:          {c['552_base_imponible']:>12,.2f} €")
    print(f"    [562] Tipo de gravamen:        {c['562_tipo_gravamen']:>11,.1f} %")
    print(f"    [599] Cuota íntegra:           {c['599_cuota_integra']:>12,.2f} €")
    print(f"    Deducciones:                   {inp['deducciones']:>12,.2f} €")
    print(f"    [601] Cuota líquida:           {c['601_cuota_liquida']:>12,.2f} €")
    print(f"    [610] Retenciones soportadas:  {c['610_retenciones']:>12,.2f} €")
    signo = "A INGRESAR" if r["resumen"]["signo"] == "ingreso" else "A DEVOLVER"
    print(f"  {'═'*54}")
    print(f"  [621] CUOTA DIFERENCIAL: {c['621_cuota_diferencial']:>12,.2f} €  →  {signo}")
    print(f"  {'═'*54}")
    if r.get("advertencias"):
        print(f"\n  ADVERTENCIAS:")
        for adv in r["advertencias"]:
            print(f"    ⚠  {adv}")
    print(f"\n  Plazo de presentación: 25 de julio {r['ejercicio'] + 1}\n")


def cmd_sii_check(periodo: str | None, ejercicio: int) -> None:
    if periodo:
        fecha_desde, fecha_hasta = quarter_date_range(ejercicio, periodo.upper())
    else:
        fecha_desde = f"{ejercicio}-01-01"
        fecha_hasta = f"{ejercicio}-12-31"

    r = check_sii_compliance(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
    res = r["resumen"]
    print(f"\n{_SEP}")
    print(f"  VERIFICACIÓN SII/VERIFACTU  {fecha_desde} → {fecha_hasta}")
    print(_SEP)
    print(f"  Total facturas:       {res['total_facturas']:>6}")
    print(f"  Facturas correctas:   {res['facturas_ok']:>6}  ({res['porcentaje_cumplimiento']}%)")
    print(f"  Con incidencias:      {res['facturas_con_errores']:>6}")
    if r["facturas_error"]:
        print(f"\n  INCIDENCIAS DETECTADAS:")
        for f in r["facturas_error"]:
            print(f"    [{f['tipo'][:3].upper()}] {f['numero']:20}  {f['fecha']}  {f['emisor'][:30]}")
            for e in f["errores"]:
                print(f"         → {e}")
    print(f"\n  RECOMENDACIONES:")
    for rec in r["recomendaciones"]:
        print(f"    • {rec}")
    print(f"{_SEP}\n")


def cmd_export(modelo: str, periodo: str, ejercicio: int,
               desde: str | None, hasta: str | None, output: str | None) -> None:
    modelo = modelo.upper()
    kwargs: dict = {}
    if modelo == "FACTURAS":
        if not (desde and hasta):
            print("Para exportar facturas usa --desde YYYY-MM-DD --hasta YYYY-MM-DD", file=sys.stderr)
            sys.exit(1)
        kwargs = {"fecha_desde": desde, "fecha_hasta": hasta}
    result = export_model(
        modelo=modelo,
        ejercicio=ejercicio,
        periodo=periodo.upper() if periodo else "anual",
        output_path=output,
        **kwargs,
    )
    print(f"\n  Exportado: {result['fichero']}  ({result['bytes']} bytes)  [{result['formato'].upper()}]\n")


def cmd_liquidaciones(ejercicio: int | None) -> None:
    rows = list_liquidaciones(ejercicio)
    if not rows:
        print("No hay liquidaciones guardadas.")
        return
    print(f"\n{_SEP}")
    print(f"  LIQUIDACIONES GUARDADAS{f'  ({ejercicio})' if ejercicio else ''}")
    print(_SEP)
    for r in rows:
        pres = r["presentado_en"] or "—"
        print(f"  Modelo {r['modelo']}  {r['periodo']}/{r['ejercicio']}  [{r['estado'].upper():9}]  presentado: {pres}")
    print(f"{_SEP}\n")


def cmd_sync(quarter: str) -> None:
    from agent import ContableAgent
    agent = ContableAgent()
    fecha_desde, fecha_hasta = quarter_date_range(config.EMPRESA_EJERCICIO, quarter)
    prompt = (
        f"Por favor, sincroniza todas las facturas del {quarter} del ejercicio {config.EMPRESA_EJERCICIO} "
        f"(del {fecha_desde} al {fecha_hasta}). "
        f"1) Lista los archivos de Drive en ese período. "
        f"2) Busca adjuntos de facturas en Gmail. "
        f"3) Parsea cada factura y guárdala en la BD. "
        f"4) Al final muestra un resumen: cuántas facturas emitidas y recibidas has procesado, "
        f"y el resultado de IVA del trimestre."
    )
    print(f"\nSincronizando facturas {quarter} ({fecha_desde} → {fecha_hasta})...\n")
    response = agent.chat(prompt)
    print(f"\n{response}\n")


def cmd_chat() -> None:
    from agent import ContableAgent
    agent = ContableAgent()
    print(f"\nAgente Contable EasyTic — escribe 'salir' para terminar\n")
    while True:
        try:
            user_input = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break
        if not user_input:
            continue
        if user_input.lower() in ("salir", "exit", "quit"):
            print("Hasta luego.")
            break
        print("Agente: ", end="", flush=True)
        response = agent.chat(user_input)
        print(response)
        print()


def cmd_serve() -> None:
    """Arranca el panel web (FastAPI + scheduler integrado)."""
    import uvicorn
    from web.app import app
    print(f"\n  Panel web → http://{config.WEB_HOST}:{config.WEB_PORT}")
    print(f"  BD: {config.DB_PATH}  |  Empresa: {config.EMPRESA_NOMBRE}\n")
    uvicorn.run(app, host=config.WEB_HOST, port=config.WEB_PORT, log_level="info")


def cmd_scheduler_standalone() -> None:
    """Ejecuta el scheduler sin panel web (útil como servicio de fondo)."""
    import time
    import scheduler as sched_mod
    sched_mod.start()
    print("Scheduler arrancado. Ctrl+C para detener.")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        sched_mod.stop()
        print("\nScheduler detenido.")


def cmd_init_db() -> None:
    get_conn()
    print(f"Base de datos inicializada en: {config.DB_PATH}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agente Contable EasyTic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  python main.py --calc 303 --periodo Q2\n"
            "  python main.py --calc 200\n"
            "  python main.py --draft 303 --periodo Q2 --ejercicio 2025\n"
            "  python main.py --sii-check --periodo Q2\n"
            "  python main.py --export 303 --periodo Q2\n"
            "  python main.py --export facturas --desde 2025-01-01 --hasta 2025-12-31\n"
            "  python main.py --liquidaciones\n"
            "  python main.py --alertas\n"
            "  python main.py --sync Q2            (requiere OAuth + API key)\n"
            "  python main.py                      (chat — requiere API key)\n"
        ),
    )
    parser.add_argument("--alertas",       action="store_true",
                        help="Muestra vencimientos fiscales próximos (30 días)")
    parser.add_argument("--calc",          metavar="303|111|200",
                        help="Calcula el modelo fiscal indicado (sin guardar)")
    parser.add_argument("--draft",         metavar="303|111|200",
                        help="Calcula y guarda borrador en BD")
    parser.add_argument("--sii-check",     action="store_true", dest="sii_check",
                        help="Verifica cumplimiento SII/Verifactu")
    parser.add_argument("--export",        metavar="303|111|200|facturas",
                        help="Exporta modelo a XML/JSON/CSV")
    parser.add_argument("--periodo",       metavar="Q1|Q2|Q3|Q4",
                        help="Trimestre para 303/111/export (default: Q1)")
    parser.add_argument("--ejercicio",     metavar="YYYY", type=int,
                        default=config.EMPRESA_EJERCICIO,
                        help=f"Año fiscal (default: {config.EMPRESA_EJERCICIO})")
    parser.add_argument("--desde",         metavar="YYYY-MM-DD",
                        help="Fecha inicio (para --export facturas)")
    parser.add_argument("--hasta",         metavar="YYYY-MM-DD",
                        help="Fecha fin (para --export facturas)")
    parser.add_argument("--output",        metavar="FICHERO",
                        help="Ruta de salida para --export")
    parser.add_argument("--serve",         action="store_true",
                        help="Arranca el panel web en http://HOST:PORT")
    parser.add_argument("--scheduler",     action="store_true",
                        help="Ejecuta el scheduler standalone (sin web)")
    parser.add_argument("--liquidaciones", action="store_true",
                        help="Lista borradores/liquidaciones guardados")
    parser.add_argument("--sync",          metavar="Q1|Q2|Q3|Q4",
                        help="Importa facturas de Drive+Gmail del trimestre (requiere OAuth)")
    parser.add_argument("--init-db",       action="store_true", dest="init_db",
                        help="Crea/verifica el esquema de la BD")
    args = parser.parse_args()

    get_conn()  # inicializa BD en todos los modos

    periodo = args.periodo or ("anual" if (args.calc or args.export or "") == "200" else "Q1")

    if args.serve:
        cmd_serve()
    elif args.scheduler:
        cmd_scheduler_standalone()
    elif args.calc:
        cmd_calc(args.calc, periodo, args.ejercicio)
    elif args.draft:
        cmd_draft(args.draft, periodo, args.ejercicio)
    elif args.sii_check:
        cmd_sii_check(args.periodo, args.ejercicio)
    elif args.export:
        cmd_export(args.export, periodo, args.ejercicio, args.desde, args.hasta, args.output)
    elif args.liquidaciones:
        cmd_liquidaciones(args.ejercicio if args.ejercicio != config.EMPRESA_EJERCICIO else None)
    elif args.alertas:
        cmd_alertas()
    elif args.sync:
        cmd_sync(args.sync.upper())
    elif args.init_db:
        cmd_init_db()
    else:
        cmd_chat()


if __name__ == "__main__":
    main()
