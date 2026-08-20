"""The cube. 3 rungs x 4 objectives x 4 shock counts, written to cube.json.

THE SEAM THIS FILE SITS ON: THE CUBE PRODUCES NUMBERS, THE MAPPING PRODUCES
PROSE. This half reads engine.py and never opens tests/test_engine.py.

    python spike_grid.py                    # sweep, validate, write cube.json
    python spike_grid.py --out /tmp/a.json  # byte-identity recipe, run twice
    python spike_grid.py --check cube.json  # re-validate a committed cube
    python spike_grid.py --audit            # the no-math review item, mechanised

THIS FILE CONTAINS NO MATH (D-11). One engine module, two entry points, no
duplicated arithmetic. Every published number in cube.json comes back from
`engine.outcome()` or `engine.breakeven()`; nothing here computes a cell. The
arithmetic that does appear is not model arithmetic and `--audit` lists all of
it in one screen:

  - `t_star + delta / 100.0`, which is D-17's definition of where the dollar
    fields are evaluated. It builds an ARGUMENT to outcome(), not an answer.
  - the ladder comparison `i < n` that builds a stops vector, and the ULP
    comparison in the slab check. Neither touches a cell value.

WHERE THE INVARIANTS LIVE (D-49). `validate_cube(cube, paths=None)` takes a
DICT. The sweep calls it on the in-memory cube before the write; `--check`
loads a committed file and calls the same function. No new artifact -- this
file is Definition of Done item 3. Three done-whens are deliberately NOT in
here and each names its own home: *no math* is a property of the source file
(review item, see `--audit`), *byte-identity* is a property of two runs (the
recipe above), and *runtime* is a measurement (printed at the end of a sweep).
FINDINGS go to scripts/measure_4a.py.

THE RUNG AXIS IS SWEPT BY REPLACING `stops` (D-32, D-33). `rung` is DERIVED by
`engine.rung_from_stops()`; it is not stored and it is not an argument. Adding
a `rung=` parameter to anything in engine.py is the signature change Section 5
exists to prevent.

LOOP ORDER IS A CACHE, NOT A STYLE QUESTION (D-48). `_accumulations()` is keyed
on (profile, shocks, SHOCK_PLACEMENT, SHOCK_AMOUNT, shape, digest) -- eight
entries, FIFO -- and `objective` does NOT enter that key. The working set is
TWELVE keys, 3 rungs x 4 shock counts. With `objective` innermost each key is
used for four consecutive cells and never revisited. Nested the other way every
accumulation runs four times against a cap of eight. The cells are emitted in
loop order rather than sorted, so a reader can see the discipline held: in
cube.json, `objective` varies fastest.

THIS FILE NEVER NAMES A RATE FOR `ruin` (D-50). `Result.ruin` is copied as-is,
at whatever rate that Result reports -- t* on a crossing cell, t_now on one
that does not cross. The comparable common-rate reading belongs to
scripts/measure_4a.py, which may call `engine._outcome_paths` because
measurement code reaches in and deliverables do not. `app.py` calls zero engine
privates; this file calls zero engine privates.
"""

import argparse
import ast
import hashlib
import json
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import engine          # noqa: E402

# --- The axes -----------------------------------------------------------------
# The three stop-vectors exist nowhere as constants -- DEFAULT_STOPS is Mid only
# -- so they are constructed here and written into the header. D-32 and D-33
# give the canonical representatives: first-3 is Low, first-6 is Mid (which IS
# the archetype under D-14 and D-19), all-10 is High.
RUNG_STOPS_CLEARED = (("low", 3), ("mid", 6), ("high", 10))
OBJECTIVES = (1, 3, 4, 5)          # 2 is REJECTED and cut (D-06)
SHOCK_COUNTS = (0, 1, 2, 3)        # D-08
DELTAS = (2, 10)                   # percentage points, D-17

# --- Header constants ---------------------------------------------------------
ENGINE_VERSION = "m3"
# 7.0, and the NAME is load-bearing: it is the rate the app's vertical line is
# drawn at, NOT the rate these cells were computed at. D-15 predicts a reviewer
# will find the balance graph and the $X/$Y sentence a few points apart and
# instructs you to LABEL the mismatch rather than close it. This is that label.
DETERMINISTIC_REFERENCE = 0.07     # D-04a's default, D-15's label

