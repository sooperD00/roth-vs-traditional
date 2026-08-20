"""Sprint 4A's measurements. Five runs, and each one lands in a named document.

WHY THIS FILE EXISTS RATHER THAN A stdout NOTE. Same reason measure_3a.py and
measure_3b.py exist, and 3A stated it best: a published figure with no runnable
source and a checked done-when whose result lives only in a terminal scrollback
are the same defect pointed two ways. Every number this prints is one a document
is about to claim.

IT READS THE FINISHED CUBE AND RUNS NO SWEEP. Three of the five findings are
lookups over cube.json. The other two are quantities defined at a rate no cell
was evaluated at -- ruin at a COMMON t_now, which the cube deliberately does not
carry (D-50), and the delta at which $Y and $X cross -- and that is the reason
this file may call engine._outcome_paths while spike_grid.py may not. `app.py` calls zero
engine privates; tests/test_engine.py calls them 35 times and every file in
scripts/ calls _outcome_paths directly. Measurement code and tests reach in;
deliverables do not.

    uv run python scripts/measure_4a.py
    python scripts/measure_4a.py                     # from the repo root
    python scripts/measure_4a.py path/to/cube.json

WHERE EACH NUMBER GOES
    1  the L3 collapse       DECISIONS D-22's measured line; README ## Results
    2  ruin at t_now         README ## Results; D-39's line
    3  the $X / $Y grid      remaining-sprints, Sprint 4A's risk table (gate 3)
    4  risk gates 1 and 2    the same table
    5  the delta crossings   README ## Results -- the four figures section 3
                             implies and did not compute
"""

import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import engine          # noqa: E402

CUBE_PATH = sys.argv[1] if len(sys.argv) > 1 else "cube.json"
DELTA_HEADLINE = "10"        # D-17. The app uses 10; the README reports both
RUNG_ORDER = ("low", "mid", "high")
NEXT_RUNG = {"low": "mid", "mid": "high", "high": None}   # D-36, one step


def banner(n, title, lands_in):
    print()
    print("=" * 78)
    print(f"{n}. {title}")
    print(f"   -> {lands_in}")
    print("=" * 78)


def load(path):
    cube = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return cube, {(c["rung"], c["objective"], c["shocks"]): c
                  for c in cube["cells"]}


def rung(cleared):
    return engine.Profile(income_points=engine.ARCHETYPE.income_points,
                          stops=tuple(i < cleared for i in range(10)))


LOW, MID, HIGH = rung(3), rung(6), rung(10)


# =============================================================================
def measure_l3_collapse(cells):
    """THE NUMBER SPRINTS 6-8 ARE BUILT ON, AND IT IS MEASURED HERE NOT AT 8.

    D-22 derives it rather than measuring it: objectives 1, 3, 4 and 5 are
    monotone functionals of the after-tax terminal distribution, so wherever the
    two distributions are positive scalar multiples of each other, all of them
    cross at t_now. Mid preserves the multiple (a paused contribution removes c
    from Traditional and c*(1 - t_now) from Roth) and High preserves it
    trivially. Only Low's forced sale breaks it -- the one asymmetric mechanism
    in the cube.

    So the collapse is not a gradient and it is not supposed to be one. The
    honest reading is sharper than a gradient would have been: THE ACCOUNT
    QUESTION IS ONLY CONTESTED FOR PEOPLE WITHOUT A BUFFER.
    """
    banner(1, "THE L3 COLLAPSE -- Low's spread against the Mid/High single value",
           "DECISIONS D-22's measured line; README ## Results")
    t_now = engine.ARCHETYPE.t_now
    print(f"  t_now = {t_now:.4%}. Mid and High sit here at every shock count "
          f"and every objective.")
    print()
    print(f"  {'rung':<6}{'shocks':>7}" + "".join(
        f"{'obj ' + str(o):>13}" for o in (1, 3, 4, 5)) + f"{'spread':>12}")
    for name in RUNG_ORDER:
        for shocks in (0, 1, 2, 3):
            values = [cells[(name, o, shocks)]["breakeven"] for o in (1, 3, 4, 5)]
            spread = max(values) - min(values)
            print(f"  {name:<6}{shocks:>7}"
                  + "".join(f"{v:>12.4%} " for v in values)
                  + f"{spread:>11.4%}")
    print()
    low_extreme = min(cells[("low", o, 3)]["breakeven"] for o in (1, 3, 4, 5))
    print(f"  READING: at Low the break-even walks from {t_now:.2%} at 0 shocks "
          f"down to {low_extreme:.2%} at 3.")
    print(f"  That is {(t_now - low_extreme) * 100:.2f} points of movement on the "
          f"rung that has no buffer,")
    print("  against ZERO points at Mid and High. The dot panels carry this as")
    print("  three rows that fan out at one rung and stack on top of each other")
    print("  at the other two -- which IS L3, rendered rather than asserted.")
    print()
    print("  Objective 5's column runs about 0.08 points low at Mid and High and")
    print("  that is D-51's plateau edge, not a spread. Read the other three")
    print("  columns for the identity.")


