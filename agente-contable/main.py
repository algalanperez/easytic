#!/usr/bin/env python3
"""
Punto de entrada del Agente Contable de EasyTic.

Modos:
  python main.py                        → chat interactivo (requiere ANTHROPIC_API_KEY)
  python main.py --alertas              → vencimientos próximos (30 días)
  python main.py --calc 303 --periodo Q2           → calcula Modelo 303
  python main.py --calc 111 --periodo Q2           → calcula Modelo 111
  python main.py --draft 303 --periodo Q2          → calcula y guarda borrador
  python main.py --draft 111 --periodo Q2
  python main.py --liquidaciones                   → lista borradores guardados
  python main.py --sync Q1              → importa facturas Drive+Gmail (requiere OAuth)
  python main.py --init-db              → crea/verifica esquema BD
"""
import argparse
import sys

from database.db import get_conn
from tools.tax_calendar import get_upcoming_deadlines, quarter_date_range
from tools.tax_models import calculate_303, calculate_111, generate_model_draft, list_liquidaciones
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
    periodo = periodo.upper()
    if modelo == "303":
        _print_303(calculate_303(ejercicio, periodo))
    elif modelo == "111":
        _print_111(calculate_111(ejercicio, periodo))
    else:
        print(f"Modelo no soportado: {modelo}. Use 303 o 111.", file=sys.stderr)
        sys.exit(1)


def cmd_draft(modelo: str, periodo: str, ejercicio: int) -> None:
    periodo = periodo.upper()
    r = generate_model_draft(modelo, ejercicio, periodo)
    if modelo == "303":
        _print_303(r)
    else:
        _print_111(r)
    print(f"  Borrador guardado en BD: {config.DB_PATH}\n")


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
            "  python main.py --draft 111 --periodo Q2 --ejercicio 2025\n"
            "  python main.py --liquidaciones\n"
            "  python main.py --alertas\n"
            "  python main.py --sync Q2            (requiere OAuth + API key)\n"
            "  python main.py                      (chat — requiere API key)\n"
        ),
    )
    parser.add_argument("--alertas",       action="store_true",
                        help="Muestra vencimientos fiscales próximos (30 días)")
    parser.add_argument("--calc",          metavar="303|111",
                        help="Calcula el modelo fiscal indicado (sin guardar)")
    parser.add_argument("--draft",         metavar="303|111",
                        help="Calcula y guarda borrador en BD")
    parser.add_argument("--periodo",       metavar="Q1|Q2|Q3|Q4", default="Q1",
                        help="Trimestre (default: Q1)")
    parser.add_argument("--ejercicio",     metavar="YYYY", type=int,
                        default=config.EMPRESA_EJERCICIO,
                        help=f"Año fiscal (default: {config.EMPRESA_EJERCICIO})")
    parser.add_argument("--liquidaciones", action="store_true",
                        help="Lista borradores/liquidaciones guardados")
    parser.add_argument("--sync",          metavar="Q1|Q2|Q3|Q4",
                        help="Importa facturas de Drive+Gmail del trimestre (requiere OAuth)")
    parser.add_argument("--init-db",       action="store_true", dest="init_db",
                        help="Crea/verifica el esquema de la BD")
    args = parser.parse_args()

    get_conn()  # inicializa BD en todos los modos

    if args.calc:
        cmd_calc(args.calc, args.periodo, args.ejercicio)
    elif args.draft:
        cmd_draft(args.draft, args.periodo, args.ejercicio)
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
