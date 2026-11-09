"use strict";

// All browser storage is guarded: a private window or blocked storage must not break the demo.
function safeGet(key) {
  try { return window.localStorage.getItem(key); } catch (e) { return null; }
}
function safeSet(key, value) {
  try { window.localStorage.setItem(key, value); } catch (e) { /* demo still works, the log just does not persist */ }
}

const T = {
  en: {
    simulatedData: "Simulated data", tagline: "Where to look, in maternal and newborn supplies. A signal about supplies, never a diagnosis.",
    loading: "Loading...", overview: "Governorates and facilities", overviewNote: "Fictional facilities in real governorates, as of week {week}. Deliveries are for the last 4 weeks.",
    ok: "Monitored", attention: "Look here", not_assessed: "Partly assessed", deliveries: "deliveries",
    alertTitle: "One alert in full", exampleNote: "This is a world where the detector fired correctly. The held-out results further down show the misses, including for this kind of alert.",
    where: "Where to look", moved: "What moved", ruled: "What was ruled out", missing: "What is missing", who: "Who acts",
    decision: "A named person confirms or stands down", name: "Name", reason: "Reason (do not name anyone)", confirm: "Confirm", standDown: "Stand down",
    decisionHelp: "Demo only. Your decision is stored in this browser and is not sent anywhere.", logTitle: "Decision log", logEmpty: "No decisions yet.", needAll: "Please enter a name and a reason.",
    confirmedAs: "Confirmed", stoodDownAs: "Stood down", by: "by", reasonLabel: "reason",
    quietTitle: "A scenario that correctly stays quiet", quietCase: "Shortage explained by delivery failure", quietResult: "No alert raised.", quietWhy: "Why it stayed quiet",
    quietNote: "Stock fell because scheduled deliveries did not arrive. The cause is recorded and logistics owns it, so the watcher logs it and routes it to logistics instead of raising an alert.",
    resultsTitle: "Held-out results (scored once)", sensitivity: "Sensitivity", falseAlarm: "False alarm rate", precision: "Precision of alerts", cleanRolling: "Clean rolling alerts per evaluation",
    baselineTitle: "Single-facility threshold baseline on the same worlds", resultsClass: "Scenario", resultsCorrect: "Correct", resultsFalse: "False alarm worlds", resultsAlerts: "Alerts", shouldAlert: "should alert", shouldQuiet: "should stay quiet",
    weak: "Weak", failuresTitle: "Misses and false alarms ({n})", none: "None.", frozenHash: "Frozen detector sha256", weakNote: "Rising tranexamic acid and blood bag use is a weak result: 10 of 30 worlds found. Likely cause, not tested further: facility counts for these items are low.",
    catalogue: "Catalogue", catalogueStatus: "Clinical mapping: pending review by Dr. Yasmeen Dabees (gynaecologist). Not yet reviewed.",
    role: "Role", stage: "Care stage", cited: "Source", uncited: "Uncited",
    footerModule: "New module built for the Sweden-UNICEF FemTech Ventures call; it has not been run in any facility.",
    footerOpen: "Only this module is open source. The rest of UltraSignal and UltraInsight are proprietary and are not included.",
    footerSim: "All data on this page is simulated. No real facility, person or customer data was used.",
  },
  ar: {
    simulatedData: "بيانات محاكاة", tagline: "إلى أين ننظر في مستلزمات صحة الأم والوليد. إشارة عن المستلزمات، وليست تشخيصا أبدا.",
    loading: "جار التحميل...", overview: "المحافظات والمنشآت", overviewNote: "منشآت خيالية في محافظات حقيقية، حتى الأسبوع {week}. الولادات عن آخر 4 أسابيع.",
    ok: "تحت المتابعة", attention: "انظر هنا", not_assessed: "تقييم جزئي", deliveries: "ولادة",
    alertTitle: "تنبيه واحد بالكامل", exampleNote: "هذا عالم أصاب فيه النظام. وتعرض نتائج الاختبار المعزول في الأسفل حالات الإخفاق أيضا، ومنها هذا النوع من التنبيهات.",
    where: "أين ننظر", moved: "ما الذي تغير", ruled: "ما الذي تم استبعاده", missing: "ما الذي ينقص", who: "من يتصرف",
    decision: "شخص مسمى يؤكد التنبيه أو يوقفه", name: "الاسم", reason: "السبب (دون ذكر أسماء أشخاص)", confirm: "تأكيد", standDown: "إيقاف التنبيه",
    decisionHelp: "للعرض فقط. يُحفظ قرارك في هذا المتصفح ولا يُرسل إلى أي مكان.", logTitle: "سجل القرارات", logEmpty: "لا توجد قرارات بعد.", needAll: "يرجى إدخال الاسم والسبب.",
    confirmedAs: "تم التأكيد", stoodDownAs: "تم الإيقاف", by: "بواسطة", reasonLabel: "السبب",
    quietTitle: "سيناريو ظل هادئا كما يجب", quietCase: "نقص يفسره تعثر التوريد", quietResult: "لم يُرفع أي تنبيه.", quietWhy: "لماذا بقي هادئا",
    quietNote: "انخفض المخزون لأن التوريدات المجدولة لم تصل. السبب مسجل واللوجستيات مسؤولة عنه، لذلك يسجله النظام ويحوله إلى اللوجستيات دون رفع تنبيه.",
    resultsTitle: "نتائج الاختبار المعزول (مرة واحدة فقط)", sensitivity: "الحساسية", falseAlarm: "معدل الإنذار الخاطئ", precision: "دقة التنبيهات", cleanRolling: "تنبيهات لكل تقييم في العوالم النظيفة",
    baselineTitle: "خط أساس حد المنشأة الواحدة على العوالم نفسها", resultsClass: "السيناريو", resultsCorrect: "صحيح", resultsFalse: "عوالم إنذار خاطئ", resultsAlerts: "تنبيهات", shouldAlert: "يجب أن ينبه", shouldQuiet: "يجب أن يبقى هادئا",
    weak: "ضعيف", failuresTitle: "الإخفاقات والإنذارات الخاطئة ({n})", none: "لا يوجد.", frozenHash: "بصمة sha256 للكاشف المجمد", weakNote: "نتيجة ارتفاع استخدام Tranexamic acid وأكياس الدم ضعيفة: اكتُشف 10 من 30 عالما. السبب المحتمل، دون اختبار إضافي: قلة الأعداد لكل منشأة في هذه الأصناف.",
    catalogue: "الكتالوج", catalogueStatus: "Clinical mapping: pending review by Dr. Yasmeen Dabees (gynaecologist). Not yet reviewed.",
    role: "الدور", stage: "مرحلة الرعاية", cited: "المصدر", uncited: "دون مصدر",
    footerModule: "New module built for the Sweden-UNICEF FemTech Ventures call; it has not been run in any facility. (وحدة جديدة، لم تعمل في أي منشأة)",
    footerOpen: "Only this module is open source. The rest of UltraSignal and UltraInsight are proprietary and are not included.",
    footerSim: "كل البيانات في هذه الصفحة محاكاة. لم تُستخدم أي بيانات لمنشأة أو شخص أو عميل حقيقي.",
  },
};
const LIMIT_AR = "Simulated results prove the mechanism works, not that it works at this accuracy in real facilities.";

