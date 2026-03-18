# tests/test_greeting_tools.py
"""
Tests unitaires pour tools/greeting_tools.py

Couvre :
- say_hello : sans nom, avec nom
"""
import sys
import types
import pytest
from unittest.mock import patch

for mod in ["sentence_transformers", "fitz"]:
    sys.modules.setdefault(mod, types.ModuleType(mod))

import tools.greeting_tools as gt


class TestSayHello:
    def test_returns_string(self):
        result = gt.say_hello()
        assert isinstance(result, str)

    def test_contains_bonjour(self):
        result = gt.say_hello()
        assert "Bonjour" in result

    def test_with_name(self):
        result = gt.say_hello(name="Alice")
        assert "Alice" in result
        assert "Bonjour" in result

    def test_without_name(self):
        result = gt.say_hello()
        assert "Prométhée" in result

    def test_none_name_treated_as_anonymous(self):
        result = gt.say_hello(name=None)
        assert "Bonjour" in result
        assert "Prométhée" in result

    def test_report_progress_called(self):
        with patch.object(gt, "report_progress") as mock_rp:
            gt.say_hello()
        mock_rp.assert_called_once()
