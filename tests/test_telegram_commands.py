# tests/test_telegram_commands.py
"""Tests unitaires pour les commandes du bot Telegram."""
import pytest
import sys
import types
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def _inject_stubs():
    """Injecte les stubs nécessaires pour importer main_telegram sans ses dépendances lourdes."""
    stubs = {
        "dotenv": MagicMock(),
        "telegram": MagicMock(),
        "telegram.ext": MagicMock(),
        "pandas": MagicMock(),
        "numpy": MagicMock(),
        "scipy": MagicMock(),
        "matplotlib": MagicMock(),
        "matplotlib.pyplot": MagicMock(),
    }
    for name, stub in stubs.items():
        sys.modules.setdefault(name, stub)

    # Config stub minimal
    config_mod = types.ModuleType("core.config")
    config_class = MagicMock()
    config_class.OPENAI_API_KEY = "test-key"
    config_class.active_model = MagicMock(return_value="test-model")
    config_mod.Config = config_class
    sys.modules.setdefault("core.config", config_mod)

    # Stub tools.register_all pour éviter les imports de pandas/scipy/etc.
    tools_mod = types.ModuleType("tools")
    tools_mod.register_all = MagicMock()
    sys.modules.setdefault("tools", tools_mod)

    # Stubs pour core.llm_service et core.tools_engine
    for mod_name in ("core.llm_service", "core.tools_engine"):
        sys.modules.setdefault(mod_name, MagicMock())


_inject_stubs()


@pytest.fixture()
def mock_update():
    """Crée un faux objet Update Telegram."""
    update = MagicMock()
    user = MagicMock()
    user.mention_html.return_value = "<b>Alice</b>"
    update.effective_user = user
    update.message = MagicMock()
    update.message.reply_html = AsyncMock()
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture()
def mock_context():
    """Crée un faux objet Context Telegram."""
    context = MagicMock()
    context.user_data = {}
    return context


@pytest.fixture()
def bonjour_fn():
    """Extrait cmd_bonjour depuis main_telegram sans exécuter le bloc __main__."""
    sys.modules.pop("main_telegram", None)
    import main_telegram  # noqa: PLC0415
    return main_telegram.cmd_bonjour


@pytest.mark.asyncio
async def test_cmd_bonjour_replies(bonjour_fn, mock_update, mock_context):
    """cmd_bonjour envoie bien un message de bienvenue via reply_html."""
    await bonjour_fn(mock_update, mock_context)

    mock_update.message.reply_html.assert_called_once()
    call_text = mock_update.message.reply_html.call_args[0][0]
    assert "Bonjour" in call_text or "bonjour" in call_text.lower()
    assert "Prométhée" in call_text


@pytest.mark.asyncio
async def test_cmd_bonjour_mentions_user(bonjour_fn, mock_update, mock_context):
    """cmd_bonjour inclut la mention HTML de l'utilisateur dans la réponse."""
    await bonjour_fn(mock_update, mock_context)

    call_text = mock_update.message.reply_html.call_args[0][0]
    assert "<b>Alice</b>" in call_text
