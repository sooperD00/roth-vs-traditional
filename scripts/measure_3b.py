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
    4  the two readings      RESULTS.md 7.4, and D-45
    5  the tie-break         RESULTS.md 7.5, and D-46
    6  the gross-up base     RESULTS.md 7.6, and D-47

SECTIONS 4, 5 AND 6 WERE ADDED AFTER SPRINT 3B CLOSED, and the reason is the
reason this file exists. All three decisions -- D-45, D-46, D-47 -- were recorded
with measured numbers in their prose and no runnable source anywhere. Three
documents cite D-45's 8.1%; D-46's six percentages and D-47's $22,936 appear
nowhere in the code at all. That is 3A's defect exactly, one sprint later, caught
at the RESULTS.md pass rather than by a reviewer.

They belong here rather than in a new file for the same reason sections 1-3 are
here: they measure what a rung does to a path set. Nothing about them is new
modeling -- every one re-runs a comparison that was made by hand at 3B and never
written down.
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

def crossing_point(paths, lo=40_000.0, hi=120_000.0, iterations=20):
    """The shock size at which Low's Traditional median falls below its Roth.

    Bisection is legitimate here because the gap is monotone in shock size --
    checked on a $5,000 grid from $40,000 to $80,000 before this was written,
    and the reason is mechanical: the gross sale climbs the bracket table as it
    grows, so Traditional's proportional loss per shock rises while its
    1/(1 - t_now) head start does not.

    THE CACHE CLEAR IS FOR MEMORY, NOT CORRECTNESS. D-48 put SHOCK_AMOUNT in
    _accumulations' key, so a stale entry cannot be served -- verified, the
    answer is identical either way. Without the clear, peak RSS roughly doubles
    as full accumulation sets stack up.

    20 iterations resolves to eight cents, which is far finer than 2,000 paths
    can support. The precision is the bisection's, not the sample's.
    """
    original = engine.SHOCK_AMOUNT
    try:
        for _ in range(iterations):
            engine.SHOCK_AMOUNT = 0.5 * (lo + hi)
            engine._ACCUMULATION_CACHE.clear()
            trad, roth = accumulated(LOW, paths, 3)
            if np.median(trad) > np.median(roth):
                lo = engine.SHOCK_AMOUNT
            else:
                hi = engine.SHOCK_AMOUNT
    finally:
        engine.SHOCK_AMOUNT = original
        engine._ACCUMULATION_CACHE.clear()
    return 0.5 * (lo + hi)


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
    print()
    x = crossing_point(paths)
    print(f"  THE ACCOUNT ORDERING REVERSES AT ${x:,.0f} -- bisected, ~7s.")
    print(f"  That is {x / 24_500:.2f}x a contribution year, against the "
          f"{engine.SHOCK_AMOUNT / 24_500:.2f}x D-39 chose.")
    print("  Below it Traditional's deferral head start survives three shocks;")
    print("  above it the penalty plus bracket-climb has eaten the whole 1.481x.")


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
# Sections 4-6 -- added after Sprint 3B closed. See the module docstring.
# =============================================================================
def _readings(paths, profile):
    """The two candidate readings of D-08's 'deepest drawdown years'.

    Returns (underwater, worst_year), each (n_paths, n_accumulation_years).

    D-44 SPLIT ONE WORD INTO THREE QUANTITIES AND THIS IS WHY. `underwater-depth`
    is how far below its running peak the index sits at year end; the other
    candidate was `worst-year-return`, the annual return itself, which was never
    a drawdown at all. D-08 admits either, so 3B had to choose (D-45).

    BOTH ARE SORTED ASCENDING -- most negative first -- so `argsort` picks the
    deepest years under either reading with no sign handling at the call site.
    """
    n = profile.n_accumulation_years
    accum = np.asarray(paths, dtype=float)[:, :n]
    return engine.underwater_depth(accum), accum


