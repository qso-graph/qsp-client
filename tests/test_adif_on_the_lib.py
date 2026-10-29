"""qsp-client's ADIF reading is qso_graph_lib.adif's, and keeps what its own scanner lost."""

from __future__ import annotations

from pathlib import Path

from qsp_client.adif.convert import parse_adif
from qsp_client.adif.reader import parse_adi_file, parse_adi_text


def test_a_tag_inside_a_value_cannot_replace_a_field():
    """The old scanner found tags anywhere, values included: this comment made the QSO
    W9XYZ's."""
    text = "<CALL:5>K1ABC<COMMENT:24>worked <CALL:5>W9XYZ too<BAND:3>20m<EOR>"
    assert parse_adi_text(text)[0]["call"] == "K1ABC"
    assert next(parse_adif(text))["comment"] == "worked <CALL:5>W9XYZ too"


def test_a_file_s_crlf_multiline_field_keeps_the_fields_after_it(tmp_path: Path):
    """read_text() turned CR LF into LF, one character short of the declared length."""
    p = tmp_path / "log.adi"
    p.write_bytes(b"<CALL:5>K1ABC<NOTES:9>one\r\ntwo<BAND:3>20m<EOR>\r\n")
    assert parse_adi_file(p)[0] == {"call": "K1ABC", "band": "20m"}


def test_header_fields_are_not_a_record():
    text = "eQSL export\n<PROGRAMID:21>eQSL.cc DownloadInBox<EOH>\n<CALL:5>K1ABC<EOR>"
    assert list(parse_adif(text)) == [{"call": "K1ABC"}]
