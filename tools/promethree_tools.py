# ============================================================================
# Prométhée — Assistant IA desktop (Physique-Chimie)
# ============================================================================
# Licence : GNU Affero General Public License v3.0 (AGPL-3.0)
#           https://www.gnu.org/licenses/agpl-3.0.html
# Année   : 2026
# ============================================================================

"""
tools/promethree_tools.py — Génération d'exercices de Physique-Chimie
=======================================================================

Outils exposés (3) :
  - generate_exercise   : Génère un exercice structuré (énoncé + barème)
  - generate_correction : Génère la correction détaillée d'un exercice
  - generate_qcm        : Génère un QCM à choix multiples avec correction

Ce module s'enregistre automatiquement dans tools_engine au premier import.
"""

from typing import Optional

from core.tools_engine import tool, set_current_family, report_progress, _TOOL_ICONS

set_current_family("promethree_tools", "Exercices Prométhée 📝", "📝")

_TOOL_ICONS.update({
    "generate_exercise":   "📋",
    "generate_correction": "✅",
    "generate_qcm":        "🔢",
})


@tool(
    name="generate_exercise",
    description=(
        "Génère un exercice de Physique ou de Chimie au format Prométhée, "
        "structuré avec un énoncé, des questions numérotées et un barème. "
        "Indiquez le niveau scolaire (ex: 'terminale', 'MPSI', 'BTS'), "
        "la discipline ('physique', 'chimie' ou 'physique-chimie') et le thème "
        "(ex: 'lois de Newton', 'équilibres acido-basiques', 'thermodynamique'). "
        "Retourne un texte structuré prêt à imprimer ou à exporter."
    ),
    parameters={
        "type": "object",
        "properties": {
            "theme": {
                "type": "string",
                "description": (
                    "Thème ou chapitre du programme visé. "
                    "Exemples : 'mécanique newtonienne', 'électrocinétique', "
                    "'réactions acido-basiques', 'cinétique chimique', 'optique'."
                ),
            },
            "niveau": {
                "type": "string",
                "description": (
                    "Niveau scolaire cible. "
                    "Exemples : 'seconde', 'premiere', 'terminale', 'MPSI', 'BTS'."
                ),
            },
            "discipline": {
                "type": "string",
                "description": "Discipline : 'physique', 'chimie' ou 'physique-chimie'. Défaut : 'physique-chimie'.",
            },
            "nb_questions": {
                "type": "integer",
                "description": "Nombre de questions à générer (1–10). Défaut : 4.",
            },
            "difficulte": {
                "type": "string",
                "description": "Niveau de difficulté : 'facile', 'moyen' ou 'difficile'. Défaut : 'moyen'.",
            },
        },
        "required": ["theme", "niveau"],
    },
)
def generate_exercise(
    theme: str,
    niveau: str,
    discipline: str = "physique-chimie",
    nb_questions: int = 4,
    difficulte: str = "moyen",
) -> str:
    """
    Retourne un exercice structuré (énoncé + questions numérotées + barème).
    La génération effective est assurée par le LLM ; ce tool construit le
    prompt structurant et retourne les métadonnées sous forme de texte.
    """
    if not theme.strip():
        return "Erreur : le thème de l'exercice ne peut pas être vide."
    if not niveau.strip():
        return "Erreur : le niveau scolaire ne peut pas être vide."

    nb_questions = max(1, min(nb_questions, 10))
    discipline = discipline.lower().strip()
    difficulte = difficulte.lower().strip()

    if difficulte not in ("facile", "moyen", "difficile"):
        difficulte = "moyen"

    report_progress(f"📋 Génération d'un exercice de {discipline} — {theme} ({niveau})…")

    return (
        f"[EXERCICE PROMÉTHÉE — {discipline.upper()} — {niveau.upper()}]\n"
        f"Thème       : {theme}\n"
        f"Difficulté  : {difficulte}\n"
        f"Nb questions: {nb_questions}\n\n"
        f"Génère maintenant un exercice de {discipline} de niveau {niveau} "
        f"portant sur le thème « {theme} » de difficulté {difficulte}, "
        f"avec {nb_questions} question(s) numérotée(s) et un barème indicatif sur 20 points. "
        f"Structure la réponse avec : "
        f"(1) un contexte / situation problème, "
        f"(2) les données numériques utiles, "
        f"(3) les questions numérotées avec leur barème, "
        f"(4) les formules clés à mobiliser."
    )


