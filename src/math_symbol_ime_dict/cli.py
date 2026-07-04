"""Command line interface for math-symbol-ime-dict."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from math_symbol_ime_dict.formats import (
    read_source,
    validate_entries,
    write_all,
    write_azookey_json,
    write_azookey_plist,
    write_google,
    write_msime,
)

DEFAULT_SOURCE = Path("data/math_symbols.csv")
DEFAULT_OUT_DIR = Path("dist")
TARGETS = ("msime", "google", "google-comments", "azookey", "all")


def _build(args: argparse.Namespace) -> int:
    source = Path(args.source)
    out_dir = Path(args.out_dir)
    entries = read_source(source)
    targets: set[str] = set(args.targets)

    written: dict[str, Path] = {}
    if "all" in targets:
        written = write_all(entries, out_dir)
    else:
        if "msime" in targets:
            path = out_dir / "msime" / "math_symbols_msime_utf16le.txt"
            write_msime(entries, path)
            written["msime"] = path
        if "google" in targets:
            path = out_dir / "google" / "math_symbols_google_utf8.tsv"
            write_google(entries, path)
            written["google"] = path
        if "google-comments" in targets:
            path = out_dir / "google" / "math_symbols_google_utf8_with_comments.tsv"
            write_google(entries, path, include_comments=True)
            written["google_with_comments"] = path
        if "azookey" in targets:
            plist_path = out_dir / "azookey" / "math_symbols_azookeymac.plist"
            json_path = out_dir / "azookey" / "math_symbols_azookey_items.json"
            write_azookey_plist(entries, plist_path)
            write_azookey_json(entries, json_path)
            written["azookey_plist"] = plist_path
            written["azookey_json"] = json_path

    print(f"entries: {len(entries)}")
    for name, path in written.items():
        print(f"{name}: {path}")
    return 0


def _validate(args: argparse.Namespace) -> int:
    entries = read_source(Path(args.source))
    validate_entries(entries)
    unique_symbols = len({entry.symbol for entry in entries})
    print(f"ok: {len(entries)} entries, {unique_symbols} unique symbols")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="math-symbol-ime-dict",
        description="Generate Microsoft IME, Google Japanese Input, and azooKey dictionaries.",
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    build = subparsers.add_parser("build", help="generate import files")
    build.add_argument("--source", default=DEFAULT_SOURCE, help="canonical CSV source")
    build.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="output directory")
    build.add_argument(
        "--targets",
        nargs="+",
        choices=TARGETS,
        default=["all"],
        help="targets to generate",
    )
    build.set_defaults(func=_build)

    validate = subparsers.add_parser("validate", help="validate the CSV source")
    validate.add_argument("--source", default=DEFAULT_SOURCE, help="canonical CSV source")
    validate.set_defaults(func=_validate)

    parser.set_defaults(
        func=_build, source=DEFAULT_SOURCE, out_dir=DEFAULT_OUT_DIR, targets=["all"]
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except BrokenPipeError:
        return 1
    except Exception as exc:  # noqa: BLE001 - CLI should report validation errors cleanly.
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
