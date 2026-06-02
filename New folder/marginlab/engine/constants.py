"""
marginlab.engine.constants
───────────────────────────────────────────────────────────────────────────
Faithful extraction of the MarginLab_Pricing_Lab_v10.xlsx model constants.
Every value here is lifted verbatim from the workbook so the native engine
reproduces the spreadsheet's numbers exactly.

Source sheets:
  CATEGORY_PRIORS!A6:E14    -> CATEGORY_PRIORS
  PSYCHOLOGY_RULES!A7:F13   -> ROLE_RULES
  PSYCHOLOGY_RULES!A20:E27  -> USD_THRESHOLDS / IDR_THRESHOLDS
  SETTINGS!B4:B16           -> DEFAULT_SETTINGS
  SENSITIVITY!B5:B7         -> SENS_MULTIPLIERS
  COMPETITOR_BENCHMARK!B5:B6-> COMP_TOLERANCE
"""

# ── Category elasticity priors (CATEGORY_PRIORS) ─────────────────────────────
# category -> (prior_elasticity, sensitivity_tier, note)
CATEGORY_PRIORS = {
    "Coffee":         (-1.10, "Moderate",  "Daily routine; competitive market."),
    "Specialty Drink":(-1.30, "Sensitive", "Substitutes within drink menu."),
    "Tea":            (-1.00, "Moderate",  "Comparable to coffee but lower volume."),
    "Pastry":         (-0.90, "Inelastic", "Often impulse-bought as an add-on."),
    "Dessert":        (-1.00, "Moderate",  "Special occasion items."),
    "Sandwich/Food":  (-0.80, "Inelastic", "Brunch and food less substitutable."),
    "Bundle":         (-0.95, "Moderate",  "Treat as basket; cross effects apply."),
    "Complement":     (-0.70, "Inelastic", "Sides, add-ons; basket effect dominates."),
    "Other":          (-1.10, "Moderate",  "Fallback when category is unspecified."),
}
PRIOR_FALLBACK = "Other"

# Categories exposed in the UI (input dropdown)
CATEGORIES = [
    "Coffee", "Specialty Drink", "Tea", "Pastry", "Dessert",
    "Sandwich/Food", "Bundle", "Complement", "Other",
]

# ── Role rules (PSYCHOLOGY_RULES) ────────────────────────────────────────────
# role -> dict(cap, floor, test_increment, description, default_action)
ROLE_RULES = {
    "Traffic Driver": dict(cap=0.03, floor=-0.05, test=0.00,
                           desc="Sharp entry price that signals fairness. Protect.",
                           default="Hold"),
    "Core":           dict(cap=0.06, floor=-0.05, test=0.02,
                           desc="High-volume standard item. Moderate moves OK.",
                           default="Small test raise"),
    "Profit Driver":  dict(cap=0.10, floor=-0.05, test=0.05,
                           desc="High-margin item that can carry most of the gain.",
                           default="Modest test raise"),
    "Premium Anchor": dict(cap=0.10, floor=-0.05, test=0.05,
                           desc="Expensive reference point; protect premium feel.",
                           default="Modest test raise"),
    "Signature":      dict(cap=0.10, floor=-0.05, test=0.05,
                           desc="Brand-defining item; can carry premium pricing.",
                           default="Modest test raise"),
    "Complement":     dict(cap=0.07, floor=-0.05, test=0.03,
                           desc="Side/add-on; basket effect dominates.",
                           default="Small test raise"),
    "Other":          dict(cap=0.05, floor=-0.05, test=0.02,
                           desc="Unspecified role — conservative default.",
                           default="Small test raise"),
}
ROLE_FALLBACK = "Other"
ROLES = list(ROLE_RULES.keys())

# ── Psychology thresholds (PSYCHOLOGY_RULES) ─────────────────────────────────
# Each entry: (threshold_price, buffer). A price landing just above a threshold
# (within buffer) is pulled back below it.
USD_THRESHOLDS = [
    (1, 0.2), (2, 0.2), (5, 0.2), (10, 0.3),
    (15, 0.3), (20, 0.4), (50, 0.5), (100, 1.0),
]
IDR_THRESHOLDS = [
    (5000, 500), (10000, 500), (15000, 500), (25000, 1000),
    (50000, 1500), (75000, 2000), (100000, 3000), (150000, 4000),
]

# ── Currency handling ────────────────────────────────────────────────────────
# Large-denomination currencies disable charm endings and use IDR-style thresholds.
LARGE_DENOM = {"IDR", "JPY", "VND"}
CURRENCIES = ["USD", "EUR", "GBP", "AUD", "CAD", "IDR", "JPY", "MYR", "PHP", "THB", "VND"]
ROUND_STEPS_SMALL = [0.01, 0.05, 0.10, 0.50, 1.00]
ROUND_STEPS_LARGE = [500, 1000, 5000]
ENDINGS = [".00", ".50", ".90", ".95", ".99"]

CURRENCY_SYMBOL = {
    "USD": "$", "EUR": "€", "GBP": "£", "AUD": "A$", "CAD": "C$",
    "IDR": "Rp", "JPY": "¥", "MYR": "RM", "PHP": "₱", "THB": "฿", "VND": "₫",
}

# ── Default settings (SETTINGS) ──────────────────────────────────────────────
DEFAULT_SETTINGS = dict(
    currency="USD",
    round_to=0.10,
    ending=".00",
    max_raise=0.10,
    max_cut=-0.05,
    shr_high=1.0,
    shr_med=0.5,
    shr_low=0.25,
    use_sample=False,          # cfg_use_sample "Yes"/"No"
)

# ── Sensitivity multipliers (SENSITIVITY) ────────────────────────────────────
SENS_CONSERVATIVE = 1.2   # elasticity scaled UP -> demand more responsive
SENS_BASELINE = 1.0
SENS_OPTIMISTIC = 0.8

# ── Competitor tolerance (COMPETITOR_BENCHMARK) ──────────────────────────────
COMP_TOL_ABOVE = 0.20
COMP_TOL_BELOW = 0.20

# ── Calibration thresholds (CALIBRATION) ─────────────────────────────────────
CAL_MIN_OBS_ESTIMATE = 10   # below this, no elasticity estimate -> prior
CAL_MIN_OBS_HIGH = 30       # below this, confidence forced to LOW
CAL_Z = 1.96                # 95% CI

# ── Confidence -> shrinkage / rollout phase ──────────────────────────────────
PHASE_BY_CONFIDENCE = {"HIGH": "Now", "MEDIUM": "Pilot", "LOW": "Test"}
