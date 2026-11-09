# Data and safety

## Person-level data

There is none. The module works only on facility-week totals. No record describes a person, not even a simulated one, and `tests/test_generator.py` fails if a field that looks person-level appears.

All facilities are fictional, with `SIM-` ids, in real Egyptian governorates. No real hospital, laboratory, or customer data was used.

## Consent architecture for any future real pilot

The module has not been run in any facility. If a pilot is ever proposed, these conditions must hold before any data flows:

1. A written agreement with the facility or authority that owns the data, defining purpose, retention and who may see alerts.
2. Only aggregated counts leave the facility. Person-level records stay in the facility's own systems and never reach the watcher.
3. Ethical review and legal review under Egyptian data protection law and any other law that applies.
4. A facility can opt out, and its data is then removed.
5. Community and clinician input, especially women's representatives, on what is monitored and how results are used.

No consent has been sought or given, because no real data has been used.

## Small-count suppression

Any count under 5 (including zero) is shown as `<5`. A rate is shown only when both its numerator and denominator are at least 5. The rule is in `watcher/privacy.py` and is applied to everything an alert or the demo shows. Rare events at small facilities could otherwise point toward individuals.

## User risk

**Misuse against facilities or staff.** A list of "where to look" could be read as a list of who failed. Alerts describe supplies, are not performance scores and are reviewed by a named person. Each alert states the cause is unknown. Deployment guidance must prohibit use in staff evaluation.

**Stigma.** Screening and treatment counts in an area can be misread as a statement about the women who live there. Alert text never mentions a condition or a person and a wording guard enforces that. Results should not be published by place without review.

**False reassurance.** No alert does not mean all is well. The detector misses real problems: on simulated held-out worlds it found only 10 of 30 cases of rising tranexamic acid and blood bag use. Facilities with too few complete weeks or counts are not assessed, and this is shown in "what is missing". A shortage with a recorded delivery failure is logged and not alerted, on the assumption that logistics owns it. If that assumption is wrong, a real shortage could go unattended, so the quiet log must be visible to the person who owns the supply route.

**False alarms.** Every false alarm costs staff time. The confirm or stand-down step and its log exist so that noisy rules can be found and dropped.

**Over-trust in a simulated result.** Simulated results prove the mechanism works, not that it works at this accuracy in real facilities.

## Security

No servers, no accounts, no messaging code and no secrets in this repository. The demo is static and sends nothing. Browser storage is used only for the demo's own decision log and language choice, inside try/catch.
