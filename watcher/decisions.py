"""Confirm / stand-down log.

Every alert is confirmed or stood down by a named person. Each decision is
appended to a JSON-lines file and linked to the previous entry by hash, so a
removed or edited line shows up when the log is checked. A decision is about an
alert, never about a person, and the free-text reason must not name anyone.
"""

import hashlib
import json

ACTIONS = ("confirm", "stand_down")


def _digest(entry):
    payload = json.dumps({k: entry[k] for k in sorted(entry) if k != "entry_hash"}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def read_log(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    except FileNotFoundError:
        return []


def record_decision(path, alert_id, decided_by, role, action, reason, at):
    """Append one decision. `at` is supplied by the caller (for example an ISO time)."""
    if action not in ACTIONS:
        raise ValueError(f"action must be one of {ACTIONS}")
    if not decided_by or not decided_by.strip():
        raise ValueError("a named person must make the decision")
    if not reason or not reason.strip():
        raise ValueError("a reason is required")
    log = read_log(path)
    previous = log[-1]["entry_hash"] if log else ""
    entry = {
        "alert_id": alert_id,
        "decided_by": decided_by.strip(),
        "role": role,
        "action": action,
        "reason": reason.strip(),
        "at": at,
        "previous_hash": previous,
    }
    entry["entry_hash"] = _digest(entry)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def verify_log(path):
    """True if every entry's hash is intact and chained to the one before."""
    previous = ""
    for entry in read_log(path):
        if entry["previous_hash"] != previous or entry["entry_hash"] != _digest(entry):
            return False
        previous = entry["entry_hash"]
    return True
