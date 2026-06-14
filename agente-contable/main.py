#!/usr/bin/env python3
"""
Punto de entrada del Agente Contable de EasyTic.

Modos:
  python main.py              → chat interactivo
  python main.py --alertas    → muestra vencimientos próximos (30 días)
  python main.py --sync Q1    → importa facturas de Drive+Gmail del trimestre
  python main.py --init-db    → crea/verifica el esquema de la BD
"""
import argparse
import sys

from database.db import get_conn          # inicializa la BD al importar
from agent import ContableAgent
from tools.tax_calendar import get_upcoming_deadlines, quarter_date_range
import config


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


def cmd_sync(quarter: str) -> None:
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
    parser = argparse.ArgumentParser(description="Agente Contable EasyTic")
    parser.add_argument("--alertas", action="store_true", help="Muestra vencimientos próximos")
    parser.add_argument("--sync",    metavar="Q1|Q2|Q3|Q4", help="Importa facturas del trimestre")
    parser.add_argument("--init-db", action="store_true", dest="init_db")
    args = parser.parse_args()

    if args.alertas:
        cmd_alertas()
    elif args.sync:
        cmd_sync(args.sync.upper())
    elif args.init_db:
        cmd_init_db()
    else:
        cmd_chat()


if __name__ == "__main__":
    main()
