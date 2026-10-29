"""
ADIF (.adi) reading into QSORecord, on qso_graph_lib.adif.

- The ADI itself is read by qso_graph_lib.adif, the fleet's one reader, as ADIF 3.1.7
  defines it. This module's own scanner looked for tags anywhere in the text, values
  included, so a COMMENT containing "<CALL:5>W9XYZ" replaced the QSO's callsign.
- Returns a list[QSORecord] (a TypedDict), with basic normalization:
    * "station_callsign" -> "station_call"
    * keys are lower_snake_case
    * common fields available when present: call, station_call, band,
      mode, qso_date, time_on, time_off, rst_rcvd, rst_sent, freq
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, cast

from qso_graph_lib import adif

__all__ = ["QSORecord", "parse_adi_file", "parse_adi_text"]


class QSORecord(TypedDict, total=False):
    """A single QSO in normalized, lower_snake_case key form."""

    call: str
    station_call: str  # normalized from station_callsign
    band: str
    mode: str
    qso_date: str  # YYYYMMDD per ADIF
    time_on: str  # HHMM[SS]
    time_off: str  # HHMM[SS]
    rst_rcvd: str
    rst_sent: str
    freq: str
    # Other keys may be present at runtime (TypedDict total=False).


def _to_snake(name: str) -> str:
    """
    Converts `str `name` to str lower case
    """
    return name.strip().lower()


def _normalize_key(k: str) -> str:
    """Map ADIF field names to the normalized keys we use."""
    k = _to_snake(k)
    if k == "station_callsign":
        return "station_call"
    return k


def parse_adi_text(text: str) -> list[QSORecord]:
    """
    Parse ADIF text into a list of QSORecord dicts.

    Parameters
    ----------
    text:
        Full contents of a .adi file (header + records).

    Returns
    -------
    list[QSORecord]
    """
    records_raw: list[dict[str, str]] = []
    for rec in adif.iter_records(text):
        cur = {_normalize_key(k): v.strip() for k, v in rec.fields.items()}
        cur = {k: v for k, v in cur.items() if v != ""}
        if cur:
            records_raw.append(cur)
    return [record_as_qso(r) for r in records_raw]


def parse_adi_file(path: str | Path, encoding: str = "utf-8") -> list[QSORecord]:
    """
    Read and parse an ADIF (.adi) file.

    Parameters
    ----------
    path:
        File path to the ADIF text.
    encoding:
        Text encoding. ADIF files are commonly UTF-8; change if needed.
    """
    # With its line ends as written: text mode turns CR LF into LF and breaks every
    # multi-line field's declared length.
    with Path(path).open(encoding=encoding, errors="replace", newline="") as f:
        return parse_adi_text(f.read())


def record_as_qso(d: dict[str, str]) -> QSORecord:
    """
    Convert a raw parsed dict to a QSORecord.

    - Normalizes ADIF field names to lower_snake_case.
    - Uppercases callsigns (`call`, `station_call`) if present.
    - Drops keys not declared in `QSORecord` (keeps the record schema-tight).
    """
    # Normalize keys first
    tmp: dict[str, str] = {_normalize_key(k): v for k, v in d.items()}

    # Keep only fields that exist on the TypedDict schema
    allowed = set(QSORecord.__annotations__.keys())
    filtered = {k: v for k, v in tmp.items() if k in allowed}

    # Normalize callsigns to uppercase (if present)
    for key in ("call", "station_call"):
        if key in filtered and isinstance(filtered[key], str):
            filtered[key] = filtered[key].upper()

    return cast(QSORecord, filtered)
