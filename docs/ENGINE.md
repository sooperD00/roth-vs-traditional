# The engine

**What this file is.** How the math works, and the five choices inside it that
change an answer. `DESIGN.md` argues *why* the model is shaped this way; this
file is *what it does*.

The engine answers one question: **at what future marginal tax rate do Roth and
Traditional tie?** Everything else in this project is presentation.

## Contract

```python
breakeven(profile, objective, shocks, policy, paths) -> Result
outcome(profile, objective, shocks, policy, paths, rate, account) -> float
```

| | |
|---|---|
| `app.py` and `spike_grid.py` both import this module | No duplicated math (D-11) |
| `paths` is passed in, never drawn inside | What makes common random numbers hold (D-07) |
| `outcome` is public | `spike_grid` calls it directly for the dollar fields (D-17) |
| Solved by bisection over the future marginal rate | Bracket `(0.01, 0.95)`, stopping at float exhaustion — both pinned in §5 and in `engine.py`'s module docstring |
| No clamping | D-38, and choice 4 below is why |

The app imports this module. The PoC is a script that imports it and prints a
table. There is one implementation of the math and two ways to reach it.

**Status: the engine is complete; one path inside it still raises — and after
Sprint 3A it is not `make_paths` any more.** Sprint 2A
landed the profile, the income curve, contributions, accumulation, the D-33
ladder and the constant-path builder. Sprint 2B landed the retirement draw, both
decumulation loops, the D-26 policy branch, the four objective reductions, ruin
detection and `outcome()`; it deleted `marker_withdrawal`, which was a pure
alias for `tax.gross_for_net`. **Sprint 2C landed `breakeven()`** — the search,
the D-06 degeneracy guard, the no-crossing sentinel and the `Result` shape.
**Sprint 3A landed the block bootstrap** — `make_paths(kind="block")`, the
`RandomState`/overlapping-starts/truncation parameters D-05 left open (D-43),
`paths_digest()` for D-41's cube header, `path_drawdown()` and the D-44
vocabulary. It also closed the two shock-free decisions Sprint 4A was blocked on:
R9's ruin question (D-39, option 1) and D-15's reconciliation. **What still
raises is `accumulate(..., shocks>0)` — the three rung mechanisms, and they are
Sprint 3B's.**

**Three parameters more were decided nowhere in this corpus and are now D-43.**
The generator is `RandomState(20260815)`, MT19937 — picked *against* current
numpy practice because NEP 19 freezes the legacy stream and declines to freeze
`default_rng`, and D-41 needs reproduction from an integer rather than from a
lockfile. Block starts are drawn from overlapping windows with no wrap. A
trailing partial block is truncated.

**Three search parameters were decided nowhere in this corpus and are pinned in
`engine.py`'s module docstring rather than invented per caller:** the bisection
bracket is `(0.01, 0.95)` — the interval D-26's row already sweeps, cited rather
than chosen; the stopping rule is float exhaustion, not a tolerance; and
`Result.ruin` is measured at the rate the `Result` reports, which is `t*` on a
crossing cell and `t_now` on one that does not cross.

**The accumulation figures in this file now come out of this repo.** The four
age-65 balances, `t_now`, the year-20 allowances and D-15's proxy all reproduce
from `uv run python engine.py` and are asserted by `tests/test_engine.py`.
**Nothing in this file is a cold-read figure any more.** The draw and the marker
came out of the repo at Sprint 2B; both thresholds came out at Sprint 2C. `uv run
python engine.py` prints all three sprints' scalars, and `tests/test_engine.py`
asserts every one of them against literals restated by hand.

