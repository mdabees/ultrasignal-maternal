import json
import unittest

from watcher.generator import GOVERNORATES, WEEKS, generate_world
from watcher.scenarios import ALL_CLASSES, planner
from watcher.util import load_catalogue

FORBIDDEN_FIELD_FRAGMENTS = ("patient", "person", "nid", "mrn", "dob", "phone", "address", "woman", "mother")


def walk_keys(value, found):
    if isinstance(value, dict):
        for key, inner in value.items():
            if isinstance(key, str):
                found.add(key)
            walk_keys(inner, found)
    elif isinstance(value, list):
        for inner in value:
            walk_keys(inner, found)


class GeneratorTests(unittest.TestCase):
    def test_same_seed_same_world(self):
        for cls in ALL_CLASSES:
            a = generate_world(11, planner(cls))
            b = generate_world(11, planner(cls))
            self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True), cls)

    def test_different_seed_different_world(self):
        self.assertNotEqual(json.dumps(generate_world(1)["service"]), json.dumps(generate_world(2)["service"]))

    def test_only_fictional_facilities_in_real_governorates(self):
        world = generate_world(3)
        governorates = {name for _, name in GOVERNORATES}
        for facility in world["facilities"]:
            self.assertTrue(facility["id"].startswith("SIM-"))
            self.assertIn("Simulated", facility["name"])
            self.assertIn(facility["governorate"], governorates)

    def test_only_weekly_facility_aggregates_no_person_fields(self):
        for cls in ALL_CLASSES:
            world = generate_world(5, planner(cls))
            keys = set()
            walk_keys(world, keys)
            for key in keys:
                lowered = key.lower()
                for fragment in FORBIDDEN_FIELD_FRAGMENTS:
                    self.assertNotIn(fragment, lowered, key)
        self.assertEqual(len(world["service"][world["facilities"][0]["id"]]), WEEKS)

    def test_catalogue_mapping_status_is_visible_and_uncited_is_honest(self):
        catalogue = load_catalogue()
        self.assertEqual(catalogue["clinical_mapping_status"], "Clinical mapping: pending review by Dr. Yasmeen Dabees (gynaecologist). Not yet reviewed.")
        for item in catalogue["items"]:
            self.assertEqual(item["cited"], bool(item["sources"]), item["id"])


if __name__ == "__main__":
    unittest.main()
