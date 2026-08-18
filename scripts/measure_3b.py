"""Sprint 3B's measurements. Three runs, and each one lands in a named document.

WHY THIS FILE EXISTS RATHER THAN A stdout NOTE. 3A's lesson, pointed the other
way: a published figure with no runnable source and a checked done-when whose
result lives only in a terminal scrollback are the same defect. Every number
this prints is one a document is about to claim.

WHY IT IS A SECOND FILE RATHER THAN AN EXTENSION OF measure_3a.py. Decided
before either run (remaining-sprints, 3B done-when). The two sprints measure
different objects -- 3A measured the path SET, 3B measures what a rung does to
it -- and 3A's IID arm is not a model this file should inherit by proximity. The
cost is named: `scripts/` remains a ninth artifact against a Definition of Done
that lists eight, and that item stays open for Sprint 10.

    uv run python scripts/measure_3b.py
    python scripts/measure_3b.py            # from the repo root

WHERE EACH NUMBER GOES
    1  toggle direction      ENGINE.md "Shock timing and size", and README
                             ## Results if the published sentence does not hold
    2  shock magnitude       README ## Scope & Branches, beside block length
    3  D-22 reproduction     DECISIONS D-22's measured line
"""

import sys
import pathlib

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import engine          # noqa: E402
import tax             # noqa: E402

N_PATHS = 2_000        # D-41. Same count the cube uses
SEED = 20_260_815      # D-41
LOW_STOPS = tuple(i < 3 for i in range(10))     # D-33 band 1-3
MID_STOPS = tuple(i < 6 for i in range(10))     # D-32 default -- the archetype
HIGH_STOPS = tuple(i < 10 for i in range(10))   # D-33 band 7-10


def rung(stops):
    return engine.Profile(income_points=engine.ARCHETYPE.income_points, stops=stops)


LOW, MID, HIGH = rung(LOW_STOPS), rung(MID_STOPS), rung(HIGH_STOPS)


def banner(n, title, lands_in):
    print()
    print("=" * 78)
    print(f"{n}. {title}")
    print(f"   -> {lands_in}")
    print("=" * 78)


def terminal_p10(profile, paths, shocks, account, rate):
    """10th percentile of the after-tax terminal distribution. Objective 4."""
    after_tax, _ = engine._outcome_paths(
        profile, shocks, None, paths, rate, account
    )
    return float(np.percentile(after_tax, 10))


def accumulated(profile, paths, shocks):
    accs = engine._accumulations(profile, paths, shocks)
    return np.array([a.trad for a in accs]), np.array([a.roth for a in accs])