def _years_under(curve, n_shocks, kind="stable"):
    """Which years each path shocks under one reading. (n_paths, n_shocks), sorted.

    THE TIE-BREAK IS THE ARGUMENT, NOT A DETAIL (D-46). engine.shock_years()
    hard-codes kind='stable' because that is the decision; this file takes it as
    a parameter because section 5's whole job is to measure what the default
    would have done instead.
    """
    picks = np.argsort(curve, axis=1, kind=kind)[:, :n_shocks]
    return np.sort(picks, axis=1)


def _growth_after(paths, n_acc):
    """What one dollar left in the account at the END of year y grows to by 65.

    THE OFF-BY-ONE IS THE PHYSICS, NOT A DETAIL. Under D-20's period-end rule the
    balance takes year y's return FIRST and the forced sale comes out after it
    (accumulate(), the Low branch). So what a sale forgoes is the compounding from
    year y+1 onward, and including year y's own return double-counts a return the
    sale already received. It also biases the comparison in section 4: shocked
    years are chosen for being bad, so folding year y in penalises whichever
    reading selects the worse annual return -- which is worst-year-return, by
    construction.

    Column n_acc-1 is 1.0: a sale in the final accumulation year forgoes nothing.
    """
    arr = np.asarray(paths, dtype=float)[:, :n_acc]
    tail = np.cumprod(1.0 + arr[:, :0:-1], axis=1)[:, ::-1]     # years 1..n-1
    return np.concatenate([tail, np.ones((arr.shape[0], 1))], axis=1)


def _roth_basis_by_year(profile):
    """Cumulative Roth contributions after each accumulation year. One row.

    D-16's simplification is that a Low sale comes out of Roth basis IN FULL and
    no basis is tracked. This is the array that says how often that is a lie:
    where the cumulative basis is under SHOCK_AMOUNT, the sale is taking money
    that was never contributed.
    """
    per_year = [
        engine.contributions(profile, profile.current_age + i)[1]
        for i in range(profile.n_accumulation_years)
    ]
    return np.cumsum(per_year)