# D-52. The DECLARED scope is the decision. SEED, N_PATHS and BLOCK_LENGTH are
# excluded because paths_digest already covers them and the two fields are meant
# to be disjoint; SAVINGS_RATE is excluded because the header's profile block
# serializes it.
FINGERPRINT_CONSTANTS = (
    "BRACKET", "POLICY_YEAR", "RETIREMENT_AGE", "ROTH_TERMINAL_MARGIN",
    "SHOCK_AMOUNT", "SHOCK_PLACEMENT", "TERMINAL_AGE",
)

# D-51. Restated as a literal rather than imported: T2C_ULP_K lives in
# tests/test_engine.py, which this sprint's seam forbids opening, and a second
# constant would be a second place to keep in step.
ULP_K = 128

RUIN_CAPTION = (
    "ONE reading, per-cell, copied from Result as-is (D-50). A crossing cell "
    "reports at its own t*; a non-crossing cell has no t* and reports at "
    "t_now. Only ruin.trad varies with the rate, and only on the 12 Low cells "
    "with shocks >= 1. The comparable common-rate reading is "
    "scripts/measure_4a.py's, not a second column."
)

BREAKEVEN_OBJ5_CAPTION = (
    "Objective 5's break-even is the LEFT EDGE OF A PLATEAU, not a point "
    "(D-51). P(not running out) counts a discrete event over n_paths, so its "
    "difference is a staircase whose zero set has WIDTH -- 0.1616 pp at the "
    "archetype, one step being 1/n_paths. bisection closes on the plateau's "
    "left edge. These cells read about 0.08 pp below t_now for that reason and "
    "NOT because the slab varies. D-22's claim is asserted directly instead: "
    "the after-tax difference is exactly 0.0 at t_now."
)

OBJ4_P10_CAPTION = (
    "Objective 4 is the 10th percentile of the after-tax TERMINAL "
    "distribution, and D-38 floors nothing, so it is a signed number that may "
    "be deeply negative. That is arithmetic bisection handles, not a broken "
    "cell."
)

OBJ5_UNITS_CAPTION = (
    "`dollars` ON THE 12 OBJECTIVE-5 CELLS IS NOT IN DOLLARS. outcome() "
    "returns the objective's reduction, and objective 5's reduction is "
    "P(not running out) -- a fraction in [0, 1], not a terminal value. The "
    "field is filled because Section 5 fills it on every crossing cell and "
    "because `roth != trad` still means delta was applied; it is captioned "
    "because a reader computing $X from this row would be subtracting two "
    "probabilities and printing the answer as money. D-23 pins the app's "
    "sentence to objective 4, so the app never reads this. The README's "
    "four-objective table does, and must name the unit."
)


# --- Header -------------------------------------------------------------------
def stops_for(cleared):
    """The stops vector with the bottom `cleared` ladder stops set (D-32/D-33)."""
    return tuple(i < cleared for i in range(len(engine.LADDER_STOPS)))


def constants_fingerprint():
    """blake2b-128 over a DECLARED, sorted list of name=repr(value) lines (D-52).

    engine_version's ENFORCEMENT rather than its duplicate: it covers what
    paths_digest cannot see -- everything downstream of the array.

    THE TWO DERIVED PROBES ARE HOW tax.py GETS COVERED WITHOUT BEING IMPORTED.
    Every tax number that reaches a cell -- the seven bracket edges, the
    standard deduction, the deferral cap, the state rate, the early-withdrawal
    penalty -- is invisible to paths_digest and would move all 48 cells
    silently, which is the hole this field exists to close. Enumerating them by
    name means importing tax into a deliverable and maintaining a list that
    grows. `t_now` moves if the brackets, the deduction, the state rate or the
    deferral cap move; the age-55 forced sale moves if the penalty or D-47's
    gross-up base moves, and it is already a published figure ($73,959.60, the
    3B self-test line). engine.contributions() supplies the sale's base, so no
    tax import is needed here.

    repr() on a float is shortest-round-trip and stable across platforms in
    Python 3. blake2b is paths_digest()'s primitive rather than a second idiom.

    [SPRINT-4B-CLEANUP] NOTHING PINS THIS VALUE YET. The header block's own
    decision table says "a test pins it -- move a model constant without
    bumping engine_version and the test fails; that is the whole mechanism."
    Sprint 4A's seam forbids opening tests/test_engine.py, so 4A can write the
    field and not its guard. Until that test exists this string is computed and
    published but never compared, which reads as coverage and is not. Sprint 4B
    already owns that file and already owns D-49's one validate_cube wire; this
    is the second wire, same commit. See D-52 and remaining-sprints 4B.
    """
    profile = engine.ARCHETYPE
    items = [(name, getattr(engine, name)) for name in FINGERPRINT_CONSTANTS]
    items.append(("archetype.t_now", profile.t_now))
    items.append(("forced_sale_at_55", engine.forced_sale_gross(
        profile.income(55),
        engine.contributions(profile, 55)[0],
        profile.state_while_working,
    )))
    blob = "\n".join("%s=%r" % pair for pair in sorted(items))
    return hashlib.blake2b(blob.encode("utf-8"), digest_size=16).hexdigest()