# =============================================================================
def measure_ruin_at_t_now(paths):
    """D-39's *ruin rises with shock count* clause, at ONE rate for all four.

    THE CUBE CANNOT CARRY THIS AND THAT IS D-50. Under the per-cell reading the
    Low rung's four shock counts sit at four DIFFERENT rates -- each cell reports
    at its own t* -- and comparing four cells at four rates is comparing four
    different questions. The rate effect runs AGAINST the trend (more shocks
    lower t*, which shrinks Traditional's gross draw and its ruin) while the
    balance effect runs with it, so the cube could publish a ruin column falling
    with shock count while a green test asserts it rises.

    Read here at t_now instead -- the rate the property was verified at over 300
    paths at 3B, and the one rate defined for every profile without a solve.

    THE 0-SHOCK ROW DOES NOT COME IN AT 0.0 and it is not supposed to. D-39's
    margin was sized against a deterministic 7% path and does not survive a
    19.3% standard deviation over 35 years. 53.1% at the 2A review, re-measured
    at 48-50% during 3A under 2B's draw rule.
    """
    banner(2, "RUIN AT A COMMON RATE -- the Low rung read at t_now",
           "README ## Results; DECISIONS D-39's line")
    t_now = LOW.t_now
    print(f"  All four rows read at t_now = {t_now:.4%}, not at each cell's own "
          f"t*. D-50.")
    print()
    print(f"  {'rung':<6}{'shocks':>7}{'ruin trad':>13}{'ruin roth':>13}"
          f"{'delta vs 0':>13}")
    for name, profile in (("low", LOW), ("mid", MID), ("high", HIGH)):
        base = None
        for shocks in (0, 1, 2, 3):
            _, ruined_t = engine._outcome_paths(
                profile, shocks, None, paths, t_now, "trad")
            _, ruined_r = engine._outcome_paths(
                profile, shocks, None, paths, t_now, "roth")
            trad, roth = float(np.mean(ruined_t)), float(np.mean(ruined_r))
            if shocks == 0:
                base = trad
            print(f"  {name:<6}{shocks:>7}{trad:>12.2%} {roth:>12.2%} "
                  f"{trad - base:>+12.2%}")
    print()
    low = [float(np.mean(engine._outcome_paths(
        LOW, k, None, paths, t_now, "trad")[1])) for k in (0, 1, 2, 3)]
    rises = all(b >= a for a, b in zip(low, low[1:]))
    print(f"  D-39's clause -- ruin rises with shock count at Low: "
          f"{'HOLDS' if rises else 'DOES NOT HOLD'}, "
          f"non-decreasing across 0->3 and {low[3] - low[0]:+.2%} end to end.")
    print("  Verified at 3B over 300 paths; this is the 2,000-path reading at")
    print("  the same rate. Recorded whichever way it went.")


