"""Simulated maternal-supply scenarios.

Five classes should alert. Five classes plus "clean" should stay quiet.

Stock-out risk versus shortage (the distinction is deliberate, see TEST_PLAN.md):

* A STOCK-OUT RISK (should alert) is forward-looking. Stock is still on the
  shelf but cover is down to a few weeks and deliveries are not replacing what
  is used. Scheduled deliveries ARE arriving, so nobody on the logistics side
  has a failure to chase. Cover is shrinking because deliveries are too small
  or use has grown. Without the alert, nobody is looking.
* A SHORTAGE EXPLAINED BY DELIVERY FAILURE (should NOT alert) has a known cause.
  Stock falls because scheduled deliveries did not arrive. The delivery record
  says so, it hits most items on a supply route at once, and logistics already
  owns it. The watcher records it in its quiet log and routes it to logistics.
* A NEWBORN ITEM SHORTAGE (should alert) has already happened: a newborn item
  has run out or nearly run out, births continue, and no delivery failure
  explains it.
"""

from watcher.generator import GOVERNORATES, WEEKS, Plan

ALERT_CLASSES = [
    "uterotonic_stockout_risk",
    "antenatal_screening_dropoff",
    "haemorrhage_treatment_rise",
    "anaemia_screening_gap",
    "newborn_item_shortage",
]
QUIET_CLASSES = [
    "bulk_order",
    "reporting_gap",
    "delivery_failure_shortage",
    "single_facility_noise",
    "seasonal_delivery_peak",
    "clean",
]
ALL_CLASSES = ALERT_CLASSES + QUIET_CLASSES

SCREENING_ITEMS = ["URINE_TEST", "SYPH_RDT", "HIV_RDT"]
TREATMENT_ITEMS = ["TXA", "BLOOD_BAG"]
NEWBORN_ITEMS = ["VIT_K", "CHX", "NEO_RESUS"]
UTEROTONICS = ["OXYTOCIN", "MISOPROSTOL"]

KIND_FOR_CLASS = {
    "uterotonic_stockout_risk": "uterotonic_stock_risk",
    "antenatal_screening_dropoff": "screening_dropoff",
    "haemorrhage_treatment_rise": "treatment_use_rise",
    "anaemia_screening_gap": "hb_screening_gap",
    "newborn_item_shortage": "newborn_item_shortage",
}


def _governorate(rng, facilities):
    return rng.choice([name for _, name in GOVERNORATES])


def _facilities_in(facilities, governorate):
    return [f for f in facilities if f["governorate"] == governorate]


def _truth(cls, should_alert, level, target, **params):
    return {
        "scenario": cls,
        "should_alert": should_alert,
        "kind": KIND_FOR_CLASS.get(cls),
        "level": level,
        "target": target,
        "params": params,
    }


def _area_change(rng, facilities, items, factor_range, cls, count=None):
    plan = Plan()
    governorate = _governorate(rng, facilities)
    pool = _facilities_in(facilities, governorate)
    affected = rng.sample(pool, count if count is not None else rng.randint(3, 5))
    onset = WEEKS - rng.randint(3, 6)
    factor = rng.uniform(*factor_range)
    for facility in affected:
        for item in items:
            for week in range(onset, WEEKS):
                plan.demand[(facility["id"], item, week)] = factor
    plan.truth = _truth(
        cls,
        True,
        "area",
        governorate,
        facilities=[f["id"] for f in affected],
        onset_week=onset,
        factor=round(factor, 3),
    )
    return plan