def build_header(paths):
    """The twelve DECIDED fields, plus `captions`.

    `generated_at` and `return_rate` are REMOVED and their absence is the
    point: the first made byte-identity unpassable by construction, and the
    second was a measurement of one draw sitting in a header whose job is to be
    reproduced from. `return_model` and `block_length` replace it -- both are
    inputs, both rebuild the array, and `paths_digest` confirms the rebuild.

    `captions` IS A THIRTEENTH FIELD AND IT IS NOT IN THE DECIDED BLOCK.
    D-50 requires the header to say at which rate `ruin` is read, and D-51
    requires it to say why objective 5's break-even sits left of t_now. Both
    are sentences and neither has a field. Recorded in DECISIONS Section 5 in
    the same commit rather than left as an undocumented extra key.

    `profile` is the archetype MINUS `stops`: ARCHETYPE.stops is Mid's value,
    so serializing it whole would assert Mid for 32 cells that used something
    else. The swept axis is recorded as an axis, in `rungs`.
    """
    profile = engine.ARCHETYPE
    return {
        "seed": engine.SEED,
        "n_paths": engine.N_PATHS,
        "return_model": "block",
        "block_length": engine.BLOCK_LENGTH,
        "paths_digest": engine.paths_digest(paths),
        "deterministic_reference": DETERMINISTIC_REFERENCE,
        "deltas": list(DELTAS),
        "engine_version": ENGINE_VERSION,
        "constants_fingerprint": constants_fingerprint(),
        "profile": {
            "name": "archetype",
            "income_points": [list(point) for point in profile.income_points],
            "savings_rate": profile.savings_rate,
            "current_age": profile.current_age,
            "state_while_working": profile.state_while_working,
            "state_in_retirement": profile.state_in_retirement,
            "d2_roth_to_cap": profile.d2_roth_to_cap,
        },
        "rungs": {
            name: "".join("1" if cleared else "0" for cleared in stops_for(n))
            for name, n in RUNG_STOPS_CLEARED
        },
        "policy": None,
        "captions": {
            "ruin": RUIN_CAPTION,
            "breakeven_objective_5": BREAKEVEN_OBJ5_CAPTION,
            "dollars_objective_4": OBJ4_P10_CAPTION,
            "dollars_objective_5": OBJ5_UNITS_CAPTION,
        },
    }


def rebuild_paths(header):
    """Rebuild the path array from the header alone, and prove it is the same one.

    D-41 requires the cube byte-reproducible FROM ITS HEADER -- from an integer,
    by a reader who has neither this environment nor its lockfile. Until now
    nothing in the repo performed that rebuild, so `paths_digest` was a header
    field no code checked. `--check` performs it.
    """
    paths = engine.make_paths(
        header["return_model"],
        header["n_paths"],
        engine.TERMINAL_AGE - header["profile"]["current_age"],
        seed=header["seed"],
    )
    rebuilt = engine.paths_digest(paths)
    if rebuilt != header["paths_digest"]:
        raise AssertionError(
            f"paths_digest mismatch: header says {header['paths_digest']}, the "
            f"rebuild gives {rebuilt}. The deck or the generator moved and this "
            "cube is not reproducible (D-41)."
        )
    return paths


