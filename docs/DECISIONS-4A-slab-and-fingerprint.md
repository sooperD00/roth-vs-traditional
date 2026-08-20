# Sprint 4A — three decisions, recorded before the first cell

**What this file is.** Three questions the Sprint 4A assessment raised, decided
and written down so the sprint reads them rather than re-derives them. Two
become decision rows (**D-51**, **D-52**); one is a rejection recorded with its
measured price. Drafted for paste into `docs/DECISIONS.md` §3 Architecture and
`docs/remaining-sprints.md` §Sprint 4A.

Same rule the 3B docs pass ran under: recorded BEFORE the first cell, so the
code reads a decision instead of inventing one at the keyboard.

---

## 1. The measurement that forced all three

Taken by calling `engine.breakeven()` and `engine.outcome()` directly, with no
sweep code in between — so the sweep cannot be the cause, and risk (d)'s *the
defect is in YOUR sweep* does not apply.

The 36-cell slab does not behave as one object. It splits by objective family:

| Cells | Objectives | Deviation from `t_now` |
|---|---|---|
| 27 | 1, 3, 4 | **1 – 9 ulps** — never bit-exact |
| 9 | 5 | **−0.0782 pp** — `0.324218` against `0.325` |

**Objectives 1, 3 and 4 are continuous in `t_later`.** The mean, the median and
the 10th percentile of the after-tax terminal distribution all move smoothly as
the rate moves, so the difference has an isolated zero and bisection to float
exhaustion lands within a few ulps of it. That is 2C's stopping rule working as
pinned, and `_selftest()` has printed *3 ulps off t_now* since 2C shipped.

**Objective 5 is a staircase.** `P(not running out)` counts a discrete event
over 2,000 paths, so it takes 2,001 values and its step is exactly `1/2000`.
The difference is not zero at a point — it is zero across an interval:

```
t_later    P_trad   P_roth      diff
0.32420    0.5135   0.5130    +0.000500
0.32430    0.5130   0.5130     0.000000   <- plateau opens
0.32500    0.5130   0.5130     0.000000   <- t_now, 48.4% of the way across
0.32550    0.5130   0.5130     0.000000
0.32600    0.5125   0.5130    -0.000500   <- plateau closes
```

Bisected edges: **[0.324218010830, 0.325834192065]**, width **0.1616 pp**.

`breakeven()` tests `(f_mid > 0.0) == (f_lo > 0.0)`. An exact zero reads as *not
positive*, so the interval closes from the right and the solver returns the
**left edge** every time. Deterministic, reproducible, byte-identity unaffected —
and 0.078 pp below where D-22 says the crossing is.

**D-22 already knows this shape and scopes it one size too small.** It says
*objective 5 degenerates to a step function that will not bisect* and attaches
that to `n_paths = 1`. At 2,000 paths the staircase does not disappear; it grows
2,000 steps. It bisects. It just has no point to land on.

**The one number that decides everything below:**

    f(t_now) == 0.0  EXACTLY, on all 9 objective-5 slab cells.

D-22's claim is true. It is the *solver output* that cannot express it.

---

## 2. D-51 — the slab check splits by objective family

> **Draft row for `docs/DECISIONS.md` §3 Architecture**

| ID | Decision | Why |
|---|---|---|
| D-51 | **The 36-cell slab check is TWO assertions over two operands, not one over 36 cells.** Recorded at the Sprint 4A assessment BEFORE the first cell. **Objectives 1, 3 and 4 — 27 cells — assert `breakeven` within `128` ulps of `t_now`**, the `T2C_ULP_K` bound 2C already set for this exact tension, restated as a literal with its citation in the assert message because `tests/test_engine.py` holds the constant and 4A may not open it. **Objective 5 — 9 cells — asserts nothing about `breakeven` at all.** It asserts D-22's actual claim instead: `outcome(trad) − outcome(roth) == 0.0` at `t_now`, **exactly, no tolerance**. `breakeven` on those 9 cells is a plateau EDGE and is published as-is with a caption. **`validate_cube(cube, paths=None)` rebuilds the path array from the header when `paths` is None**, which widens D-49 and is the price | The done-when said *equal `t_now` exactly* and *assert as an identity, not a tolerance*, and those two clauses point at different operands. **D-22's exact identity is `roth/trad`, an accumulation ratio, asserted bit-exact at 3B inside 4 ULP. The slab check reads `breakeven()`'s output, which is a SOLVER RESULT.** A solver that stops at float exhaustion cannot be bit-exact and 2C said so in writing. **The split is the same reasoning D-49 already used one level up** — invariants have operands, and lumping them into one home is what made this look hard. Objectives 1/3/4 have a continuous crossing and an ulp bound is a REPRESENTATION tolerance, which §5 has now reconciled three times. Objective 5 has a crossing INTERVAL 0.1616 pp wide, so no bound on `breakeven` is honest at any width: it would be sized against a sampling artifact, and the artifact shrinks with `n_paths`. Asserting the difference at `t_now` is exact, costs 18 `outcome()` calls, and is the only form that stays true if `n_paths` moves |

