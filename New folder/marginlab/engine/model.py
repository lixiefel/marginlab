"""
marginlab.engine.model
───────────────────────────────────────────────────────────────────────────
Native port of the v10 pricing pipeline. Reproduces, per item, the exact
OPTIMIZER column chain (K..AA), then MENU_ENGINEERING, SENSITIVITY,
COMPETITOR_BENCHMARK and QA_CHECKS.

Pipeline per item (OPTIMIZER row logic):
  H  elasticity = calibrated estimate else category prior else "Other"
  K  Lerner P*  = cost*e/(e+1)            if e < -1   else "test"
  L  shrink     = {HIGH:1.0, MED:0.5, LOW:0.25}
  M  target     = F*(1+role_test)         if test
                  F + shrink*(P*-F)        otherwise
  P  role clamp = clamp(M, F*(1+floor), F*(1+cap))
  Q  global     = clamp(P, F*(1+max_cut), F*(1+max_raise))
  R  threshold  = pull below a psychology threshold if within its buffer
  T  price      = round R to step, re-clamped to bounds, charm ending applied
  V  demand     = G*(T/F)^e               (constant elasticity)
  X  Δprofit/mo = ((T-E)*V - (F-E)*G) * 30
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from statistics import median
from typing import Optional

from .constants import (
    CATEGORY_PRIORS, PRIOR_FALLBACK, ROLE_RULES, ROLE_FALLBACK,
    USD_THRESHOLDS, IDR_THRESHOLDS, LARGE_DENOM,
    SENS_CONSERVATIVE, SENS_BASELINE, SENS_OPTIMISTIC,
    COMP_TOL_ABOVE, COMP_TOL_BELOW, PHASE_BY_CONFIDENCE,
)
from .calibration import Calibration


# ── Excel-equivalent rounding ────────────────────────────────────────────────
def _floor(x: float, sig: float) -> float:
    if sig == 0:
        return x
    return math.floor(x / sig + 1e-9) * sig

def _ceil(x: float, sig: float) -> float:
    if sig == 0:
        return x
    return math.ceil(x / sig - 1e-9) * sig

def _mround(x: float, m: float) -> float:
    if m == 0:
        return x
    # Excel rounds halves away from zero
    return math.floor(x / m + 0.5) * m if x >= 0 else -math.floor(-x / m + 0.5) * m

def _ending_value(ending: str) -> float:
    try:
        return float(ending)
    except (TypeError, ValueError):
        return 0.0


# ── Inputs / outputs ─────────────────────────────────────────────────────────
@dataclass
class Item:
    name: str
    category: str
    role: str
    cost: float
    price: float
    monthly_units: int
    competitors: list = field(default_factory=list)


@dataclass
class Settings:
    currency: str = "USD"
    round_to: float = 0.10
    ending: str = ".00"
    max_raise: float = 0.10
    max_cut: float = -0.05
    shr_high: float = 1.0
    shr_med: float = 0.5
    shr_low: float = 0.25


@dataclass
class ItemResult:
    # identity
    name: str
    category: str
    role: str
    # economics
    cost: float
    price_from: float
    price_to: float
    delta_pct: float
    monthly_units: int
    # demand response
    elasticity: float
    source: str               # Estimated | Prior
    confidence: str           # HIGH | MEDIUM | LOW
    projected_units: float
    delta_profit_mo: float
    # classification
    quadrant: str             # Star | Plowhorse | Puzzle | Dog
    action: str               # Raise | Cut | Hold
    market: str               # Above/Within/Below market | No comp data
    phase: str                # Now | Pilot | Test
    narrative: str
    comp_min: Optional[float] = None
    comp_max: Optional[float] = None
    comp_avg: Optional[float] = None
    # sensitivity (per item, monthly Δ profit)
    sens_low: float = 0.0     # conservative (e×1.2)
    sens_base: float = 0.0
    sens_high: float = 0.0    # optimistic (e×0.8)
    # diagnostics
    role_cap_binding: bool = False
    role_floor_binding: bool = False


@dataclass
class QAResult:
    hard_fails: int
    soft_warns: int
    info: int
    ready: str                # "Ready" | "Fix first"
    items_missing_category: int
    items_missing_role: int
    items_cost_ge_price: int
    items_zero_units: int
    role_cap_binding: int
    role_floor_binding: int
    demo_mode: bool


@dataclass
class AuditResult:
    settings: Settings
    items: list[ItemResult]
    # headline
    monthly_lift: float
    baseline_profit_mo: float
    lift_pct: float
    changes_count: str
    confidence: str
    best_item: str
    # sensitivity totals
    sens_conservative: float
    sens_baseline: float
    sens_optimistic: float
    sens_robust: str          # "Yes" | "No"
    # governance
    qa: QAResult
    banner: Optional[str]
    # chart helpers
    med_units: float = 0.0
    med_margin_pct: float = 0.0


# ── threshold logic (OPTIMIZER R) ────────────────────────────────────────────
def _apply_threshold(q: float, currency: str, round_to: float) -> float:
    table = IDR_THRESHOLDS if currency in LARGE_DENOM else USD_THRESHOLDS
    margin = 1.0 if currency in LARGE_DENOM else 0.01
    # MATCH(q, thresholds, 1): largest threshold <= q
    matched = None
    for thr, buf in table:
        if thr <= q:
            matched = (thr, buf)
        else:
            break
    if matched is None:
        return q
    thr, buf = matched
    if thr < q <= thr + buf:
        return _floor(thr - margin, round_to)
    return q


# ── recommended price + charm (OPTIMIZER T) ──────────────────────────────────
def _recommend_price(F, R, role_cap, role_floor, s: Settings) -> float:
    cap_eff = min(role_cap, s.max_raise)
    floor_eff = max(role_floor, s.max_cut)
    hi = _floor(F * (1 + cap_eff), s.round_to)
    lo = _ceil(F * (1 + floor_eff), s.round_to)
    base = min(hi, max(lo, _mround(R, s.round_to)))

    ending = _ending_value(s.ending)
    charm_on = s.round_to <= 0.5 and ending > 0
    if not charm_on:
        return base

    # charm helpers (Y up, Z dn)
    y = _ceil(R - ending, 1) + ending
    z = _floor(R - ending, 1) + ending

    def in_bounds(v):
        return lo <= v <= hi

    direction = 1 if base > F else (-1 if base < F else 0)
    if direction > 0:
        if y >= F and in_bounds(y):
            return y
        if z > F and in_bounds(z):
            return z
        return base
    if direction < 0:
        if z <= F and in_bounds(z):
            return z
        if y < F and in_bounds(y):
            return y
        return base
    # flat: pick nearest charm to F that is in bounds
    if abs(y - F) <= abs(z - F):
        return y if in_bounds(y) else base
    return z if in_bounds(z) else base


# ── per-item optimize ────────────────────────────────────────────────────────
def _optimize_item(it: Item, cal: Optional[Calibration], s: Settings):
    F, E, G_month = it.price, it.cost, it.monthly_units
    G = G_month / 30.0  # daily qty

    # H elasticity + source + confidence
    prior = CATEGORY_PRIORS.get(it.category, CATEGORY_PRIORS[PRIOR_FALLBACK])[0]
    if cal is not None and cal.has_estimate:
        e, source, confidence = cal.elasticity, "Estimated", cal.confidence
    else:
        e, source, confidence = prior, "Prior", "LOW"

    role = ROLE_RULES.get(it.role, ROLE_RULES[ROLE_FALLBACK])

    # K Lerner P*
    is_test = not (e < -1)
    lerner = E * e / (e + 1) if not is_test else None

    # L shrinkage
    shrink = {"HIGH": s.shr_high, "MEDIUM": s.shr_med, "LOW": s.shr_low}[confidence]

    # M shrunk target
    if is_test:
        target = F * (1 + role["test"])
    else:
        target = F + shrink * (lerner - F)

    # P role clamp
    role_hi = F * (1 + role["cap"])
    role_lo = F * (1 + role["floor"])
    after_role = min(role_hi, max(role_lo, target))
    cap_binding = target > role_hi
    floor_binding = target < role_lo

    # Q global guard
    after_global = min(F * (1 + s.max_raise), max(F * (1 + s.max_cut), after_role))

    # R psychology threshold
    after_thr = _apply_threshold(after_global, s.currency, s.round_to)

    # T recommended price
    T = _recommend_price(F, after_thr, role["cap"], role["floor"], s)
    T = max(T, 0.0)

    # U delta %
    delta_pct = (T / F - 1) if F else 0.0

    # V projected demand, X monthly delta profit
    proj = G * (T / F) ** e if F > 0 else 0.0
    delta_daily = (T - E) * proj - (F - E) * G
    delta_month = delta_daily * 30.0

    # action
    if T > F:
        action = "Raise"
    elif T < F:
        action = "Cut"
    else:
        action = "Hold"

    return dict(
        e=e, source=source, confidence=confidence, T=T, delta_pct=delta_pct,
        proj_month=proj * 30.0, delta_month=delta_month, action=action,
        cap_binding=cap_binding, floor_binding=floor_binding,
    )


# ── menu engineering (MENU_ENGINEERING) ──────────────────────────────────────
def _menu_engineering(items: list[Item]):
    units = [it.monthly_units for it in items]
    margins = [(it.price - it.cost) / it.price if it.price > 0 else 0 for it in items]
    med_units = median(units) if units else 0
    med_margin = median(margins) if margins else 0

    out = {}
    for it, m in zip(items, margins):
        pop = "High" if it.monthly_units >= med_units else "Low"
        mar = "High" if m >= med_margin else "Low"
        if pop == "High" and mar == "High":
            quad, act = "Star", "Hold / protect leadership"
        elif pop == "High" and mar == "Low":
            quad, act = "Plowhorse", "Modest raise to capture margin"
        elif pop == "Low" and mar == "High":
            quad, act = "Puzzle", "Reposition / promote / test premium"
        else:
            quad, act = "Dog", "Consider removal or simplification"
        narrative = f"{quad} ({pop.lower()} volume, {mar.lower()} margin). {act}."
        out[it.name] = (quad, narrative)
    return out


# ── competitor positioning (COMPETITOR_BENCHMARK) ────────────────────────────
def _market_position(it: Item, rec_price: float):
    comps = [c for c in (it.competitors or []) if c and c > 0]
    if not comps:
        return "No comp data", None, None, None
    mn, mx = min(comps), max(comps)
    avg = sum(comps) / len(comps)
    if rec_price > mx * (1 + COMP_TOL_ABOVE):
        pos = "Above market"
    elif rec_price < mn * (1 - COMP_TOL_BELOW):
        pos = "Below market"
    else:
        pos = "Within market"
    return pos, mn, mx, avg


# ── sensitivity (SENSITIVITY) ────────────────────────────────────────────────
def _sensitivity(F, E, G_daily, T, e, mult) -> float:
    return (((T - E) * G_daily * (T / F) ** (e * mult)) - ((F - E) * G_daily)) * 30.0


# ── aggregate confidence ─────────────────────────────────────────────────────
def _aggregate_confidence(results: list[ItemResult]) -> str:
    movers = [r for r in results if r.action != "Hold"] or results
    if not movers:
        return "LOW"
    # profit-weighted vote; ties resolve downward (more conservative)
    weights = {"HIGH": 0.0, "MEDIUM": 0.0, "LOW": 0.0}
    for r in movers:
        weights[r.confidence] += abs(r.delta_profit_mo) + 1.0
    return max(("LOW", "MEDIUM", "HIGH"), key=lambda k: (weights[k], -["LOW", "MEDIUM", "HIGH"].index(k)))


# ── public entry point ───────────────────────────────────────────────────────
def run_audit(items: list[Item], settings: Settings,
              calibrations: Optional[dict[str, Calibration]] = None,
              demo_mode: bool = False) -> AuditResult:
    calibrations = calibrations or {}
    me = _menu_engineering(items)

    results: list[ItemResult] = []
    baseline_total = 0.0
    for it in items:
        cal = calibrations.get(it.name)
        opt = _optimize_item(it, cal, settings)
        quad, narrative = me[it.name]
        market, c_min, c_max, c_avg = _market_position(it, opt["T"])
        G = it.monthly_units / 30.0

        r = ItemResult(
            name=it.name, category=it.category, role=it.role,
            cost=it.cost, price_from=it.price, price_to=opt["T"],
            delta_pct=opt["delta_pct"], monthly_units=it.monthly_units,
            elasticity=opt["e"], source=opt["source"], confidence=opt["confidence"],
            projected_units=opt["proj_month"], delta_profit_mo=opt["delta_month"],
            quadrant=quad, action=opt["action"], market=market,
            phase=PHASE_BY_CONFIDENCE[opt["confidence"]],
            narrative=narrative,
            comp_min=c_min, comp_max=c_max, comp_avg=c_avg,
            role_cap_binding=opt["cap_binding"], role_floor_binding=opt["floor_binding"],
        )
        r.sens_low = _sensitivity(it.price, it.cost, G, opt["T"], opt["e"], SENS_CONSERVATIVE)
        r.sens_base = _sensitivity(it.price, it.cost, G, opt["T"], opt["e"], SENS_BASELINE)
        r.sens_high = _sensitivity(it.price, it.cost, G, opt["T"], opt["e"], SENS_OPTIMISTIC)
        results.append(r)
        baseline_total += (it.price - it.cost) * G * 30.0

    monthly_lift = sum(r.delta_profit_mo for r in results)
    lift_pct = (monthly_lift / baseline_total) if baseline_total else 0.0
    movers = sum(1 for r in results if r.action != "Hold")
    changes_count = f"{movers} of {len(results)}"
    confidence = _aggregate_confidence(results)
    best = max(results, key=lambda r: r.delta_profit_mo, default=None)
    best_item = best.name if best and best.delta_profit_mo > 0 else "—"

    sc = sum(r.sens_low for r in results)
    sb = sum(r.sens_base for r in results)
    so = sum(r.sens_high for r in results)
    robust = "Yes" if (sc >= 0 and sb >= 0 and so >= 0) else "No"

    # QA
    miss_cat = sum(1 for it in items if it.name and not it.category)
    miss_role = sum(1 for it in items if it.name and not it.role)
    cost_ge = sum(1 for it in items if it.name and it.price > 0 and it.cost >= it.price)
    zero_units = sum(1 for it in items if it.name and it.monthly_units == 0)
    cap_bind = sum(1 for r in results if r.role_cap_binding)
    floor_bind = sum(1 for r in results if r.role_floor_binding)
    hard = sum(1 for v in (miss_cat, miss_role, cost_ge, zero_units) if v > 0)
    soft = sum(1 for v in (cap_bind, floor_bind) if v > 0)
    qa = QAResult(
        hard_fails=hard, soft_warns=soft, info=0,
        ready="Ready" if hard == 0 else "Fix first",
        items_missing_category=miss_cat, items_missing_role=miss_role,
        items_cost_ge_price=cost_ge, items_zero_units=zero_units,
        role_cap_binding=cap_bind, role_floor_binding=floor_bind,
        demo_mode=demo_mode,
    )
    banner = None
    if hard > 0:
        banner = ("Data-quality warning — one or more hard checks are failing. "
                  "Review inputs before showing a client; headline numbers may mislead.")
    elif demo_mode:
        banner = "Demo mode active — running on synthetic data. Switch off before client delivery."

    me_units = [it.monthly_units for it in items]
    me_margins = [(it.price - it.cost) / it.price if it.price > 0 else 0 for it in items]
    med_u = median(me_units) if me_units else 0
    med_m = median(me_margins) if me_margins else 0

    return AuditResult(
        settings=settings, items=results,
        monthly_lift=monthly_lift, baseline_profit_mo=baseline_total, lift_pct=lift_pct,
        changes_count=changes_count, confidence=confidence, best_item=best_item,
        sens_conservative=sc, sens_baseline=sb, sens_optimistic=so, sens_robust=robust,
        qa=qa, banner=banner, med_units=med_u, med_margin_pct=med_m,
    )
