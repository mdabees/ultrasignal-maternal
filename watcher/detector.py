"""The alert logic: deterministic statistics and rules only. No machine learning.

For one world and one as-of week, assess() returns alerts, a quiet log (what was
looked at and why it was left alone) and the list of facility/measure pairs
that could not be assessed.

Each facility is compared with its own normal and, for area-level signals, with
peers in other governorates. An area-level signal needs several separate
facilities, each passing the test on its own counts.
"""

import math
import statistics

from watcher import alerts as text
from watcher.privacy import show_count, show_rate
from watcher.scenarios import NEWBORN_ITEMS, SCREENING_ITEMS, TREATMENT_ITEMS, UTEROTONICS

CONFIG = {
    "recent_weeks": 4,
    "baseline_weeks": 29,
    "gap_weeks": 1,
    "min_baseline_ok": 20,
    "min_recent_ok": 4,
    "min_completeness": 0.8,
    "min_expected_count": 4,
    "area_min_facilities": 3,
    "area_ratio_up": 1.2,
    "area_ratio_down": 0.85,
    "area_z": 1.5,
    "area_pooled_z": 3.0,
    "delivery_failure_weeks": 8,
    "delivery_failure_share": 0.5,
    "cover_weeks_risk": 3.5,
    "replenishment_share": 0.75,
    "cover_consecutive": 2,
    "cover_mean_weeks": 8,
    "cover_trend_weeks": 4,
    "newborn_weeks": 3,
    "newborn_ratio": 0.5,
    "newborn_cover_weeks": 1.0,
    "newborn_min_expected": 5,
    "newborn_volume_floor": 0.7,
}

AREA_RULES = [
    {"kind": "treatment_use_rise", "items": TREATMENT_ITEMS, "driver": "deliveries", "direction": "up", "per": "per 100 deliveries", "per_ar": "لكل 100 ولادة"},
    {"kind": "screening_dropoff", "items": SCREENING_ITEMS, "driver": "anc_visits", "direction": "down", "per": "per 100 antenatal visits", "per_ar": "لكل 100 زيارة متابعة حمل"},
    {"kind": "hb_screening_gap", "items": ["HB_TEST"], "driver": "anc_visits", "direction": "down", "per": "per 100 antenatal visits", "per_ar": "لكل 100 زيارة متابعة حمل"},
]


def _ok(world, fid, week):
    row = world["service"][fid][week]
    return row["reported"] and row["completeness"] >= CONFIG["min_completeness"]


def _windows(as_of):
    recent_start = as_of - CONFIG["recent_weeks"] + 1
    baseline_end = recent_start - CONFIG["gap_weeks"] - 1
    baseline_start = baseline_end - CONFIG["baseline_weeks"] + 1
    return baseline_start, baseline_end, recent_start


def _failed_share(world, fid, items, as_of):
    """Share of scheduled deliveries for these items recorded as failed recently."""
    due = failed = 0
    for item in items:
        for week in range(max(0, as_of - CONFIG["delivery_failure_weeks"] + 1), as_of + 1):
            row = world["item"][fid][item][week]
            if row["delivery_due"]:
                due += 1
                failed += 1 if row["delivery_failed"] else 0
    return failed / due if due else 0.0


def compare_rate(world, fid, items, driver, as_of, direction):
    """Compare a facility's recent rate with its own baseline; None if not assessable."""
    baseline_start, baseline_end, recent_start = _windows(as_of)
    weekly = []
    for week in list(range(max(0, baseline_start), baseline_end + 1)) + list(range(recent_start, as_of + 1)):
        if _ok(world, fid, week):
            num = sum(world["item"][fid][item][week]["issued"] or 0 for item in items)
            weekly.append((week, num, world["service"][fid][week][driver] or 0))
    base = [(n, d) for w, n, d in weekly if w <= baseline_end]
    recent = [(w, n, d) for w, n, d in weekly if w >= recent_start]
    if len(base) < CONFIG["min_baseline_ok"] or len(recent) < CONFIG["min_recent_ok"]:
        return None
    n0, d0 = sum(n for n, _ in base), sum(d for _, d in base)
    n1, d1 = sum(n for _, n, _ in recent), sum(d for _, _, d in recent)
    if n0 == 0 or d0 == 0 or d1 == 0 or n0 / d0 * d1 < CONFIG["min_expected_count"]:
        return None
    rate0 = n0 / d0
    expected = rate0 * d1
    dispersion = max(1.0, sum((n - rate0 * d) ** 2 / (rate0 * d) for n, d in base if rate0 * d > 0) / len(base))
    z = (n1 - expected) / math.sqrt(expected * (1 + d1 / d0) * dispersion)
    ratio = (n1 / d1) / rate0

    # Leave out the week most favourable to a signal, to catch one-off spikes.
    extreme = max if direction == "up" else min
    drop = extreme(recent, key=lambda row: row[1] / row[2] if row[2] else 0.0)
    trimmed_n, trimmed_d = n1 - drop[1], d1 - drop[2]
    trimmed_ratio = (trimmed_n / trimmed_d) / rate0 if trimmed_d else 1.0
    return {
        "fid": fid, "n0": n0, "d0": d0, "n1": n1, "d1": d1,
        "rate0": rate0, "rate1": n1 / d1, "z": z, "ratio": ratio, "trimmed_ratio": trimmed_ratio,
    }


