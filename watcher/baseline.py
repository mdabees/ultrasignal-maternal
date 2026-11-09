"""The comparison baseline: a single-facility threshold.

For each facility and watched item, it flags a week where the count is more
than 3 standard deviations from that facility's own recent mean, or where stock
cover is under 2 weeks. It has no peer check, no several-facilities rule and no
ordinary-cause checks. It exists to show what the detector's extra rules buy.
"""

import statistics

from watcher.scenarios import NEWBORN_ITEMS, SCREENING_ITEMS, TREATMENT_ITEMS, UTEROTONICS

WATCH = {
    "TXA": ("treatment_use_rise", "up"),
    "BLOOD_BAG": ("treatment_use_rise", "up"),
    "URINE_TEST": ("screening_dropoff", "down"),
    "SYPH_RDT": ("screening_dropoff", "down"),
    "HIV_RDT": ("screening_dropoff", "down"),
    "HB_TEST": ("hb_screening_gap", "down"),
}


def assess_baseline(world, as_of=None):
    as_of = world["weeks"] - 1 if as_of is None else as_of
    alerts = []
    for f in world["facilities"]:
        fid = f["id"]
        for item, (kind, direction) in WATCH.items():
            series = [r["issued"] for r in world["item"][fid][item][:as_of + 1] if r["issued"] is not None]
            if len(series) < 34:
                continue
            base = series[:-6]
            mean, sd = statistics.fmean(base), statistics.pstdev(base) or 1.0
            recent = series[-6:]
            hit = any(v > mean + 3 * sd for v in recent) if direction == "up" else any(v < mean - 3 * sd for v in recent)
            if hit:
                alerts.append({"kind": kind, "level": "area", "where": {"governorate": f["governorate"], "facilities": [fid]}})
        for item in UTEROTONICS + NEWBORN_ITEMS:
            rows = [r for r in world["item"][fid][item][:as_of + 1] if r["issued"] is not None]
            if len(rows) < 8:
                continue
            use = statistics.fmean(r["issued"] for r in rows[-8:])
            if use > 0 and rows[-1]["stock_end"] / use < 2.0:
                kind = "uterotonic_stock_risk" if item in UTEROTONICS else "newborn_item_shortage"
                alerts.append({"kind": kind, "level": "facility", "where": {"governorate": f["governorate"], "facilities": [fid]}, "item": item})
    return {"alerts": alerts, "quiet": [], "not_assessed": []}
