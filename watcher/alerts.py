"""Alert wording in English and Arabic.

Alert text talks only about supplies and counts at facilities. It never names a
condition, a person or a cause. The wording guard below enforces this and is
applied to every alert the detector builds.
"""

import re

FORBIDDEN_WORDS = {
    "en": (
        r"\bdiagnos", r"\bpatient", r"\bwom[ae]n\b", r"\bmother", r"\bgirl", r"\bshe\b", r"\bher\b", r"\banaemi",
        r"\banemi", r"\bhaemorrhag", r"\bhemorrhag", r"\bbleed", r"eclampsia", r"\bsepsis", r"\binfected",
        r"\bdisease", r"\bsuffer", r"\bpositive for",
    ),
    "ar": ("تشخيص", "مريض", "مصاب", "نزيف", "نزف", "فقر الدم", "تسمم", "عدوى", "امرأة", "سيدة"),
}

LABELS = {
    "uterotonic_stock_risk": {"en": "Uterotonic stock running short", "ar": "مخزون uterotonics يقترب من النفاد"},
    "screening_dropoff": {"en": "Antenatal screening tests per visit falling", "ar": "انخفاض اختبارات الفحص لكل زيارة متابعة حمل"},
    "treatment_use_rise": {"en": "Tranexamic acid and blood bag use per 100 deliveries rising", "ar": "ارتفاع استخدام Tranexamic acid وأكياس الدم لكل 100 ولادة"},
    "hb_screening_gap": {"en": "Haemoglobin tests per antenatal visit falling", "ar": "انخفاض اختبارات الهيموجلوبين لكل زيارة متابعة حمل"},
    "newborn_item_shortage": {"en": "Newborn item running out while births continue", "ar": "نفاد صنف لحديثي الولادة مع استمرار الولادات"},
}

ROLES = {
    "area": {"en": "Governorate maternal health coordinator (district lead)", "ar": "منسق صحة الأم في المحافظة (مسؤول المنطقة)"},
    "facility": {"en": "Facility pharmacy and stores lead, with the facility maternity lead", "ar": "مسؤول الصيدلية والمخازن في المنشأة مع مسؤول قسم الولادة"},
}

RULED_OUT = {
    "seasonal": {
        "en": "A seasonal peak in deliveries: the measure is per delivery or per visit, and other governorates did not move in the same way.",
        "ar": "ذروة موسمية في الولادات: المقياس لكل ولادة أو زيارة، ولم تتحرك المحافظات الأخرى بالطريقة نفسها.",
    },
    "bulk": {
        "en": "A one-off bulk order: the change still holds with the single largest week removed.",
        "ar": "طلبية كبيرة لمرة واحدة: يبقى التغير قائما بعد حذف أكبر أسبوع.",
    },
    "reporting": {
        "en": "Reporting gaps: only weeks with at least 80 percent complete reporting were used.",
        "ar": "فجوات الإبلاغ: استخدمت فقط الأسابيع التي اكتمل فيها الإبلاغ بنسبة 80 بالمئة على الأقل.",
    },
    "delivery_failure": {
        "en": "A recorded delivery failure: scheduled deliveries for these items did arrive in the last 8 weeks.",
        "ar": "تعثر توريد مسجل: وصلت التوريدات المجدولة لهذه الأصناف خلال آخر 8 أسابيع.",
    },
    "single_facility": {
        "en": "A single facility's noise: the change is seen at several separate facilities, each tested on its own counts.",
        "ar": "تذبذب منشأة واحدة: ظهر التغير في عدة منشآت منفصلة، واختبرت كل منها بأرقامها وحدها.",
    },
    "volume": {
        "en": "A simple fall in visits or deliveries: the measure is per visit or per delivery, and care volumes did not fall.",
        "ar": "انخفاض بسيط في الزيارات أو الولادات: المقياس لكل زيارة أو ولادة، ولم تنخفض أعداد الخدمات.",
    },
}

