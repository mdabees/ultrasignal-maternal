# Sources for the catalogue

Clinical mapping: pending review by Dr. Yasmeen Dabees (gynaecologist). Not yet reviewed.

Each item in `data/catalogue.json` points to source ids below. Every URL was opened with web tools on 2026-11-09 unless the note says otherwise. Notes state exactly what was seen, because some WHO pages block automated access.

| Id | Source | URL | What was checked |
|---|---|---|---|
| UNCOLSC-2012 | UN Commission on Life-Saving Commodities for Women and Children, Commissioners' Report, Sept 2012, Table 1 | https://aa.unfpa.org/sites/default/files/pub-pdf/Final%20UN%20Commission%20Report_14sept2012.pdf | Read the 13 commodities in Table 1. Lists oxytocin, misoprostol, magnesium sulfate, chlorhexidine and resuscitation devices. |
| EML-OXYTOCIN | WHO eEML entry, oxytocin, uterotonics section | https://list.essentialmeds.org/recommendations/303 | Seen via the eEML search page. The linked recommendation page itself timed out on a direct fetch. |
| EML-MISOPROSTOL | WHO eEML entries, misoprostol, uterotonics | https://list.essentialmeds.org/recommendations/908 | Seen via the eEML search page; postpartum indication listed. |
| EML-MGSO4 | WHO eEML entries, magnesium sulfate | https://list.essentialmeds.org/recommendations/58 | Eclampsia and severe pre-eclampsia entries seen via the eEML search page (see also /recommendations/942). |
| EML-CA-GLUCONATE | WHO eEML, calcium gluconate, antidote section (hypermagnesaemia) | https://list.essentialmeds.org/recommendations/42 | Entry seen via the eEML search page. |
| EML-TXA | WHO eEML, tranexamic acid, medicines administered to the mother (postpartum) | https://list.essentialmeds.org/recommendations/909 | Entry seen via the eEML search page. |
| EML-CHX | WHO eEML, chlorhexidine 7.1% digluconate, medicines administered to the neonate | https://list.essentialmeds.org/recommendations/355 | Entry seen via the eEML search page. |
| EML-PHYTOMENADIONE | WHO eEML, phytomenadione, disorders of the fetus or newborn | https://list.essentialmeds.org/recommendations/841 | Entry seen via the eEML search page. |
| EML-FERROUS-FOLIC | WHO eEML, ferrous salt + folic acid | https://list.essentialmeds.org/medicines/394 | Listed under antianaemia medicines. Page does not state pregnancy as the indication wording. |
| TXA-2017 | WHO recommendation on tranexamic acid for the treatment of postpartum haemorrhage, 2017 | https://www.who.int/publications/i/item/9789241550154 | Publication page read; title and date confirmed. |
| ANC-2016 | WHO recommendations on antenatal care for a positive pregnancy experience, 2016 | https://www.who.int/publications/i/item/9789241549912 | Publication page read; title and date confirmed. Full guideline text could not be opened with web tools (blocked). Recommendation wording and numbers were seen only through a search-engine excerpt, so no recommendation number is quoted here. |
| EDL-HB | WHO electronic Essential Diagnostics List (fifth list), haemoglobin | https://edl.who-healthtechnologies.org/recommendations/8 | Entry read from the eEDL listing. |
| EDL-URINE | WHO eEDL, urinalysis test strips | https://edl.who-healthtechnologies.org/recommendations/6 | Entry read from the eEDL listing. |
| EDL-HIV | WHO eEDL, antibodies to HIV 1/2, rapid test | https://edl.who-healthtechnologies.org/recommendations/25 | Entry read from the eEDL listing. |
| EDL-SYPHILIS | WHO eEDL, antibodies to Treponema pallidum, rapid test | https://edl.who-healthtechnologies.org/recommendations/37 | Entry read from the eEDL listing. |
| DUAL-RDT-2019 | WHO policy brief, dual HIV/syphilis rapid diagnostic tests can be used as the first test in antenatal care, 2019 | https://www.who.int/publications/i/item/WHO-CDS-HIV-19.38 | Publication page read; title, year and core recommendation confirmed. |
| UNFPA-CDK-2024 | UNFPA Palestine, Individual Clean Delivery Kits Guidance Notes, Dec 2024 | https://palestine.unfpa.org/en/publications/individual-clean-delivery-kits-guidance-notes | Publication page read. Note: UNFPA Palestine guidance, not a WHO list. |

## Could not be cited

- **Blood collection and transfusion bags (BLOOD_BAG).** No public listing naming blood bags could be confirmed. The WHO Interagency List of Priority Medical Devices for RMNCH (https://www.who.int/publications/i/item/9789241565028, 2016) is the most likely source, but its page does not mention blood bags and the full list could not be read. The item is marked uncited in the catalogue and the demo.

## Could not be fully verified

- **WHO Model List of Essential Medicines, 24th list (2025).** Its publication page confirms it exists (https://www.who.int/publications/i/item/B09474), but the PDF was blocked (HTTP 403). The eEML database at list.essentialmeds.org was used instead, and its pages do not state which list edition they reflect.
- **Chlorhexidine cord care.** A search-engine excerpt of the WHO 2022 postnatal care guideline (https://www.who.int/publications/i/item/9789240045989) describes chlorhexidine for cord care as context-specific. Its full text was not read. This is flagged for the clinical reviewer.

## Statement of the review status

All stage and role assignments above are a supply-planning mapping. They are not clinical guidance and have not been reviewed by a clinician.
