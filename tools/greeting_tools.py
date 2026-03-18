# ============================================================================
# Prométhée — Assistant IA desktop (Physique-Chimie)
# ============================================================================

"""
greeting_tools.py — Outil de salutation pour Prométhée
=======================================================

- Répond à une salutation de l'utilisateur avec un message de bienvenue.
"""

from typing import Optional

from core.tools_engine import report_progress, set_current_family, tool

set_current_family("greeting_tools", "Salutations", "👋")


@tool(
    name="say_hello",
    description="Répond à une salutation de l'utilisateur avec un message de bienvenue personnalisé. "
    "Utilisez cet outil lorsque l'utilisateur dit 'bonjour', 'salut', 'hello' ou toute autre salutation.",
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Prénom ou nom de l'utilisateur à saluer (optionnel).",
            }
        },
        "required": [],
    },
)
def say_hello(name: Optional[str] = None) -> str:
    """
    Renvoie un message de bienvenue à l'utilisateur.
    """
    report_progress("Préparation du message de salutation...")
    if name:
        return f"Bonjour, {name} ! Je suis Prométhée, votre assistant IA spécialisé en Physique-Chimie. Comment puis-je vous aider ?"
    return "Bonjour ! Je suis Prométhée, votre assistant IA spécialisé en Physique-Chimie. Comment puis-je vous aider ?"
