# tests/test_curriculum_tools.py
"""
Tests unitaires pour tools/curriculum_tools.py

Couvre :
- get_curriculum_guidelines : RAG indisponible, dossier vide, dossier absent,
  aucun résultat de recherche, résultat valide.
- _ingest_curriculum_files : dossier absent, fichiers déjà ingérés, nouveaux
  fichiers, extensions rejetées.
"""
import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── Stubs pour les dépendances lourdes absentes en CI ────────────────────────
for _mod in ["sentence_transformers", "fitz", "pubchempy", "scipy", "scipy.constants"]:
    sys.modules.setdefault(_mod, types.ModuleType(_mod))

import tools.curriculum_tools as ct
import core.rag_engine as rag


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _rag_unavailable():
    return patch.object(rag, "is_available", return_value=False)


def _rag_available():
    return patch.object(rag, "is_available", return_value=True)


def _no_sources():
    return patch.object(rag, "list_sources", return_value=[])


def _no_context():
    return patch.object(rag, "build_rag_context", return_value="")


def _with_context(text="### Contexte documentaire pertinent :\n[1] 🌐 (doc.pdf, score=0.92)\nPassage utile.\n"):
    return patch.object(rag, "build_rag_context", return_value=text)


def _ingest_ok(count=5):
    return patch.object(rag, "ingest_file", return_value=count)


# ─────────────────────────────────────────────────────────────────────────────
# Tests de get_curriculum_guidelines
# ─────────────────────────────────────────────────────────────────────────────


class TestGetCurriculumGuidelinesUnavailable:
    def test_returns_json_when_rag_unavailable(self):
        with _rag_unavailable():
            result = ct.get_curriculum_guidelines("optique")
        data = json.loads(result)
        assert data["status"] == "unavailable"

    def test_message_present_when_unavailable(self):
        with _rag_unavailable():
            result = ct.get_curriculum_guidelines("mécanique")
        data = json.loads(result)
        assert "message" in data and len(data["message"]) > 0


class TestGetCurriculumGuidelinesNoDocuments:
    def test_returns_no_documents_when_dir_missing(self, tmp_path):
        missing_dir = tmp_path / "nonexistent"
        with _rag_available(), patch.object(ct, "_PROGRAMMES_DIR", missing_dir):
            result = ct.get_curriculum_guidelines("thermodynamique")
        data = json.loads(result)
        assert data["status"] == "no_documents"

    def test_returns_no_documents_when_dir_empty(self, tmp_path):
        empty_dir = tmp_path / "programmes"
        empty_dir.mkdir()
        with _rag_available(), patch.object(ct, "_PROGRAMMES_DIR", empty_dir):
            result = ct.get_curriculum_guidelines("thermodynamique")
        data = json.loads(result)
        assert data["status"] == "no_documents"

    def test_message_contains_eduscol_url(self, tmp_path):
        empty_dir = tmp_path / "p"
        empty_dir.mkdir()
        with _rag_available(), patch.object(ct, "_PROGRAMMES_DIR", empty_dir):
            result = ct.get_curriculum_guidelines("chimie")
        data = json.loads(result)
        assert "eduscol" in data["message"].lower()