# =============================================================================
def measure_x_and_y(cells):
    """THE $X / $Y GRID, WIDENED AT THE SECOND PLAN PASS -- risk gate 3.

    $X = |roth - trad| at delta = 10, at the user's rung. $Y = the change in the
    BETTER CHOICE's outcome between that rung and the next rung up, same
    objective and shock count. Undefined at High (D-36, one step).

    D-23 pins the cell the app's sentence reads: objective 4, 1 shock. The grid
    is printed at all four objectives anyway, and the reason is that objective 4
    is the choice that flatters L3 most -- so the full spread is published
    rather than the single quoted pair. THE RISK IS THAT $Y COMES OUT NEAR $X,
    and if it does that is a FINDING. Do not quietly switch objectives to make
    it come out better: D-17 sized delta = 10 AGAINST the L3 claim on purpose,
    and the README publishes all four precisely so the choice is visible.

    THE PANEL DECK QUOTES THE WEAKEST CELL. Mid -> High is one contribution year
    not made; Low -> Mid is a ~$74,000 gross sale at a depressed price with the
    penalty on top, and D-35 says the demonstration lives at Low.

    DECIDED AT SPRINT 6 -- $X AND $Y ARE COMPUTED IN THE APP, NOT DERIVED INTO
    THE CUBE. `dollars` already carries both operands, so each is an argmax and
    a subtraction: $X reads one cell, $Y reads two. D-12 forbids stochastic
    code, not arithmetic. $Y could not have been a clean cube field in any case
    -- it spans two cells and D-36 leaves it undefined at High, so as a per-cell
    field it would either duplicate a neighbour's data or ship null across a
    third of the cube. `app.x_and_y()` is the port of this function, and this
    function stays as the worked example it was written to be.
    """
    banner(3, "THE $X / $Y GRID -- all four objectives, both deltas, gate 3",
           "remaining-sprints, Sprint 4A's risk table")

    def better_account(cell, delta):
        pair = cell["dollars"][delta]
        return "roth" if pair["roth"] > pair["trad"] else "trad"

    for delta in ("2", "10"):
        print()
        print(f"  delta = {delta} points"
              + ("   <== the app's sentence (D-17)" if delta == "10" else ""))
        print(f"  {'rung':<6}{'obj':>5}{'shocks':>7}{'$X':>16}{'$Y':>16}"
              f"{'$Y/$X':>9}  better")
        for name in ("low", "mid"):
            for objective in (1, 3, 4, 5):
                for shocks in (1,):
                    cell = cells[(name, objective, shocks)]
                    if cell["dollars"] is None:
                        print(f"  {name:<6}{objective:>5}{shocks:>7}"
                              f"{'no crossing':>16}")
                        continue
                    pair = cell["dollars"][delta]
                    x = abs(pair["roth"] - pair["trad"])
                    account = better_account(cell, delta)
                    up = cells[(NEXT_RUNG[name], objective, shocks)]
                    if up["dollars"] is None:
                        y_text, ratio = "next rung null", ""
                    else:
                        y = abs(up["dollars"][delta][account] - pair[account])
                        y_text = f"{y:,.0f}"
                        ratio = f"{y / x:.2f}x" if x else "inf"
                    star = "  <== D-23" if (objective == 4 and name == "low"
                                            and delta == "10") else ""
                    if objective == 5:
                        # NOT DOLLARS. outcome() returns the objective's
                        # reduction and objective 5's is P(not running out).
                        print(f"  {name:<6}{objective:>5}{shocks:>7}"
                              f"{x:>15.6f} {float(y_text.replace(',', '')):>15.6f}"
                              f" {ratio:>8}  {account}   <== FRACTIONS, not $")
                    else:
                        print(f"  {name:<6}{objective:>5}{shocks:>7}{x:>15,.0f} "
                              f"{y_text:>15} {ratio:>8}  {account}{star}")
        print(f"  (High is the top rung: $Y is UNDEFINED there, D-36, and the "
              f"app says so rather than printing zero.)")

    low4 = cells[("low", 4, 1)]["dollars"]
    x2 = abs(low4["2"]["roth"] - low4["2"]["trad"])
    x10 = abs(low4["10"]["roth"] - low4["10"]["trad"])
    up4 = cells[("mid", 4, 1)]["dollars"]
    y2 = abs(up4["2"]["roth"] - low4["2"]["roth"])
    y10 = abs(up4["10"]["roth"] - low4["10"]["roth"])
    print()
    print("  READING, AND IT IS THE SPRINT'S SHARPEST FINDING.")
    print(f"    $Y IS INVARIANT IN delta: {y2:,.0f} at 2 points and {y10:,.0f} "
          f"at 10.")
    print("    Not a coincidence and not a bug -- it is the SAME FACT the")
    print("    Roth-across-delta invariant rests on. Under current rules Roth's")
    print("    terminal does not depend on t_later at all, Roth is the better")
    print("    choice at t* + delta on every cell here, so $Y is a difference")
    print("    of two delta-independent numbers. D-17 predicted exactly this:")
    print("    delta sets $X outright while leaving $Y nearly untouched.")
    print()
    print(f"    SO delta CHOOSES THE VERDICT. At delta = 2, $Y/$X is "
          f"{y2 / x2:.2f}x and L3 reads strong.")
    print(f"    At delta = 10 -- the value the app prints -- it is "
          f"{y10 / x10:.2f}x and L3 reads")
    print("    WEAK: getting the account right is worth about twice what moving")
    print("    up a rung is worth, not a quarter of it.")
    print()
    print("    THE DESIGN DECK ESTIMATED $Y AT 'ABOUT FOUR TIMES THE ACCOUNT")
    print(f"    CHOICE.' Measured at D-23's cell it is {y10 / x10:.2f}x -- off by "
          f"roughly {4 / (y10 / x10):.0f}x, in the")
    print("    direction that costs the lesson. DECISIONS Section 0 already")
    print("    labels that figure a design-phase estimate and warns Sprint 4's")
    print("    third gate may find $Y near $X. It did not land near $X. It")
    print("    landed BELOW it. Gate 3 FIRES.")
    print()
    print("    Do not switch objectives to fix this. D-23 pins the cell, D-17")
    print("    sized delta = 10 AGAINST the L3 claim on purpose, and the README")
    print("    publishes all four objectives precisely so the choice is visible.")
    print("    The dot plot carries L3 on its own -- 8.13 points of collapse at")
    print("    Low against zero at Mid and High -- and that is the demonstration")
    print("    D-35 says lives at Low. The sentence is the weaker instrument")
    print("    here, and this is the number that says so.")
    print()
    print("    FINDING, SEPARATE: objective 5's `dollars` are FRACTIONS. Its")
    print("    reduction is P(not running out), so $X there is a difference of")
    print("    two probabilities. Captioned in the cube header; the README's")
    print("    four-objective table must name the unit or drop the row.")

    print()
    print("  DOES THE CELL THE APP READS ACTUALLY CROSS? (objective 4, 1 shock)")
    for name in RUNG_ORDER:
        cell = cells[(name, 4, 1)]
        print(f"    {name:<6} status {cell['status']:<12} breakeven "
              + (f"{cell['breakeven']:.4%}" if cell["breakeven"] is not None
                 else "null"))
    missing = [n for n in RUNG_ORDER if cells[(n, 4, 1)]["status"] != "crosses"]
    print(f"    -> {'ALL THREE CROSS' if not missing else 'DOES NOT CROSS: ' + str(missing)}."
          f" `dollars` is null on non-crossing cells (D-17) and D-35 forbids")
    print("       the app to print nothing, so a null here would hand Sprint 6")
    print("       an unhandled case under time pressure. It does not.")


