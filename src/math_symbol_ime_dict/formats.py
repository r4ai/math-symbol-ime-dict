"""Dictionary file readers and writers.

The project keeps the dictionary content in one UTF-8 CSV file and writes
IME-specific import files from that source.
"""

from __future__ import annotations

import csv
import json
import plistlib
import uuid
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

REQUIRED_COLUMNS = {
    "reading",
    "symbol",
    "msime_pos",
    "google_pos",
    "azookey_hint",
    "comment",
}
AZOOKEY_MAC_PREF_KEY = "dev.ensan.inputmethod.azooKeyMac.preference.user_dictionary_temporal2"
AZOOKEY_NAMESPACE = uuid.UUID("695b8a79-512d-4701-aa4b-e079246c8ae9")


@dataclass(frozen=True, slots=True)
class Entry:
    """One source dictionary row."""

    reading: str
    symbol: str
    msime_pos: str
    google_pos: str
    azookey_hint: str
    comment: str

    @classmethod
    def from_row(cls, row: dict[str, str], line_number: int) -> Entry:
        """Create and validate an entry from a CSV row."""
        values = {key: (row.get(key) or "").strip() for key in REQUIRED_COLUMNS}
        missing = [key for key, value in values.items() if not value]
        if missing:
            joined = ", ".join(sorted(missing))
            raise ValueError(f"line {line_number}: missing required field(s): {joined}")
        if "\t" in values["reading"] or "\t" in values["symbol"]:
            raise ValueError(f"line {line_number}: tabs are not allowed in reading/symbol")
        if "\n" in values["reading"] or "\n" in values["symbol"]:
            raise ValueError(f"line {line_number}: newlines are not allowed")
        return cls(
            reading=values["reading"],
            symbol=values["symbol"],
            msime_pos=values["msime_pos"],
            google_pos=values["google_pos"],
            azookey_hint=values["azookey_hint"],
            comment=values["comment"],
        )


def read_source(path: Path) -> list[Entry]:
    """Read the canonical UTF-8 CSV source file."""
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            joined = ", ".join(sorted(missing))
            raise ValueError(f"source CSV is missing required column(s): {joined}")
        entries = [Entry.from_row(row, reader.line_num) for row in reader]
    validate_entries(entries)
    return entries


def validate_entries(entries: Sequence[Entry]) -> None:
    """Validate duplicate keys and basic field constraints."""
    seen: set[tuple[str, str]] = set()
    duplicates: list[str] = []
    for entry in entries:
        key = (entry.reading, entry.symbol)
        if key in seen:
            duplicates.append(f"{entry.reading!r}->{entry.symbol!r}")
        seen.add(key)
    if duplicates:
        sample = ", ".join(duplicates[:10])
        raise ValueError(f"duplicate reading/symbol pairs: {sample}")


def _tab_lines(rows: Iterable[Sequence[str]]) -> str:
    return "\r\n".join("\t".join(row) for row in rows) + "\r\n"


def write_msime(entries: Sequence[Entry], path: Path) -> None:
    """Write a Microsoft IME import file.

    Microsoft IME handles UTF-16 LE with BOM reliably. Python's utf-16 encoder
    writes a BOM and uses the platform-independent byte order marker.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    text = _tab_lines((entry.reading, entry.symbol, entry.msime_pos) for entry in entries)
    path.write_bytes(text.encode("utf-16"))


def write_google(entries: Sequence[Entry], path: Path, *, include_comments: bool = False) -> None:
    """Write a Google Japanese Input / Mozc user dictionary TSV.

    The portable three-column form is: reading, word, part of speech. The
    optional fourth column is a comment, matching the dictionary tool UI.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if include_comments:
        rows = ((entry.reading, entry.symbol, entry.google_pos, entry.comment) for entry in entries)
    else:
        rows = ((entry.reading, entry.symbol, entry.google_pos) for entry in entries)
    path.write_text(_tab_lines(rows), encoding="utf-8", newline="")


def _stable_azookey_id(entry: Entry) -> str:
    return str(uuid.uuid5(AZOOKEY_NAMESPACE, f"{entry.reading}\t{entry.symbol}"))


def azookey_payload(entries: Sequence[Entry]) -> dict[str, list[dict[str, str]]]:
    """Return the azooKeyMac user dictionary JSON payload."""
    return {
        "items": [
            {
                "id": _stable_azookey_id(entry),
                "word": entry.symbol,
                "reading": entry.reading,
                "hint": entry.azookey_hint,
            }
            for entry in entries
        ]
    }


def write_azookey_json(entries: Sequence[Entry], path: Path) -> None:
    """Write a human-readable azooKey payload for review and debugging."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = azookey_payload(entries)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_azookey_plist(entries: Sequence[Entry], path: Path) -> None:
    """Write an azooKey for macOS defaults-import plist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload_bytes = json.dumps(
        azookey_payload(entries),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    wrapped = {AZOOKEY_MAC_PREF_KEY: payload_bytes}
    with path.open("wb") as file:
        plistlib.dump(wrapped, file, fmt=plistlib.FMT_XML, sort_keys=True)


def write_all(entries: Sequence[Entry], out_dir: Path) -> dict[str, Path]:
    """Write all supported import files and return their paths."""
    outputs = {
        "msime": out_dir / "msime" / "math_symbols_msime_utf16le.txt",
        "google": out_dir / "google" / "math_symbols_google_utf8.tsv",
        "google_with_comments": out_dir / "google" / "math_symbols_google_utf8_with_comments.tsv",
        "azookey_plist": out_dir / "azookey" / "math_symbols_azookeymac.plist",
        "azookey_json": out_dir / "azookey" / "math_symbols_azookey_items.json",
    }
    write_msime(entries, outputs["msime"])
    write_google(entries, outputs["google"])
    write_google(entries, outputs["google_with_comments"], include_comments=True)
    write_azookey_plist(entries, outputs["azookey_plist"])
    write_azookey_json(entries, outputs["azookey_json"])
    return outputs
