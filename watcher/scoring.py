"""Scoring, seed rules and freezing.

Metrics are defined in TEST_PLAN.md. The score of a run never depends on the
order worlds are visited in.
"""

import hashlib
import json

from watcher.scenarios import ALERT_CLASSES, ALL_CLASSES, QUIET_CLASSES, planner
from watcher.generator import generate_world
from watcher.detector import assess
from watcher.baseline import assess_baseline
from watcher.util import ROOT

FROZEN_FILES = [
    "watcher/alerts.py",
    "watcher/baseline.py",
    "watcher/detector.py",
    "watcher/generator.py",
    "watcher/privacy.py",
    "watcher/scenarios.py",
    "watcher/scoring.py",
]

DEV_SEED_START = 1000
DEV_WORLDS_PER_CLASS = 15
HELDOUT_WORLDS_PER_CLASS = 30
CLEAN_ROLLING_WEEKS = 8


def file_sha256(relative_path):
    """sha256 of a file, normalised to LF so it matches on any machine."""
    data = (ROOT / relative_path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def frozen_manifest():
    files = {path: file_sha256(path) for path in FROZEN_FILES}
    bundle = hashlib.sha256("".join(f"{p}:{h}\n" for p, h in sorted(files.items())).encode()).hexdigest()
    return {"detector_sha256": files["watcher/detector.py"], "bundle_sha256": bundle, "files": files}


def dev_seeds():
    """Seeds used to tune the detector. Never used for the held-out score."""
    return [DEV_SEED_START + i for i in range(DEV_WORLDS_PER_CLASS * len(ALL_CLASSES))]


def heldout_seeds(bundle_sha256):
    """The held-out seeds, fixed by rule from the frozen bundle hash.

    Rule: seed_i is the first 12 hex digits of sha256("<bundle>:<i>"). The seeds
    could not be known while the detector was being tuned, because they depend
    on the hash of the finished, frozen code.
    """
    count = HELDOUT_WORLDS_PER_CLASS * len(ALL_CLASSES)
    return [int(hashlib.sha256(f"{bundle_sha256}:{i}".encode()).hexdigest()[:12], 16) for i in range(count)]


def class_for_index(index):
    """World i always tests class i mod 11."""
    return ALL_CLASSES[index % len(ALL_CLASSES)]


def match(alert, truth):
    """Does this alert hit the scenario's true location and kind?"""
    if alert["kind"] != truth["kind"]:
        return False
    if truth["level"] == "area":
        return alert["where"]["governorate"] == truth["target"]
    return truth["target"] in alert["where"]["facilities"]


def _describe_failure(cls, world, outcome):
    truth = world["scenario"]
    example = {"seed": world["seed"], "class": cls, "truth": truth["params"], "target": truth["target"]}
    if outcome["alerts"]:
        example["alerts"] = [{"kind": a["kind"], "where": a["where"]} for a in outcome["alerts"]]
    return example


def score(seeds, assessor=assess, max_examples=5):
    """Score a list of seeds. Returns per-class results and overall figures."""
    per_class = {cls: {"worlds": 0, "correct": 0, "false_alarm_worlds": 0, "alerts": 0, "correct_alerts": 0, "failures": []} for cls in ALL_CLASSES}
    clean_rolling = {"evaluations": 0, "alerts": 0}

    for index, seed in enumerate(seeds):
        cls = class_for_index(index)
        world = generate_world(seed, planner(cls))
        truth = world["scenario"]
        outcome = assessor(world)
        row = per_class[cls]
        row["worlds"] += 1
        row["alerts"] += len(outcome["alerts"])

        if truth["should_alert"]:
            hits = [a for a in outcome["alerts"] if match(a, truth)]
            row["correct_alerts"] += len(hits)
            if hits:
                row["correct"] += 1
            elif len(row["failures"]) < max_examples:
                row["failures"].append(_describe_failure(cls, world, outcome))
            extra = len(outcome["alerts"]) - len(hits)
            if extra > 0:
                row["false_alarm_worlds"] += 1
        else:
            if outcome["alerts"]:
                row["false_alarm_worlds"] += 1
                if len(row["failures"]) < max_examples:
                    row["failures"].append(_describe_failure(cls, world, outcome))
            else:
                row["correct"] += 1

        if cls == "clean":
            for as_of in range(world["weeks"] - CLEAN_ROLLING_WEEKS, world["weeks"]):
                clean_rolling["evaluations"] += 1
                clean_rolling["alerts"] += len(assessor(world, as_of)["alerts"])

    should = [per_class[c] for c in ALERT_CLASSES]
    quiet = [per_class[c] for c in QUIET_CLASSES]
    total_alerts = sum(r["alerts"] for r in per_class.values())
    correct_alerts = sum(r["correct_alerts"] for r in should)
    return {
        "per_class": per_class,
        "overall": {
            "sensitivity": _ratio(sum(r["correct"] for r in should), sum(r["worlds"] for r in should)),
            "quiet_worlds_kept_quiet": _ratio(sum(r["correct"] for r in quiet), sum(r["worlds"] for r in quiet)),
            "false_alarm_rate_quiet_worlds": _ratio(sum(r["false_alarm_worlds"] for r in quiet), sum(r["worlds"] for r in quiet)),
            "precision_of_alerts": _ratio(correct_alerts, total_alerts),
            "alerts_total": total_alerts,
            "clean_rolling_alerts_per_evaluation": _ratio(clean_rolling["alerts"], clean_rolling["evaluations"]),
            "clean_rolling_evaluations": clean_rolling["evaluations"],
        },
    }


def _ratio(numerator, denominator):
    return round(numerator / denominator, 4) if denominator else None


def round_trip(obj):
    """JSON-safe copy of a result, for reports."""
    return json.loads(json.dumps(obj))