def _passes(r, peer_ratio, direction):
    adjusted = r["ratio"] / peer_ratio if peer_ratio else r["ratio"]
    trimmed = r["trimmed_ratio"] / peer_ratio if peer_ratio else r["trimmed_ratio"]
    if direction == "up":
        return adjusted >= CONFIG["area_ratio_up"] and trimmed >= CONFIG["area_ratio_up"] and r["z"] >= CONFIG["area_z"]
    return adjusted <= CONFIG["area_ratio_down"] and trimmed <= CONFIG["area_ratio_down"] and r["z"] <= -CONFIG["area_z"]


def _quiet(code, level, where, en, ar):
    return {"code": code, "level": level, "where": where, "en": en, "ar": ar}


def _ruled(*codes):
    return [{"code": code, **text.RULED_OUT[code]} for code in codes]


def _missing(*entries):
    return list(entries)


def _area_rule(world, as_of, rule, results):
    governorates = {}
    for f in world["facilities"]:
        governorates.setdefault(f["governorate"], []).append(f)

    # One comparison per facility, shared across governorate loops for peers.
    comparisons = {}
    for f in world["facilities"]:
        comparisons[f["id"]] = compare_rate(world, f["id"], rule["items"], rule["driver"], as_of, rule["direction"])
    # Facilities with a recorded delivery failure are excluded: their fall has a known cause.
    excluded = {f["id"] for f in world["facilities"] if _failed_share(world, f["id"], rule["items"], as_of) >= CONFIG["delivery_failure_share"]}

    for governorate, facilities in sorted(governorates.items()):
        ids = {f["id"] for f in facilities}
        peers = [c["ratio"] for fid, c in comparisons.items() if c and fid not in ids]
        peer_ratio = statistics.median(peers) if peers else None
        assessed = [comparisons[f["id"]] for f in facilities if comparisons[f["id"]] and f["id"] not in excluded]
        moved = [c for c in assessed if _passes(c, peer_ratio, rule["direction"])]
        unassessed = sorted(f["id"] for f in facilities if comparisons[f["id"]] is None)
        for fid in unassessed:
            results["not_assessed"].append({"facility": fid, "measure": rule["kind"], "reason": "too few complete weeks or counts"})
        # A failure-affected facility that would otherwise have moved goes to the quiet log.
        blocked = [fid for fid in sorted(ids & excluded) if comparisons[fid] and _passes(comparisons[fid], peer_ratio, rule["direction"])]
        if blocked:
            results["quiet"].append(_quiet("delivery_failure", "area", governorate,
                "A change at " + ", ".join(blocked) + " is explained by recorded delivery failures. Logged and routed to logistics, not raised as an alert.",
                "التغير في " + ", ".join(blocked) + " يفسره تعثر توريد مسجل. تم تسجيله وتحويله إلى اللوجستيات دون رفع تنبيه."))

        if not moved:
            continue
        if len(moved) < CONFIG["area_min_facilities"]:
            ids_text = ", ".join(c["fid"] for c in moved)
            results["quiet"].append(_quiet("single_facility", "area", governorate,
                f"{ids_text} moved on {text.LABELS[rule['kind']]['en'].lower()}, below the {CONFIG['area_min_facilities']} separate facilities needed. Logged, not raised.",
                f"{ids_text} تحركت في: {text.LABELS[rule['kind']]['ar']}، وهو أقل من {CONFIG['area_min_facilities']} منشآت منفصلة مطلوبة. تم تسجيله دون رفع تنبيه."))
            continue

        pooled_n0, pooled_d0 = sum(c["n0"] for c in assessed), sum(c["d0"] for c in assessed)
        pooled_n1, pooled_d1 = sum(c["n1"] for c in assessed), sum(c["d1"] for c in assessed)
        pooled_rate0 = pooled_n0 / pooled_d0
        expected = pooled_rate0 * pooled_d1
        pooled_z = (pooled_n1 - expected) / math.sqrt(expected * (1 + pooled_d1 / pooled_d0))
        strong = pooled_z >= CONFIG["area_pooled_z"] if rule["direction"] == "up" else pooled_z <= -CONFIG["area_pooled_z"]
        if not strong:
            results["quiet"].append(_quiet("pooled_weak", "area", governorate,
                f"Several facilities in {governorate} moved, but the combined change was not strong enough. Logged, not raised.",
                f"تحركت عدة منشآت في {governorate} لكن التغير المجمع لم يكن كافيا. تم تسجيله دون رفع تنبيه."))
            continue

        # Haemoglobin gap only when the other screening tests held at the same facilities.
        if rule["kind"] == "hb_screening_gap":
            moved_ids = [c["fid"] for c in moved]
            others = [compare_rate(world, fid, SCREENING_ITEMS, "anc_visits", as_of, "down") for fid in moved_ids]
            if sum(1 for o in others if o and o["ratio"] <= CONFIG["area_ratio_down"]) >= len(moved_ids) / 2:
                results["quiet"].append(_quiet("covered_by_screening_dropoff", "area", governorate,
                    "Haemoglobin tests fell together with other screening. Reported once, under the screening alert.",
                    "انخفضت اختبارات الهيموجلوبين مع بقية الفحوصات. تم الإبلاغ مرة واحدة ضمن تنبيه الفحص."))
                continue

        results["alerts"].append(_area_alert(world, as_of, rule, governorate, moved, unassessed, peer_ratio, (pooled_n0, pooled_d0, pooled_n1, pooled_d1), excluded))


