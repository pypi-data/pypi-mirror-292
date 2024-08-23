import sys

from unittest.mock import patch
from importlib import import_module, reload
from cared import main


def test_cared_and_cared_cli_installed(capsys, monkeypatch):
    """Test for cared and cared-cli installed"""
    cared_cli = type(sys)("cared_cgi")
    with patch.dict(sys.modules, {"cared_cli": cared_cli}):
        reload(sys.modules["cared"])
        import_module("cared_cli")
        monkeypatch.setattr("sys.argv", ["cared", "hello"])
        main()
    captured = capsys.readouterr()
    assert 'The package "cared" has no functionality.' in captured.out


def test_only_cared_installed(capsys, monkeypatch):
    """Test for only cared installed"""
    with patch.dict(sys.modules, {"cared_cli": None}):
        reload(sys.modules["cared"])
        monkeypatch.setattr("sys.argv", ["cared", "hello"])
        main()
    captured = capsys.readouterr()
    assert 'You most likely want "cared-cli" instead' in captured.out
