"""The qsp-adif-convert command answers --help."""

import pytest

from qsp_client.adif.convert import main


def test_convert_help(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as done:
        main(["--help"])
    assert done.value.code == 0
    assert "qsp-adif-convert" in capsys.readouterr().out