@tool(
    name="generate_correction",
    description=(
        "Génère la correction détaillée et rédigée d'un exercice de Physique-Chimie. "
        "Fournissez l'énoncé complet (ou les questions) et le niveau scolaire. "
        "La correction inclut les calculs intermédiaires, les unités, et des conseils "
        "méthodologiques. Idéal après avoir utilisé generate_exercise."
    ),
    parameters={
        "type": "object",
        "properties": {
            "enonce": {
                "type": "string",
                "description": "Texte complet de l'exercice à corriger (énoncé + questions).",
            },
            "niveau": {
                "type": "string",
                "description": "Niveau scolaire pour adapter le niveau de détail de la correction.",
            },
            "avec_conseils": {
                "type": "boolean",
                "description": "Si true, ajoute des conseils méthodologiques pour l'élève. Défaut : true.",
            },
        },
        "required": ["enonce", "niveau"],
    },
)
def generate_correction(
    enonce: str,
    niveau: str,
    avec_conseils: bool = True,
) -> str:
    """
    Retourne une instruction structurée pour générer la correction d'un exercice.
    """
    if not enonce.strip():
        return "Erreur : l'énoncé de l'exercice ne peut pas être vide."
    if not niveau.strip():
        return "Erreur : le niveau scolaire ne peut pas être vide."

    report_progress(f"✅ Génération de la correction ({niveau})…")

    conseils_instr = (
        " Ajoute une section 'Conseils méthodologiques' avec 2 à 3 conseils pratiques."
        if avec_conseils else ""
    )

    return (
        f"[CORRECTION PROMÉTHÉE — {niveau.upper()}]\n\n"
        f"Corrige l'exercice suivant de façon détaillée et rédigée, "
        f"en montrant tous les calculs intermédiaires avec leurs unités SI. "
        f"Numérote tes réponses pour correspondre aux questions de l'énoncé. "
        f"Encadre les résultats finaux.{conseils_instr}\n\n"
        f"--- ÉNONCÉ ---\n{enonce}"
    )


@tool(
    name="generate_qcm",
    description=(
        "Génère un QCM (Questionnaire à Choix Multiples) de Physique-Chimie "
        "avec correction intégrée. Précisez le thème, le niveau, et le nombre "
        "de questions. Chaque question comporte 4 propositions (A, B, C, D) "
        "dont exactement une est correcte. Compatible avec l'export Moodle XML "
        "(lms_tools). Mots-clés déclencheurs : 'QCM', 'quiz', 'questionnaire à choix', "
        "'Prométhée QCM'."
    ),
    parameters={
        "type": "object",
        "properties": {
            "theme": {
                "type": "string",
                "description": "Thème du QCM (ex: 'optique géométrique', 'titrage acido-basique').",
            },
            "niveau": {
                "type": "string",
                "description": "Niveau scolaire (ex: 'terminale', 'MPSI', 'BTS').",
            },
            "nb_questions": {
                "type": "integer",
                "description": "Nombre de questions du QCM (1–20). Défaut : 5.",
            },
            "avec_correction": {
                "type": "boolean",
                "description": "Si true, inclut la correction après le QCM. Défaut : true.",
            },
        },
        "required": ["theme", "niveau"],
    },
)
def generate_qcm(
    theme: str,
    niveau: str,
    nb_questions: int = 5,
    avec_correction: bool = True,
) -> str:
    """
    Retourne une instruction structurée pour générer un QCM de Physique-Chimie.
    """
    if not theme.strip():
        return "Erreur : le thème du QCM ne peut pas être vide."
    if not niveau.strip():
        return "Erreur : le niveau scolaire ne peut pas être vide."

    nb_questions = max(1, min(nb_questions, 20))

    report_progress(f"🔢 Génération d'un QCM {theme} — {niveau} ({nb_questions} questions)…")

    correction_instr = (
        " Après le QCM, donne la correction en indiquant la bonne réponse "
        "et une brève explication pour chaque question."
        if avec_correction else ""
    )

    return (
        f"[QCM PROMÉTHÉE — {niveau.upper()} — {theme.upper()}]\n\n"
        f"Génère un QCM de {nb_questions} question(s) de Physique-Chimie "
        f"de niveau {niveau} sur le thème « {theme} ». "
        f"Pour chaque question : "
        f"(1) une question claire et précise, "
        f"(2) quatre propositions numérotées A, B, C, D, "
        f"(3) une seule bonne réponse par question.{correction_instr}"
    )