def _area_alert(world, as_of, rule, governorate, moved, unassessed, peer_ratio, pooled, excluded):
    kind = rule["kind"]
    n0, d0, n1, d1 = pooled
    change = (n1 / d1) / (n0 / d0) - 1 if n0 else 0
    what_moved = [{
        "scope": governorate,
        "baseline": show_rate(n0, d0),
        "recent": show_rate(n1, d1),
        "change_pct": round(change * 100),
        "en": f"{governorate}: {show_rate(n0, d0)} {rule['per']} in the baseline, {show_rate(n1, d1)} in the last {CONFIG['recent_weeks']} weeks.",
        "ar": f"{governorate}: {show_rate(n0, d0)} {rule['per_ar']} في خط الأساس، و{show_rate(n1, d1)} في آخر {CONFIG['recent_weeks']} أسابيع.",
    }]
    for c in sorted(moved, key=lambda m: m["fid"]):
        what_moved.append({
            "scope": c["fid"],
            "baseline": show_rate(c["n0"], c["d0"]),
            "recent": show_rate(c["n1"], c["d1"]),
            "change_pct": round((c["ratio"] - 1) * 100),
            "en": f"{c['fid']}: {show_rate(c['n0'], c['d0'])} before, {show_rate(c['n1'], c['d1'])} recently.",
            "ar": f"{c['fid']}: {show_rate(c['n0'], c['d0'])} سابقا، و{show_rate(c['n1'], c['d1'])} مؤخرا.",
        })
    codes = ["seasonal", "bulk", "reporting", "delivery_failure", "single_facility"]
    if rule["direction"] == "down":
        codes.append("volume")
    missing = [text.MISSING["cause"], text.MISSING["scope"]]
    if unassessed:
        missing.append({"en": text.MISSING["unassessed"]["en"].format(items=", ".join(unassessed)), "ar": text.MISSING["unassessed"]["ar"].format(items=", ".join(unassessed))})
    return _finish({
        "alert_id": f"AL-{kind}-{governorate}-W{as_of:02d}",
        "kind": kind, "level": "area",
        "where": {"governorate": governorate, "facilities": sorted(c["fid"] for c in moved)},
        "label": text.LABELS[kind],
        "prompt": {lang: text.PROMPT[kind][lang].format(n=len(moved), where=governorate) for lang in ("en", "ar")},
        "what_moved": what_moved,
        "ruled_out": _ruled(*codes),
        "missing": missing,
        "who_acts": text.ROLES["area"],
        "status": "awaiting_review",
        "peer_median_ratio": round(peer_ratio, 3) if peer_ratio else None,
    })