const CLASS_NAMES = {
  uterotonic_stockout_risk: { en: "Uterotonic stock-out risk", ar: "خطر نفاد uterotonics" },
  antenatal_screening_dropoff: { en: "Antenatal screening drop-off", ar: "تراجع فحوصات متابعة الحمل" },
  haemorrhage_treatment_rise: { en: "Rising tranexamic acid and blood bag use", ar: "ارتفاع استخدام Tranexamic acid وأكياس الدم" },
  anaemia_screening_gap: { en: "Haemoglobin screening gap", ar: "فجوة فحص الهيموجلوبين" },
  newborn_item_shortage: { en: "Newborn item shortage", ar: "نقص صنف لحديثي الولادة" },
  bulk_order: { en: "Bulk order", ar: "طلبية كبيرة" },
  reporting_gap: { en: "Reporting gap", ar: "فجوة إبلاغ" },
  delivery_failure_shortage: { en: "Shortage explained by delivery failure", ar: "نقص يفسره تعثر التوريد" },
  single_facility_noise: { en: "Single-facility noise", ar: "تذبذب منشأة واحدة" },
  seasonal_delivery_peak: { en: "Seasonal delivery peak", ar: "ذروة موسمية للولادات" },
  clean: { en: "Clean world", ar: "عالم نظيف" },
};
const ROLE_AR = { screen: "فحص", prevent: "وقاية", treat: "علاج", escalate: "تصعيد" };
const STAGE_AR = { antenatal: "متابعة الحمل", delivery: "الولادة", postnatal: "ما بعد الولادة", newborn: "حديث الولادة" };
const QUIET = ["bulk_order", "reporting_gap", "delivery_failure_shortage", "single_facility_noise", "seasonal_delivery_peak", "clean"];

