"""
marginlab.engine.calibration
───────────────────────────────────────────────────────────────────────────
Native port of the CALIBRATION sheet.

For each item with daily POS observations (price, qty), estimate own-price
elasticity by OLS of ln(qty) on ln(price):

    ê     = SSxy / SSxx                       (slope)
    SE    = sqrt( SSres / (N-2) / SSxx )      (standard error of slope)
    CI    = ê ± 1.96 * SE                     (95%)

Confidence tier (matches J6 logic):
    N < CAL_MIN_OBS_HIGH (30)      -> LOW
    CI_high <= -1                  -> HIGH   (elastic, direction certain)
    else                           -> MEDIUM
    N < CAL_MIN_OBS_ESTIMATE (10)  -> no estimate (falls back to prior, LOW)

In production mode (no client SALES_DATA), every item falls back to the
category prior at LOW confidence — exactly the spreadsheet's behaviour.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional, Iterable

from .constants import CAL_MIN_OBS_ESTIMATE, CAL_MIN_OBS_HIGH, CAL_Z


@dataclass
class Calibration:
    item: str
    n_obs: int
    elasticity: Optional[float]      # None -> use prior
    std_error: Optional[float]
    ci_low: Optional[float]
    ci_high: Optional[float]
    confidence: str                  # HIGH | MEDIUM | LOW
    note: str

    @property
    def has_estimate(self) -> bool:
        return self.elasticity is not None


@dataclass
class Observation:
    item: str
    price: float
    qty: float


def calibrate_item(item: str, obs: Iterable[Observation]) -> Calibration:
    """Run the ln-ln OLS regression for a single item's observations."""
    pts = [(o.price, o.qty) for o in obs
           if o.item == item and o.price > 0 and o.qty > 0]
    n = len(pts)

    if n < CAL_MIN_OBS_ESTIMATE:
        return Calibration(item, n, None, None, None, None, "LOW",
                           "No / insufficient sales rows — using category prior.")

    lnp = [math.log(p) for p, _ in pts]
    lnq = [math.log(q) for _, q in pts]
    mp = sum(lnp) / n
    mq = sum(lnq) / n

    ssxx = sum((x - mp) ** 2 for x in lnp)
    ssxy = sum((x - mp) * (y - mq) for x, y in zip(lnp, lnq))
    if ssxx == 0:
        return Calibration(item, n, None, None, None, None, "LOW",
                           "No price variation — cannot estimate elasticity.")

    beta = ssxy / ssxx
    ssres = sum((y - mq - beta * (x - mp)) ** 2 for x, y in zip(lnp, lnq))

    se = math.sqrt(ssres / (n - 2) / ssxx) if n > 2 else None
    ci_lo = beta - CAL_Z * se if se is not None else None
    ci_hi = beta + CAL_Z * se if se is not None else None

    # Confidence tiering (J6)
    if n < CAL_MIN_OBS_HIGH:
        conf, note = "LOW", "Low sample (<30 obs) — CI is wide."
    elif ci_hi is not None and ci_hi <= -1:
        conf, note = "HIGH", "OK — CI cleanly excludes -1."
    else:
        conf, note = "MEDIUM", "CI crosses -1 — direction uncertain; pilot first."

    # QA soft flag: CI upper bound > 0 means demand could slope upward.
    if ci_hi is not None and ci_hi > 0:
        conf = "LOW"
        note = "CI crosses zero — treat as LOW regardless of N."

    return Calibration(item, n, beta, se, ci_lo, ci_hi, conf, note)


def calibrate_all(items: list[str], observations: list[Observation]) -> dict[str, Calibration]:
    return {it: calibrate_item(it, observations) for it in items}
