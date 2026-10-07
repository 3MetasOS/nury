"""Demo: the 9pm phone call.

Scenario: a congregant calls her pastor — her husband was detained by ICE this
evening. The pastor opens the agent and types what she told him.

Usage:
    python -m demo.demo_scenario --dry-run   # canned outputs, no API key needed
    python -m demo.demo_scenario              # live via Gloo AI Studio
    python -m demo.demo_scenario --auto-approve   # skip pastor review pauses
"""

import argparse
import sys

sys.path.insert(0, ".")

from crisis_agent import guardrails, stages
from crisis_agent.gloo_client import GlooClient

INTAKE = (
    "Maria called at 9:10pm, very upset, speaking Spanish. Her husband Jose was "
    "detained by ICE officers outside his workplace in Aurora around 6pm today. "
    "Officers did not show a warrant that she knows of. Jose has lived here 14 "
    "years; they have two kids, 8 and 11, both US citizens. Maria is afraid to "
    "leave the house tomorrow. She wants to know what to do tonight."
)

# Canned stage outputs so the demo runs (and rehearses) without an API key.
DRY_RUN = [
    {
        "title": "1. Triage",
        "content": (
            "SITUATION: Husband (Jose) detained by ICE ~6pm today in Aurora; "
            "wife Maria (Spanish-speaking) called pastor at 9:10pm, distressed.\n"
            "PEOPLE: Jose (detained, 14 years in US), Maria, two US-citizen children (8, 11).\n"
            "LOCATION: Aurora, Colorado.\n"
            "LANGUAGE: Spanish.\n"
            "URGENCY: HIGH — detention just occurred; family needs tonight's plan "
            "and an attorney by morning.\n"
            "MISSING FACTS: (1) Was a judicial warrant shown? (2) Where was Jose taken? "
            "(3) Does the family have an immigration attorney already?"
        ),
        "sources": ["pastor intake"],
    },
    {
        "title": "2. Rights brief",
        "content": (
            "Para la familia, esta noche:\n"
            "• Tiene derecho a guardar silencio. No tiene que responder preguntas "
            "sobre su estatus migratorio (ACLU).\n"
            "• No abra la puerta sin una orden firmada por un juez (ACLU).\n"
            "• No firme ningún documento sin un abogado — podría renunciar a una "
            "audiencia (ACLU).\n"
            "• Pida hablar con un abogado de inmigración de inmediato (ACLU).\n"
            "• No mienta ni use documentos falsos (ACLU).\n"
            "Hable con un abogado calificado antes de tomar cualquier decisión."
        ),
        "sources": ["ACLU Know Your Rights (aclu.org/know-your-rights/immigrants-rights)"],
    },
    {
        "title": "3. Attorney directory",
        "content": (
            "RECURSOS NACIONALES\n"
            "• Immigration Advocates Network — directorio de ayuda legal gratuita: "
            "immigrationadvocates.org/nonprofit/legaldirectory/\n"
            "• AILA Lawyer Search — encuentre un abogado: ailalawyer.com\n"
            "• National Immigration Project: nipnlg.org\n\n"
            "LOCAL (Aurora/Denver)\n"
            "• [TODO] Agregar abogados y organizaciones locales verificados.\n\n"
            "Antes de llamar tenga listo: nombres completos, fechas, y cualquier documento."
        ),
        "sources": ["attorney_directory.json"],
    },
    {
        "title": "4. Family checklist",
        "content": (
            "HAGA ESTA NOCHE:\n"
            "1. Mantenga la calma y quédese con los niños en un lugar seguro.\n"
            "2. Escriba todo lo que recuerde: hora, lugar, qué dijeron los agentes.\n"
            "3. Llame a una persona de confianza y comparta lo ocurrido.\n"
            "4. Reúna documentos: identificaciones, comprobantes de los 14 años aquí.\n"
            "5. No vaya sola a buscarlo de noche; coordine con el pastor.\n\n"
            "NO HAGA:\n"
            "• No firme nada sin un abogado. • No abra la puerta sin orden judicial.\n"
            "• No mienta a los agentes. • No publique detalles en redes sociales."
        ),
        "sources": ["pastor intake"],
    },
    {
        "title": "5. Pastoral message draft",
        "content": (
            "María, acabo de escuchar lo de José y estoy orando por ustedes en este "
            "momento. No están solos — la iglesia está con su familia. Ya estamos "
            "buscando un abogado de inmigración y le preparé una lista de pasos para "
            "esta noche. Mañana temprano hablamos. Dios está con ustedes."
        ),
        "sources": ["pastor intake"],
    },
]


def print_stage(stage):
    bar = "=" * 60
    print(f"\n{bar}\n{stage['title']}\n{bar}")
    print(stage["content"])
    print(f"\nSources: {', '.join(stage.get('sources', []))}")
    print(f"Disclaimer: {stage.get('disclaimer', guardrails.disclaimer())}")
    problems = guardrails.check_output(stage["content"])
    if problems:
        print(f"!! safety check flagged: {problems}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--auto-approve", action="store_true")
    args = parser.parse_args()

    print("INTAKE (pastor types what Maria told him):")
    print(f'"{INTAKE}"')

    if args.dry_run:
        print("\n[dry-run: canned outputs, no API calls]")
        for stage in DRY_RUN:
            stage = dict(stage)
            stage.setdefault("disclaimer", guardrails.disclaimer())
            stage.setdefault("needs_review", True)
            print_stage(stage)
            if not args.auto_approve:
                ok = input("\nPastor approves? [Y/n] ").strip().lower()
                if ok not in ("", "y", "yes"):
                    print("Pipeline stopped by pastor.")
                    return
        print("\nDemo complete — every stage approved by the pastor.")
        return

    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass  # optional: run_live_test.sh already sources .env via bash

    client = GlooClient()

    def approve(stage):
        if args.auto_approve:
            return True
        answer = input("\nPastor approves and continues? [Y/n] ").strip().lower()
        return answer in ("", "y", "yes")

    try:
        results = stages.run_pipeline(client, INTAKE, approve=approve, language="es")
    except Exception as e:  # noqa: BLE001 — surface cleanly for the demo
        print(f"\nPipeline error: {e}")
        return
    for stage in results:
        print_stage(stage)
    print("\nDemo complete.")


if __name__ == "__main__":
    main()