# --- The sweep ----------------------------------------------------------------
def sweep(paths):
    """48 cells, `objective` INNERMOST. Returns the cube dict.

    Every number in a cell comes back from breakeven() or outcome(). `policy` is
    passed explicitly on every call: breakeven() takes it positionally with no
    default, and every cell in this cube is policy=None (D-26 -- policy is not a
    cube axis; the toggle moves the headline line, never the dots).

    THE FILL IS KEYED OFF `status == "crosses"`, NEVER OFF `dollars is None`.
    breakeven() always returns dollars as None (2C, Section 5) and this file is
    the only thing that fills it, so a null arriving here means NOT FILLED YET
    and never NO CROSSING. Keyed off the null instead, every crossing cell is
    silently skipped and every other gate on the done-when list still passes.
    """
    cells = []
    for rung_name, cleared in RUNG_STOPS_CLEARED:
        profile = engine.Profile(
            income_points=engine.ARCHETYPE.income_points, stops=stops_for(cleared)
        )
        if profile.rung != rung_name:
            raise AssertionError(
                f"stops vector for {rung_name!r} derives as {profile.rung!r} "
                "(D-33 banding). The sweep axis is wrong before a cell exists."
            )
        for shocks in SHOCK_COUNTS:
            for objective in OBJECTIVES:
                result = engine.breakeven(profile, objective, shocks, None, paths)
                cells.append({
                    "rung": rung_name,
                    "objective": objective,
                    "shocks": shocks,
                    "breakeven": result.breakeven,
                    "status": result.status,
                    "dollars": _dollars(profile, objective, shocks, paths, result),
                    "ruin": dict(result.ruin),
                })
    return {"header": build_header(paths), "cells": cells}


def _dollars(profile, objective, shocks, paths, result):
    """Both outcomes at t* +/- delta, delta in {2, 10} percentage points (D-17).

    At t* the two outcomes are equal by construction, so $X would be zero. delta
    is the assumed size of the miss. Null on a non-crossing cell -- there is no
    t* to offset from.
    """
    if result.status != "crosses":
        return None
    filled = {}
    for delta in DELTAS:
        rate = result.breakeven + delta / 100.0
        filled[str(delta)] = {
            "roth": engine.outcome(
                profile, objective, shocks, None, paths, rate, "roth"),
            "trad": engine.outcome(
                profile, objective, shocks, None, paths, rate, "trad"),
        }
    return filled


