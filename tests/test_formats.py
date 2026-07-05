from __future__ import annotations

import json
import plistlib
import tempfile
import unittest
from pathlib import Path

from math_symbol_ime_dict.formats import AZOOKEY_MAC_PREF_KEY, read_source, write_all


class FormatGenerationTests(unittest.TestCase):
    def test_build_outputs_expected_land_entry(self) -> None:
        source = Path("data/math_symbols.csv")
        entries = read_source(source)
        self.assertGreaterEqual(len(entries), 700)
        self.assertTrue(any(entry.reading == "land" and entry.symbol == "∧" for entry in entries))
        self.assertTrue(any(entry.reading == "Land" and entry.symbol == "∧" for entry in entries))
        self.assertTrue(any(entry.reading == "Mland" and entry.symbol == "∧" for entry in entries))
        self.assertTrue(
            any(entry.reading == "Malpha" and entry.symbol == "\u03b1" for entry in entries)
        )
        self.assertTrue(
            any(entry.reading == "MAlpha" and entry.symbol == "\u0391" for entry in entries)
        )
        self.assertTrue(
            any(entry.reading == "Mrightarrow" and entry.symbol == "→" for entry in entries)
        )
        self.assertTrue(
            any(entry.reading == "MRightarrow" and entry.symbol == "⇒" for entry in entries)
        )
        has_fullwidth_caret = any(
            entry.reading == "\uff3e\uff3e" and entry.symbol == "∧" for entry in entries
        )
        self.assertTrue(has_fullwidth_caret)
        self.assertTrue(
            any(entry.reading == "M\uff0d\uff1e" and entry.symbol == "→" for entry in entries)
        )
        self.assertTrue(
            any(entry.reading == "M\u30fc\uff1e" and entry.symbol == "→" for entry in entries)
        )
        symbols_by_reading: dict[str, str] = {}
        for entry in entries:
            previous_symbol = symbols_by_reading.setdefault(entry.reading, entry.symbol)
            self.assertEqual(previous_symbol, entry.symbol, entry.reading)

        with tempfile.TemporaryDirectory() as tmp:
            outputs = write_all(entries[:5], Path(tmp))
            msime = outputs["msime"].read_text(encoding="utf-16")
            google = outputs["google"].read_text(encoding="utf-8")
            self.assertIn("land\t∧\t短縮よみ", msime)
            self.assertIn("Land\t∧\t短縮よみ", msime)
            self.assertIn("Mland\t∧\t短縮よみ", msime)
            self.assertIn("land\t∧\t短縮よみ", google)
            self.assertIn("Land\t∧\t短縮よみ", google)
            self.assertIn("Mland\t∧\t短縮よみ", google)

            with outputs["azookey_plist"].open("rb") as file:
                plist = plistlib.load(file)
            payload = json.loads(plist[AZOOKEY_MAC_PREF_KEY].decode("utf-8"))
            self.assertEqual(payload["items"][0]["reading"], "land")
            self.assertEqual(payload["items"][0]["word"], "∧")


if __name__ == "__main__":
    unittest.main()