let lang = "en";
const urlLang = new URLSearchParams(window.location.search).get("lang");
const savedLang = urlLang || safeGet("usmw-lang");
if (savedLang === "ar" || savedLang === "en") lang = savedLang;
let DATA = null;

function t(key, vars) {
  let out = T[lang][key] || key;
  if (vars) for (const k in vars) out = out.replace("{" + k + "}", vars[k]);
  return out;
}
function el(tag, attrs, children) {
  const node = document.createElement(tag);
  if (attrs) for (const k in attrs) {
    if (k === "class") node.className = attrs[k];
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), attrs[k]);
    else node.setAttribute(k, attrs[k]);
  }
  (children || []).forEach((c) => { if (c !== null && c !== undefined) node.append(c); });
  return node;
}
function tag() { return el("span", { class: "tag" }, [t("simulatedData")]); }
function sectionTitle(key) { return el("h2", null, [t(key), tag()]); }
function pct(x) { return x === null || x === undefined ? "n/a" : (x * 100).toFixed(1) + "%"; }

function renderOverview() {
  const card = el("section", { class: "card" }, [sectionTitle("overview"),
    el("p", { class: "muted" }, [t("overviewNote", { week: DATA.as_of_week })]),
    el("div", { class: "legend" }, [el("span", { class: "attention" }, [t("attention")]), el("span", { class: "not_assessed" }, [t("not_assessed")]), el("span", { class: "ok" }, [t("ok")])]),
  ]);
  DATA.overview.forEach((group) => {
    const chips = el("div", { class: "chips" }, group.facilities.map((f) =>
      el("div", { class: "chip " + f.status }, [el("b", null, [f.id]), el("span", { class: "st" }, [t(f.status) + ", " + f.deliveries_last_4_weeks + " " + t("deliveries")])])
    ));
    const count = (status) => group.facilities.filter((f) => f.status === status).length;
    const summary = `${group.governorate}: ${count("attention")} ${t("attention")}, ${count("not_assessed")} ${t("not_assessed")}, ${count("ok")} ${t("ok")}`;
    if (count("attention")) {
      card.append(el("div", { class: "gov" }, [el("div", { class: "gov-name" }, [summary]), chips]));
    } else {
      card.append(el("details", { class: "gov" }, [el("summary", null, [summary]), chips]));
    }
  });
  return card;
}

function renderList(items) {
  return el("ul", { class: "plain" }, items.map((entry) => el("li", null, [entry[lang]])));
}

function decisionStoreKey() { return "usmw-log-" + DATA.alert.alert_id; }
function loadDecisions() {
  const raw = safeGet(decisionStoreKey());
  if (!raw) return [];
  try { return JSON.parse(raw); } catch (e) { return []; }
}

