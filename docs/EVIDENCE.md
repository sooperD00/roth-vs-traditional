# Evidence

**What this file is.** Measurements a decision cites, kept where they were taken.
A decision row states a conclusion; this file holds the run underneath it, so the
conclusion stays checkable after the sprint that produced it has closed.

**Precedence.** `DECISIONS.md` wins on what was *decided*. This file wins on what
was *measured* — if a decision row and a measurement here disagree, the
measurement is the fact and the row is the stale copy. That is the same exemption
`ENGINE.md` already carries for the block-vs-IID table. Nothing here is a
contract and nothing here plans a sprint.

**Why it exists as a file rather than as prose inside a decision.** Sprint 3A
found five documents citing one measurement whose code was not in this repo, and
`scripts/measure_3a.py` was written so all five became checkable by one command.
This is that rule applied to the measurements that have no script — taken by hand
at an assessment, before the code they govern existed.

| Entry | Cites it |
|---|---|
| [The objective-5 plateau](#the-objective-5-plateau) | D-51 · `cube.json`'s `breakeven_objective_5` caption · Tech Debt's `n_paths` lever |
| [The engine fix that was measured and rejected](#the-engine-fix-that-was-measured-and-rejected) | D-51 · Tech Debt, Phase N |

*Both entries were taken at the Sprint 4A assessment, before the first cell was
written. Recorded then so the sprint read a decision instead of inventing one at
the keyboard.*

---

# The objective-5 plateau

Taken by calling `engine.breakeven()` and `engine.outcome()` directly, with no
sweep code in between — so the sweep cannot be the cause.

**The 36-cell slab does not behave as one object. It splits by objective family:**

| Cells | Objectives | Deviation from `t_now` |
|---|---|---|
| 27 | 1, 3, 4 | **1 – 9 ulps** — never bit-exact |
| 9 | 5 | **−0.0782 pp** — `0.324218` against `0.325` |

**Objectives 1, 3 and 4 are continuous in `t_later`.** The mean, the median and
the 10th percentile of the after-tax terminal distribution all move smoothly as
the rate moves, so the difference has an isolated zero and bisection to float
exhaustion lands within a few ulps of it. That is 2C's stopping rule working as
pinned, and `_selftest()` has printed *3 ulps off t_now* since 2C shipped.

**Objective 5 is a staircase.** `P(not running out)` counts a discrete event over
2,000 paths, so it takes 2,001 values and its step is exactly `1/2000`. The
difference is not zero at a point — it is zero across an interval:

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

**The one number that decides everything downstream:**

    f(t_now) == 0.0  EXACTLY, on all 9 objective-5 slab cells.

D-22's claim is true. It is the *solver output* that cannot express it. That is
why D-51 splits the slab check by operand rather than bounding `breakeven`
everywhere: no bound is honest at any width, because it would be sized against a
sampling artifact that shrinks with `n_paths`.

*Verified bit-exact on all nine at Sprint 4A. Worst ulp deviation on the other 27:
9 ulps, against the 128 D-51 asserts.*

---

# The engine fix that was measured and rejected

The preference was for fixing `breakeven()` to return the plateau's midpoint
rather than its left edge. Measured before deciding:

| | Deviation from `t_now` |
|---|---|
| Today — plateau left edge | **−0.0782 pp** |
| After the fix — plateau midpoint | **+0.0026 pp** |
| Exact | 0.0000 pp |

**A 30× improvement that is still not exact.** The done-when would still need a
tolerance, that tolerance would still be sized against a sampling artifact, and
the artifact still shrinks with `n_paths` and moves with the seed. The fix buys a
smaller wrong number, not a right one.

**And the cost is a sprint, not an afternoon.** Two bisections instead of one —
the left edge and the right edge — plus a branch that objectives 1, 3 and 4 never
take, plus a decision row, plus re-verification of the whole suite against a
changed solver.

**The reason underneath, and it is the real one.** The plateau is a property of
the SAMPLE, not of the model. `P(not running out)` over 2,000 draws is a
staircase; over the population it is a smooth curve crossing cleanly at `t_now`.
Changing the solver to chase a step edge treats a sampling artifact as a bug in
the search. **D-51 asserts the population claim directly** — the difference is
zero at `t_now` — and gets it exactly, for 18 function calls and no engine edit.

**If it ever becomes a product problem rather than an assertion problem, the
cheap lever is `n_paths`, not the solver.** The width falls roughly as
`1/n_paths`, so 20,000 paths puts it under a basis point without touching a line
of `engine.py`. Recorded as Phase N, not scheduled.
