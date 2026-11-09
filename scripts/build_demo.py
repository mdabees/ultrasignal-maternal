"""Build docs/data/demo.json for the static demo from the module's own output.

Demo seeds are separate from dev and held-out seeds. The alert world is the first
demo seed where the detector fires correctly, so it shows a successful case;
the held-out results on the same page show the misses.
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from watcher.detector import assess
from watcher.generator import generate_world
from watcher.privacy import show_count
from watcher.scenarios import planner
from watcher.scoring import match
from watcher.util import ROOT, load_catalogue, lower_priority

DEMO_SEED_START = 9000
LIMIT = "Simulated results prove the mechanism works, not that it works at this accuracy in real facilities."


def first_seed(cls, start, predicate):
    for seed in range(start, start + 300):
        world = generate_world(seed, planner(cls))
        result = assess(world)
        if predicate(world, result):
            return seed, world, result
    raise SystemExit(f"no demo seed found for {cls}")


def alert_hits_truth(world, result):
    return any(match(alert, world["scenario"]) for alert in result["alerts"])


def overview(world, result, alert_facilities):
    not_assessed = {row["facility"] for row in result["not_assessed"]}
    groups = {}
    for facility in world["facilities"]:
        fid = facility["id"]
        rows = world["service"][fid][-4:]
        deliveries = sum(r["deliveries"] for r in rows if r["reported"] and r["deliveries"] is not None)
        status = "attention" if fid in alert_facilities else "not_assessed" if fid in not_assessed else "ok"
        groups.setdefault(facility["governorate"], []).append(
            {"id": fid, "name": facility["name"], "status": status, "deliveries_last_4_weeks": show_count(deliveries)}
        )
    return [{"governorate": name, "facilities": facilities} for name, facilities in sorted(groups.items())]


def short_failure(example):
    truth = example.get("truth", {})
    parts = [f"seed {example['seed']}"]
    if example.get("target"):
        parts.append(f"target {example['target']}")
    if "onset_week" in truth:
        parts.append(f"onset week {truth['onset_week']}")
    if "factor" in truth:
        parts.append(f"factor {truth['factor']}")
    if example.get("alerts"):
        parts.append("raised " + ", ".join(sorted({a["kind"] for a in example["alerts"]})))
    return ", ".join(parts)


def holdout_summary():
    with open(ROOT / "reports" / "holdout.json", encoding="utf-8") as handle:
        report = json.load(handle)
    classes = []
    for cls, row in report["detector"]["per_class"].items():
        classes.append(
            {
                "class": cls,
                "worlds": row["worlds"],
                "correct": row["correct"],
                "false_alarm_worlds": row["false_alarm_worlds"],
                "alerts": row["alerts"],
                "failures": [short_failure(f) for f in row["failures"][:4]],
                "failure_count": len(row["failures"]),
            }
        )
    return {
        "frozen_detector_sha256": report["frozen"]["detector_sha256"],
        "overall": report["detector"]["overall"],
        "baseline_overall": report["baseline"]["overall"],
        "per_class": classes,
        "limit": LIMIT,
    }


def main():
    lower_priority()
    alert_seed, world, result = first_seed("haemorrhage_treatment_rise", DEMO_SEED_START, alert_hits_truth)
    alert = [a for a in result["alerts"] if match(a, world["scenario"])][0]
    quiet_seed, _, quiet_result = first_seed(
        "delivery_failure_shortage", DEMO_SEED_START, lambda w, r: not r["alerts"] and any(e["code"] == "delivery_failure" for e in r["quiet"])
    )
    catalogue = load_catalogue()
    demo = {
        "simulated": True,
        "label": "Simulated data",
        "limit": LIMIT,
        "as_of_week": result["as_of_week"],
        "alert_world": {"seed": alert_seed, "class": "haemorrhage_treatment_rise"},
        "overview": overview(world, result, set(alert["where"]["facilities"])),
        "alert": alert,
        "quiet_case": {
            "seed": quiet_seed,
            "class": "delivery_failure_shortage",
            "alerts": quiet_result["alerts"],
            "quiet": [e for e in quiet_result["quiet"] if e["code"] == "delivery_failure"][:6],
        },
        "holdout": holdout_summary(),
        "catalogue": {"status": catalogue["clinical_mapping_status"], "items": catalogue["items"]},
    }
    target = ROOT / "docs" / "data" / "demo.json"
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(demo, handle, ensure_ascii=False, indent=1)
    print(f"wrote {target} alert_seed={alert_seed} quiet_seed={quiet_seed}")


if __name__ == "__main__":
    main()