function renderDecision() {
  const name = el("input", { id: "dec-name", type: "text", value: "Sim Reviewer A" });
  const reason = el("textarea", { id: "dec-reason", rows: "2" }, []);
  const err = el("div", { class: "err" }, []);
  const log = el("ul", { class: "log" }, []);
  function drawLog() {
    log.textContent = "";
    const entries = loadDecisions();
    if (!entries.length) log.append(el("li", null, [t("logEmpty")]));
    entries.slice().reverse().forEach((e) => {
      log.append(el("li", null, [`${e.action === "confirm" ? t("confirmedAs") : t("stoodDownAs")} ${t("by")} ${e.name}. ${t("reasonLabel")}: ${e.reason} (${e.at})`]));
    });
  }
  function act(action) {
    const who = name.value.trim(), why = reason.value.trim();
    if (!who || !why) { err.textContent = t("needAll"); return; }
    err.textContent = "";
    const entries = loadDecisions();
    entries.push({ alert: DATA.alert.alert_id, action, name: who, reason: why, at: new Date().toISOString() });
    safeSet(decisionStoreKey(), JSON.stringify(entries));
    reason.value = "";
    drawLog();
  }
  drawLog();
  return el("div", { class: "decide" }, [
    el("h3", null, [t("decision")]),
    el("label", { for: "dec-name" }, [t("name")]), name,
    el("label", { for: "dec-reason" }, [t("reason")]), reason,
    el("div", { class: "buttons" }, [
      el("button", { class: "act", type: "button", onclick: () => act("confirm") }, [t("confirm")]),
      el("button", { class: "act secondary", type: "button", onclick: () => act("stand_down") }, [t("standDown")]),
    ]),
    err,
    el("p", { class: "muted" }, [t("decisionHelp")]),
    el("h3", null, [t("logTitle")]),
    log,
  ]);
}

function renderAlert() {
  const a = DATA.alert;
  return el("section", { class: "card" }, [
    sectionTitle("alertTitle"),
    el("p", { class: "muted" }, [t("exampleNote")]),
    el("div", { class: "alert-head" }, [el("strong", null, [a.label[lang]]), el("span", { class: "pill" }, [a.where.governorate])]),
    el("p", null, [a.prompt[lang]]),
    el("div", { class: "alert-grid" }, [
      el("div", null, [el("h3", null, [t("where")]), el("ul", { class: "plain" }, [el("li", null, [a.where.governorate]), ...a.where.facilities.map((f) => el("li", null, [f]))]),
        el("h3", null, [t("moved")]), renderList(a.what_moved)]),
      el("div", null, [el("h3", null, [t("ruled")]), renderList(a.ruled_out), el("h3", null, [t("missing")]), renderList(a.missing), el("h3", null, [t("who")]), el("p", null, [a.who_acts[lang]])]),
    ]),
    renderDecision(),
  ]);
}

function renderQuiet() {
  const q = DATA.quiet_case;
  return el("section", { class: "card" }, [
    sectionTitle("quietTitle"),
    el("p", null, [el("strong", null, [t("quietCase") + ". "]), el("span", { class: "quiet-ok" }, [t("quietResult")])]),
    el("p", null, [t("quietNote")]),
    el("h3", null, [t("quietWhy")]),
    renderList(q.quiet.slice(0, 3)),
  ]);
}

