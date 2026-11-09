# Model card: UltraSignal Maternal Watcher

Simulated results prove the mechanism works, not that it works at this accuracy in real facilities.

## What it is

A rule-based statistical detector. There is no machine learning, no trained model and no learned weight. Given weekly facility aggregates of maternal and newborn item use, stock and screening counts, it produces alerts about supplies and services for a district or facility lead to review.

## Intended use

Show a governorate or facility lead where to look. A named person decides whether to act.

## Not intended for

Diagnosing, triaging or making any decision about any individual. Performance review of staff or facilities. Replacing clinical judgement, supply audits or logistics systems.

## Input and output

Input: facility-week totals of deliveries, antenatal visits, items issued, items received, stock on hand, delivery due and failed flags, reporting completeness. Output: alerts with where to look, what moved, what was ruled out, what is missing and who acts; a quiet log; a list of what could not be assessed.

## Logic

Per-facility Poisson comparison of the recent 4 weeks with a 29-week baseline, overdispersion allowed, peer adjustment against other governorates, one-week spike check by leaving out the largest week, at least 3 separate facilities for area-level signals, pooled area check. Stock rules use weeks of cover and whether deliveries replaced use. Full thresholds are in `watcher/detector.py` (`CONFIG`).

## Evaluation

See `TEST_PLAN.md` and `reports/holdout.json`. One held-out run on 330 simulated worlds: sensitivity 78.0%, false alarm rate 2.8% over should-quiet worlds, precision 95.3%. Weak spot: rising tranexamic acid and blood bag use across facilities, 10 of 30. Baseline for comparison: 78.0% sensitivity, 100% false alarm rate, 10.0% precision.

## Limits and known issues

- Simulator and detector share authors and scenario families. Real data will behave differently.
- Low weekly counts weaken area-level tests. The rising tranexamic acid and blood bag signal is the clearest example.
- Seasonal demand rises can raise false stock alerts.
- Any threshold is simulation-tuned and would need local calibration before any use.
- Clinical mapping: pending review by Dr. Yasmeen Dabees (gynaecologist). Not yet reviewed.

## Status

New module built for the Sweden-UNICEF FemTech Ventures call; it has not been run in any facility.
