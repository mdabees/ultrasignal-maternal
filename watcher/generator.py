"""Deterministic generator of fictional facility-week aggregates.

Every number here is invented. Governorate names are real; facilities are not.
Only weekly facility totals exist. There is no person-level record of any kind,
not even a simulated one.

A world is built from a seed and a Plan. The Plan (see scenarios.py) says what
happens during the run; the generator only applies it, so a run is fully
reproducible from (seed, scenario class).
"""

import math
import random
from dataclasses import dataclass, field

WEEKS = 60
FACILITIES_PER_GOVERNORATE = 6
GOVERNORATES = [
    ("CAI", "Cairo"),
    ("GIZ", "Giza"),
    ("ALX", "Alexandria"),
    ("DAK", "Dakahlia"),
    ("SHR", "Sharqia"),
    ("QEN", "Qena"),
]

# Item -> (what drives its use, simulated units per driver event).
# These rates are simulation settings, not clinical facts.
ITEM_PROFILES = {
    "IFA": ("anc_visits", 1.00),
    "HB_TEST": ("anc_visits", 0.60),
    "URINE_TEST": ("anc_visits", 0.60),
    "SYPH_RDT": ("anc_visits", 0.35),
    "HIV_RDT": ("anc_visits", 0.35),
    "OXYTOCIN": ("deliveries", 1.00),
    "MISOPROSTOL": ("deliveries", 0.25),
    "MGSO4": ("deliveries", 0.04),
    "CA_GLUCONATE": ("deliveries", 0.015),
    "TXA": ("deliveries", 0.06),
    "BLOOD_BAG": ("deliveries", 0.05),
    "CDK": ("deliveries", 0.40),
    "CHX": ("deliveries", 0.70),
    "VIT_K": ("deliveries", 0.95),
    "NEO_RESUS": ("deliveries", 0.05),
}

COVER_TARGET_WEEKS = 10


@dataclass
class Plan:
    """What the scenario does. Empty Plan means a clean world."""

    truth: dict = field(default_factory=dict)
    demand: dict = field(default_factory=dict)  # (fid, item, week) -> multiplier
    volume: dict = field(default_factory=dict)  # (fid, driver, week) -> multiplier
    receipts: dict = field(default_factory=dict)  # (fid, item, week) -> fraction of a cycle's use that arrives
    failed: set = field(default_factory=set)  # (fid, item, week)
    missing: set = field(default_factory=set)  # (fid, week)
    partial: dict = field(default_factory=dict)  # (fid, week) -> completeness
    bulk: dict = field(default_factory=dict)  # (fid, item, week) -> multiplier


def poisson(rng, lam):
    """Poisson draw from the standard library's generator."""
    if lam <= 0:
        return 0
    if lam > 40:
        return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))
    limit = math.exp(-lam)
    count, product = 0, 1.0
    while True:
        count += 1
        product *= rng.random()
        if product <= limit:
            return count - 1


def build_facilities(rng):
    """Return fictional facilities with SIM- ids, one larger facility per governorate."""
    facilities = []
    for code, governorate in GOVERNORATES:
        for number in range(1, FACILITIES_PER_GOVERNORATE + 1):
            larger = number == 1
            deliveries = rng.uniform(70, 120) if larger else rng.uniform(18, 40)
            anc_visits = rng.uniform(80, 150) if larger else rng.uniform(40, 100)
            facilities.append(
                {
                    "id": f"SIM-{code}-{number:02d}",
                    "name": f"Simulated {'Larger' if larger else 'Primary'} Unit {code}-{number:02d}",
                    "governorate": governorate,
                    "route": "R1" if number % 2 else "R2",
                    "level": "sim-larger-unit" if larger else "sim-primary-unit",
                    "base": {"deliveries": deliveries, "anc_visits": anc_visits},
                    "rate_factor": {item: min(1.3, max(0.7, rng.gauss(1.0, 0.1))) for item in ITEM_PROFILES},
                    "cycle": rng.choice([2, 3]),
                    "phase": rng.randrange(3),
                }
            )
    return facilities


def _season(week, phase):
    return 1.0 + 0.08 * math.sin(2 * math.pi * (week / 52.0 + phase))


def _simulate_facility(rng, facility, plan, phase):
    fid = facility["id"]
    service, items = [], {item: [] for item in ITEM_PROFILES}
    stock = {}
    trailing = {item: [] for item in ITEM_PROFILES}
    for item, (driver, rate) in ITEM_PROFILES.items():
        stock[item] = COVER_TARGET_WEEKS * rate * facility["rate_factor"][item] * facility["base"][driver]

    for week in range(WEEKS):
        missing = (fid, week) in plan.missing
        completeness = plan.partial.get((fid, week), 1.0)
        counts = {}
        for driver in ("deliveries", "anc_visits"):
            mean = facility["base"][driver] * _season(week, phase)
            mean *= plan.volume.get((fid, driver, week), 1.0) * max(0.5, rng.gauss(1.0, 0.07))
            counts[driver] = poisson(rng, mean)

        if missing:
            service.append({"week": week, "reported": False, "completeness": 0.0, "deliveries": None, "anc_visits": None})
        else:
            service.append(
                {
                    "week": week,
                    "reported": True,
                    "completeness": completeness,
                    "deliveries": int(round(counts["deliveries"] * completeness)),
                    "anc_visits": int(round(counts["anc_visits"] * completeness)),
                }
            )

        for item, (driver, rate) in ITEM_PROFILES.items():
            lam = rate * facility["rate_factor"][item] * counts[driver] * plan.demand.get((fid, item, week), 1.0)
            demand = poisson(rng, lam)

            due = week % facility["cycle"] == facility["phase"] % facility["cycle"]
            failed = due and (fid, item, week) in plan.failed
            received = 0
            if due and not failed:
                past = trailing[item][-16:]
                mean_use = sum(past) / len(past) if past else lam
                order = max(0.0, COVER_TARGET_WEEKS * mean_use - stock[item])
                short_supply = plan.receipts.get((fid, item, week))
                if short_supply is not None:
                    # The scheduled delivery arrives but holds only this fraction of a cycle's use.
                    order = min(order, short_supply * mean_use * facility["cycle"])
                received = int(round(order))

            bulk = plan.bulk.get((fid, item, week))
            if bulk:
                extra = int(round(bulk * max(lam, 1.0)))
                received += extra
                demand += extra

            stock[item] += received
            issued = int(min(demand, stock[item]))
            stock[item] -= issued
            trailing[item].append(issued)

            if missing:
                row = {"issued": None, "received": None, "stock_end": None, "delivery_due": None, "delivery_failed": None}
            else:
                row = {
                    "issued": int(round(issued * completeness)),
                    "received": received,
                    "stock_end": int(round(stock[item])),
                    "delivery_due": due,
                    "delivery_failed": failed,
                }
            items[item].append(row)
    return service, items


def generate_world(seed, build_plan=None):
    """Build a whole world from a seed. Same seed and plan builder, same world."""
    rng = random.Random(seed)
    facilities = build_facilities(rng)
    plan = build_plan(rng, facilities) if build_plan else Plan(truth={"scenario": "clean", "should_alert": False})
    phase = rng.random()
    world = {"seed": seed, "weeks": WEEKS, "scenario": plan.truth, "facilities": facilities, "service": {}, "item": {}}
    for facility in facilities:
        service, items = _simulate_facility(rng, facility, plan, phase)
        world["service"][facility["id"]] = service
        world["item"][facility["id"]] = items
    return world