function renderHoldout() {
  const h = DATA.holdout;
  const stat = (value, labelKey) => el("div", { class: "stat" }, [el("b", null, [value]), el("span", null, [t(labelKey)])]);
  const rows = h.per_class.map((row) => {
    const name = CLASS_NAMES[row.class] ? CLASS_NAMES[row.class][lang] : row.class;
    const isQuiet = QUIET.includes(row.class);
    const weak = row.class === "haemorrhage_treatment_rise";
    const failures = row.failures.length
      ? el("details", null, [el("summary", null, [t("failuresTitle", { n: row.failure_count })]), el("ul", { class: "plain" }, row.failures.map((f) => el("li", null, [f])))])
      : el("span", { class: "muted" }, [t("none")]);
    return el("tr", weak ? { class: "weak" } : null, [
      el("td", null, [name, " ", el("span", { class: "muted" }, ["(" + t(isQuiet ? "shouldQuiet" : "shouldAlert") + ")"]), weak ? el("span", { class: "pill" }, [t("weak")]) : null]),
      el("td", { class: "num" }, [row.correct + " / " + row.worlds]),
      el("td", { class: "num" }, [String(row.false_alarm_worlds)]),
      el("td", null, [failures]),
    ]);
  });
  return el("section", { class: "card" }, [
    sectionTitle("resultsTitle"),
    el("p", { class: "limit" }, [lang === "ar" ? LIMIT_AR : h.limit]),
    el("div", { class: "stats" }, [stat(pct(h.overall.sensitivity), "sensitivity"), stat(pct(h.overall.false_alarm_rate_quiet_worlds), "falseAlarm"), stat(pct(h.overall.precision_of_alerts), "precision"), stat(String(h.overall.clean_rolling_alerts_per_evaluation), "cleanRolling")]),
    el("p", { class: "muted" }, [t("weakNote")]),
    el("div", { class: "table-wrap" }, [el("table", null, [
      el("thead", null, [el("tr", null, [el("th", null, [t("resultsClass")]), el("th", null, [t("resultsCorrect")]), el("th", null, [t("resultsFalse")]), el("th", null, [t("failuresTitle", { n: "" }).replace(" ()", "")])])]),
      el("tbody", null, rows),
    ])]),
    el("h3", null, [t("baselineTitle")]),
    el("div", { class: "stats" }, [stat(pct(h.baseline_overall.sensitivity), "sensitivity"), stat(pct(h.baseline_overall.false_alarm_rate_quiet_worlds), "falseAlarm"), stat(pct(h.baseline_overall.precision_of_alerts), "precision")]),
    el("p", { class: "muted" }, [t("frozenHash") + ": " + h.frozen_detector_sha256]),
  ]);
}

function renderCatalogue() {
  const rows = DATA.catalogue.items.map((item) => el("tr", null, [
    el("td", null, [item.name]),
    el("td", null, [item.stages.map((s) => (lang === "ar" ? STAGE_AR[s] : s)).join(", ")]),
    el("td", null, [lang === "ar" ? ROLE_AR[item.role] : item.role]),
    el("td", null, [item.cited ? item.sources.join(", ") : t("uncited")]),
  ]));
  return el("section", { class: "card" }, [
    sectionTitle("catalogue"),
    el("p", { class: "limit" }, [t("catalogueStatus")]),
    el("div", { class: "table-wrap" }, [el("table", null, [
      el("thead", null, [el("tr", null, [el("th", null, ["SKU"]), el("th", null, [t("stage")]), el("th", null, [t("role")]), el("th", null, [t("cited")])])]),
      el("tbody", null, rows),
    ])]),
  ]);
}

function applyStatic() {
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.querySelectorAll("[data-t]").forEach((n) => { n.textContent = t(n.getAttribute("data-t")); });
  document.getElementById("lang").textContent = lang === "ar" ? "English" : "العربية";
}

function render() {
  applyStatic();
  const app = document.getElementById("app");
  app.textContent = "";
  if (!DATA) return;
  app.append(renderOverview(), renderAlert(), renderQuiet(), renderHoldout(), renderCatalogue());
  const foot = document.getElementById("foot");
  foot.textContent = "";
  foot.append(el("p", null, [t("footerModule")]), el("p", null, [t("footerOpen")]), el("p", null, [t("footerSim")]));
}

document.getElementById("lang").addEventListener("click", () => {
  lang = lang === "en" ? "ar" : "en";
  safeSet("usmw-lang", lang);
  render();
});

applyStatic();
fetch("data/demo.json").then((r) => r.json()).then((d) => { DATA = d; render(); }).catch(() => {
  document.getElementById("app").textContent = "Could not load demo data.";
});