# --- The invariants (D-49) ----------------------------------------------------
def validate_cube(cube, paths=None):
    """Every property of the cube AS DATA. Takes a dict; returns a count.

    THE _selftest() HOUSE PATTERN, aimed at a dict. One call, no test runner,
    fails loudly. Used twice already in this repo -- engine.py and
    return_series.py -- and this is the third.

    `paths` IS OPTIONAL AND THAT WIDENS D-49, which said this function takes a
    dict. It still does. What is added is that objective 5's slab assertion
    cannot be made against the cube's own numbers (D-51): the published
    break-even there is a plateau edge, and D-22's claim is about the
    DIFFERENCE at t_now, which only the engine can evaluate. When `paths` is
    None the array is rebuilt from the header, which is what makes `--check`
    re-derive rather than re-read. The cost is that this is no longer a pure
    data function and `--check` grows a deck dependency; the gain is that
    `paths_digest` is finally verified by something.

    Raises AssertionError on the first failure, with the reason in the message.
    AssertionError rather than `assert` where a reason must survive: `python -O`
    deletes the statement, and a guard that vanishes under a flag is not a guard.
    """
    checks = 0
    header, cells = cube["header"], cube["cells"]
    if paths is None:
        paths = rebuild_paths(header)
    profiles = {
        name: engine.Profile(
            income_points=engine.ARCHETYPE.income_points, stops=stops_for(n))
        for name, n in RUNG_STOPS_CLEARED
    }
    t_now = engine.ARCHETYPE.t_now
    tolerance = ULP_K * np.spacing(t_now)

    # 1. Exactly 48 cells, against Section 5's contract.
    n_expected = len(RUNG_STOPS_CLEARED) * len(OBJECTIVES) * len(SHOCK_COUNTS)
    if len(cells) != n_expected:
        raise AssertionError(
            f"{len(cells)} cells, expected {n_expected} = 3 rungs x 4 objectives "
            "x 4 shock counts. Objective 2 is cut (D-06)."
        )
    checks += 1

    # 2. Every cell validates against the Section 5 field contract.
    seen = set()
    for cell in cells:
        key = (cell["rung"], cell["objective"], cell["shocks"])
        if key in seen:
            raise AssertionError(f"duplicate cell {key}: the sweep repeated itself")
        seen.add(key)
        if cell["status"] not in ("crosses", "always_roth", "always_trad"):
            raise AssertionError(f"cell {key}: unknown status {cell['status']!r}")
        if (cell["status"] == "crosses") != (cell["breakeven"] is not None):
            raise AssertionError(
                f"cell {key}: status {cell['status']!r} disagrees with a "
                f"breakeven of {cell['breakeven']!r}. When status is not "
                "'crosses', breakeven is null (Section 5)."
            )
    checks += 1

    # 3. THE SLAB, PART ONE -- objectives 1, 3 and 4, 27 cells (D-22, D-51).
    #    The scalar multiple holds per path, so the crossing is exact -- but
    #    breakeven() is a SOLVER and stops at float exhaustion (2C), so the
    #    assertion is an ULP bound and not bit-equality. This is a
    #    REPRESENTATION tolerance, not a modeling one: the same reconciliation
    #    Section 5 already writes for 2A's 4-ulp identity and T1's K = 16.
    slab = 0
    for cell in _slab_cells(cells):
        if cell["objective"] == 5:
            continue
        off = abs(cell["breakeven"] - t_now)
        if off > tolerance:
            raise AssertionError(
                f"SLAB BROKE at {cell['rung']}/obj{cell['objective']}/"
                f"{cell['shocks']} shocks: breakeven {cell['breakeven']!r} is "
                f"{off / np.spacing(t_now):.0f} ulps off t_now {t_now!r}, past "
                f"the {ULP_K}-ulp bound. That bound is T2C_ULP_K (DECISIONS "
                "Section 5, 2C's stopping rule), measured worst 36 across "
                "eight (profile, rate) pairs and 9 at this archetype. If the "
                "Mid or High slab varies, THE DEFECT IS IN THE SWEEP, not in "
                "the engine -- D-22's multiple is exact and 3B asserts it "
                "inside a 4-ULP bound one sprint earlier. Do not widen this."
            )
        slab += 1
    checks += 1

    # 4. THE SLAB, PART TWO -- objective 5, 9 cells (D-51).
    #    P(not running out) counts a discrete event over n_paths, so its
    #    difference is a STAIRCASE and its zero set has width. breakeven()
    #    returns the plateau's left edge, which is about 0.08 pp below t_now and
    #    is not a defect. D-22's actual claim is asserted instead, exactly.
    for cell in _slab_cells(cells):
        if cell["objective"] != 5:
            continue
        profile = profiles[cell["rung"]]
        gap = (engine.outcome(profile, 5, cell["shocks"], None, paths, t_now,
                              "trad")
               - engine.outcome(profile, 5, cell["shocks"], None, paths, t_now,
                                "roth"))
        if gap != 0.0:
            raise AssertionError(
                f"SLAB BROKE at {cell['rung']}/obj5/{cell['shocks']} shocks: "
                f"P(not running out) differs by {gap!r} at t_now. D-22 says "
                "the two after-tax distributions are related by a scalar that "
                "equals 1 there, so every monotone functional of them ties. "
                "This is the objective-5 form of that claim and it is exact -- "
                "the published breakeven on this cell is a plateau EDGE and "
                "cannot carry it (D-51)."
            )
        slab += 1
    checks += 1

    if slab != 36:
        raise AssertionError(
            f"the slab covered {slab} cells, expected 36 = the whole Mid and "
            "High slabs at every shock count (32) plus Low's 0-shock row (4). "
            "D-22."
        )

    # 5. The 12 informative cells must NOT all read t_now.
    #    A broken sweep returning t_now everywhere passes the slab check on 36
    #    cells and fails only on the 12 nobody has looked at yet.
    varying = [
        cell for cell in cells
        if cell["rung"] == "low" and cell["shocks"] >= 1
    ]
    if len(varying) != 12:
        raise AssertionError(f"expected 12 Low shocked cells, found {len(varying)}")
    moved = [
        cell for cell in varying
        if cell["breakeven"] is None or abs(cell["breakeven"] - t_now) > tolerance
    ]
    if not moved:
        raise AssertionError(
            "all 12 Low shocked cells read t_now. Low's forced sale is the ONLY "
            "asymmetric mechanism in the cube (D-22) and it is not firing -- "
            "the sweep is passing the same profile to every rung, or the shock "
            "count is not reaching accumulate()."
        )
    checks += 1

    # 6. `dollars` is filled iff the cell crosses, and this file is the only
    #    thing that fills it (D-17, 2C).
    for cell in cells:
        if cell["status"] == "crosses":
            if cell["dollars"] is None:
                raise AssertionError(
                    f"cell {cell['rung']}/obj{cell['objective']}/"
                    f"{cell['shocks']}: crosses but dollars is null. "
                    "breakeven() always returns this null and spike_grid fills "
                    "it -- a null here means NOT FILLED YET, never NO CROSSING."
                )
            if set(cell["dollars"]) != {str(d) for d in DELTAS}:
                raise AssertionError(
                    f"cell {cell['rung']}/obj{cell['objective']}/"
                    f"{cell['shocks']}: dollars keys are "
                    f"{sorted(cell['dollars'])}, expected both deltas (D-17)"
                )
        elif cell["dollars"] is not None:
            raise AssertionError(
                f"cell {cell['rung']}/obj{cell['objective']}/{cell['shocks']}: "
                f"status {cell['status']!r} but dollars is populated. A "
                "non-crossing cell has no t* to offset from and stays null."
            )
    checks += 2

    # 7. roth != trad within each delta. If they match, delta was not applied
    #    and $X is zero -- the headline sentence loses its first magnitude.
    for cell in cells:
        if cell["dollars"] is None:
            continue
        for delta, pair in cell["dollars"].items():
            if pair["roth"] == pair["trad"]:
                raise AssertionError(
                    f"cell {cell['rung']}/obj{cell['objective']}/"
                    f"{cell['shocks']} at delta {delta}: roth == trad "
                    f"({pair['roth']!r}). At t* they are equal by construction, "
                    "so an equal pair here means the offset never reached "
                    "outcome() and $X would publish as zero (D-17)."
                )
    checks += 1

    # 8. Roth's dollar outcome is IDENTICAL across both deltas.
    #    IT IS FREE BECAUSE `policy` IS NULL ON EVERY CELL. Under D-26's branch
    #    Roth's terminal DOES depend on t_later -- the bequest at 100 is
    #    ordinary income beyond whatever allowance is left -- so this line goes
    #    silently wrong the day policy enters the cube. The reason travels with
    #    the assert because that is the only place a future reader will meet it.
    for cell in cells:
        if cell["dollars"] is None:
            continue
        values = {pair["roth"] for pair in cell["dollars"].values()}
        if len(values) != 1:
            raise AssertionError(
                f"cell {cell['rung']}/obj{cell['objective']}/{cell['shocks']}: "
                f"Roth's outcome moved across delta ({sorted(values)!r}). Under "
                "current rules Roth's terminal does not depend on t_later at "
                "all, so this is free ONLY BECAUSE policy is null on every cell "
                "(D-49). If policy has entered the cube, this assertion is no "
                "longer valid and must be removed rather than widened."
            )
    checks += 1

    # 9. `ruin` populated on all 48, per-cell, copied from Result as-is (D-50).
    #    The field is asserted PRESENT and populated. No trend is asserted
    #    across cells: the Low rung's four shock counts sit at four different
    #    rates, so comparing them would be comparing four different questions.
    #    D-39's *rises with shock count* clause lives in measure_4a.py, at a
    #    common t_now.
    for cell in cells:
        ruin = cell["ruin"]
        if set(ruin) != {"roth", "trad"}:
            raise AssertionError(
                f"cell {cell['rung']}/obj{cell['objective']}/{cell['shocks']}: "
                f"ruin keys {sorted(ruin)}, expected roth and trad"
            )
        for account, value in ruin.items():
            if not isinstance(value, float) or not 0.0 <= value <= 1.0:
                raise AssertionError(
                    f"cell {cell['rung']}/obj{cell['objective']}/"
                    f"{cell['shocks']}: ruin.{account} is {value!r}, not a "
                    "fraction in [0, 1]"
                )
    checks += 1

    # 10. A non-crossing cell survives the sweep -- lands in the file with a
    #     null breakeven and a status, rather than raising. THE CUBE-SCALE
    #     VERSION OF T4, which is green at 2C; this asserts the sweep-level
    #     behaviour and does not re-derive 2C's work. Objectives 4 and 5
    #     genuinely do not cross for some cells (R3). If every cell crosses,
    #     that is a FINDING and measure_4a.py reports it -- so this is a
    #     REPORTED count here rather than a raise, and the reason is that a
    #     sprint cannot assert the presence of a case the model may not contain.
    sentinels = [cell for cell in cells if cell["status"] != "crosses"]
    return checks, slab, sentinels