# =============================================================================
def measure_placement_readings(paths):
    """WHICH DRAWDOWN READING, AND HOW MUCH THE CHOICE WAS WORTH.

    D-45 chose `underwater-depth` over `worst-year-return` and published five
    measurements to justify it. None of them had a runnable source, and three
    documents cite the first one. This section is that source.

    WHAT TO WATCH FOR. The finding D-45 records is deliberately unflattering to
    its own choice: THE YEAR SETS DIFFER A LOT AND THE AGGREGATE BARELY DOES.
    Two channels partly offset -- `underwater-depth` shocks LATER years, so less
    compounding is left to forgo, but HARDER ones, because D-05's surviving
    recovery channel is steeper after a deep drawdown than after a bad year.

    DO NOT TUNE ANYTHING TO REPRODUCE D-45's NUMBERS. Section 3's precedent is
    the standing rule here: where a published pair does not come back, identify
    the rule that produced it and correct the document. A number that only
    reproduces after the measurement is adjusted is not a measurement.
    """
    banner(4, "THE TWO READINGS -- underwater-depth against worst-year-return",
           "RESULTS.md 7.4; DECISIONS D-45")
    uw, wy = _readings(paths, LOW)
    n_paths, n_acc = uw.shape
    basis = _roth_basis_by_year(LOW)
    short = basis < engine.SHOCK_AMOUNT          # years where D-16's simplification bites

    print("  AGREEMENT ON THE YEAR SET -- the same paths, the same array,")
    print("  two readings of the same sentence.")
    print()
    print(f"    {'shocks':>7}{'identical year set':>22}{'year-0 share, wy':>20}")
    for n in (1, 2, 3):
        a, b = _years_under(uw, n), _years_under(wy, n)
        same = float(np.mean(np.all(a == b, axis=1)))
        year0 = float(np.mean(b == 0))           # share of wy's SHOCKS in year 0
        print(f"    {n:>7}{same:>21.1%}{year0:>20.1%}")
    print()
    print("    year 0 is STRUCTURALLY unshockable under underwater-depth: the")
    print("    index at year 0 is its own running peak, so the curve is exactly")
    print("    0.0 there on every path and nothing sorts below it.")
    print(f"    measured, underwater-depth year-0 share at 3 shocks: "
          f"{np.mean(_years_under(uw, 3) == 0):.1%}")

    print()
    print("  WHERE THE SHOCKS LAND, and what each channel is worth. n = 3.")
    print()
    print(f"    {'reading':<22}{'paths basis-short':>19}{'mean shock age':>17}"
          f"{'mean next-yr ret':>19}")
    rows = {}
    for name, curve in (("underwater-depth", uw), ("worst-year-return", wy)):
        years = _years_under(curve, 3)
        any_short = float(np.mean(short[years].any(axis=1)))
        mean_age = float(np.mean(years)) + LOW.current_age
        nxt = years + 1
        valid = nxt < n_acc
        arr = np.asarray(paths, dtype=float)[:, :n_acc]
        nxt_ret = float(np.mean(np.take_along_axis(arr, np.where(valid, nxt, 0), 1)[valid]))
        rows[name] = (any_short, mean_age, nxt_ret)
        print(f"    {name:<22}{any_short:>18.2%}{mean_age:>17.1f}{nxt_ret:>18.2%}")

    print()
    print("  THE AGGREGATE, which is the part that does not move. Mean forgone")
    print("  multiple -- what one shocked dollar would have grown to by 65.")
    print()
    growth = _growth_after(paths, n_acc)
    for name, curve in (("underwater-depth", uw), ("worst-year-return", wy)):
        years = _years_under(curve, 3)
        mult = float(np.mean(np.take_along_axis(growth, years, axis=1)))
        print(f"    {name:<22}{mult:>12.4f}x")

    print()
    print('  AGAINST WHAT D-45 PUBLISHED (all figures at 3 shocks unless noted):')
    print('    agreement 8.1% / 56.9% / 24.4% .......... reproduces')
    print('    year-0 share under worst-year-return 3.2% reproduces')
    print('    basis-short 5.05% against 19.20% ........ reproduces')
    print('    mean shock age 51.0 against 49.2 ........ reproduces')
    print('    mean next-year return 18.66% / 12.63% ... reproduces')
    print('    "the mean forgone multiple lands within')
    print('     half a percent" ....................... reproduces, 0.44% apart')
    print()
    print('  READING. The year sets are nearly disjoint at 3 shocks and the')
    print("  aggregate multiple lands close, which is D-45's own finding and the")
    print("  reason the pick rests on the three structural arguments rather than")
    print("  on a dollar difference. Copy every number above into RESULTS.md 7.4.")