# =============================================================================
def measure_toggle(paths):
    """DOES SHOCK PLACEMENT MOVE THE TAIL, AND IN WHICH DIRECTION.

    ENGINE.md asserts flatly that flipping the toggle "deflates the tail
    visibly" and calls it the cheapest demonstration in the project. The 3B
    done-when hedges the same claim. They cannot both be right, and the plan is
    the one that learned from D-05 -- where a named fudge factor's stated reason
    failed measurement and the failure was written down rather than the reason
    quietly rewritten.

    So: report the direction measured. DO NOT TUNE THE TOGGLE UNTIL IT AGREES
    WITH THE SENTENCE. If it does not deflate, ENGINE.md's sentence changes and
    the README's ## Results takes a third entry. That is a finding, not a
    failure.

    KNOW BEFORE READING THE OUTPUT (D-05, R8): the block-vs-IID comparison has
    already run against the real series and block does NOT fatten the tail. The
    toggle's job is therefore narrower than it was written -- it demonstrates
    that PLACEMENT matters, not that the return model does.
    """
    banner(1, "UNCORRELATED TOGGLE -- does placement move the 10th percentile?",
           'ENGINE.md "Shock timing and size"; README ## Results if it flips')
    original = engine.SHOCK_PLACEMENT
    rows = []
    try:
        for placement in ("correlated", "uncorrelated"):
            engine.SHOCK_PLACEMENT = placement
            engine._ACCUMULATION_CACHE.clear()
            for shocks in (1, 3):
                trad_65, _ = accumulated(LOW, paths, shocks)
                rows.append((
                    placement, shocks,
                    float(np.percentile(trad_65, 10)),
                    float(np.median(trad_65)),
                    terminal_p10(LOW, paths, shocks, "trad", LOW.t_now),
                ))
    finally:
        engine.SHOCK_PLACEMENT = original
        engine._ACCUMULATION_CACHE.clear()

    print(f"{'placement':<14}{'shocks':>7}{'trad_65 p10':>16}{'trad_65 med':>16}"
          f"{'after-tax p10':>16}")
    for p, s, p10, med, t10 in rows:
        print(f"{p:<14}{s:>7}{p10:>16,.0f}{med:>16,.0f}{t10:>16,.0f}")

    print()
    for shocks in (1, 3):
        c = next(r for r in rows if r[0] == "correlated" and r[1] == shocks)
        u = next(r for r in rows if r[0] == "uncorrelated" and r[1] == shocks)
        delta = (c[2] - u[2]) / abs(u[2]) if u[2] else float("nan")
        verdict = ("correlated placement DEFLATES the tail"
                   if c[2] < u[2] else
                   "correlated placement does NOT deflate the tail")
        print(f"  {shocks} shock(s): trad_65 p10 correlated {c[2]:,.0f} vs "
              f"uncorrelated {u[2]:,.0f}  ({delta:+.2%})")
        print(f"             -> {verdict}")
    print()
    print("  Both numbers are recorded whichever way this went (3B done-when).")


# =============================================================================
def measure_shock_magnitude(paths):
    """CUT LADDER ITEM 2, 3B's HALF. It gates nothing and it is the first thing
    to drop on an overrun -- so if you are reading this under time pressure,
    this is the run to skip and the README row reverts from *measured* to *what
    it would take*.

    $40,000 is a named fudge factor (D-39), chosen at 1.6x a contribution year
    so the forced sale and the skipped contribution are the same order of
    magnitude. This is the same treatment block length gets at 3A.
    """
    banner(2, "SHOCK MAGNITUDE SENSITIVITY -- $25,000 and $80,000 against $40,000",
           "README ## Scope & Branches, beside the block-length row")
    original = engine.SHOCK_AMOUNT
    base = None
    try:
        for amount in (25_000, 40_000, 80_000):
            engine.SHOCK_AMOUNT = amount
            engine._ACCUMULATION_CACHE.clear()
            trad_65, roth_65 = accumulated(LOW, paths, 3)
            sale = engine.forced_sale_gross(
                LOW.income(55),
                tax.contribution(LOW.income(55), LOW.savings_rate),
                LOW.state_while_working,
                amount,
            )
            med = float(np.median(trad_65))
            if amount == 40_000:
                base = med
            print(f"  ${amount:>6,}  gross sale at 55 ${sale:>10,.2f}  "
                  f"trad_65 median ${med:>12,.0f}  "
                  f"roth_65 median ${float(np.median(roth_65)):>12,.0f}")
    finally:
        engine.SHOCK_AMOUNT = original
        engine._ACCUMULATION_CACHE.clear()
    print()
    print(f"  Deltas are taken against the $40,000 base of ${base:,.0f}.")
    print("  The gross sale is superlinear in the net amount, because the")
    print("  withdrawal climbs the bracket table as it grows (D-16's PIN).")