### D-51 — what the two asserts look like, and what the widening costs

**The ulp assert, 27 cells.** `128` is restated rather than imported. `T2C_ULP_K`
lives in `tests/test_engine.py`; 4A's seam forbids opening it, and a second
constant would be a second place to keep in step. The message carries the
citation the way the Roth-across-δ assert carries its reason:

    128 ulps, = T2C_ULP_K (DECISIONS §5, 2C's stopping rule). Measured worst
    at 4A: 9 ulps at the archetype. 2C measured 36 across eight (profile,
    rate) pairs and set 128 against that with 3x headroom.

**The zero assert, 9 cells.** Two `outcome()` calls per cell at `t_now`,
subtracted, compared to `0.0`. It must carry its own reason, same shape:

    objective 5 is P(not running out) over n_paths, so its difference is a
    staircase and its zero set has WIDTH (0.1616 pp at n_paths=2000).
    breakeven() returns the plateau's left edge. D-22's claim is that the
    difference IS zero at t_now, and that is what this asserts.

**The widening of D-49, named rather than absorbed.** D-49 says `validate_cube`
takes a dict. It still does. What is added is a second parameter: when `paths`
is None the function rebuilds the array from the header's `seed`, `n_paths`,
`return_model`, `block_length` and the profile's `current_age`, and checks the
rebuild against the header's `paths_digest` before using it.

| | |
|---|---|
| **Cost** | `validate_cube` is no longer a pure data function. `--check` grows an engine import, a deck dependency, and about **5 seconds** |
| **Gain** | `--check` now *re-derives* rather than re-reading. **`paths_digest` was a header field nothing verified** — the reader who rebuilds the array and compares is exactly the failure mode ENGINE.md says the digest exists for, and until now nothing in the repo performed it |
| **Unchanged** | `spike_grid` still calls `validate_cube` on the in-memory cube before the write, and passes the array it already has, so the sweep path costs nothing extra |

**The caption the 9 cells ship with.** The header block gains one sentence beside
`ruin`'s, in the same voice:

    objective 5's break-even is the left edge of a plateau, not a point.
    P(not running out) is a staircase over n_paths, so its crossing has
    width -- 0.1616 pp at the archetype. The cells read about 0.08 pp below
    t_now for that reason and not because the slab varies.

---

## 3. D-52 — `constants_fingerprint`'s scope, recipe, and its missing test

> **Draft row for `docs/DECISIONS.md` §3 Architecture**

| ID | Decision | Why |
|---|---|---|
| D-52 | **`constants_fingerprint` is a blake2b-128 hex digest over a DECLARED, sorted list of `name=repr(value)` lines — seven `engine` module constants plus two derived probes** — and the declared list is the decision. Constants: `BRACKET`, `POLICY_YEAR`, `RETIREMENT_AGE`, `ROTH_TERMINAL_MARGIN`, `SHOCK_AMOUNT`, `SHOCK_PLACEMENT`, `TERMINAL_AGE`. Probes: `archetype.t_now` and `forced_sale_gross()` at age 55. **`SEED`, `N_PATHS` and `BLOCK_LENGTH` are EXCLUDED — `paths_digest` already covers them** and the two fields are meant to be disjoint. `SAVINGS_RATE` is excluded because the header's `profile` block serializes it. **`spike_grid.py` does not import `tax`** | **The two probes are how `tax.py` gets covered without being read.** Every tax number that reaches the cube — the seven bracket edges, the standard deduction, the deferral cap, the state rate, the early-withdrawal penalty — is invisible to `paths_digest` and would move every cell silently, which is precisely the hole this field exists to close. Enumerating them by name means importing `tax` into a deliverable and knowing a list that will grow. **Two derived floats cover the surface instead:** `t_now` moves if the brackets, the deduction, the state rate or the deferral cap move; the age-55 forced sale moves if the penalty or the gross-up rule moves, and it is already a published figure ($73,959.60, the 3B line). `engine.contributions()` supplies the sale's base, so no `tax` import is needed. `repr()` on a float is shortest-round-trip and stable across platforms in Python 3, and blake2b is the repo's one hashing idiom (`paths_digest`) rather than a second |

### D-52 — the recipe, and the reference value

```python
NAMES = ("BRACKET", "POLICY_YEAR", "RETIREMENT_AGE", "ROTH_TERMINAL_MARGIN",
         "SHOCK_AMOUNT", "SHOCK_PLACEMENT", "TERMINAL_AGE")
items = [(n, getattr(engine, n)) for n in NAMES]
items.append(("archetype.t_now", A.t_now))
items.append(("forced_sale_at_55", engine.forced_sale_gross(
    A.income(55), engine.contributions(A, 55)[0], A.state_while_working)))
blob = "\n".join("%s=%r" % kv for kv in sorted(items))
fingerprint = hashlib.blake2b(blob.encode("utf-8"), digest_size=16).hexdigest()
```

**Reference value at the current constants:** `c00a62111fef4a93d5eaee2377420afb`

If the first cube run prints something else, a model constant moved between this
assessment and the sprint, and `engine_version` needs bumping before the cube
ships. That is the field working, not failing.

### D-52 — THE MECHANISM IS NOT COMPLETE AT 4A AND THIS IS THE HANDOFF

The header block's own table says of `constants_fingerprint`: *A test pins it.
Move a model constant without bumping the label and the test fails; that is the
whole mechanism.*

**4A cannot write that test.** `tests/test_engine.py` is 4A's seam. Shipped
without it the field is a string nobody checks — decorative, and decorative is
worse than absent because it reads as coverage.

    [ ] Sprint 4B, added to its done-when list: one test pinning
        cube.json's constants_fingerprint against a fresh computation.
        4B already owns the file and already owns the one validate_cube
        call D-49 hands it. This is the second wire, same commit.

Recorded here because `readinglist.sh` cannot see a decision written at sprint N
for sprint N+1 — the Housekeeping item's own generalization, firing for the
second time.

---

## 4. Option (d), the engine fix — REJECTED, and here is the price it does not buy

The preference was for fixing `breakeven()` to return the plateau's midpoint
rather than its left edge. Measured before deciding:

| | Deviation from `t_now` |
|---|---|
| Today — plateau left edge | **−0.0782 pp** |
| After the fix — plateau midpoint | **+0.0026 pp** |
| Exact | 0.0000 pp |

**A 30× improvement that is still not exact.** The done-when would still need a
tolerance, that tolerance would still be sized against a sampling artifact, and
the artifact still shrinks with `n_paths` and moves with the seed. The fix buys
a smaller wrong number, not a right one.

**And the cost is a sprint, not an afternoon.** Two bisections instead of one —
the left edge and the right edge — plus a branch that objectives 1, 3 and 4
never take, plus a decision row, plus re-verification of 247 green tests against
a changed solver. It cannot happen inside 4A at all: an engine change needs a
test, `tests/test_engine.py` is 4A's seam, and shipping the change untested is
the shape this project's whole process refuses.

**The reason underneath, and it is the real one.** The plateau is a property of
the SAMPLE, not of the model. `P(not running out)` over 2,000 draws is a
staircase; over the population it is a smooth curve crossing cleanly at `t_now`.
Changing the solver to chase a step edge treats a sampling artifact as a bug in
the search. **D-51 asserts the population claim directly** — the difference is
zero at `t_now` — and gets it exactly, for 18 function calls and no engine edit.

*A pre-work sprint is not needed.* If objective 5's plateau ever becomes a
product problem rather than an assertion problem, the cheap lever is `n_paths`,
not the solver: the width falls roughly as `1/n_paths`, so 20,000 paths puts it
under a basis point without touching a line of `engine.py`. Recorded as Phase N,
not scheduled.

---

## 5. Amended Sprint 4A build order — with CLEANUP folded in

> **Replaces the seven-step list in `docs/remaining-sprints.md` §Sprint 4A.**
> Steps 1–7 are unchanged in substance; step 3 gains D-51's split and step 1
> gains D-52's recipe.

| # | Step | Gate |
|---|---|---|
| 1 | `spike_grid.py` skeleton + the twelve-field header. `paths_digest` from `engine.paths_digest()`, `constants_fingerprint` per D-52 | fingerprint prints `c00a6211…`; digest prints `48f9c1b9…` |
| 2 | The sweep. 48 cells, **`objective` innermost**, rung axis by replacing `stops`, `policy=None` passed explicitly | 48 cells, 12 accumulations |
| 3 | **`validate_cube(cube, paths=None)` — WRITTEN third.** D-51's two asserts. No bare asserts in the sweep loop | 27 within 128 ulps · 9 at exactly 0.0 · 12 Low cells NOT all `t_now` |
| 4 | `dollars` at `t* ± δ`, δ ∈ {2, 10}. **Fill keyed off `status == "crosses"`** | both δ keys on crossing cells, null elsewhere |
| 5 | `ruin` copied per-cell from `Result` as-is (D-50). No rate named in `spike_grid.py` | populated on all 48 |
| 6 | `--check`, then `scripts/measure_4a.py` | `--check` on the committed file, cold, passes |
| 7 | Runtime + byte-identity | two runs, `sha256sum` equal |

**CLEANUP — enumerated by grep, not by memory (Housekeeping's own rule).**
There are **no `[SPRINT-4-CLEANUP]` code tags**; 3B removed the last engine tag.
Everything 4A owes is documentation.

| C# | Item | Lands in |
|---|---|---|
| C1 | Header field list rewritten to the DECIDED twelve fields, **same commit as the cube** | `DECISIONS §5` |
| C2 | Cube-timing note **rewritten, not corrected a third time**: 0.46–0.54 s cold, 0.28 s warm, 17–25 s for 48, on a real `(2000, 65)` bootstrap | Tech Debt |
| C3 | Accumulation-cache re-timing closed against the same real bootstrap | Tech Debt |
| C4 | Objective 4's fallback reading stays unreachable from §5 — no signature change taken | Tech Debt |
| C5 | `scripts/` now holds three files. **Note it; do not close it** — it is Sprint 10's | Housekeeping |
| C6 | Three stale numbers: *"3B and 4A tied behind it at 22"* (4A is 30, Sprint 6 is tied not largest); *"against 4A's 22-minute budget"* ×2 | `remaining-sprints` |
| C7 | The slab done-when rewritten to D-51's two clauses — *equal `t_now` exactly* is not achievable against a solver output and 2C said so first | `remaining-sprints` §4A |
| C8 | `tests/test_engine.py` is **2,438 lines**, not the *~1,555* Sprint 4B is sized against | `remaining-sprints` §4B |
| C9 | The `constants_fingerprint` pinning test added to Sprint 4B's done-when list (D-52) | `remaining-sprints` §4B |

---

## 6. What Nicole runs

Nothing here needs her machine before the sprint. Two commands at the sprint's
close, both already on the plan:

```
python spike_grid.py --out /tmp/cube_a.json
python spike_grid.py --out /tmp/cube_b.json
sha256sum /tmp/cube_a.json /tmp/cube_b.json      # must match

python spike_grid.py --check cube.json           # cold, rebuilds the paths
uv run pytest                                    # 247, unchanged by this sprint
python scripts/measure_4a.py                     # the four findings
```

**RNU gates, one each, at one atomic commit:** `spike_grid.py`,
`scripts/measure_4a.py`, and the C1/C6/C7/C8/C9 doc edits.
