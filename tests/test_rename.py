"""The qsp-mcp -> qsp-client rename keeps existing setups working."""

from __future__ import annotations

import pytest

from qsp_client import cli


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "DEFAULT_CONFIG_PATHS", [
        tmp_path / ".config" / "qsp-client" / "config.json",
        tmp_path / ".qsp-client.json",
        tmp_path / ".config" / "qsp-mcp" / "config.json",
        tmp_path / ".qsp-mcp.json",
    ])
    return tmp_path


def write(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}")
    return path


def test_old_config_still_found(home):
    old = write(home / ".config" / "qsp-mcp" / "config.json")
    assert cli._find_config() == old


def test_new_config_wins_over_old(home):
    write(home / ".config" / "qsp-mcp" / "config.json")
    new = write(home / ".config" / "qsp-client" / "config.json")
    assert cli._find_config() == new


def test_default_paths_new_first_then_old():
    names = [str(p) for p in cli.DEFAULT_CONFIG_PATHS]
    assert "qsp-client" in names[0] and "qsp-client" in names[1]
    assert "qsp-mcp" in names[2] and "qsp-mcp" in names[3]


def test_old_command_says_it_moved_then_runs(monkeypatch, capsys):
    ran = []
    monkeypatch.setattr(cli, "main", lambda: ran.append(True))
    cli.main_renamed()
    assert ran == [True]
    assert "qsp-mcp is now qsp-client" in capsys.readouterr().err


def test_version_is_qsp_clients(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["qsp-client", "--version"])
    with pytest.raises(SystemExit):
        cli._parse_args()
    assert capsys.readouterr().out.startswith("qsp-client ")