def build_plan(cls, rng, facilities, **overrides):
    """Return the Plan for a class. Overrides are used only by unit tests."""
    if cls == "clean":
        return Plan(truth=_truth("clean", False, None, None))

    if cls == "uterotonic_stockout_risk":
        plan = Plan()
        facility = rng.choice(facilities)
        items = [rng.choice(UTEROTONICS)]
        onset = WEEKS - rng.randint(8, 14)
        receipts = rng.uniform(0.1, 0.6)
        demand = rng.uniform(1.0, 1.3)
        for item in items:
            for week in range(onset, WEEKS):
                plan.receipts[(facility["id"], item, week)] = receipts
                plan.demand[(facility["id"], item, week)] = demand
        plan.truth = _truth(cls, True, "facility", facility["id"], items=items, onset_week=onset, receipts=round(receipts, 3), demand=round(demand, 3))
        return plan

    if cls == "antenatal_screening_dropoff":
        return _area_change(rng, facilities, SCREENING_ITEMS + ["HB_TEST"], (0.45, 0.80), cls, overrides.get("count"))

    if cls == "haemorrhage_treatment_rise":
        return _area_change(rng, facilities, TREATMENT_ITEMS, (1.3, 2.0), cls, overrides.get("count"))

    if cls == "anaemia_screening_gap":
        return _area_change(rng, facilities, ["HB_TEST"], (0.40, 0.75), cls, overrides.get("count"))

    if cls == "newborn_item_shortage":
        plan = Plan()
        facility = rng.choice(facilities)
        weights = {"VIT_K": 5, "CHX": 4, "NEO_RESUS": 1}
        items = rng.sample(list(weights), counts=list(weights.values()), k=1)
        if rng.random() < 0.35:
            items = sorted(set(items + rng.sample(list(weights), counts=list(weights.values()), k=1)))
        onset = WEEKS - rng.randint(11, 16)
        for item in items:
            for week in range(onset, WEEKS):
                plan.receipts[(facility["id"], item, week)] = 0.0
        plan.truth = _truth(cls, True, "facility", facility["id"], items=items, onset_week=onset)
        return plan

    if cls == "bulk_order":
        plan = Plan()
        governorate = _governorate(rng, facilities)
        affected = rng.sample(_facilities_in(facilities, governorate), rng.randint(3, 4))
        item = rng.choice(["OXYTOCIN", "TXA", "HB_TEST", "VIT_K"])
        week = rng.randint(54, 58)
        multiplier = rng.uniform(4.0, 8.0)
        for facility in affected:
            plan.bulk[(facility["id"], item, week)] = multiplier
        plan.truth = _truth(cls, False, "area", governorate, facilities=[f["id"] for f in affected], item=item, week=week, multiplier=round(multiplier, 2))
        return plan

    if cls == "reporting_gap":
        plan = Plan()
        governorate = _governorate(rng, facilities)
        affected = rng.sample(_facilities_in(facilities, governorate), rng.randint(1, 3))
        for facility in affected:
            length = rng.randint(2, 5)
            start = rng.randint(WEEKS - 8, WEEKS - length)
            for week in range(start, start + length):
                plan.missing.add((facility["id"], week))
            for week in range(WEEKS - 4, WEEKS):
                if (facility["id"], week) not in plan.missing and rng.random() < 0.5:
                    plan.partial[(facility["id"], week)] = rng.uniform(0.4, 0.7)
        plan.truth = _truth(cls, False, "area", governorate, facilities=[f["id"] for f in affected])
        return plan

    if cls == "delivery_failure_shortage":
        plan = Plan()
        governorate = _governorate(rng, facilities)
        route = rng.choice(["R1", "R2"])
        affected = [f for f in _facilities_in(facilities, governorate) if f["route"] == route]
        start = WEEKS - rng.randint(5, 9)
        for facility in affected:
            for item in _all_items():
                for week in range(start, WEEKS):
                    plan.failed.add((facility["id"], item, week))
        plan.truth = _truth(cls, False, "area", governorate, route=route, facilities=[f["id"] for f in affected], start_week=start)
        return plan

    if cls == "single_facility_noise":
        plan = Plan()
        facility = rng.choice(facilities)
        rising = rng.random() < 0.5
        items = TREATMENT_ITEMS if rising else ["HB_TEST"]
        factor = rng.uniform(1.8, 3.0) if rising else rng.uniform(0.3, 0.6)
        onset = WEEKS - rng.randint(3, 6)
        for item in items:
            for week in range(onset, WEEKS):
                plan.demand[(facility["id"], item, week)] = factor
        plan.truth = _truth(cls, False, "facility", facility["id"], items=items, factor=round(factor, 3))
        return plan

    if cls == "seasonal_delivery_peak":
        plan = Plan()
        peak = rng.uniform(1.25, 1.45)
        onset = WEEKS - rng.randint(4, 7)
        for facility in facilities:
            for week in range(onset, WEEKS):
                plan.volume[(facility["id"], "deliveries", week)] = peak
                plan.volume[(facility["id"], "anc_visits", week)] = 1.0 + (peak - 1.0) / 2
        plan.truth = _truth(cls, False, "national", None, peak=round(peak, 3), onset_week=onset)
        return plan

    raise ValueError(f"unknown scenario class: {cls}")


def _all_items():
    from watcher.generator import ITEM_PROFILES

    return list(ITEM_PROFILES)


def planner(cls, **overrides):
    """Return a function suitable for generate_world(seed, build_plan=...)."""

    def build(rng, facilities):
        return build_plan(cls, rng, facilities, **overrides)

    return build