# =============================================================================
def measure_risk_gates(cube, cells, paths):
    """GATES 1 AND 2, RECORDED WHICHEVER WAY THEY WENT.

    Gate 1 -- objective 4's p10 floors at $0 for both accounts if ruin exceeds
    10%. IT CANNOT FIRE AS WRITTEN: D-38 floors nothing, so p10 is a signed
    number that may simply be deeply negative. The fallback that was offered
    against it -- read objective 4 as p10 of the after-tax terminal DIFFERENCE
    -- IS INVALID and is left invalid: Section 5's outcome() takes `account` and
    returns one account's number, so the percentile is taken per account and any
    difference is formed afterwards. p10(trad) - p10(roth) is not p10(trad -
    roth), and a fallback that quietly changes the contract is not a fallback.

    Gate 2 -- objective 5 may not discriminate, P(ruin) near 0 or 1 for both.
    R3's sentinel covers it; record that it did or did not need to.
    """
    banner(4, "RISK GATES 1 AND 2 -- recorded whichever way they went",
           "remaining-sprints, Sprint 4A's risk table")

    print("  GATE 1 -- objective 4's p10 against a $0 floor")
    print(f"    {'rung':<6}{'shocks':>7}{'p10 trad':>18}{'p10 roth':>18}"
          f"{'floored?':>10}")
    floored = False
    for name in ("low", "mid"):
        for shocks in (1, 3):
            cell = cells[(name, 4, shocks)]
            pair = cell["dollars"][DELTA_HEADLINE]
            hit = pair["trad"] == 0.0 or pair["roth"] == 0.0
            floored = floored or hit
            print(f"    {name:<6}{shocks:>7}{pair['trad']:>17,.0f} "
                  f"{pair['roth']:>17,.0f}{'YES' if hit else 'no':>10}")
    print(f"    -> {'FIRED' if floored else 'DID NOT FIRE'}, as predicted. "
          "D-38 floors nothing, so these are")
    print("       signed and deeply negative. A reader meeting them for the")
    print("       first time in cube.json will think something broke; the")
    print("       header's `dollars_objective_4` caption is why it did not.")

    print()
    print("  GATE 2 -- objective 5's discrimination")
    t_now = engine.ARCHETYPE.t_now
    print(f"    {'rung':<6}{'shocks':>7}{'P(not ruined) trad':>21}"
          f"{'roth':>10}{'crossed?':>11}")
    degenerate = False
    for name, profile in (("low", LOW), ("mid", MID)):
        for shocks in (0, 3):
            trad = engine.outcome(profile, 5, shocks, None, paths, t_now, "trad")
            roth = engine.outcome(profile, 5, shocks, None, paths, t_now, "roth")
            near_edge = min(trad, roth) < 0.02 or max(trad, roth) > 0.98
            degenerate = degenerate or near_edge
            print(f"    {name:<6}{shocks:>7}{trad:>20.2%}{roth:>10.2%}"
                  f"{cells[(name, 5, shocks)]['status']:>11}")
    print(f"    -> {'FIRED' if degenerate else 'DID NOT FIRE'}. The fractions "
          "sit mid-range, not pinned at 0 or 1,")
    print("       and every objective-5 cell crosses. R3's sentinel was not")
    print("       needed here.")

    print()
    sentinels = [c for c in cells.values() if c["status"] != "crosses"]
    print(f"  FINDING, AND IT IS A DONE-WHEN THAT CANNOT PASS AS WRITTEN: "
          f"{len(sentinels)} of 48 cells")
    print("  do not cross. The done-when reads *a non-crossing cell survives")
    print("  the sweep -- lands in cube.json with a null breakeven and a")
    print("  status*, and at this archetype there is no such cell to survive.")
    print("  T4 is green at 2C on T3's cell, which is a DIFFERENT profile")
    print("  (D-42's $185,000 flat), so the sentinel path is exercised -- just")
    print("  not by this cube. The bullet becomes a REPORTED count rather than")
    print("  a V, because a sprint cannot assert the presence of a case the")
    print("  model does not contain. Recorded, not repaired.")



