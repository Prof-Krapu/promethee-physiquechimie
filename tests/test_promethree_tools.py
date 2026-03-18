# tests/test_promethree_tools.py
"""
Tests unitaires pour tools/promethree_tools.py

Couvre :
- generate_exercise : cas nominal, validation des entrées, bornes nb_questions
- generate_correction : cas nominal, validation des entrées, option avec_conseils
- generate_qcm : cas nominal, validation des entrées, bornes nb_questions
"""
import pytest
from unittest.mock import patch

import tools.promethree_tools as pt


# ── generate_exercise ─────────────────────────────────────────────────────────

class TestGenerateExercise:
    def test_nominal(self):
        result = pt.generate_exercise(theme="mécanique newtonienne", niveau="terminale")
        assert "EXERCICE PROMÉTHÉE" in result
        assert "mécanique newtonienne" in result
        assert "terminale" in result.lower()

    def test_includes_nb_questions(self):
        result = pt.generate_exercise(theme="optique", niveau="seconde", nb_questions=6)
        assert "6" in result

    def test_empty_theme_returns_error(self):
        result = pt.generate_exercise(theme="   ", niveau="terminale")
        assert result.startswith("Erreur")

    def test_empty_niveau_returns_error(self):
        result = pt.generate_exercise(theme="optique", niveau="   ")
        assert result.startswith("Erreur")

    def test_nb_questions_clamped_min(self):
        result = pt.generate_exercise(theme="énergie", niveau="premiere", nb_questions=0)
        assert "1" in result

    def test_nb_questions_clamped_max(self):
        result = pt.generate_exercise(theme="énergie", niveau="premiere", nb_questions=99)
        assert "10" in result

    def test_difficulte_defaults_to_moyen_when_invalid(self):
        result = pt.generate_exercise(theme="énergie", niveau="premiere", difficulte="inconnu")
        assert "moyen" in result

    def test_discipline_included(self):
        result = pt.generate_exercise(theme="titrage", niveau="terminale", discipline="chimie")
        assert "chimie" in result.lower()

    def test_report_progress_called(self):
        with patch("tools.promethree_tools.report_progress") as mock_rp:
            pt.generate_exercise(theme="thermodynamique", niveau="MPSI")
        mock_rp.assert_called_once()


# ── generate_correction ───────────────────────────────────────────────────────

class TestGenerateCorrection:
    def test_nominal(self):
        enonce = "Un objet de masse 2 kg est soumis à une force de 10 N. Calculer l'accélération."
        result = pt.generate_correction(enonce=enonce, niveau="seconde")
        assert "CORRECTION PROMÉTHÉE" in result
        assert enonce in result

    def test_empty_enonce_returns_error(self):
        result = pt.generate_correction(enonce="   ", niveau="terminale")
        assert result.startswith("Erreur")

    def test_empty_niveau_returns_error(self):
        result = pt.generate_correction(enonce="Énoncé.", niveau="   ")
        assert result.startswith("Erreur")

    def test_avec_conseils_true_includes_instruction(self):
        result = pt.generate_correction(enonce="Énoncé.", niveau="seconde", avec_conseils=True)
        assert "Conseils" in result

    def test_avec_conseils_false_excludes_instruction(self):
        result = pt.generate_correction(enonce="Énoncé.", niveau="seconde", avec_conseils=False)
        assert "Conseils" not in result

    def test_report_progress_called(self):
        with patch("tools.promethree_tools.report_progress") as mock_rp:
            pt.generate_correction(enonce="Énoncé.", niveau="seconde")
        mock_rp.assert_called_once()


# ── generate_qcm ──────────────────────────────────────────────────────────────

class TestGenerateQcm:
    def test_nominal(self):
        result = pt.generate_qcm(theme="optique géométrique", niveau="seconde")
        assert "QCM PROMÉTHÉE" in result
        assert "optique géométrique" in result
        assert "seconde" in result.lower()

    def test_nb_questions_included(self):
        result = pt.generate_qcm(theme="acide-base", niveau="terminale", nb_questions=8)
        assert "8" in result

    def test_empty_theme_returns_error(self):
        result = pt.generate_qcm(theme="   ", niveau="terminale")
        assert result.startswith("Erreur")

    def test_empty_niveau_returns_error(self):
        result = pt.generate_qcm(theme="optique", niveau="   ")
        assert result.startswith("Erreur")

    def test_nb_questions_clamped_min(self):
        result = pt.generate_qcm(theme="forces", niveau="seconde", nb_questions=0)
        assert "1" in result

    def test_nb_questions_clamped_max(self):
        result = pt.generate_qcm(theme="forces", niveau="seconde", nb_questions=50)
        assert "20" in result

    def test_avec_correction_true_includes_instruction(self):
        result = pt.generate_qcm(theme="thermochimie", niveau="terminale", avec_correction=True)
        assert "correction" in result.lower()

    def test_avec_correction_false_excludes_instruction(self):
        result = pt.generate_qcm(
            theme="thermochimie", niveau="terminale", avec_correction=False
        )
        # Without correction, the correction instruction text should not appear
        assert "Après le QCM" not in result

    def test_report_progress_called(self):
        with patch("tools.promethree_tools.report_progress") as mock_rp:
            pt.generate_qcm(theme="cinétique", niveau="terminale")
        mock_rp.assert_called_once()