| Section | |
|---|---|
| [Five load-bearing choices](#five-load-bearing-choices) | The decisions that change an answer |
| [Where the paths come from](#where-the-paths-come-from) | The return series, and a fudge factor that got measured |
| [Shock timing and size](#shock-timing-and-size) | Three rungs, three code branches |
| [Output — the cube](#output--the-cube) | 48 cells and what each one carries |
| [Tests](#tests) | Three suites, and which claim each defends |

---

# Five load-bearing choices

## 1. Same pre-tax dollars

$1,000 into a Roth costs more take-home than $1,000 into a Traditional, because
the Roth dollar was already taxed. Comparing them as equals quietly favors Roth,
and most calculators do exactly that.

So the comparison is $X into Traditional against $X·(1−t) into Roth. Under that
convention the growth factor appears identically on both sides and divides out,
which is what makes the return rate irrelevant. **The convention is load-bearing,
not cosmetic** — L1 is a consequence of it.

At the archetype that is $24,500 to Traditional against $16,538 to Roth. The Roth
deliberately under-fills, and the app says so.

## 2. Both accounts have to fund the same life

The spending path is not a replacement rate. It is the level real after-tax
amount that leaves 15% of the Roth's age-65 balance at 100 — sized off the Roth
because it is the smaller account and therefore the binding one.

This started as an 80% replacement of final working income, which turned out to
bankrupt both accounts: $160,000 a year against a $24,500 deferral cap is not
fundable at any return rate, and the terminal-wealth objective returned $0 = $0
with no crossing. Sizing off the larger account is no better — it starves the
Roth, and every Roth-side objective then reports ruin, so the model measures the
spending assumption instead of the tax question.

The honest consequence is published rather than hidden: at the archetype the draw
is $108,397 a year, which is **54% of final working income.** A $24,500 cap
cannot fund 80% of a $200,000 income. Social Security and the grayed
excess-savings row are where the rest comes from, and neither is in this model.

## 3. The deterministic answer is the stochastic one with the noise turned off

At a `(1, n_years)` constant-return paths array the engine produces the headline
break-even rate. Same function, same code path. The app's number and the grid's
numbers cannot drift apart, because there is nothing for them to drift from.

Deterministic mode is a **shape, not a flag**. `make_paths(kind, ...)` builds
either a constant array or a bootstrap array, and the engine cannot tell which it
received.

## 4. Nothing is clamped at zero

Balances are allowed to go negative. Ruin is a recorded flag, not an absorbing
floor.

This is not a stylistic choice. Objectives 1 through 3 bisect on the difference
between two terminal values, and that difference is monotone in the future rate
only if the arithmetic runs. Clamp it and both sides pile up at $0 across a range
of rates, the difference goes flat, and bisection returns whichever endpoint it
started nearest. Objectives 4 and 5 read the flag; nobody reads a clamped
balance.

**The rule extends to the bequest, and that is where it is easy to miss.** Under
the "nevermind" policy the Roth's terminal balance is tax-free up to whatever
allowance is left and ordinary income beyond it — which reads naturally as
`min(B, rem) + max(0, B − rem)·(1 − t_later)`. That `max(0, ...)` is a clamp
wearing tax logic, and with it the second threshold does not exist at all: the
difference never changes sign and the solver returns a sentinel where the
headline should be. The signed form, `rem + (B − rem)·(1 − t_later)`, is the one
that crosses at 58.4%. `DECISIONS.md` carries all three readings and what each
one measures.

## 5. Common random numbers

The `(n_paths, n_years)` array is drawn once and reused across every cell, both
account types, and every step of the bisection.

The quantity of interest is a small difference between two large numbers.
Evaluate the two sides on independent draws and sampling noise swamps the
difference you came to measure; evaluate them on the same draws and the noise
cancels. The comparison is paired, the cube is reproducible from
`seed = 20260815` at `n_paths = 2000`, and forty-eight cells cost almost nothing.

# Where the paths come from

The engine resamples five-year runs of historical returns rather than drawing
years independently. The deck is `return_series.py` — 98 annual real total
returns on US equities, 1928 through 2025, from Damodaran's series with CPI from
the same workbook, deflated on load. It compounds at 6.78% real against an 8.61%
arithmetic mean; the 1.83-point gap is variance drag and matches σ²/2 at a 19.30%
standard deviation.

## What the block bootstrap does and does not buy

This is the one modeling choice that changes an answer, so it got a reason. Then
it got measured, and the reason was wrong.

**The reason written first.** A life event costs you far more when it forces a
sale during a downturn, and that requires bad years to arrive in runs. Draw years
independently and a crash is followed by an ordinary year, so the mechanism
survives and the magnitude doesn't.

**What 4,000 paths on the real series actually say** — `path-drawdown` (D-44),
measured over the **30-year accumulation window**, not the full 65-year path.
Reproduced at Sprint 3A by `scripts/measure_3a.py`; the right-hand column is the
gate-two measurement it reproduces.

**THE WINDOW IS LOAD-BEARING AND IT WAS MISSING FROM THIS CAPTION UNTIL SPRINT
3A.** Read "each path" as the whole 65 years and the same measurement returns
−51.9% / −53.0% and −66.7% / −72.0% — every number below goes stale in five
documents at once. Accumulation is the right window because that is where a
shock lands (D-08).

| | Block(5) | IID | published |
|---|---|---|---|
| Median `path-drawdown` | −42.2% | −42.0% | −42.6 / −43.0 |
| p10 `path-drawdown` | −59.6% | **−63.7%** | −59.7 / −64.3 |
| Year after the worst year | **+17.1%** | +10.1% | +17.0 / +9.5 |
| Next three years, cumulative | **+39.9%** | +33.2% | +39.5 / +32.1 |
| …of which negative | 5.4% | 20.0% | 5% / 21% |

Block bootstrap has the **thinner** left tail and the **faster** rebound. It is
the conservative model here, which is the opposite of what was claimed.

**ONE ROW CARRIES THE FINDING AND ONE DOES NOT, WHICH SPRINT 3A MEASURED AND
THIS TABLE USED TO OBSCURE.** Across five seeds at 4,000 paths the **p10 pair
says *block thinner* five times out of five**; the **median pair splits three to
two** at a gap of a few tenths of a point. The median row is sampling noise and
must be read as noise — the *tail* is the claim. This matters practically:
measure on one seed and a median inversion reads as a defect worth an afternoon.
Both readings are asserted in `tests/test_engine.py`, the p10 as a direction and
the median as noise.

**Why.** The lag-1 autocorrelation of annual US real returns is **−0.035** —
essentially zero, faintly negative. The runs intuition is real at monthly and
daily frequency and real in the narrative of 1929–32, but ninety-eight annual
observations cannot see it. And this record's crashes came packaged with their
own recoveries: 1931 sits in a block with 1933, 1974 with 1975, 2008 with 2009.
Keeping the runs intact keeps the rebounds intact too.

**Why block stays anyway.** The forced-sale mechanism survives through a
different channel. A shock at the Low rung sells $40,000 at a depressed price,
and what it costs is the compounding you gave up — so a *faster* rebound makes
that cost **larger**, not smaller. Block also reproduces history's own worst
five-year sequence: the median path's worst five-year run lands at
**−10.28%** annualized over the full path, against a published −10.26%.
**The number reproduces; the clause attached to it does not.** −10.26% is
exactly 1937–41 — it is the deck's own worst five-year window — but only
**12.6%** of paths actually draw that block. The median path's worst run
*coincides* with 1937–41's depth through a rolling window that usually
straddles two drawn blocks. Read strictly to the blocks themselves, the median
path's worst *drawn* run is −7.27%, which is 1973–77. Same shape as this
section's other correction: the measurement stands, the story told about it was
tightened.

**And the honest limit.** Ninety-eight years at block length five is about **19.6
independent blocks.** That is the same n ≈ 5 critique this project makes of
Bengen's 4% rule, now pointed at this model. The structure assumption cannot be
validated at n ≈ 20; it can only be stated.

The alternative worth naming: a parametric Monte Carlo is the conventional pick
here, and it is thin-tailed *and* memoryless. It buys smoothness, and on this
evidence it would have cost less than assumed.

Block length is five years — a choice rather than a derivation, with sensitivity
at three and ten in Scope & Branches. **Measuring the fudge factor is what caught
the bad reason.** That is the whole argument for naming them.

# Shock timing and size

Life events land in each path's worst accumulation years, found by sorting on
drawdown. There is no correlation coefficient — the placement is the correlation,
and there is nothing to calibrate or defend.

An uncorrelated toggle scatters them randomly instead. Flipping it deflates the
tail visibly, which is the cheapest demonstration in the project that the
mechanism is doing real work.

A shock is $40,000 real. That is a named fudge factor, chosen at 1.6× a
contribution year so that the forced sale and the skipped contribution are the
same order of magnitude; sensitivity at $25,000 and $80,000 goes in Scope &
Branches, the same treatment block length gets.

What a shock costs depends on the rung, and these are three code branches rather
than three settings of a severity dial:

| Rung | What happens |
|---|---|
| Low | Sell at the shocked year's price. Traditional takes the 10% early-withdrawal penalty plus ordinary income; Roth basis comes out free |
| Mid | No sale. Contributions stop that year and resume after |
| High | Absorbed by cash. The portfolio never notices |

Mid is the interesting one. Pausing contributions during a drawdown means you
stop buying at exactly the moment prices are lowest — a real cost that appears
nowhere on a statement. Low sells at the bottom, mid fails to buy at the bottom,
and high does neither.

# Output — the cube

The PoC writes a cube: three rungs × four objectives × four shock counts. Each
cell carries the break-even rate, a status field for the cells where the two
choices never cross, both dollar outcomes at two miss sizes, and the ruin
fractions.

The dollar fields exist because the headline sentence compares two magnitudes —
what choosing correctly is worth against what moving up a rung is worth — and a
break-even expressed in tax points cannot make that comparison. They were
specified before the engine was written, since adding them later means running
everything again.

The status field exists because the tail objectives genuinely have no crossing
point inside a plausible range. That is an answer, not an error, and the demo
should not die on the interesting cases.

# Tests

Three suites, 189 tests. `tests/test_tax.py` — 35 tests, each defending a number
published in `DECISIONS.md`, with the literals restated by hand rather than
imported. `tests/test_engine.py` — opened at Sprint 2A, 128 tests: 54 over the
profile, the ladder, contributions and accumulation, 47 added at Sprint 2B over
the draw, decumulation, the D-26 policy branch, the objective reduction and ruin,
3 added post-2B over `geometric_mean`'s overflow (D-39), 24 added at Sprint
2C over the search, the bracket, the sentinel and the `Result` fields, and **19
added at Sprint 3A** over the bootstrap, the D-43 parameters, the digest,
`path-drawdown`, the overflow gate D-39 called *a gate whose failing input
cannot yet be constructed*, and the three measurement records. **One test was
DELETED at 3A rather than skipped** — `test_block_paths_still_raise` asserted a
`NotImplementedError` that no longer exists, and a test of scaffolding outlives
its subject silently. `tests/test_deploy_config.py` — opened at P3a, 8 tests parsing
`railway.toml`. Those eight guard the deploy config rather than the engine, and
they are counted here because `uv run pytest` runs them; the eight numbered
tests below are a different set entirely.

No sprint creates `tests/test_engine.py` — Sprint 2A opened it. **Sprint 4 closes
by collecting and mapping** T1–T8 into it, each docstring naming the sentence it
protects. **T1 and T2 are green as of Sprint 2B; T3, T4 and T5 as of Sprint 2C.**
T6–T8 are Sprint 3. Each asserts a claim made elsewhere in the docs:

| Test | Defends |
|---|---|
| T1 · Equal rates at both ends produce equal outcomes | The identity is real |
| T2 · `t*` unchanged across 4, 7, 9, 12 percent, **and the common draw cancels out of the difference** — `after_tax_trad(100) − roth(100)` is identical at draw = 0, $108,397 and $250,000 | The return rate never affects the choice. **Corrected at Sprint 2A:** the trajectories are not a scalar multiple of each other through decumulation, so the assertion is on the difference, not the ratio — and that is the stronger claim, holding for any `r` and any draw rather than the four sampled |
| T3 · At the $185,000 test profile with the cap binding, Roth shelters strictly more | The same-dollars trap, and why the limit matters |
| T4 · A no-crossing cell returns a sentinel rather than raising | The demo survives the interesting cases |
| T5 · **In the base case**, the today's-law marker is strictly below `t*` | You defer at marginal and withdraw across the whole structure from zero. **The scope is load-bearing and this row used to drop it:** at D-40's early-career preset the marker is 15.9% against `t*` = 12.0%, and that inversion is *why* the preset carries the flip. §6 has always read *in the base case*; this row and remaining-sprints' 2C done-when did not. Corrected at Sprint 2C, with the preset asserted as T5's teeth |
| T6 · Low rung — a shock realizes a sale; Traditional takes the penalty, Roth basis is free | The forced-liquidation branch |
| T7 · Mid rung — a shock skips a contribution year and nothing is sold | The shares not bought |
| T8 · High rung — a shock leaves the portfolio untouched | The control case |

T6–T8 assert the *mechanism*, not the magnitude. Three rungs are three code
branches, so three tests — a severity dial would have needed one.