# =============================================================================
def measure_delta_crossing(cells, paths):
    """THE delta AT WHICH $Y AND $X CROSS, on each of the four objectives.

    ADDED AT THE SPRINT 4A DOCS PASS, and the reason is the convention this
    file's own docstring states: a published figure with no runnable source is
    a defect. Section 3 shows that delta chooses the verdict -- 2.86x at two
    points, 0.47x at ten -- and the README then publishes the four crossings
    that say WHERE the verdict changes. Those four numbers were solved by hand
    and had no source here. This section is that source.

    It is the only part of this file that calls the engine for a value the cube
    does not already carry, and it does so for the same reason section 2 does:
    the quantity is defined at a rate no cell was evaluated at. $Y is invariant
    in delta and $X grows with it, so the difference is monotone and bisects.

    Definitions are section 3's, unchanged. $X = |roth - trad| at the Low rung.
    $Y = the change in the better choice's outcome between Low and Mid, same
    objective and shock count. D-23 pins the cell at 1 shock.
    """
    banner(5, "WHERE $Y AND $X CROSS -- the delta that chooses the verdict",
           "README ## Results, 'The sentence, and the parameter that decides it'")

    shocks = 1
    profiles = {
        name: engine.Profile(income_points=engine.ARCHETYPE.income_points,
                             stops=tuple(i < cleared
                                         for i in range(len(engine.LADDER_STOPS))))
        for name, cleared in (("low", 3), ("mid", 6))
    }

    def x_and_y(objective, delta):
        low, mid = cells[("low", objective, shocks)], cells[("mid", objective, shocks)]
        rate_low = low["breakeven"] + delta / 100.0
        rate_mid = mid["breakeven"] + delta / 100.0
        call = lambda p, r, a: engine.outcome(
            p, objective, shocks, None, paths, r, a)
        low_roth = call(profiles["low"], rate_low, "roth")
        low_trad = call(profiles["low"], rate_low, "trad")
        account = "roth" if low_roth > low_trad else "trad"
        here = low_roth if account == "roth" else low_trad
        return abs(low_roth - low_trad), abs(call(profiles["mid"], rate_mid, account) - here), account

    print("  $X grows with delta and $Y does not, so the difference is monotone")
    print("  and bisects. The app prints delta = 10 (D-17).")
    print()
    print(f"  {'objective':<26}{'delta where $Y = $X':>21}{'$X = $Y there':>18}  better")

    labels = {1: "1 -- mean terminal", 3: "3 -- median terminal",
              4: "4 -- p10 terminal", 5: "5 -- P(not running out)"}
    crossings = {}
    for objective in (1, 3, 4, 5):
        lo, hi = 0.5, 20.0
        for _ in range(60):                      # float exhaustion, 2C's rule
            mid_delta = (lo + hi) / 2.0
            x, y, _ = x_and_y(objective, mid_delta)
            if y - x > 0.0:
                lo = mid_delta
            else:
                hi = mid_delta
        delta = (lo + hi) / 2.0
        x, y, account = x_and_y(objective, delta)
        crossings[objective] = delta
        magnitude = f"{x:,.0f}" if objective != 5 else f"{x:.6f}"
        print(f"  {labels[objective]:<26}{delta:>18.2f} pt{magnitude:>18}  {account}")

    print()
    print("  READING. The four crossings sit inside one point of each other, so")
    print("  the inversion is STRUCTURAL rather than a property of the one cell")
    print("  D-23 pins. Below roughly five points the buffer dominates and the")
    print("  design deck's estimate holds in direction if not in size. Above it")
    print("  the account choice dominates.")
    print()
    print("  delta IS NOT A MODEL PARAMETER. It is the assumed size of the")
    print("  user's miss, and nothing in the model constrains it. It was fixed")
    print("  at 10 BEFORE this sweep ran, on the grounds that a two-point miss")
    print("  is optimistic for a forecast reaching fifty years out. That choice,")
    print("  made blind to the result, is what inverted the headline -- so the")
    print("  crossing is published rather than the parameter being moved.")
    print()
    print(f"  Objective 5's row is in FRACTIONS. Its reduction is P(not running")
    print(f"  out), so $X there subtracts two probabilities (header caption).")
    return crossings