def _slab_cells(cells):
    """The 36 cells D-22 puts at t_now: all of Mid and High, plus Low at 0 shocks.

    Mid preserves the scalar multiple (a paused contribution removes c from
    Traditional and c*(1-t_now) from Roth) and High preserves it trivially.
    Low at 0 shocks runs no branch at all. Only Low with shocks >= 1 varies.
    """
    for cell in cells:
        if cell["rung"] in ("mid", "high") or cell["shocks"] == 0:
            yield cell


# --- The no-math review item, mechanised --------------------------------------
def audit_math(path=None):
    """List every arithmetic node in this file, so the review item is one screen.

    D-11's *no math in spike_grid* is a property of the SOURCE FILE, not of the
    cube, so no function that reads cube.json can see it and it is a review item
    rather than a V. This makes the review mechanical without pretending to be a
    gate: it reports, it does not fail. `test_the_engine_never_clamps_a_balance_
    at_zero` is the precedent for the shape.
    """
    path = pathlib.Path(path or __file__)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    lines = source.splitlines()
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.BinOp, ast.AugAssign)) and hasattr(node, "lineno"):
            found.append((node.lineno, lines[node.lineno - 1].strip()))
    # The words that would appear if an expression were touching a cell value.
    # A hit is not a failure -- it is the short list a human actually reads.
    suspect = ("outcome", "breakeven", "dollars", "ruin", "roth", "trad", "rate")
    print(f"AST ARITHMETIC AUDIT -- {path.name} (D-11, review item)")
    print("=" * 78)
    flagged = 0
    for lineno, text in sorted(set(found)):
        mark = "  <== READ THIS ONE" if any(w in text for w in suspect) else ""
        if mark:
            flagged += 1
        print(f"  line {lineno:>4}  {text}{mark}")
    print("=" * 78)
    print(f"  {len(set(found))} arithmetic expressions, {flagged} naming a cell "
          "value or a rate.")
    print("  The rest are counters, string joins and indices. Every flagged")
    print("  line should be D-17's delta offset building an ARGUMENT to")
    print("  outcome(), or a tolerance -- never a published number.")
    return found


