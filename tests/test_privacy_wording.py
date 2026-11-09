import re
import unittest

from watcher.alerts import WordingError, all_alert_strings, guard_text
from watcher.detector import assess
from watcher.generator import generate_world
from watcher.privacy import SUPPRESSED_COUNT, SUPPRESSED_RATE, show_count, show_rate
from watcher.scenarios import ALERT_CLASSES, planner


class SuppressionTests(unittest.TestCase):
    def test_counts_under_five_are_hidden(self):
        for value in (0, 1, 2, 3, 4):
            self.assertEqual(show_count(value), SUPPRESSED_COUNT)
        self.assertEqual(show_count(5), "5")

    def test_rates_with_small_parts_are_hidden(self):
        self.assertEqual(show_rate(4, 100), SUPPRESSED_RATE)
        self.assertEqual(show_rate(10, 4), SUPPRESSED_RATE)
        self.assertEqual(show_rate(5, 100), "5.0")

    def test_no_small_stock_count_shown_in_any_alert(self):
        seen = 0
        for cls in ALERT_CLASSES:
            for seed in range(2000, 2030):
                world = generate_world(seed, planner(cls))
                for alert in assess(world)["alerts"]:
                    for entry in alert["what_moved"]:
                        for language in ("en", "ar"):
                            match = re.search(r"(stock on hand|المخزون المتاح) ([^.،؛]*)", entry[language])
                            if match:
                                seen += 1
                                self.assertNotRegex(match.group(2).strip(), r"^[0-4]$")
        self.assertGreater(seen, 0, "the check never looked at a stock figure")


class WordingGuardTests(unittest.TestCase):
    def test_guard_rejects_diagnosis_words(self):
        for text in ("the patient has anaemia", "diagnosis suspected", "bleeding reported", "حالة نزيف", "تشخيص محتمل"):
            with self.assertRaises(WordingError):
                guard_text(text)

    def test_guard_allows_ordinary_supply_wording(self):
        guard_text("other governorates did not move in the same way; maternal health coordinator")

    def test_every_alert_passes_the_guard_and_is_produced(self):
        produced = 0
        for cls in ALERT_CLASSES:
            for seed in range(2000, 2030):
                for alert in assess(generate_world(seed, planner(cls)))["alerts"]:
                    produced += 1
                    guard_text(*all_alert_strings(alert))
                    self.assertIn(alert["who_acts"]["en"], ("Governorate maternal health coordinator (district lead)", "Facility pharmacy and stores lead, with the facility maternity lead"))
                    self.assertTrue(alert["ruled_out"] and alert["missing"] and alert["what_moved"])
        self.assertGreater(produced, 0)


if __name__ == "__main__":
    unittest.main()
