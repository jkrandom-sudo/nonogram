import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import i18n as i18n_mod
import score as score_mod
import settings as settings_mod
from sound import Sound


class TestI18n(unittest.TestCase):
    def test_zh_and_en_keys_match(self):
        zh_keys = set(i18n_mod.STRINGS["zh"].keys())
        en_keys = set(i18n_mod.STRINGS["en"].keys())
        self.assertEqual(zh_keys, en_keys, msg=f"missing: {zh_keys ^ en_keys}")

    def test_t_basic(self):
        self.assertEqual(i18n_mod.t("zh", "on"), "开")
        self.assertEqual(i18n_mod.t("en", "on"), "on")

    def test_t_format(self):
        s = i18n_mod.t("en", "puzzle_label", name="Heart")
        self.assertIn("Heart", s)

    def test_t_missing_key_falls_back(self):
        self.assertEqual(i18n_mod.t("zh", "no_such_key_xyz"), "no_such_key_xyz")

    def test_t_unknown_lang_falls_back_to_english(self):
        self.assertEqual(i18n_mod.t("xx", "on"), "on")


class TestSettings(unittest.TestCase):
    def test_load_returns_defaults_when_missing(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "settings.json"
            s = settings_mod.load(path)
            for k, v in settings_mod.DEFAULTS.items():
                self.assertEqual(s[k], v)

    def test_save_then_load(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "settings.json"
            s = settings_mod.load(path)
            s["lang"] = "en"
            s["sound"] = False
            s["volume"] = 2
            s["size"] = 10
            settings_mod.save(s, path)
            s2 = settings_mod.load(path)
            self.assertEqual(s2["lang"], "en")
            self.assertEqual(s2["sound"], False)
            self.assertEqual(s2["volume"], 2)
            self.assertEqual(s2["size"], 10)

    def test_load_repairs_invalid_values(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "settings.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"lang": "fr", "sound": "yes", "volume": 99, "size": 7}, f)
            s = settings_mod.load(path)
            self.assertEqual(s["lang"], "zh")
            self.assertEqual(s["sound"], True)
            self.assertEqual(s["volume"], 1)
            self.assertEqual(s["size"], 5)

    def test_cycle_lang(self):
        s = {"lang": "zh"}
        settings_mod.cycle_lang(s)
        self.assertEqual(s["lang"], "en")
        settings_mod.cycle_lang(s)
        self.assertEqual(s["lang"], "zh")

    def test_toggle_sound(self):
        s = {"sound": True}
        settings_mod.toggle_sound(s)
        self.assertFalse(s["sound"])

    def test_cycle_volume(self):
        s = {"volume": 0}
        settings_mod.cycle_volume(s)
        self.assertEqual(s["volume"], 1)
        s["volume"] = 3
        settings_mod.cycle_volume(s)
        self.assertEqual(s["volume"], 0)

    def test_cycle_size(self):
        s = {"size": 5}
        settings_mod.cycle_size(s)
        self.assertEqual(s["size"], 10)
        settings_mod.cycle_size(s)
        self.assertEqual(s["size"], 5)


class TestScore(unittest.TestCase):
    def test_compute_score_basic(self):
        # 5x5 base = 1250
        self.assertEqual(score_mod.compute_score(5, 25, 0), 1250)

    def test_move_penalty(self):
        # 5x5 with 30 moves → penalty (30-25)*2 = 10
        self.assertEqual(score_mod.compute_score(5, 30, 0), 1240)

    def test_hint_penalty(self):
        self.assertEqual(score_mod.compute_score(5, 25, 2), 1200)

    def test_floors_at_zero(self):
        self.assertEqual(score_mod.compute_score(5, 100000, 100), 0)

    def test_bigger_board_higher_base(self):
        self.assertGreater(score_mod.compute_score(10, 100, 0),
                           score_mod.compute_score(5, 25, 0))

    def test_load_save_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "scores.json"
            self.assertEqual(score_mod.load(path), [])
            score_mod.add("alice", 1000, "puzzle1", 10, path=path)
            score_mod.add("bob", 1500, "puzzle2", 20, path=path)
            score_mod.add("carol", 500, "puzzle3", 30, path=path)
            scores = score_mod.load(path)
            self.assertEqual(len(scores), 3)
            self.assertEqual(scores[0]["name"], "bob")  # highest score first

    def test_truncated_to_max_entries(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "scores.json"
            for i in range(20):
                score_mod.add(f"p{i}", i * 100, "x", i, path=path)
            scores = score_mod.load(path)
            self.assertEqual(len(scores), score_mod.MAX_ENTRIES)


class TestSound(unittest.TestCase):
    def test_disabled_emits_nothing(self):
        out = io.StringIO()
        s = Sound(enabled=False, volume=2, output=out)
        s.fill()
        s.win()
        self.assertEqual(out.getvalue(), "")

    def test_zero_volume_emits_nothing(self):
        out = io.StringIO()
        s = Sound(enabled=True, volume=0, output=out)
        s.fill()
        self.assertEqual(out.getvalue(), "")

    def test_emits_bells(self):
        out = io.StringIO()
        s = Sound(enabled=True, volume=2, output=out)
        s.fill()       # 1 * 2 = 2
        s.mark()       # 1 * 2 = 2
        s.illegal()    # 2 * 2 = 4
        s.win()        # 3 * 2 = 6
        self.assertEqual(out.getvalue().count("\a"), 14)

    def test_volume_clamped(self):
        s = Sound(enabled=True, volume=99)
        self.assertEqual(s.volume, 3)
        s2 = Sound(enabled=True, volume=-5)
        self.assertEqual(s2.volume, 0)


if __name__ == "__main__":
    unittest.main()
