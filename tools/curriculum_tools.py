# ============================================================================
# Prométhée — Assistant IA desktop (Physique-Chimie)
# ============================================================================
# Auteur  : Vincent DURIEUX
# Licence : GNU Affero General Public License v3.0 (AGPL-3.0)
#           https://www.gnu.org/licenses/agpl-3.0.html
# Année   : 2026
# ----------------------------------------------------------------------------
# Ce fichier fait partie du projet Prométhée.
# Vous pouvez le redistribuer et/ou le modifier selon les termes de la
# licence AGPL-3.0 publiée par la Free Software Foundation.
# ============================================================================

"""
curriculum_tools.py — Consultation des programmes officiels de Physique-Chimie
===============================================================================

Outil exposé (1) :

  get_curriculum_guidelines : Interroge un moteur RAG local alimenté par
      les Bulletins Officiels (B.O.) de l'Éducation Nationale déposés dans
      le dossier data/programmes_eduscol/.

      Les fichiers PDF et texte sont ingérés automatiquement au premier appel
      (via rag_engine.ingest_file) et stockés dans Qdrant en scope global
      pour être réutilisés entre les sessions.

Utilisation typique :
    « Quelles sont les capacités exigibles en optique en Terminale ? »
    → Le LLM appelle get_curriculum_guidelines(query="capacités optique", level="Terminale")
    → Le moteur RAG renvoie les passages pertinents extraits des B.O.

Mots-clés déclencheurs (à mentionner dans votre message) :
    « Eduscol », « programme officiel », « au programme », « B.O. »,
    « Bulletin Officiel », « capacités exigibles ».
"""

import json
import logging
from pathlib import Path

import core.rag_engine as rag
from core.tools_engine import report_progress, set_current_family, tool

_log = logging.getLogger(__name__)

# Dossier contenant les Bulletins Officiels (PDF / TXT)
_PROGRAMMES_DIR = Path(__file__).parent.parent / "data" / "programmes_eduscol"

# Extensions acceptées pour l'ingestion
_ACCEPTED_EXTENSIONS = {".pdf", ".txt", ".md"}

set_current_family("curriculum_tools", "Programmes Eduscol (RAG)", "📋")


def _ingest_curriculum_files() -> list[str]:
    """
    Parcourt data/programmes_eduscol/ et ingère les nouveaux fichiers dans Qdrant.

    Les fichiers déjà présents dans les sources globales de Qdrant sont ignorés
    pour éviter la duplication des chunks à chaque appel.

    Returns
    -------
    list[str]
        Noms des fichiers nouvellement ingérés lors de cet appel.
    """
    if not _PROGRAMMES_DIR.exists():
        return []

    files = [
        f for f in _PROGRAMMES_DIR.iterdir()
        if f.suffix.lower() in _ACCEPTED_EXTENSIONS and f.is_file()
    ]
    if not files:
        return []

    # Sources déjà indexées dans le scope global
    already_ingested = {s["source"] for s in rag.list_sources(conversation_id=None)}

    newly_ingested: list[str] = []
    for f in files:
        if f.name in already_ingested:
            _log.debug(f"[curriculum] Déjà ingéré : {f.name}")
            continue
        count = rag.ingest_file(str(f), conversation_id=None)
        if count > 0:
            newly_ingested.append(f.name)
            _log.info(f"[curriculum] Ingéré : {f.name} ({count} chunks)")
        else:
            _log.warning(f"[curriculum] Échec d'ingestion : {f.name}")

    return newly_ingested


@tool(
    name="get_curriculum_guidelines",
    description=(
        "Consulte les programmes officiels de Physique-Chimie de l'Éducation Nationale "
        "(Bulletins Officiels / Eduscol) via un moteur RAG local. "
        "Les documents PDF déposés dans data/programmes_eduscol/ sont vectorisés "
        "automatiquement (modèle all-MiniLM-L6-v2, 100 % CPU) et interrogés par "
        "recherche sémantique. "
        "Idéal pour vérifier les capacités exigibles, les notions au programme ou "
        "les limites d'un niveau donné (Seconde, Première, Terminale, MPSI, MP). "
        "Mots-clés déclencheurs : 'Eduscol', 'programme officiel', 'au programme', "
        "'capacités exigibles', 'BO', 'Bulletin Officiel'."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Question ou notion à rechercher dans les programmes officiels. "
                    "Ex : 'capacités exigibles en optique en Terminale', "
                    "'loi de Beer-Lambert au programme de Première', "
                    "'mécanique quantique en MPSI'."
                ),
            },
            "level": {
                "type": "string",
                "description": (
                    "Niveau scolaire ciblé (optionnel). "
                    "Ex : 'Seconde', 'Première', 'Terminale', 'MPSI', 'MP', 'Lycée'."
                ),
            },
        },
        "required": ["query"],
    },
)
def get_curriculum_guidelines(query: str, level: str = "") -> str:
    """
    Interroge les Bulletins Officiels via RAG.

    Les fichiers présents dans data/programmes_eduscol/ sont ingérés
    automatiquement au premier appel si ce n'est pas déjà fait.

    Parameters
    ----------
    query : str
        Question sur le programme ou notion à vérifier.
    level : str, optional
        Niveau scolaire pour affiner la recherche.

    Returns
    -------
    str
        JSON contenant le statut et les passages pertinents extraits des B.O.,
        ou un message d'erreur clair si le RAG n'est pas disponible.
    """
    report_progress("Consultation des programmes officiels Eduscol (RAG)...")

    # ── 1. Vérifier la disponibilité du moteur RAG ───────────────────────────
    if not rag.is_available():
        return json.dumps(
            {
                "status": "unavailable",
                "message": (
                    "Le moteur RAG n'est pas disponible (Qdrant ou le modèle "
                    "d'embeddings non initialisé). Vérifiez l'installation de "
                    "qdrant-client et sentence-transformers."
                ),
            },
            ensure_ascii=False,
        )

    # ── 2. Vérifier la présence de fichiers ──────────────────────────────────
    if not _PROGRAMMES_DIR.exists() or not any(
        f for f in _PROGRAMMES_DIR.iterdir()
        if f.suffix.lower() in _ACCEPTED_EXTENSIONS and f.is_file()
    ):
        return json.dumps(
            {
                "status": "no_documents",
                "message": (
                    f"Aucun document trouvé dans {_PROGRAMMES_DIR}. "
                    "Déposez-y les B.O. officiels au format PDF ou texte "
                    "depuis le site Eduscol (https://eduscol.education.fr/)."
                ),
            },
            ensure_ascii=False,
        )

    # ── 3. Ingérer les nouveaux fichiers ─────────────────────────────────────
    newly_ingested = _ingest_curriculum_files()
    if newly_ingested:
        _log.info(f"[curriculum] Nouveaux fichiers ingérés : {newly_ingested}")

    # ── 4. Construire la requête enrichie avec le niveau ─────────────────────
    full_query = f"{level} {query}".strip() if level else query

    # ── 5. Recherche sémantique dans le RAG ──────────────────────────────────
    context = rag.build_rag_context(full_query, conversation_id=None)

    if not context:
        return json.dumps(
            {
                "status": "no_results",
                "query": full_query,
                "message": (
                    "Aucun passage pertinent trouvé pour cette requête dans les "
                    "programmes disponibles. Essayez avec des termes différents "
                    "ou vérifiez que les B.O. correspondants sont dans "
                    "data/programmes_eduscol/."
                ),
            },
            ensure_ascii=False,
        )

    return json.dumps(
        {
            "status": "ok",
            "query": full_query,
            "context": context,
        },
        ensure_ascii=False,
        indent=2,
    )
