# UltraSignal Maternal Watcher

An open-source module that watches facility consumption of maternal and newborn supplies, reads it with screening counts, and tells a district or facility lead where to look. Statistics and rules only. It never diagnoses and never concerns an individual.

New module built for the Sweden-UNICEF FemTech Ventures call; it has not been run in any facility.

Only this module is open source. The rest of UltraSignal and UltraInsight are proprietary and are not included.

Clinical mapping: pending review by Dr. Yasmeen Dabees (gynaecologist). Not yet reviewed.

Everything in this repository runs on simulated data. No real facility, person or customer data was used. The module has no pilot, no partner and no endorsement from UNICEF or any government.

## What it is

Facility-level weekly aggregates go in. Each facility is compared with its own recent normal and, for area-level signals, with peers in other governorates. An area-level signal needs at least three separate facilities, each passing the test on its own counts. Ordinary causes are checked (bulk orders, reporting gaps, recorded delivery failures, single-facility noise, seasonal delivery peaks).

Each alert states where to look, what moved, what was ruled out, what is missing and who acts. A named person confirms or stands down, and every decision is logged. Counts under 5 are hidden in anything an alert or the demo shows.

Scenarios it should alert on: uterotonic stock-out risk, antenatal screening drop-off, rising tranexamic acid and blood bag use across nearby facilities, haemoglobin screening gaps, newborn item shortages.

Scenarios it should stay quiet on: bulk orders, reporting gaps, supply shortages explained by delivery failure, single-facility noise, seasonal delivery peaks. See `TEST_PLAN.md` for how a stock-out risk differs from a shortage.

## What it is not

Not a diagnostic tool and not a medical device. Not based on person-level data, and it holds none, not even simulated. Not proven in a real facility. Not a forecast of clinical outcomes.

## Run it in under 2 minutes

Python 3.12+ and the standard library only.

```
python -m unittest discover -t . -s tests
python scripts/run_example.py
python -m http.server 8000 --directory docs
```

The last line serves the demo at http://localhost:8000. The unit tests take about 30 seconds. `reports/test_output.txt` holds the actual output of the last full test run.

## Results (held-out, scored once)

Simulated results prove the mechanism works, not that it works at this accuracy in real facilities.

Frozen detector sha256: `0ad940a8f0fbdb4f320a39e7afabb3faed3f385fa5f70797bf7bc7b0c97a6ba2` (commit `3951589`, see `reports/FROZEN.json`). 330 worlds, seeds fixed by a rule stated in `TEST_PLAN.md` before scoring, run once by `scripts/score_holdout.py`. Full results with every miss are in `reports/holdout.json`.

Note on commit IDs: before first publication the commit author address was changed to a private address, which changes every commit ID but no file. `reports/holdout.json` was left untouched, so it records the freeze commit under its earlier ID, `bde9fd2`, which is `3951589` here. The file hashes in `reports/FROZEN.json` are what bind the score to the code.

| | Detector | Single-facility threshold baseline |
|---|---|---|
| Sensitivity over should-alert scenarios | **78.0%** (117 of 150) | 78.0% |
| False alarm rate over should-stay-quiet worlds | **2.8%** (5 of 180) | 100% |
| Precision of alerts | **95.3%** | 10.0% |
| Clean rolling alerts per evaluation | **0** | 6.0 |

| Scenario | Correct | False alarm worlds | Miss or false alarm examples |
|---|---|---|---|
| Uterotonic stock-out risk | 26 / 30 | 0 | 4 misses |
| Antenatal screening drop-off | 28 / 30 | 0 | 2 misses |
| **Rising tranexamic acid and blood bag use** | **10 / 30** | 0 | **20 misses. Weak.** |
| Haemoglobin screening gap | 26 / 30 | 0 | 4 misses |
| Newborn item shortage | 27 / 30 | 0 | 3 misses |
| Bulk order (should stay quiet) | 30 / 30 | 0 | none |
| Reporting gap (should stay quiet) | 30 / 30 | 0 | none |
| Delivery failure shortage (should stay quiet) | 30 / 30 | 0 | none |
| Single-facility noise (should stay quiet) | 29 / 30 | 1 | 1 false alarm |
| Seasonal delivery peak (should stay quiet) | 26 / 30 | 4 | 4 false alarms |
| Clean world (should stay quiet) | 30 / 30 | 0 | none |

Plainly: detection of rising tranexamic acid and blood bag use across facilities is **weak**, finding 10 of 30 held-out worlds, against 10 of 15 in the development set. The likely cause is that these items have low weekly counts at each facility, so the per-facility test has little power, but that was not investigated further. It has not been re-tuned and will not be, because the held-out set is scored once. Seasonal peaks caused 4 false alarms on uterotonic stock, which is a real weakness of the stock rule when demand rises fast.

These numbers are good partly because the detector and the simulator were written by the same team and use the same scenario families. Held-out seeds were unseen, but the scenario families were not. Treat them as evidence that the logic runs as described, not as an estimate of real-world accuracy.

## Limits

- Simulated data only. Real data is messier in ways this simulator does not capture.
- Thresholds were tuned on simulated dev worlds, not on any real data.
- The clinical mapping has not been reviewed.
- Comparison is only against a simple single-facility threshold.

## Repository

`watcher/` module, `tests/` unit tests, `scripts/` freeze, score, demo build, `reports/` scored results and test output, `data/` catalogue, `docs/` the static demo site (GitHub Pages ready), and `TEST_PLAN.md`, `MODEL_CARD.md`, `DATA_AND_SAFETY.md`, `SOURCES.md`, `LICENSE` (Apache-2.0).