class TestGetCurriculumGuidelinesNoResults:
    def test_returns_no_results_when_context_empty(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        (d / "prog.txt").write_text("contenu programme", encoding="utf-8")
        with (
            _rag_available(),
            patch.object(ct, "_PROGRAMMES_DIR", d),
            _no_sources(),
            _ingest_ok(),
            _no_context(),
        ):
            result = ct.get_curriculum_guidelines("notion inconnue")
        data = json.loads(result)
        assert data["status"] == "no_results"
        assert "query" in data

    def test_query_included_in_no_results_response(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        (d / "prog.txt").write_text("x", encoding="utf-8")
        with (
            _rag_available(),
            patch.object(ct, "_PROGRAMMES_DIR", d),
            _no_sources(),
            _ingest_ok(),
            _no_context(),
        ):
            result = ct.get_curriculum_guidelines("loi de Faraday", level="Terminale")
        data = json.loads(result)
        assert "Terminale" in data["query"] or "Faraday" in data["query"]


class TestGetCurriculumGuidelinesSuccess:
    def test_returns_ok_status(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        (d / "prog.txt").write_text("programme officiel", encoding="utf-8")
        with (
            _rag_available(),
            patch.object(ct, "_PROGRAMMES_DIR", d),
            _no_sources(),
            _ingest_ok(),
            _with_context(),
        ):
            result = ct.get_curriculum_guidelines("optique géométrique")
        data = json.loads(result)
        assert data["status"] == "ok"

    def test_context_included_in_response(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        (d / "prog.txt").write_text("programme officiel", encoding="utf-8")
        ctx = "### Contexte documentaire pertinent :\n[1] 🌐 (bo.pdf, score=0.95)\nLoi de Beer-Lambert.\n"
        with (
            _rag_available(),
            patch.object(ct, "_PROGRAMMES_DIR", d),
            _no_sources(),
            _ingest_ok(),
            _with_context(ctx),
        ):
            result = ct.get_curriculum_guidelines("Beer-Lambert")
        data = json.loads(result)
        assert "Beer-Lambert" in data["context"]

    def test_level_prepended_to_query(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        (d / "prog.txt").write_text("x", encoding="utf-8")
        captured_queries: list[str] = []

        def _fake_build(q, **kw):
            captured_queries.append(q)
            return "### Contexte\n[1] (src, score=0.8)\nPassage.\n"

        with (
            _rag_available(),
            patch.object(ct, "_PROGRAMMES_DIR", d),
            _no_sources(),
            _ingest_ok(),
            patch.object(rag, "build_rag_context", side_effect=_fake_build),
        ):
            ct.get_curriculum_guidelines("mécanique des fluides", level="MPSI")

        assert captured_queries and "MPSI" in captured_queries[0]

    def test_returns_string(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        (d / "prog.txt").write_text("x", encoding="utf-8")
        with (
            _rag_available(),
            patch.object(ct, "_PROGRAMMES_DIR", d),
            _no_sources(),
            _ingest_ok(),
            _with_context(),
        ):
            result = ct.get_curriculum_guidelines("chimie organique")
        assert isinstance(result, str)

    def test_result_is_valid_json(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        (d / "prog.txt").write_text("x", encoding="utf-8")
        with (
            _rag_available(),
            patch.object(ct, "_PROGRAMMES_DIR", d),
            _no_sources(),
            _ingest_ok(),
            _with_context(),
        ):
            result = ct.get_curriculum_guidelines("spectrométrie")
        assert isinstance(json.loads(result), dict)


# ─────────────────────────────────────────────────────────────────────────────
# Tests de _ingest_curriculum_files
# ─────────────────────────────────────────────────────────────────────────────


class TestIngestCurriculumFiles:
    def test_returns_empty_when_dir_missing(self, tmp_path):
        missing = tmp_path / "nonexistent"
        with patch.object(ct, "_PROGRAMMES_DIR", missing):
            assert ct._ingest_curriculum_files() == []

    def test_returns_empty_when_dir_empty(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        with patch.object(ct, "_PROGRAMMES_DIR", d), _no_sources():
            assert ct._ingest_curriculum_files() == []

    def test_ignores_unsupported_extensions(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        (d / "readme.rst").write_text("texte", encoding="utf-8")
        (d / "data.csv").write_text("a,b", encoding="utf-8")
        with patch.object(ct, "_PROGRAMMES_DIR", d), _no_sources(), _ingest_ok():
            result = ct._ingest_curriculum_files()
        assert result == []

    def test_skips_already_ingested_files(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        (d / "prog.txt").write_text("contenu", encoding="utf-8")
        sources = [{"source": "prog.txt", "count": 3, "scope": "global"}]
        with (
            patch.object(ct, "_PROGRAMMES_DIR", d),
            patch.object(rag, "list_sources", return_value=sources),
            _ingest_ok(),
        ):
            result = ct._ingest_curriculum_files()
        assert result == []

    def test_ingests_new_txt_file(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        (d / "nouveau.txt").write_text("contenu programme", encoding="utf-8")
        with patch.object(ct, "_PROGRAMMES_DIR", d), _no_sources(), _ingest_ok(count=3):
            result = ct._ingest_curriculum_files()
        assert "nouveau.txt" in result

    def test_ingests_new_md_file(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        (d / "prog.md").write_text("# Programme", encoding="utf-8")
        with patch.object(ct, "_PROGRAMMES_DIR", d), _no_sources(), _ingest_ok(count=2):
            result = ct._ingest_curriculum_files()
        assert "prog.md" in result

    def test_skips_file_when_ingest_returns_zero(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        (d / "vide.txt").write_text("", encoding="utf-8")
        with patch.object(ct, "_PROGRAMMES_DIR", d), _no_sources(), _ingest_ok(count=0):
            result = ct._ingest_curriculum_files()
        assert result == []

    def test_ingests_multiple_files(self, tmp_path):
        d = tmp_path / "programmes"
        d.mkdir()
        (d / "a.txt").write_text("premier", encoding="utf-8")
        (d / "b.txt").write_text("deuxième", encoding="utf-8")
        with patch.object(ct, "_PROGRAMMES_DIR", d), _no_sources(), _ingest_ok(count=4):
            result = ct._ingest_curriculum_files()
        assert len(result) == 2
