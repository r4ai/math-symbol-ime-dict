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

        with tempfile.TemporaryDirectory() as tmp:
            outputs = write_all(entries[:3], Path(tmp))
            msime = outputs["msime"].read_text(encoding="utf-16")
            google = outputs["google"].read_text(encoding="utf-8")
            self.assertIn("land\t∧\t短縮よみ", msime)
            self.assertIn("land\t∧\t短縮よみ", google)

            with outputs["azookey_plist"].open("rb") as file:
                plist = plistlib.load(file)
            payload = json.loads(plist[AZOOKEY_MAC_PREF_KEY].decode("utf-8"))
            self.assertEqual(payload["items"][0]["reading"], "land")
            self.assertEqual(payload["items"][0]["word"], "∧")


if __name__ == "__main__":
    unittest.main()