# --- Output -------------------------------------------------------------------
def markdown_grid(cube):
    """The stdout table. Three blocks, one per rung, objective across the top."""
    out = []
    t_now = engine.ARCHETYPE.t_now
    by_key = {
        (c["rung"], c["objective"], c["shocks"]): c for c in cube["cells"]
    }
    for rung_name, _ in RUNG_STOPS_CLEARED:
        out.append("")
        out.append(f"### {rung_name.upper()} — break-even future marginal rate")
        out.append("")
        out.append("| shocks | " + " | ".join(
            f"obj {o}" for o in OBJECTIVES) + " |")
        out.append("|---" * (len(OBJECTIVES) + 1) + "|")
        for shocks in SHOCK_COUNTS:
            row = [str(shocks)]
            for objective in OBJECTIVES:
                cell = by_key[(rung_name, objective, shocks)]
                if cell["breakeven"] is None:
                    row.append(cell["status"])
                else:
                    mark = "" if cell["objective"] != 5 else " *"
                    same = "" if abs(cell["breakeven"] - t_now) > 1e-9 else " ="
                    row.append(f"{cell['breakeven']:.4%}{same}{mark}")
            out.append("| " + " | ".join(row) + " |")
    out.append("")
    out.append("`=` marks a cell at t_now within 1e-9. `*` marks objective 5, "
               "whose break-even is a plateau edge (D-51).")
    return "\n".join(out)