MISSING = {
    "cause": {
        "en": "The cause. Counts can say where to look, not why it moved.",
        "ar": "السبب. الأرقام تدل على مكان البحث وليس على سبب التغير.",
    },
    "scope": {
        "en": "Anything about individuals: the watcher holds facility totals only, by design.",
        "ar": "أي شيء عن الأفراد: يحتفظ النظام بمجاميع المنشآت فقط، وهذا مقصود.",
    },
    "unassessed": {
        "en": "Facilities in this governorate not assessed (too few complete weeks or too few counts): {items}.",
        "ar": "منشآت في هذه المحافظة لم يتم تقييمها (أسابيع مكتملة قليلة أو أرقام قليلة): {items}.",
    },
}

PROMPT = {
    "uterotonic_stock_risk": {
        "en": "Check {item} stock at {where}. Cover is about {cover} weeks and scheduled deliveries are arriving, so look at order size and use. This is a signal about supplies, not about any person.",
        "ar": "راجع مخزون {item} في {where}. التغطية نحو {cover} أسابيع والتوريدات المجدولة تصل، فراجع حجم الطلب والاستخدام. هذه إشارة عن المستلزمات وليست عن أي شخص.",
    },
    "newborn_item_shortage": {
        "en": "Check {item} at {where}. Use per delivery has fallen sharply, stock is very low and deliveries continue. This is a signal about supplies, not about any person.",
        "ar": "راجع {item} في {where}. انخفض الاستخدام لكل ولادة بشدة والمخزون منخفض جدا والولادات مستمرة. هذه إشارة عن المستلزمات وليست عن أي شخص.",
    },
    "treatment_use_rise": {
        "en": "Tranexamic acid and blood bag use per 100 deliveries rose at {n} separate facilities in {where}. Check stock, records and referral patterns. This is a signal about supplies, not about any person.",
        "ar": "ارتفع استخدام Tranexamic acid وأكياس الدم لكل 100 ولادة في {n} منشآت منفصلة في {where}. راجع المخزون والسجلات ومسارات الإحالة. هذه إشارة عن المستلزمات وليست عن أي شخص.",
    },
    "screening_dropoff": {
        "en": "Urine, syphilis and HIV screening tests per antenatal visit fell at {n} separate facilities in {where}. Check test availability and how screening is being offered. This is a signal about services and supplies, not about any person.",
        "ar": "انخفضت اختبارات البول والزهري وHIV لكل زيارة متابعة حمل في {n} منشآت منفصلة في {where}. راجع توفر الاختبارات وطريقة تقديم الفحص. هذه إشارة عن الخدمات والمستلزمات وليست عن أي شخص.",
    },
    "hb_screening_gap": {
        "en": "Haemoglobin tests per antenatal visit fell at {n} separate facilities in {where} while other screening held. Check test availability and how testing is being offered. This is a signal about services and supplies, not about any person.",
        "ar": "انخفضت اختبارات الهيموجلوبين لكل زيارة متابعة حمل في {n} منشآت منفصلة في {where} بينما بقي الفحص الآخر مستقرا. راجع توفر الاختبارات وطريقة تقديم الفحص. هذه إشارة عن الخدمات والمستلزمات وليست عن أي شخص.",
    },
}


class WordingError(ValueError):
    """Alert text used a word the guard forbids."""


def guard_text(*texts):
    """Raise WordingError if any string contains a forbidden word."""
    for text in texts:
        lowered = text.lower()
        for pattern in FORBIDDEN_WORDS["en"] + FORBIDDEN_WORDS["ar"]:
            if re.search(pattern, lowered):
                raise WordingError(f"forbidden wording {pattern!r} in alert text: {text}")


def all_alert_strings(alert):
    """Every human-readable string an alert carries, in both languages."""
    strings = []
    for section in ("label", "prompt"):
        strings += [alert[section]["en"], alert[section]["ar"]]
    strings += [alert["who_acts"]["en"], alert["who_acts"]["ar"]]
    for key in ("ruled_out", "missing", "what_moved"):
        for entry in alert[key]:
            strings += [entry["en"], entry["ar"]]
    return strings