# =============================================================================
def reproduce_d22_low_ratios():
    """D-22 PUBLISHES TWO LOW RATIOS WITH NO RUNNABLE SOURCE IN THIS REPO.

    "Measured on a constant-return path, roth/trad holds at 0.675000000000 for
    Mid and High at 0, 1 and 3 shocks, and moves to 0.689633 and 0.708591 at
    Low." The first three reproduce exactly. The last two do not, and this
    identifies what produced them rather than shrugging at the gap.

    The search is over every (shock year, gross-up rule) pair. Exactly one
    combination lands on 0.689633: a FLAT `t_now` gross-up with the shock at
    year 9 -- which is the reading D-16's PIN was written to reject, and which
    independently corroborates D-16's own flat-reading table, measured in the
    same gate-two pass.

    So D-22's pair is stale for a known reason. The values that replace it are
    printed below and they have a source: this function.
    """
    banner(3, "D-22's PUBLISHED LOW RATIOS -- reproduce, or identify what made them",
           "DECISIONS D-22, the measured line")
    path = engine.make_paths("constant", 1, LOW.n_years, 0.07)[0]
    n_acc = LOW.n_accumulation_years
    published = {1: 0.689633, 3: 0.708591}

    print("  Mid and High, the three that DO reproduce:")
    for profile in (MID, HIGH):
        for shocks in (0, 1, 3):
            a = engine.accumulate(profile, path, shocks=shocks)
            print(f"    {profile.rung:<5} {shocks} shocks  "
                  f"roth/trad {a.roth / a.trad:.12f}   "
                  f"1 - t_now {1 - a.t_now:.12f}")

    print()
    print("  Low, under this sprint's decided rules (D-45/D-46/D-47):")
    for shocks in (1, 3):
        a = engine.accumulate(LOW, path, shocks=shocks)
        print(f"    {shocks} shocks  roth/trad {a.roth / a.trad:.6f}   "
              f"D-22 published {published[shocks]:.6f}   "
              f"MISMATCH {a.roth / a.trad - published[shocks]:+.6f}")

    def ratio_at(year, withdrawal):
        trad = roth = 0.0
        for i in range(n_acc):
            c_trad, c_roth = engine.contributions(LOW, LOW.current_age + i)
            trad = trad * 1.07 + c_trad
            roth = roth * 1.07 + c_roth
            if i == year:
                trad -= withdrawal(LOW.current_age + i)
                roth -= 40_000.0
        return roth / trad

    rules = {
        "D-47 exact (this sprint)": lambda age: engine.forced_sale_gross(
            LOW.income(age),
            tax.contribution(LOW.income(age), LOW.savings_rate), True, 40_000.0),
        "exact, base = gross income": lambda age: engine.forced_sale_gross(
            LOW.income(age), 0.0, True, 40_000.0),
        "flat t_now 32.5%": lambda age: 40_000.0 / (1 - 0.10 - 0.325),
        "flat federal 24%": lambda age: 40_000.0 / (1 - 0.10 - 0.24),
        "flat marginal at income": lambda age: 40_000.0 / (
            1 - 0.10 - tax.marginal_rate(LOW.income(age))),
    }

    print()
    print("  Which (year, rule) pair produces D-22's 1-shock 0.689633?")
    for name, rule in rules.items():
        hits = [(abs(ratio_at(y, rule) - published[1]), y, ratio_at(y, rule))
                for y in range(n_acc)]
        err, year, value = min(hits)
        flag = "  <== EXACT" if err < 1e-6 else ""
        print(f"    {name:<28} closest year {year:>2} (age {LOW.current_age + year})"
              f" -> {value:.6f}   err {err:.2e}{flag}")

    print()
    print("  READING: the published pair was taken with the FLAT t_now gross-up")
    print("  that D-16's PIN rejects, at a scattered year. It is stale for a")
    print("  known reason, not wrong for an unknown one. D-22's measured line")
    print("  is corrected to the values above and cites this file.")


# =============================================================================
def main():
    print("Sprint 3B measurements --", f"n_paths={N_PATHS}, seed={SEED}")
    print("Placement:", engine.SHOCK_PLACEMENT,
          "| shock:", f"${engine.SHOCK_AMOUNT:,}",
          "| block length:", engine.BLOCK_LENGTH)
    paths = engine.make_paths("block", N_PATHS, engine.ARCHETYPE.n_years, seed=SEED)
    print("Digest:", engine.paths_digest(paths), "(D-41; must match 3A's)")

    measure_toggle(paths)
    measure_shock_magnitude(paths)
    reproduce_d22_low_ratios()

    print()
    print("=" * 78)
    print("Every number above belongs to a document. Copy it there before you")
    print("close the terminal -- that is the whole reason this file exists.")
    print("=" * 78)


if __name__ == "__main__":
    main()
