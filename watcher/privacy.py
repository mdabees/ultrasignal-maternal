"""Small-count suppression.

Rule: any count under 5 is shown as "<5", including zero. A rate is shown only
when both its numerator and denominator are at least 5. Everything an alert or
the demo displays goes through these two functions.
"""

SMALL_COUNT_THRESHOLD = 5
SUPPRESSED_COUNT = "<5"
SUPPRESSED_RATE = "suppressed"


def show_count(value):
    """Return a display string for a count, hiding anything under the threshold."""
    if value < SMALL_COUNT_THRESHOLD:
        return SUPPRESSED_COUNT
    return str(int(value))


def show_rate(numerator, denominator, per=100):
    """Return a display string for numerator/denominator * per, or hide it."""
    if denominator < SMALL_COUNT_THRESHOLD or numerator < SMALL_COUNT_THRESHOLD:
        return SUPPRESSED_RATE
    return f"{numerator / denominator * per:.1f}"