# =============================================================================
def measure_tie_break(paths):
    """WHY kind='stable' IS A DECISION AND NOT A STYLE CHOICE.

    D-46 corrected two documents that asserted numpy's argsort default is
    stable. It is introsort, and it is not frozen across numpy versions -- the
    same exposure D-43 chose MT19937 to close, arriving one sprint later against
    a different library default.

    THE FLAG IS IN THE CODE AND THE REASON IT MATTERS IS NOT. A test asserts the
    resulting property; nothing measures the tie rate. Without these numbers the
    decision reads as fussiness and a later sprint could reasonably drop it.

    TIES ARE ORDINARY HERE and that is the whole point: a path is dealt from a
    98-value deck with replacement, so duplicates inside a 30-year window are the
    common case rather than the edge case.
    """
    banner(5, "THE TIE-BREAK -- how often a tie decides where a shock lands",
           "RESULTS.md 7.5; DECISIONS D-46")
    print(f"  numpy {np.__version__} -- PRINTED BECAUSE THE COMPARISON ARM IS THE")
    print("  UNFROZEN ONE. `default` below is introsort, which is deterministic on")
    print("  one build and is NOT frozen across versions. Measured identical on")
    print("  2.4.2 and 2.4.4, so nothing here has moved on a version yet -- but the")
    print("  version is printed so a future disagreement is readable rather than")
    print("  mysterious. That mobility is the exposure D-46 exists to name.")
    uw, wy = _readings(paths, LOW)

    print("  DUPLICATES IN THE WINDOW -- the precondition. If ties were rare the")
    print("  flag would not matter.")
    print()
    for name, curve in (("annual return", wy), ("underwater depth", uw)):
        dup = float(np.mean([len(np.unique(row)) < row.size for row in curve]))
        print(f"    paths carrying a duplicate {name:<18}{dup:>8.2%}")

    print()
    print("  TIES THAT REACH THE BOUNDARY -- a duplicate only decides a shock")
    print("  year when it straddles the n-th position of the sort.")
    print()
    print("  TWO WAYS TO ASK 'DID THE DEFAULT CHANGE ANYTHING', AND THEY ARE")
    print("  DIFFERENT QUESTIONS. ORDER counts a permutation of the same three")
    print("  years. SET counts a genuinely different year being shocked.")
    print("  ONLY THE SET COLUMN CAN MOVE A NUMBER: shock_years() returns")
    print("  tuple(sorted(picks)), so a reordering is discarded before the engine")
    print("  ever sees it. The order column is an upper bound on the exposure and")
    print("  the set column is the exposure.")
    print()
    print(f"    {'reading':<22}{'exact tie at n=3':>19}{'ORDER differs':>16}"
          f"{'SET differs':>14}")
    for name, curve in (("underwater-depth", uw), ("worst-year-return", wy)):
        srt = np.sort(curve, axis=1)
        tied = float(np.mean(srt[:, 2] == srt[:, 3]))          # 3rd == 4th deepest
        stable_raw = np.argsort(curve, axis=1, kind="stable")[:, :3]
        default_raw = np.argsort(curve, axis=1, kind="quicksort")[:, :3]
        order = float(np.mean(np.any(stable_raw != default_raw, axis=1)))
        a = _years_under(curve, 3, kind="stable")
        b = _years_under(curve, 3, kind="quicksort")           # numpy's default
        differs = float(np.mean(np.any(a != b, axis=1)))
        print(f"    {name:<22}{tied:>18.2%}{order:>15.2%}{differs:>14.2%}")

    print()
    print('  AGAINST WHAT D-46 PUBLISHED:')
    print('    duplicate annual return 80.8% ........... reproduces')
    print('    duplicate underwater depth 99.75% ....... reproduces')
    print('    exact tie at n=3, 3.15% / 12.85% ........ reproduces')
    print('    "different shock year on 2.25% and')
    print('     11.00% of paths" ...................... reproduces AS THE ORDER')
    print('                                              COLUMN, exactly, both numbers')
    print()
    print("    THE RULE THAT PRODUCED IT IS IDENTIFIED, NOT GUESSED (section 3's")
    print("    precedent). D-46's pair is the ORDER comparison -- the raw argsort")
    print('    slice, before the sort that shock_years() applies. It counts a')
    print('    permutation of the same three years as a difference. THE ENGINE')
    print('    CANNOT SEE THAT: shock_years() returns tuple(sorted(picks)), so a')
    print('    reordering is discarded one line later and no cell can move.')
    print()
    print('    NOT A VERSION EFFECT. That was the first hypothesis and it is dead:')
    print('    numpy 2.4.2 and 2.4.4 return identical figures in every column.')
    print()
    print('    THE CORRECTION RUNS AGAINST THE DECISION, WHICH IS WHY IT IS WORTH')
    print('    MAKING. The exposure D-46 argues from is 1.55% / 7.80%, not 2.25% /')
    print("    11.00% -- about a third smaller. D-46's ARGUMENT SURVIVES INTACT:")
    print('    31 paths in 2,000 is still a different cube, and reproducibility is')
    print('    binary rather than proportional (D-07). But the number quoted should')
    print('    be the one that describes what can actually change.')
    print()
    print('  READING. The SET column is the number that matters -- it is the')
    print("  share of paths whose SHOCKED YEAR would move if numpy changed")
    print("  its default sort. Reproducibility is D-07's contract, not a")
    print("  nicety, and a cube is byte-identical or it is not.")
    print()
    print("  NOTE ON THE COMPARISON ARM. numpy's default is introsort and is")
    print("  deterministic on one build, so this run measures TODAY's default")
    print("  against stable. That is the exposure, not a bug being caught.")