def write_cube(cube, path):
    """Deterministic bytes. No generated_at, no timestamps, no set iteration.

    json writes floats via repr(), which is shortest-round-trip, and dict order
    is insertion order in Python 3.7+, so two runs at the same seed produce
    byte-identical files. That gate no longer carries an asterisk.

    WRITTEN AS BYTES, NOT AS TEXT, AND THAT IS THE WHOLE POINT OF THIS LINE.
    `write_text()` opens in TEXT mode, and on Windows text mode translates every
    "\\n" to "\\r\\n" on the way out -- so the function whose job is deterministic
    bytes would hand the platform a chance to edit them. Found at the Sprint 4A
    review by a CROSS-MACHINE hash comparison: the same cube came out 23,216
    bytes on Linux and 24,280 on Windows, a difference of exactly 1,064 bytes
    against 1,064 lines. The content was identical; the line endings were not.

    THE DONE-WHEN CANNOT SEE THIS. Two runs on one machine agree with each
    other whichever convention that machine uses, so byte-identity passes while
    D-41's actual claim -- reproducible by a reader who has neither this
    environment nor its lockfile -- is broken. Same class as ENGINE.md's
    native-byte-order note for paths_digest, one layer up, and this one needs no
    strange hardware. `.gitattributes` pins the checkout side; this pins the
    write side. Both are needed: a fix here still loses to a Git conversion.
    """
    path = pathlib.Path(path)
    payload = json.dumps(cube, indent=2, ensure_ascii=True) + "\n"
    path.write_bytes(payload.encode("utf-8"))
    return path


# --- Entry points -------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="cube.json",
                        help="where to write the cube (default: cube.json)")
    parser.add_argument("--check", metavar="CUBE",
                        help="re-run the invariants against a committed cube")
    parser.add_argument("--audit", action="store_true",
                        help="list this file's arithmetic (D-11 review item)")
    args = parser.parse_args(argv)

    if args.audit:
        audit_math()
        return 0

    if args.check:
        cube = json.loads(pathlib.Path(args.check).read_text(encoding="utf-8"))
        started = time.perf_counter()
        checks, slab, sentinels = validate_cube(cube)
        print(f"spike_grid --check OK -- {args.check} | {len(cube['cells'])} "
              f"cells | {checks} invariants | {slab}-cell slab | "
              f"{len(sentinels)} non-crossing | digest "
              f"{cube['header']['paths_digest']} REBUILT AND MATCHED | "
              f"fingerprint {cube['header']['constants_fingerprint']} | "
              f"{time.perf_counter() - started:.1f}s")
        return 0

    print(f"spike_grid -- seed {engine.SEED}, n_paths {engine.N_PATHS}, "
          f"block {engine.BLOCK_LENGTH}, placement {engine.SHOCK_PLACEMENT}, "
          f"shock ${engine.SHOCK_AMOUNT:,}")
    paths = engine.make_paths("block", engine.N_PATHS, engine.ARCHETYPE.n_years)
    print(f"digest {engine.paths_digest(paths)} (D-41) | fingerprint "
          f"{constants_fingerprint()} (D-52)")

    started = time.perf_counter()
    cube = sweep(paths)
    elapsed = time.perf_counter() - started

    checks, slab, sentinels = validate_cube(cube, paths)
    written = write_cube(cube, args.out)

    print(markdown_grid(cube))
    print()
    print(f"spike_grid 4A OK -- {len(cube['cells'])} cells in {elapsed:.1f}s "
          f"({elapsed / len(cube['cells']):.2f}s per cell) | {checks} invariants "
          f"| {slab}-cell slab exact | {len(sentinels)} non-crossing | "
          f"-> {written}")
    if not sentinels:
        print("  FINDING: every cell crosses. R3's sentinel is unexercised at "
              "cube scale; T4 remains green at 2C. measure_4a.py reports it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