def _finish(alert):
    text.guard_text(*text.all_alert_strings(alert))
    return alert


def _cover(world, fid, item, as_of):
    """Weeks of cover, using the latest reported weeks only."""
    rows = [(w, world["item"][fid][item][w]) for w in range(max(0, as_of - CONFIG["cover_mean_weeks"] + 1), as_of + 1) if _ok(world, fid, w)]
    if len(rows) < 3:
        return None
    mean_issue = sum(r["issued"] for _, r in rows) / len(rows)
    if mean_issue <= 0:
        return None
    stock_series = [(w, r["stock_end"]) for w, r in rows]
    last = stock_series[-CONFIG["cover_consecutive"]:]
    return {
        "mean_issue": mean_issue,
        "cover": [s / mean_issue for _, s in last],
        "stock_now": stock_series[-1][1],
        "stock_before": stock_series[0][1],
        "received": sum(r["received"] for _, r in rows),
        "issued": sum(r["issued"] for _, r in rows),
    }


def _peer_cover(world, facilities, item, as_of, skip):
    values = []
    for f in facilities:
        if f["id"] == skip:
            continue
        c = _cover(world, f["id"], item, as_of)
        if c:
            values.append(c["cover"][-1])
    return statistics.median(values) if values else None


def _stock_rules(world, as_of, results):
    for f in world["facilities"]:
        fid = f["id"]
        for item in UTEROTONICS:
            c = _cover(world, fid, item, as_of)
            if c is None:
                results["not_assessed"].append({"facility": fid, "measure": item, "reason": "too few complete weeks"})
                continue
            low_cover = all(cover < CONFIG["cover_weeks_risk"] for cover in c["cover"])
            # A low point between deliveries is normal; deliveries not replacing use is not.
            not_replaced = c["received"] <= CONFIG["replenishment_share"] * c["issued"]
            if not (low_cover and not_replaced) or c["stock_now"] >= c["stock_before"]:
                continue
            if _failed_share(world, fid, [item], as_of) >= CONFIG["delivery_failure_share"]:
                results["quiet"].append(_quiet("delivery_failure", "facility", fid,
                    f"{item} cover is low at {fid} because scheduled deliveries did not arrive. Logged and routed to logistics, not raised as an alert.",
                    f"تغطية {item} منخفضة في {fid} لأن التوريدات المجدولة لم تصل. تم تسجيله وتحويله إلى اللوجستيات دون رفع تنبيه."))
                continue
            peers = _peer_cover(world, world["facilities"], item, as_of, fid)
            cover = c["cover"][-1]
            what_moved = [{
                "scope": fid,
                "baseline": "",
                "recent": f"{cover:.1f}",
                "change_pct": None,
                "en": f"{item} at {fid}: about {cover:.1f} weeks of cover at recent use, stock on hand {show_count(c['stock_now'])}.",
                "ar": f"{item} في {fid}: نحو {cover:.1f} أسبوع تغطية عند معدل الاستخدام الأخير، المخزون المتاح {show_count(c['stock_now'])}.",
            }]
            if peers is not None:
                what_moved.append({
                    "scope": "peers", "baseline": "", "recent": f"{peers:.1f}", "change_pct": None,
                    "en": f"Peer facilities: median cover about {peers:.1f} weeks.",
                    "ar": f"المنشآت المقارنة: متوسط التغطية نحو {peers:.1f} أسبوع.",
                })
            results["alerts"].append(_facility_alert("uterotonic_stock_risk", f, as_of, what_moved,
                {lang: text.PROMPT["uterotonic_stock_risk"][lang].format(item=item, where=fid, cover=f"{cover:.1f}") for lang in ("en", "ar")},
                item, ["delivery_failure", "replenishment", "reporting"]))

        for item in NEWBORN_ITEMS:
            _newborn_rule(world, f, item, as_of, results)