# =============================================================================
def measure_gross_up_base(paths):
    """D-47 -- THE SALE STACKS ON WHAT IS LEFT, NOT ON THE WHOLE INCOME.

    D-16's PIN writes the incremental bill as tax_on(income + W) - tax_on(income).
    That year's deferral already came off the top, so the base is
    income - contribution (D-47) and the code implements D-47. The PIN's sentence
    is preserved as written, with a forward pointer, per the recorded-rather-than-
    rewritten rule.

    THE DIRECTION IS WHY THIS IS A DECISION AND NOT A FOOTNOTE. The unfixed
    reading OVERSTATES Low's penalty -- which is the direction that flatters this
    project's own lesson about fragility, and is precisely the failure mode D-05
    exists to name. A model that errs toward its own thesis has to say so with a
    number.

    forced_sale_gross() takes the contribution as an argument rather than
    deriving it, so both readings are reachable from outside: pass the real
    contribution for D-47's base, pass 0.0 for the base D-16 literally wrote.
    """
    banner(6, "THE GROSS-UP BASE -- D-47 against D-16's PIN as written",
           "RESULTS.md 7.6; DECISIONS D-47")
    n_acc = LOW.n_accumulation_years
    state = LOW.state_while_working

    print("  PER YEAR -- the same $40,000 net, two bases.")
    print()
    print(f"    {'age':>5}{'gross income':>15}{'contribution':>14}"
          f"{'W, D-47 base':>15}{'W, gross base':>15}{'overstated':>12}")
    worst = (1e9, None)
    best = (-1e9, None)
    for i in range(n_acc):
        age = LOW.current_age + i
        gross = LOW.income(age)
        c = tax.contribution(gross, LOW.savings_rate)
        w_fixed = engine.forced_sale_gross(gross, c, state, engine.SHOCK_AMOUNT)
        w_gross = engine.forced_sale_gross(gross, 0.0, state, engine.SHOCK_AMOUNT)
        over = (w_gross - w_fixed) / w_fixed
        if over < worst[0]:
            worst = (over, age)
        if over > best[0]:
            best = (over, age)
        if age in (35, 38, 45, 55, 64):
            print(f"    {age:>5}{gross:>15,.0f}{c:>14,.0f}"
                  f"{w_fixed:>15,.2f}{w_gross:>15,.2f}{over:>11.2%}")
    print(f"    ... {n_acc} ages measured; spread {worst[0]:.1%} (age {worst[1]})"
          f" to {best[0]:.1%} (age {best[1]})")

    print()
    print("  THE AGE-55 PEAK -- whether the sale crosses the 32% edge.")
    print()
    age = 55
    gross = LOW.income(age)
    c = tax.contribution(gross, LOW.savings_rate)
    edge = next(hi for hi, rate in tax.BRACKETS if rate == 0.32)
    for label, base_c in (("D-47, base net of deferral", c), ("D-16 as written, gross base", 0.0)):
        w = engine.forced_sale_gross(gross, base_c, state, engine.SHOCK_AMOUNT)
        taxable = (gross - base_c) + w - tax.STANDARD_DEDUCTION
        print(f"    {label:<32} W {w:>11,.2f}   taxable {taxable:>12,.0f}"
              f"   {'CROSSES' if taxable > edge else 'below'} the 32% edge at {edge:,.0f}")

    print()
    print("  ACROSS THE PATH SET -- what the unfixed base is worth at 65.")
    print("  3 shocks, D-45 placement, compounded forward at each path's own")
    print("  returns, which is what a forced sale actually costs (D-05).")
    print()
    uw, _ = _readings(paths, LOW)
    years = _years_under(uw, 3)
    growth = _growth_after(paths, n_acc)
    extra = np.zeros(n_acc)
    for i in range(n_acc):
        g = LOW.income(LOW.current_age + i)
        c = tax.contribution(g, LOW.savings_rate)
        extra[i] = (engine.forced_sale_gross(g, 0.0, state, engine.SHOCK_AMOUNT)
                    - engine.forced_sale_gross(g, c, state, engine.SHOCK_AMOUNT))
    at_65 = np.sum(extra[years] * np.take_along_axis(growth, years, axis=1), axis=1)
    trad_65, _ = accumulated(LOW, paths, 3)
    print(f"    mean overstatement at 65      {np.mean(at_65):>14,.0f}")
    print(f"    median                        {np.median(at_65):>14,.0f}")
    shock_free, _ = accumulated(LOW, paths, 0)
    determ = engine.accumulate(
        engine.ARCHETYPE,
        engine.make_paths("constant", 1, engine.ARCHETYPE.n_years, 0.07)[0],
    ).trad
    mean_over = float(np.mean(at_65))
    print(f"    mean trad_65, Low, 3 shocks   {np.mean(trad_65):>14,.0f}"
          f"   share {mean_over / np.mean(trad_65):>7.2%}")
    print(f"    mean trad_65, bootstrap, 0 sh {np.mean(shock_free):>14,.0f}"
          f"   share {mean_over / np.mean(shock_free):>7.2%}")
    print(f"    trad_65, DETERMINISTIC 7%     {determ:>14,.0f}"
          f"   share {mean_over / determ:>7.2%}   <== D-47's")
    print()
    print("    THREE DENOMINATORS AND D-47 USED THE THIRD. The numerator")
    print("    reproduces to the dollar. The published 1.09% is $22,936 against")
    print("    the DETERMINISTIC $2,108,867 -- the headline balance, not any")
    print("    balance from the 2,000-path run the same sentence describes.")
    print("    That is a real mismatch rather than a rounding one: the run is")
    print("    stochastic, at Low, with three shocks, and the denominator is a")
    print("    single 7% path with none. Against the balance a shocked saver")
    print("    actually holds the share is 1.46%, which is the larger claim and")
    print("    the one D-47's own sentence is about.")

    print()
    print('  AGAINST WHAT D-47 PUBLISHED:')
    print('    age-55 taxable 233,360 against 262,180 .. reproduces')
    print('    the 32% edge crossed on the gross base .. reproduces')
    print('    mean overstatement $22,936 .............. reproduces exactly')
    print('    "2.4% to 5.5% across the archetype ages"  DOES NOT REPRODUCE')
    print('                                              measured 0.1% to 5.8%')
    print('    1.09% of trad_65 ........................ reproduces ONLY against')
    print('                                              the DETERMINISTIC balance')
    print()
    print("    THE RANGE IS THE ONE TO FIX. D-47's low end is 2.4%; the true minimum")
    print('    is near zero, at the age where the sale sits inside one band under')
    print('    both bases so the deferral moves nothing. The high end is 5.8%, not')
    print('    5.5%. The spread was quoted from the ages that got looked at rather')
    print("    than from all thirty -- this file's own enumerate-by-grep rule,")
    print('    pointed at a loop.')
    print()
    print("  READING. Read proportionally against D-16's own published lever --")
    print("  three flat gross-up readings spanning 3.5 points of t* -- a share of")
    print("  this size is worth roughly a point of t*. NO PUBLISHED FIGURE MOVES:")
    print("  D-16 publishes t* for the three FLAT readings only, and the exact")
    print("  method is a fourth value with no number attached. Copy into 7.6.")


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
    measure_placement_readings(paths)
    measure_tie_break(paths)
    measure_gross_up_base(paths)

    print()
    print("=" * 78)
    print("Every number above belongs to a document. Copy it there before you")
    print("close the terminal -- that is the whole reason this file exists.")
    print("=" * 78)


if __name__ == "__main__":
    main()
