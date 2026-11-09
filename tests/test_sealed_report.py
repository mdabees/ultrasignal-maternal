"""The held-out report must match the frozen detector. Created at freeze time."""

import json
import unittest

from watcher.scoring import file_sha256, frozen_manifest, heldout_seeds
from watcher.util import ROOT


class SealedReportTests(unittest.TestCase):
    def setUp(self):
        with open(ROOT / "reports" / "FROZEN.json", encoding="utf-8") as handle:
            self.frozen = json.load(handle)
        with open(ROOT / "reports" / "holdout.json", encoding="utf-8") as handle:
            self.holdout = json.load(handle)

    def test_detector_file_matches_frozen_hash(self):
        self.assertEqual(file_sha256("watcher/detector.py"), self.frozen["detector_sha256"])

    def test_all_frozen_files_unchanged(self):
        self.assertEqual(frozen_manifest()["files"], self.frozen["files"])

    def test_report_was_produced_by_the_frozen_code(self):
        self.assertEqual(self.holdout["frozen"]["detector_sha256"], self.frozen["detector_sha256"])
        self.assertEqual(self.holdout["frozen"]["bundle_sha256"], self.frozen["bundle_sha256"])

    def test_seed_rule_reproduces_the_seeds(self):
        self.assertEqual(self.holdout["seeds"], heldout_seeds(self.frozen["bundle_sha256"]))

    def test_scored_exactly_once(self):
        self.assertEqual(self.holdout["score_runs"], 1)


if __name__ == "__main__":
    unittest.main()