def _newborn_rule(world, f, item, as_of, results):
    fid = f["id"]
    weeks = CONFIG["newborn_weeks"]
    recent = [w for w in range(as_of - weeks + 1, as_of + 1) if _ok(world, fid, w)]
    baseline_start, baseline_end, _ = _windows(as_of)
    base = [w for w in range(max(0, baseline_start), baseline_end + 1) if _ok(world, fid, w)]
    if len(recent) < 2 or len(base) < CONFIG["min_baseline_ok"]:
        results["not_assessed"].append({"facility": fid, "measure": item, "reason": "too few complete weeks"})
        return
    issued0 = sum(world["item"][fid][item][w]["issued"] for w in base)
    drivers0 = sum(world["service"][fid][w]["deliveries"] for w in base)
    if drivers0 == 0 or issued0 == 0:
        return
    rate0 = issued0 / drivers0
    drivers1 = sum(world["service"][fid][w]["deliveries"] for w in recent)
    expected = rate0 * drivers1
    if expected < CONFIG["newborn_min_expected"]:
        results["not_assessed"].append({"facility": fid, "measure": item, "reason": "too few counts"})
        return
    issued1 = sum(world["item"][fid][item][w]["issued"] for w in recent)
    ratio = issued1 / expected
    if ratio > CONFIG["newborn_ratio"]:
        return
    if drivers1 / len(recent) < CONFIG["newborn_volume_floor"] * (drivers0 / len(base)):
        return
    mean_issue = issued0 / len(base)
    stock = world["item"][fid][item][recent[-1]]["stock_end"]
    if stock / mean_issue >= CONFIG["newborn_cover_weeks"]:
        return
    if _failed_share(world, fid, [item], as_of) >= CONFIG["delivery_failure_share"]:
        results["quiet"].append(_quiet("delivery_failure", "facility", fid,
            f"{item} use fell at {fid} because scheduled deliveries did not arrive. Logged and routed to logistics, not raised as an alert.",
            f"انخفض استخدام {item} في {fid} لأن التوريدات المجدولة لم تصل. تم تسجيله وتحويله إلى اللوجستيات دون رفع تنبيه."))
        return
    what_moved = [{
        "scope": fid, "baseline": show_rate(issued0, drivers0), "recent": show_rate(issued1, drivers1),
        "change_pct": round((issued1 / drivers1 / rate0 - 1) * 100) if drivers1 else None,
        "en": f"{item} at {fid}: {show_rate(issued0, drivers0)} per 100 deliveries before, {show_rate(issued1, drivers1)} in the last {len(recent)} complete weeks; stock on hand {show_count(stock)}.",
        "ar": f"{item} في {fid}: {show_rate(issued0, drivers0)} لكل 100 ولادة سابقا، و{show_rate(issued1, drivers1)} في آخر {len(recent)} أسابيع مكتملة؛ المخزون المتاح {show_count(stock)}.",
    }]
    results["alerts"].append(_facility_alert("newborn_item_shortage", f, as_of, what_moved,
        {lang: text.PROMPT["newborn_item_shortage"][lang].format(item=item, where=fid) for lang in ("en", "ar")},
        item, ["delivery_failure", "reporting", "volume"]))


def _facility_alert(kind, facility, as_of, what_moved, prompt, item, codes):
    return _finish({
        "alert_id": f"AL-{kind}-{facility['id']}-{item}-W{as_of:02d}",
        "kind": kind, "level": "facility",
        "where": {"governorate": facility["governorate"], "facilities": [facility["id"]]},
        "item": item,
        "label": text.LABELS[kind],
        "prompt": prompt,
        "what_moved": what_moved,
        "ruled_out": _ruled(*codes),
        "missing": [text.MISSING["cause"], text.MISSING["scope"]],
        "who_acts": text.ROLES["facility"],
        "status": "awaiting_review",
    })


def assess(world, as_of=None):
    """Assess a world as of a given week. Same world, same answer."""
    as_of = world["weeks"] - 1 if as_of is None else as_of
    results = {"as_of_week": as_of, "alerts": [], "quiet": [], "not_assessed": []}
    for rule in AREA_RULES:
        _area_rule(world, as_of, rule, results)
    _stock_rules(world, as_of, results)
    results["alerts"].sort(key=lambda a: a["alert_id"])
    return results