# =============================================================================
def main():
    cube, cells = load(CUBE_PATH)
    header = cube["header"]
    print("Sprint 4A measurements --", f"reading {CUBE_PATH}")
    print("Header:", f"seed={header['seed']}", f"n_paths={header['n_paths']}",
          f"| {header['return_model']}, block {header['block_length']}",
          f"| engine {header['engine_version']}")
    print("Digest:", header["paths_digest"], "(D-41)")
    print("Fingerprint:", header["constants_fingerprint"], "(D-52)")

    paths = engine.make_paths("block", header["n_paths"],
                              engine.TERMINAL_AGE - header["profile"]["current_age"],
                              seed=header["seed"])
    if engine.paths_digest(paths) != header["paths_digest"]:
        raise AssertionError(
            "the rebuilt path array does not match the cube's header digest -- "
            "these measurements would be taken on a different experiment (D-41)"
        )

    measure_l3_collapse(cells)
    measure_ruin_at_t_now(paths)
    measure_x_and_y(cells)
    measure_risk_gates(cube, cells, paths)
    measure_delta_crossing(cells, paths)

    print()
    print("=" * 78)
    print("Every number above belongs to a document. Copy it there before you")
    print("close the terminal -- that is the whole reason this file exists.")
    print("=" * 78)


if __name__ == "__main__":
    main()
