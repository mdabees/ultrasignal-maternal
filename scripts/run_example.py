"""Print one simulated alert and one quiet log entry. Takes a few seconds."""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from watcher.detector import assess
from watcher.generator import generate_world
from watcher.scenarios import planner
from watcher.util import lower_priority

if __name__ == "__main__":
    lower_priority()
    world = generate_world(9003, planner("haemorrhage_treatment_rise"))
    result = assess(world)
    alert = result["alerts"][0]
    print("Simulated data. Where to look:", alert["where"])
    print(alert["prompt"]["en"])
    for entry in alert["ruled_out"]:
        print(" ruled out:", entry["en"])
    print("who acts:", alert["who_acts"]["en"])

    quiet = assess(generate_world(9000, planner("delivery_failure_shortage")))
    print("\nSimulated data. Delivery failure world alerts:", len(quiet["alerts"]))
    print(json.dumps(quiet["quiet"][0], ensure_ascii=False))
