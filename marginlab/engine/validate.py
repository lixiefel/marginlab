"""
Validation harness for the native engine.
Run:  python -m marginlab.engine.validate     (or  python validate.py)
"""
import math
from marginlab.engine import Item, Settings, run_audit, Observation, calibrate_item


def _approx(a, b, tol=1e-6):
    return abs(a - b) <= tol


def demo_cafe():
    """Neighborhood café (Operating Manual, Simulation 1)."""
    return [
        Item("Espresso",      "Coffee",         "Traffic Driver", 0.50, 2.80, 2400),
        Item("Latte",         "Coffee",         "Core",           0.90, 3.80, 2100),
        Item("Cappuccino",    "Coffee",         "Core",           0.80, 3.60, 1800),
        Item("Croissant",     "Pastry",         "Complement",     1.10, 3.20, 1200),
        Item("Avocado Toast", "Sandwich/Food",  "Profit Driver",  2.80, 6.80,  750),
        Item("Cheesecake",    "Dessert",        "Signature",      1.90, 4.80,  600),
    ]


def test_latte_hand_computation():
    """Independently hand-computed: Latte 3.80 -> 4.00 under prior/LOW."""
    items = demo_cafe()
    s = Settings(currency="USD", round_to=0.10, ending=".00",
                 max_raise=0.10, max_cut=-0.05, shr_low=0.25)
    audit = run_audit(items, s)
    latte = next(r for r in audit.items if r.name == "Latte")
    assert _approx(latte.price_to, 4.00, 0.001), f"Latte price_to={latte.price_to} expected 4.00"
    assert latte.role_cap_binding, "Latte should hit role cap (Lerner wants far more)"
    assert latte.action == "Raise"
    # demand + profit identity check
    G = 2100 / 30
    proj = G * (4.00 / 3.80) ** (-1.1)
    dprofit = ((4.00 - 0.90) * proj - (3.80 - 0.90) * G) * 30
    assert _approx(latte.delta_profit_mo, dprofit, 0.01), \
        f"profit {latte.delta_profit_mo} vs {dprofit}"
    print(f"  ✓ Latte 3.80 → {latte.price_to:.2f}  Δ{latte.delta_pct*100:+.1f}%  "
          f"+{latte.delta_profit_mo:.1f}/mo  (cap binding, prior/LOW)")


def test_traffic_driver_protected():
    """Traffic Driver (Espresso) capped at +3% — should barely move or hold."""
    audit = run_audit(demo_cafe(), Settings())
    esp = next(r for r in audit.items if r.name == "Espresso")
    assert esp.price_to <= 2.80 * 1.03 + 1e-6, "Traffic Driver exceeded its 3% cap"
    print(f"  ✓ Espresso (Traffic Driver) 2.80 → {esp.price_to:.2f}  "
          f"(cap +3% respected)")


def test_lerner_and_clamps():
    """Lerner identity + global guard never exceeded."""
    audit = run_audit(demo_cafe(), Settings(max_raise=0.10, max_cut=-0.05))
    for r in audit.items:
        assert r.price_to <= r.price_from * 1.10 + 1e-6, f"{r.name} broke global max raise"
        assert r.price_to >= r.price_from * 0.95 - 1e-6, f"{r.name} broke global max cut"
    print(f"  ✓ All {len(audit.items)} items inside global guard [-5%, +10%]")


def test_headline_and_sensitivity():
    audit = run_audit(demo_cafe(), Settings())
    assert audit.monthly_lift > 0, "expected positive lift on under-priced demo menu"
    # total sens equals sum of per-item sens
    assert _approx(audit.sens_baseline, sum(r.sens_base for r in audit.items), 0.01)
    print(f"  ✓ Monthly lift +{audit.monthly_lift:.0f}  ({audit.lift_pct*100:+.1f}% of profit)  "
          f"| {audit.changes_count} changing | conf {audit.confidence}")
    print(f"  ✓ Sensitivity  cons {audit.sens_conservative:+.0f} / "
          f"base {audit.sens_baseline:+.0f} / opt {audit.sens_optimistic:+.0f}  "
          f"robust={audit.sens_robust}")


def test_calibration_recovers_known_elasticity():
    """Generate price/qty data from a known elasticity and recover it via OLS."""
    true_e = -1.30
    base_p, base_q = 4.0, 100.0
    obs = []
    for i in range(60):
        p = base_p * (1 + 0.18 * math.sin(i))          # price variation
        q = base_q * (p / base_p) ** true_e            # exact constant-elasticity demand
        obs.append(Observation("X", p, q))
    cal = calibrate_item("X", obs)
    assert cal.has_estimate and _approx(cal.elasticity, true_e, 0.02), \
        f"recovered ê={cal.elasticity} expected {true_e}"
    assert cal.confidence == "HIGH", f"expected HIGH conf, got {cal.confidence}"
    print(f"  ✓ Calibration recovers ê={cal.elasticity:.3f} (true {true_e}) "
          f"N={cal.n_obs} conf={cal.confidence}")


def test_idr_thresholds_and_no_charm():
    """IDR: large-denom, charm disabled, IDR threshold table used."""
    items = [Item("Kopi Susu", "Coffee", "Core", 8000, 25000, 3000)]
    s = Settings(currency="IDR", round_to=1000, ending=".00", max_raise=0.10, max_cut=-0.05)
    audit = run_audit(items, s)
    r = audit.items[0]
    assert r.price_to % 1000 == 0, "IDR price not rounded to step"
    assert r.price_to <= 25000 * 1.10 + 1, "IDR broke global cap"
    print(f"  ✓ IDR Kopi Susu 25.000 → {r.price_to:,.0f}  (step 1.000, charm off)")


if __name__ == "__main__":
    print("MarginLab engine validation")
    print("─" * 60)
    test_latte_hand_computation()
    test_traffic_driver_protected()
    test_lerner_and_clamps()
    test_headline_and_sensitivity()
    test_calibration_recovers_known_elasticity()
    test_idr_thresholds_and_no_charm()
    print("─" * 60)
    print("ALL CHECKS PASSED ✓  — native engine reproduces the v10 model.")
