# Test plan

This file is committed before any held-out score exists. It fixes what is measured, how the seeds are chosen and what the comparison is.

## Scope of the test

A "world" is one fictional run: 60 weeks, 36 fictional facilities in 6 real Egyptian governorates, generated from one integer seed and one scenario class. The detector is evaluated as of the last week (week 59).

Limits, stated up front:

- Held-out worlds differ from dev worlds in their seeds only. The scenario families are the same and the detector was written knowing them, so the score is optimistic. Fresh scenario families written by someone else would be a stronger test and have not been done.
- A real weekly run would have more chances to raise a false alarm than a single evaluation. The rolling figure below only partly covers that.
- Simulated results prove the mechanism works, not that it works at this accuracy in real facilities.

## Definitions: stock-out risk versus shortage

These are deliberately distinct and the code follows them (`watcher/scenarios.py`, `watcher/detector.py`).

| | Stock-out risk (should alert) | Newborn item shortage (should alert) | Supply shortage from delivery failure (should NOT alert) |
|---|---|---|---|
| Time | Forward-looking | Already happening | Already happening |
| Stock | Cover under 3.5 weeks, and falling | Very low (under 1 week of normal use), and use per delivery has halved | Falling |
| Deliveries | Scheduled deliveries are arriving, but bring less than is used (last 8 weeks received at most 75 percent of issued) | No recorded delivery failure | Recorded failures on at least half of scheduled deliveries for that item in the last 8 weeks |
| Who owns it | Nobody yet, so an alert is useful | Nobody yet, so an alert is useful | Logistics already owns it, so it goes in the quiet log and is routed to logistics |

A shortage caused by a delivery failure is still a real problem. It is left out because the watcher's job is to find what nobody is looking at, and a recorded failure already has an owner. The risk that this suppresses a real signal is listed in `DATA_AND_SAFETY.md`.

## Scenario classes

Should alert: `uterotonic_stockout_risk`, `antenatal_screening_dropoff`, `haemorrhage_treatment_rise`, `anaemia_screening_gap`, `newborn_item_shortage`.

Should NOT alert: `bulk_order`, `reporting_gap`, `delivery_failure_shortage`, `single_facility_noise`, `seasonal_delivery_peak`, `clean`.

The first two area-level "should alert" classes and `anaemia_screening_gap` need at least 3 separate facilities in the governorate. Facility-level classes need one facility.

## Metrics (fixed before scoring)

Sensitivity, per class and overall: share of should-alert worlds with at least one alert of the true kind at the true location (the governorate for area-level scenarios, the facility for facility-level ones).

False alarm rate: share of should-NOT-alert worlds (including clean) with any alert at any location. Any alert counts. In a should-alert world, alerts other than the correct one are also counted and shown.

Precision of alerts: correct alerts divided by all alerts over the whole run.

Clean rolling rate: for each clean world, the detector is also evaluated as of each of the last 8 weeks. The figure is alerts per evaluation.

Every miss and every false alarm is listed with its seed and parameters in `reports/holdout.json`, up to 1000 examples per class.

## Comparison baseline

`watcher/baseline.py`, a single-facility threshold: for each facility and watched item, flag if any of the last 6 weekly counts is more than 3 standard deviations from that facility's own mean, or if stock cover is under 2 weeks. It has no peers, no several-facilities rule and no ordinary-cause checks. It is scored on the same worlds with the same rules. Alert matching is by kind and location.

## Procedure

1. Tune only on dev seeds: `1000` onward, 15 worlds per class, 165 worlds. Dev results are in `reports/dev.json`.
2. Freeze: commit the detector, `reports/FROZEN.json` holds the sha256 of `watcher/detector.py` and of a bundle of every file the score depends on. The commit message records them.
3. Held-out seeds are fixed by this rule, which cannot be applied before the freeze because it depends on the frozen hash: `seed_i` is the first 12 hex digits of `sha256("<bundle_sha256>:<i>")` read as an integer, for i from 0 to 329 (30 worlds per class across 11 classes). World i tests class `i mod 11`.
4. `scripts/score_holdout.py` runs exactly once. It refuses to run if `reports/holdout.json` already exists, if any frozen file changed, or if the working tree is not clean.
5. The output is published as it comes out, in `reports/holdout.json` and in the README, misses included.
6. No re-tuning after step 4. If the score is weak it is published as weak and described as weak.
