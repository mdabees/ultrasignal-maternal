"""Score the held-out seeds exactly once. Refuses to run twice or on unfrozen code.

Run this only after reports/FROZEN.json is committed. Its output, weak or
strong, is published as it comes out.
"""

import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from watcher.baseline import assess_baseline
from watcher.scoring import frozen_manifest, heldout_seeds, score
from watcher.util import ROOT, lower_priority

LIMIT = "Simulated results prove the mechanism works, not that it works at this accuracy in real facilities."


def main():
    lower_priority()
    target = ROOT / "reports" / "holdout.json"
    if target.exists():
        sys.exit("reports/holdout.json already exists. The held-out set is scored once only.")
    with open(ROOT / "reports" / "FROZEN.json", encoding="utf-8") as handle:
        frozen = json.load(handle)
    manifest = frozen_manifest()
    if manifest["files"] != frozen["files"]:
        sys.exit("Frozen files changed since FROZEN.json was written. Refusing to score.")
    status = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip()
    if status:
        sys.exit(f"Working tree is not clean, refusing to score:\n{status}")
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()

    started = time.time()
    seeds = heldout_seeds(frozen["bundle_sha256"])
    detector = score(seeds, max_examples=1000)
    baseline = score(seeds, assess_baseline, max_examples=3)

    report = {
        "frozen": {"detector_sha256": frozen["detector_sha256"], "bundle_sha256": frozen["bundle_sha256"], "git_commit": commit},
        "seed_rule": 'seed_i = first 12 hex digits of sha256("<bundle_sha256>:<i>"), i in 0..329. Class of world i is class i mod 11.',
        "seeds": seeds,
        "score_runs": 1,
        "limit": LIMIT,
        "detector": detector,
        "baseline": baseline,
    }
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1)
        handle.write("\n")
    print(f"scored {len(seeds)} worlds in {time.time() - started:.1f}s")
    print("DETECTOR", json.dumps(detector["overall"]))
    for cls, row in detector["per_class"].items():
        print(f"  {cls:30s} correct={row['correct']}/{row['worlds']} false_alarm_worlds={row['false_alarm_worlds']} alerts={row['alerts']}")
    print("BASELINE", json.dumps(baseline["overall"]))


if __name__ == "__main__":
    main()
