"""Score the detector on dev seeds only. This is the only place tuning happens."""

import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from watcher.baseline import assess_baseline
from watcher.scoring import dev_seeds, score
from watcher.util import ROOT, lower_priority


def summary(result):
    for cls, row in result["per_class"].items():
        print(f"  {cls:30s} worlds={row['worlds']:3d} correct={row['correct']:3d} false_alarm_worlds={row['false_alarm_worlds']:3d} alerts={row['alerts']:3d}")
    print(" ", json.dumps(result["overall"]))


if __name__ == "__main__":
    lower_priority()
    started = time.time()
    seeds = dev_seeds()
    detector = score(seeds)
    baseline = score(seeds, assess_baseline)
    print("DEV detector:")
    summary(detector)
    print("DEV baseline:")
    summary(baseline)
    report = {"seeds": "dev (range only, never held-out)", "detector": detector, "baseline": baseline}
    with open(ROOT / "reports" / "dev.json", "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1)
    print(f"took {time.time() - started:.1f}s")
