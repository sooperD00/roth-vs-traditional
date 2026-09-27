# Results

> **Working record.**
> I built this project with an AI model, and the model wrote much of this file during the build.
> The file keeps the build's bookkeeping: sprint numbers, two design gates (cold reviews by a fresh agent with no access to the design conversation), and decision IDs that resolve in [DECISIONS.md](DECISIONS.md).
> CONTEXT, TRADEOFFS, the sprint plan and the gate reviews are design-phase files I kept private.
> Start with the [README](../README.md).

**What this file is.** What building the model actually taught me, written as
results rather than as decisions. A decision row says what was chosen. This file
says what came back, what it cost to find out, and which parts I still cannot
reproduce on demand.

**Precedence.** `DECISIONS.md` wins on what was *decided*. This file wins on what
was *measured* — where a decision row and a result here disagree, the measurement
is the fact and the row is the stale copy. Nothing here is a contract and nothing
here plans a sprint.

**It is unfinished on purpose.** Sections that are done are written as finished
prose with their sources attached. Sections that are not done sit in the place
they belong, carrying the objection and a checklist instead of a conclusion. A
results file that only holds the finished results is a highlight reel.

---

## How to read a claim

Every claim in this file is one of four kinds, and the distinction is the whole
point of the file.

| | Kind | What it means |
|---|---|---|
| 📌 | **Assumed** | Chosen, not derived. Nothing below rests on it being *right* — it is the price of admission, and §1 lists all of them |
| 🔒 | **Derived** | Follows from the model's structure. A test asserts it; no measurement can confirm or refute it. If it fails, the code is broken, not the world |
| ✅ | **Measured** | A script or a self-test produces it. Re-runnable today, one command |
| ⚠️ | **Unsourced** | Published somewhere in this corpus, and nothing in the repo reproduces it. A claim in this state is an assertion wearing a number |

The distinction between 🔒 and ✅ is the one I most want a reader to hold.
`t*` = 32.5% at the base case is not a discovery — it is `t_now` restated, and
§2 explains why. The findings that cost something are in §4 through §8.

**Source lines** name the runnable thing first, then the record:

> *Source — `scripts/measure_3a.py` §1, captured in
> `scripts/out_measure_3a_20260818-1502.txt`. Recorded in D-05. Asserted by
> `tests/test_engine.py`.*

---

## Contents

| § | | Status |
|---|---|---|
| [1](#1--what-is-assumed) | What is assumed | complete |
| [2](#2--what-is-true-by-construction) | What is true by construction | complete |
| [3](#3--the-headline-numbers) | The headline numbers | complete |
| [4](#4--when-the-rule-moves) | When the rule moves | complete |
| [5](#5--the-return-model-and-a-reason-that-failed) | The return model, and a reason that failed | complete |
| [6](#6--running-out-of-money) | Running out of money | complete |
| [7](#7--life-events) | Life events | complete |
| [8](#8--fragility-against-the-account-choice) | Fragility against the account choice | complete |
| [9](#9--what-the-model-gets-wrong-on-purpose) | What the model gets wrong on purpose | **unsourced** |
| [10](#10--reproducibility) | Reproducibility | mostly complete |
| [11](#11--known-limits) | Known limits | what the model does not settle |

---

# 1 — What is assumed

Nothing in §2 through §10 is evidence that these are right. They are what had to
be fixed before anything could be computed at all, and every one of them is a
place a reader may disagree without disagreeing with a result.

## 1.1 Conventions — choices about what the model means

📌 These change what the numbers *are*, not how big they are.

| Convention | What it says | Recorded |
|---|---|---|
| **Same pre-tax dollars** | $X into Traditional against $X·(1−`t_now`) into Roth. Comparing same *nominal* dollars quietly favours Roth | D-01 |
| **Nothing clamps at zero** | Balances go negative; ruin is a recorded flag, not a floor | D-38 |
| **Common random numbers** | One path array, reused across every cell, both accounts, every bisection step | D-07 |
| **`t_now` is one scalar per profile** | The deferral rate at the current age, not recomputed per year | §5 |
| **Shocks land in accumulation only** | Ages 35–64. All three rung mechanisms are defined on a contribution stream | D-08 |
| **The draw is sized off the Roth** | The level real after-tax amount leaving 15% of the Roth's age-65 balance at 100 | D-39 |
| **The policy is Roth-only** | Traditional needs no branch, and that absence in the code *is* the asymmetry | D-09 |
| **Shock placement is the correlation** | Shocks go to each path's deepest `underwater-depth` years by `argsort`. There is no coefficient | D-08, D-45 |
| **The tie-break is the earlier year** | `argsort(kind="stable")`, named rather than inherited | D-46 |

## 1.2 Fudge factors — named numbers with nothing behind them

📌 A number I picked. The right-hand column is the honest one: it says whether I
went back and found out how much the pick was worth.

| Factor | Value | Chosen because | Sensitivity |
|---|---|---|---|
| Block length | **5 years** | Keeps history's bad sequences intact as sequences | ✅ run at 3A — §5.3 |
| Shock amount | **$40,000 real** | 1.6× a contribution year, so a forced sale and a skipped contribution are the same order of magnitude | ✅ run at 3B — §7.2 |
| Miss size `δ` | **10 points** | A two-point miss is optimistic for a forecast reaching fifty years out. Fixed *before* the sweep ran | ✅ crossing solved at 4A — §8.3 |
| Roth terminal margin | **15%** | So the base case does not sit exactly at zero | ✅ measured at 3A, and its justification did not survive — §6.1 |
| Paths | **2,000** | Enough for a stable p10, cheap enough for 48 cells | not swept |
| Seed | **20260815** | Reproducibility is the point, not the value | n/a |

## 1.3 Inputs — the archetype

📌 Every one of these is a control in the app. The panel resets them in seconds,
which is the intended use.

| Input | Value | Recorded |
|---|---|---|
| Income shape | (35, $165,000) · (38, $75,000) · (55, $200,000) · (65, $200,000), linear | D-19 |
| Savings rate | 20%, capped at the deferral limit | D-28 |
| State tax | 8.5% while working, none in retirement | D-21, D-30 |
| Retirement / terminal age | 65 / 100 | D-20 |
| Policy year `N` | 20 | D-09, D-26 |
| 2026 brackets, deduction, cap | Seven edges · $16,100 · $24,500 | D-21, verified against IRS IR-2025-103 and Rev. Proc. 2025-32 |

## 1.4 What is not modelled at all

📌 Named in the UI as not-done rather than silently absent. Two of these have a
measured size and are therefore results — see §9.

Employer match · the taxable side account · RMDs · Social Security · real
per-state tax rates · MFJ and Head of Household · over-65 deductions · SALT
deductibility.

*Source — DECISIONS §4's departure dispositions and the README's
`## Scope & Branches`.*

---

# 2 — What is true by construction

🔒 These are the results that cost nothing to find and everything to state
clearly. They are properties of the algebra, not of the data, and the test suite
asserts them rather than measuring them. **A reader who mistakes one of these for
a discovery has misread the project.**

## 2.1 The return rate cannot change the answer

`(1−t)·(1+r)ⁿ` and `(1+r)ⁿ·(1−t)` are the same expression. The growth factor
appears identically on both sides and divides out. Whether the market returns 7%
or 12% cannot move which account wins.

**Measured at the archetype, `t*` = 32.5000% at every `r ∈ {4, 7, 9, 12}%`** —
not approximately, and not four coincidences. The cancellation is exact, and the
sweep exists so a skeptic can try to break it.

This holds *only* under the same-pre-tax-dollars convention (§1.1). L1 is a
consequence of that choice rather than a separate fact, which is why the app
states the convention in a sentence rather than burying it.

*Source — `uv run python engine.py`, the `2C OK` line. Asserted by
`tests/test_engine.py` as T1 and T2 (five functions). Recorded in D-01, D-22.*

## 2.2 In the base case the break-even is your current rate, restated

Under D-01 the after-tax Traditional trajectory is the Roth trajectory scaled by
`(1−t_later)`. So with no asymmetric mechanism running, `t*` **is** `t_now`.

**32.5% is a definition, not a finding.** The app says so in as many words —
*at these settings the break-even is just your current combined rate; here is
what moves it* — because a number that looks like a result and is not is the
easiest thing on the page to over-trust.

Measured: `t*` lands **3 ulps** from `t_now` at the archetype and **20** at the
early-career preset. That gap is float representation, not modelling.

*Source — `engine.py` `2C OK` line. Recorded in D-22, GATE-2 §1.*

## 2.3 The accumulation ratio is exact

`roth₆₅ / trad₆₅ == 1 − t_now`, at every rung, every return rate, and every shock
count **as long as no shock forces a sale.** Measured: `0.675000000000` against
`1 − t_now` of `0.675000000000`.

This is the cheapest test in the project and the most useful. A broken
contribution rule moves it by roughly 1e12 ulps; the gate is 4 ulps.

*Source — `engine.py` `3B OK` line. Asserted as T7 and T8. Recorded in D-22.*

## 2.4 Two thirds of the cube is derivable before it runs

Only the Low rung's forced sale is asymmetric between the two accounts. Mid
pauses contributions and High absorbs the shock in cash — neither touches the
ratio in §2.3. So **36 of 48 cells must equal `t_now` exactly**, and the
interesting cells are the 12 at Low with at least one shock.

**The collapse is a cliff, not a gradient**, and that is the stronger statement.
It was derived first and confirmed second, which is the order that makes the
confirmation worth something.

*Source — `python spike_grid.py --check cube.json`, the 36-cell slab invariant.
Recorded in D-22, split by operand in D-51. See §8.4 for the one wrinkle.*

---

# 3 — The headline numbers

✅ Everything here comes out of the deterministic engine at 7% real, and
reproduces from one command.

| | Reference archetype | Early-career preset |
|---|---|---|
| Income now | $165,000 | $60,000 |
| `t_now` = `t*`, rules hold | **32.5000%** | **12.0%** |
| Today's-law effective marker | **15.1849%** | **15.9%** |
| Verdict | Traditional by 17.3 points | **Roth** by 3.9 points |
| `t*` if treatment moves at year 20 | **58.4064%** | **29.1%** |
| Verdict under the policy | Traditional, by more | **Traditional** — flipped |
| Traditional balance at 65 | $2,108,867 | $1,749,149 |
| Roth balance at 65 | $1,423,485 | $1,539,251 |
| Frozen allowance at year 20 | $607,475 | ⚠️ $631,049 |
| Modeled draw | $108,397/yr, 54% of final income | ⚠️ $117,212/yr, 59% |

⚠️ **Two cells in that table are not reproducible and both are the preset's.**
The preset's frozen allowance and its modelled draw appear in `README.md` and
here, and **nowhere in the code** — no test asserts them and no self-test line
prints them, while every archetype figure beside them is asserted and every other
preset figure (`t*`, the marker, the policy threshold, both balances) is too.
They are the two cells of the headline table that a cold reader cannot check.
This is the same defect class as §9, one table over and much cheaper to close.

- [ ] Add the preset's allowance and draw to `engine.py`'s `2B` self-test line,
      or assert both in `tests/test_engine.py` with the literals restated by hand
- [ ] Until then, treat both as design-phase figures rather than engine outputs

**The two rates on that list are different units and the axis says so.** You
defer at a **marginal** rate and withdraw across the whole bracket structure from
zero, which is an **effective** rate. Without that sentence the natural misreading
is *my rate is 15.2%, the break-even is 32.5%, so my taxes would have to double* —
and that is where a careful non-expert lands unaided.

**The draw is 54% of final income, not the 80% every replacement-rate table
publishes.** That is reported as an outcome rather than hidden: a $24,500 cap
cannot fund 80% of a $200,000 income at any return rate, and the rest would have
to come from Social Security and the taxable account this model does not contain.
An earlier version assumed 80% and bankrupted both accounts — Roth at 79,
Traditional at 92.

*Source — `uv run python engine.py`, the `2A`, `2B` and `2C` lines. Every figure
restated by hand and asserted in `tests/test_engine.py`. Recorded in D-15, D-19,
D-24, D-26, D-39, D-40. The 80% failure is GATE-2 §3.*

---

# 4 — When the rule moves

✅ **The strongest single finding in the project, and the design deck had it
backwards.**

The scenario is "nevermind": after year 20, Roth withdrawals above a frozen
allowance become ordinary income. Traditional is untouched.

**A policy that harms only Roth raises the rate at which Roth becomes
worthwhile.** Solving for the tie under D-26's frozen allowance `A`:

```
t*_policy  =  t_now · T₆₅  /  ( t_now · T₆₅ + A )
```

which exceeds `t_now` whenever `A < R₆₅` — and `A` is the Roth balance eleven
years before 65, so it always is. The threshold moves **right**, away from the
marker. **32.5% → 58.4%**, against a 15.2% marker.

So the scenario you were told makes Roth safe is the one that widens
Traditional's lead.

**The error is traceable, which is why it is worth writing down.** The accordion
mockup's note read *"in year 20 all tax benefits go away."* All benefits —
including Traditional's deduction — could plausibly move the threshold down.
D-09 narrowed it to Roth only, for a good reason, and **the graphic was never
recomputed.** A decision moved and a picture did not follow it. The deck drew the
second threshold at 14% with Roth winning to its right, which requires the policy
to *help* Roth.

**The flip is real, and it belongs to someone else.** At the early-career preset:
12.0% under current rules against a 15.9% marker, so Roth — then 29.1% once the
rule moves, so Traditional. **The rule change costs the low-bracket saver Roth was
supposed to be for.**

*Source — `engine.py` `2C OK` line, both profiles. Recorded in D-26, D-40.
Found at design gate two by a fresh agent working from the documents alone —
`review/GATE-2.md` §2. Narrative in `DESIGN.md` part 4.*

> **One caveat on the algebra, and it does not change the conclusion.** Both terms
> are future values at 100. Substitute age-65 magnitudes into the expression above
> and it returns **53.0%**, not 58.4% — so a reader recomputing by hand will land
> somewhere else. The inequality, and therefore the whole argument, is unaffected.
> D-40 carries the corrected form.

---

# 5 — The return model, and a reason that failed

This is the section where the project's own methodology got tested on itself.

## 5.1 The block bootstrap was chosen to fatten the tail. It thins it. ✅

The reason written first: a life event costs far more when it forces a sale
during a downturn, and that needs bad years to arrive in runs. Draw years
independently and a crash is followed by an ordinary year, so the mechanism
survives and the magnitude does not.

Then it was measured, over the 30-year accumulation window:

| | Block(5) | IID |
|---|---|---|
| Median `path-drawdown` | −42.2% | −42.0% |
| **p10 `path-drawdown`** | **−59.6%** | **−63.7%** |
| Year after the worst year | **+17.1%** | +10.1% |
| Next three years, cumulative | **+39.9%** | +33.2% |

**Block has the thinner left tail and the faster rebound.** It is the
conservative model here, which is the opposite of what was claimed.

**One number explains it.** The lag-1 autocorrelation of annual US real returns
is **−0.035** — essentially zero, faintly negative. The runs intuition is real at
daily and monthly frequency and real in the narrative of 1929–32, but
ninety-eight annual observations cannot see it. And this record's crashes came
packaged with their own recoveries: 1931 sits in a block with 1933, 1974 with
1975, 2008 with 2009.

**One row carries the finding and one does not.** Across five seeds the p10 pair
says *block thinner* five times out of five; the median pair splits three to two
at a gap of a few tenths of a point. **The median row is sampling noise and must
be read as noise.** Measure on one seed and a median inversion reads as a defect
worth an afternoon.

**The pick survives on a different argument than the one it was chosen for.** A
Low-rung shock sells $40,000 at a depressed price, and what it costs is the
compounding forgone — so a *faster* rebound makes that cost **larger**, not
smaller. That is the channel that holds. The failed reason is written down rather
than quietly replaced, and measuring the fudge factor is what caught it.

*Source — `scripts/measure_3a.py` §1 and §1b, 4,000 paths averaged over five
seeds, captured in `scripts/out_measure_3a_20260818-1502.txt`. Recorded in D-05,
R8. Both readings asserted in `tests/test_engine.py` — the p10 as a direction,
the median as noise.*

## 5.2 The window was load-bearing and was missing from the caption ✅

Read "each path" as the whole 65 years instead of the 30-year accumulation window
and the same measurement returns −51.9% / −53.0% and −66.7% / −72.0%. Every
number above goes stale in five documents at once.

Accumulation is the right window because that is where a shock lands (D-08). The
caption now says so. **This is a result about documentation, not about markets,
and it is here because it nearly cost five documents their numbers.**

*Source — `ENGINE.md`, the block-vs-IID table caption. Found at Sprint 3A.*

## 5.3 Block length is the larger fudge factor, and it gates nothing ✅

| Block length | Median `path-drawdown` | p10 `path-drawdown` |
|---|---|---|
| 3 | −44.7% | −65.1% |
| **5** | **−42.6%** | **−59.4%** |
| 10 | −41.8% | −54.8% |

**Monotone.** A shorter block breaks history's runs into smaller pieces and
deepens the tail; a longer one averages over more of the record and shallows it.

**The p10 spread across that range is about ten points, which is wider than the
block-versus-IID gap §5.1 is about.** The arbitrary number moves the tail more
than the modelling choice does. Nothing published moves with it — the cube ran at
five — and the direction is what the sensitivity was for.

*Source — `scripts/measure_3a.py` §5, 4,000 paths at seed 20260815, same
capture file. Table published in `ENGINE.md`.*

## 5.4 A number reproduced and the sentence attached to it did not ✅

Two documents read *the median path's worst five-year run lands at −10.26%, which
is exactly 1937–41.*

**The number reproduces: −10.28%.** The clause does not. Only **12.6%** of paths
draw that block at all. The median path's worst run is a rolling window that
usually straddles two drawn blocks and happens to score the same depth. Read
strictly to the blocks themselves, the median path's worst *drawn* run is
**−7.27%**, which is 1973–77.

Same shape as §5.1: the measurement stands, the story told about it was tightened.

*Source — `scripts/measure_3a.py` §2, same capture. Corrected in D-05 and
`ENGINE.md` at the 3A docs pass.*

## 5.5 The honest limit ✅

Ninety-eight years at block length five is about **19.6 independent blocks.**

That is the same n ≈ 5 critique this project makes of Bengen's 4% rule, now
pointed at this model. **The structure assumption cannot be validated at n ≈ 20;
it can only be stated.** Saying it first is the whole defence.

## 5.6 One quantity, three published values ✅

`p10 path-drawdown` at block 5 appears three times at three slightly different
numbers, and none supersedes another.

| Value | What produced it |
|---|---|
| **−59.6%** | `measure_3a.py` §1 — 4,000 paths **averaged over five seeds** |
| −59.4% | `measure_3a.py` §5 — 4,000 paths at **seed 20260815 only** |
| −59.3% | `uv run python engine.py`, the `3A OK` line — **2,000 paths** at the same seed |

**Quote the five-seed figure.** A reader who finds two of these and assumes one
is a typo has found the reason this note exists.

*Source — reconciliation table in `ENGINE.md`.*

---

# 6 — Running out of money

## 6.1 The base case ruins about half the time regardless of margin ✅

D-39 sizes the draw to leave 15% of the Roth's age-65 balance at 100, so the base
case is not sitting exactly at zero where any shock ruins every objective at once.

**Over 2,000 shock-free block-bootstrap paths, the Roth balance goes negative
before 100 about half the time.** Three seeds: **48.7%, 48.2%, 49.4%.**

That is sequence-of-returns risk rather than a tuning error. A level real draw
against a 19.30% standard deviation over 35 years ruins about half the time by
construction, and no plausible margin closes it.

**The figure was re-measured rather than inherited, and it moved in the direction
that would have flattered us.** The original 53.1% was taken with the draw sized
at the 7% deterministic solve; Sprint 2B pinned the bootstrap draw at the series'
own compounded rate, which is a smaller draw and therefore less ruin. It fell four
points and did not fall far enough to matter.

**The consequence was a gate that could not pass.** Sprint 4A had been written to
require *ruin is 0.0 across the 0-shock slab*. It was replaced with *ruin is
measured and reported on the slab, and rises with shock count* — reporting the
number as a finding rather than engineering around it.

*Source — `scripts/measure_3a.py` §3, captured in
`scripts/out_measure_3a_20260818-1502.txt`. Recorded in D-39 and R9.*

## 6.2 Ruin rises with shock count, as it should ✅

At the Low rung, read at a common `t_now`:

| Shocks | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Ruin | **48.70%** | 55.95% | 65.40% | 74.20% |

*Source — `scripts/measure_4a.py` §2, captured in
`scripts/out_measure_4a_20260819-2237.txt`. The per-cell reading published in
`cube.json` is D-50's; this common-rate reading is the script's.*

## 6.3 Nothing is floored, and the tail numbers are signed 🔒

A path that runs out at 72 keeps compounding a negative number for 28 more years.
So objective 4's tenth percentile is deeply negative — **−$9,506,737** for Roth
and **−$11,109,050** for Traditional at Low with one shock.

**Those are not wealth figures. They are depth of hole at the tenth percentile.**
The gap between them is real and the levels are not spendable, which is one
reason §8.3 prefers the dot plot over the dollar sentence.

*Source — `scripts/measure_4a.py` §4. The no-clamp rule is D-38, and §2.1 is why
it cannot be relaxed: clamp the balances and the difference goes flat over a range
of rates, and bisection returns whichever endpoint it started nearest.*

---

# 7 — Life events

Three rungs, three code branches. Low sells at the bottom, Mid fails to buy at the
bottom, High does neither.

**All six results in this section are reproducible.** Three of them were not
until the results pass: D-45, D-46 and D-47 each carried measured numbers in
prose with no runnable source, which is 3A's defect one sprint later. They are now
`scripts/measure_3b.py` §4, §5 and §6 — one script, as predicted, and **two of the
three published figures did not survive the re-run.**

## 7.1 Placement matters, and it is the cheapest demonstration in the project ✅

Shocks are placed at each path's deepest drawdown years. Flipping to uncorrelated
placement scatters them randomly. Measured at Low over 2,000 paths, Traditional's
balance at 65 at the tenth percentile:

| Shocks | Correlated | Uncorrelated | Difference |
|---|---|---|---|
| 1 | $851,000 | $893,087 | **−4.71%** |
| 3 | $576,048 | $666,761 | **−13.60%** |

**Note what this does and does not demonstrate.** The sentence used to read
*deflates the tail visibly* with nothing behind it. It is now measured — but §5.1
already showed the *return model* does not fatten the tail. So the toggle's job is
narrower than it was written: **it shows that shock placement matters, not that
the return model does.**

*Source — `scripts/measure_3b.py` §1, captured in
`scripts/out_measure_3b_20260818-1607.txt`. Published in `ENGINE.md`.*

## 7.2 The shock magnitude is load-bearing, and $80,000 breaks the model's premise ✅

$40,000 was picked at 1.6× a contribution year. Measured at $25,000 and $80,000,
at Low, three shocks, 2,000 paths:

| Shock | Gross sale at 55 | All-in cost | `trad₆₅` median | `roth₆₅` median |
|---|---|---|---|---|
| $25,000 | $43,657 | 42.7% | $1,613,286 | $1,135,589 |
| $40,000 | $73,960 | 45.9% | $1,217,364 | $925,751 |
| $80,000 | $158,506 | 49.5% | **$295,296** | **$390,411** |

**At $80,000 the account ordering reverses.** Traditional finishes below Roth —
and `trad₆₅` is pre-tax while `roth₆₅` is already after tax, so on the median path
there is no retirement tax rate, including zero, at which Traditional recovers.
**The breakeven does not move. It stops existing.**

**Two multipliers produce it, one fixed and one growing.** Traditional starts
ahead by `1 / (1 − t_now)` = 1.481×, because the deferral buys more shares. But
each forced sale costs Traditional 1.98× what it costs Roth. That second
multiplier is the one that moves — the gross sale runs 1.75×, 1.85×, 1.98× across
the three shock sizes, because the withdrawal climbs the bracket table as it
grows. A fixed head start against a growing per-shock penalty, and enough shocks
consume it.

**The crossing is at $67,471** — 2.75× a contribution year, against the 1.63×
that was chosen. So $40,000 sits at 59% of the flip point: inside the safe
regime, but not by an order of magnitude, and that is now a number rather than a
hope.

**This is the finding the deterministic model cannot produce.** With no shocks the
ratio is pinned at `1 − t_now` exactly (§2.3). The reversal is reachable only
through the one asymmetric mechanism in the cube — the 10% penalty plus the
incremental bracket on a forced sale. **Tax deferral is leverage, and leverage
amplifies both directions.**

**Read it with its limits.** Both outcomes at $80,000 are bad — those are
near-ruin balances after a career of $24,500/year contributions. And it is a
median, not a distribution.

*Source — `scripts/measure_3b.py` §2, captured in
`scripts/out_measure_3b_20260818-1607.txt`, which is the run carrying the
bisected crossing. Reasoning that promoted this from a sensitivity row to a
headline result is in `scripts/learning_3b_20260818-1502.txt`.*

## 7.3 A published pair did not reproduce, and the run identified why ✅

D-22 published Low's `roth/trad` ratios as `.689633` and `.708591`. The engine
returns **0.705664** at one shock and **0.855412** at three.

**They do not reproduce, and the measurement says what produced the originals
rather than guessing.** A negative result recorded as a negative result.

*Source — `scripts/measure_3b.py` §3. Also printed on `engine.py`'s `3B OK` line,
so the disagreement is visible on every run rather than filed away.*

## 7.4 Which drawdown reading, and what the choice was worth ✅

D-08 says shocks land at each path's `n` deepest drawdown years. **That reads two
ways, and the two readings are not close.** `underwater-depth` — how far below its
running peak the index sits at the end of a year — was chosen over
`worst-year-return`, the annual return itself.

**The year sets are nearly disjoint at three shocks.**

| Shocks | Identical year set | Year-0 share, `worst-year-return` |
|---|---|---|
| 1 | 56.9% | 4.3% |
| 2 | 24.4% | 3.3% |
| **3** | **8.1%** | **3.2%** |

**Year 0 is structurally unshockable under the chosen reading** — the index at
year 0 is its own running peak, so the curve is exactly 0.0 there on every path
and nothing sorts below it. Measured: 0.0%. The rejected reading put 3.2% of its
shocks there, in the year cumulative Roth basis is one contribution against a
$40,000 sale.

**Where the shocks land, at three shocks:**

| Reading | Paths basis-short | Mean shock age | Mean next-year return |
|---|---|---|---|
| `underwater-depth` | **5.05%** | 51.0 | **+18.66%** |
| `worst-year-return` | 19.20% | 49.2 | +12.63% |

**Two channels carry the difference and they partly offset.** The chosen reading
shocks **later** years — less compounding left to forgo — but **harder** ones,
because the recovery channel §5.1 identified is steeper after a deep drawdown than
after a single bad year.

**So the year sets differ a lot and the aggregate barely does.** Mean forgone
multiple, what one shocked dollar would have grown to by 65: **5.0550×** against
**5.0326×**, 0.44% apart.

That is unflattering to the choice and it is the reason the pick rests on the
three structural arguments — the word used honestly, year 0 unshockable, a quarter
as many shocks where basis is short — rather than on a dollar difference.

**One thing this measurement caught in its own code.** The forgone multiple has to
compound from year `y+1`, not `y`: under D-20 the balance takes year `y`'s return
first and the sale comes out after it. Including year `y` penalises whichever
reading selects the worse annual return — `worst-year-return`, by construction —
and reported a false 14.7% gap instead of 0.44%. `_growth_after()`'s docstring
carries it so nobody re-derives it wrong.

*Source — `scripts/measure_3b.py` §4, 2,000 paths at seed 20260815, captured in
`scripts/out_measure_3b_20260820-2115_claude.txt`. Recorded in D-45. **All six published
figures reproduce.***

## 7.5 The tie-break, and the number that was measuring the wrong thing ✅

`argsort(kind="stable")` resolves ties to the earlier year, named rather than
inherited, because **numpy's default is introsort and is not stable** — two
documents had asserted that it was.

**Ties are ordinary here, which is the precondition.** A path is dealt from a
98-value deck with replacement, so duplicates inside a 30-year window are the
common case:

| | |
|---|---|
| Paths carrying a duplicate annual return | **80.80%** |
| Paths carrying a duplicate underwater depth | **99.75%** |

**A duplicate only matters when it straddles the n-th position of the sort:**

| Reading | Exact tie at n=3 | ORDER differs | **SET differs** |
|---|---|---|---|
| `underwater-depth` | 3.15% | 2.25% | **1.55%** |
| `worst-year-return` | 12.85% | 11.00% | **7.80%** |

**The two right-hand columns are different questions and only one of them can
move a number.** ORDER counts a permutation of the same three years. SET counts a
genuinely different year being shocked. `shock_years()` returns
`tuple(sorted(picks))`, so **a reordering is discarded one line later and the
engine never sees it.**

**D-46 published the ORDER pair.** It reproduces exactly — 2.25% and 11.00%, both
numbers — but it is an upper bound on the exposure rather than the exposure. The
real figure is about a third smaller.

**The correction runs against the decision, which is why it is worth making.**
D-46's argument survives untouched: 1.55% of 2,000 paths is 31 paths, and D-07's
reproducibility is binary rather than proportional — a cube is byte-identical or
it is not. Only the number changes.

**It is not a version effect, and that was the first hypothesis.** numpy 2.4.2 and
2.4.4 return identical figures in every column. The section prints the numpy
version anyway, so a future disagreement is readable rather than mysterious — the
comparison arm is the unfrozen one, and that mobility is the whole exposure D-43
chose MT19937 to close one sprint earlier against a different library default.

*Source — `scripts/measure_3b.py` §5, same capture. Recorded in D-46, which now
carries both columns.*

## 7.6 The gross-up base ✅

Low's forced sale grosses up against `income(age) − contribution`, not gross
income. That year's deferral already came off the top, so a withdrawal stacks on
what is left.

**Across the archetype's thirty accumulation years the unfixed base overstates the
sale by 0.1% to 5.8%** — near zero at age 48, where the sale sits inside one band
under both bases so the deferral moves nothing, and 5.8% at the age-55 income
peak.

**At that peak it decides a bracket:**

| Base | Gross sale | Taxable | 32% edge at $256,225 |
|---|---|---|---|
| D-47, net of deferral | $73,959.60 | $233,360 | below |
| D-16 as written, gross | $78,280.11 | $262,180 | **crosses** |

**Over the path set — three shocks, 2,000 paths, compounded forward at each path's
own returns — the unfixed base is worth $22,936 mean at 65.** As a share, it
depends entirely on the denominator:

| Denominator | Share |
|---|---|
| mean `trad₆₅`, Low, three shocks | **1.46%** |
| mean `trad₆₅`, bootstrap, no shocks | 0.88% |
| `trad₆₅` deterministic 7%, $2,108,867 | 1.09% |

**D-47 published 1.09%, which divides a stochastic Low-with-three-shocks numerator
by the deterministic headline balance.** The numerator reproduces to the dollar;
the denominator is a different population. **1.46% is the share of what a shocked
saver actually holds**, and it is the one D-47's own sentence is about.

**The direction is why this is a decision rather than a footnote.** The unfixed
reading *overstates* Low's penalty — the direction that flatters this project's
own lesson about fragility, and precisely the failure mode §5.1 exists to name.
Read proportionally against D-16's own published lever, three flat gross-up
readings spanning 3.5 points of `t*`, a share this size is worth roughly a point.
**No published figure moves**: D-16 publishes `t*` for the three flat readings
only, and the exact method is a fourth value with no number attached.

*Source — `scripts/measure_3b.py` §6, same capture. Recorded in D-47, whose range
and denominator were both corrected here.*

# 8 — Fragility against the account choice

This is L3: for most people, where you sit on the resilience ladder moves the
outcome more than the account election does. It is a comparison of magnitudes,
and the cube exists so both magnitudes are on the same page.

## 8.1 The collapse ✅

Break-even at objective 4, across shock counts:

| Rung | 0 shocks | 1 | 2 | 3 |
|---|---|---|---|---|
| **Low** | 32.5000% | 30.8987% | 28.0158% | 24.4070% |
| Mid | 32.5000% | 32.5000% | 32.5000% | 32.5000% |
| High | 32.5000% | 32.5000% | 32.5000% | 32.5000% |

**8.13 points of movement at one rung and none at the other two** — not
approximately none, exactly none, for the reason §2.4 derives. **The account
question is contested for people without a buffer and settled for everyone else.**

*Source — `scripts/measure_4a.py` §1, captured in
`scripts/out_measure_4a_20260819-2237.txt`.*

## 8.2 The objective menu is contested only at Low ✅

Across objectives 1, 3 and 4 the break-even spread is **1.4656 points at Low with
three shocks** and **exactly 0.0000 at Mid and High**, at every shock count.

The design expectation was *same inputs, swap the objective, watch the answer
flip* — a demo about the definition of "optimal." **The divergence is real and it
is not a property of the objective menu.** It is §8.1 read down a column instead
of across a row.

**That is not a smaller lesson than the one intended.** It says the definition of
optimal is contested for exactly the population the fragility argument is about.
The radio button stays; its caption changes from *watch this move* to *watch who
this moves for*.

*Source — `scripts/measure_4a.py` §1, same capture.*

## 8.3 The design estimate was wrong by about eight times, and δ is why ✅

The design deck said moving up a resilience rung was worth about **four times**
getting the account right. Measured at the cell the app's sentence reads —
objective 4, one shock, the Low rung:

| | δ = 2 points | δ = 10 points |
|---|---|---|
| **$X** — getting the account right | $264,662 | $1,602,313 |
| **$Y** — moving up one rung | $756,988 | $756,988 |
| ratio | 2.86× | **0.47×** |

**$Y does not move, and that is not a rounding artifact.** Under current rules a
Roth terminal value does not depend on the future tax rate at all. Roth is the
better account on every cell in this grid, so $Y is a difference between two Roth
outcomes and the rate never enters it. $X is a difference between Roth and
Traditional, and Traditional's after-tax terminal falls as the rate rises.

**So δ chooses the verdict.** Solved on all four objectives:

| objective | δ where $Y = $X |
|---|---|
| 1 — mean terminal | 6.10 points |
| 3 — median terminal | 5.58 points |
| 4 — p10 terminal | 4.82 points |
| 5 — P(not running out) | 5.56 points |

Below roughly five points the buffer dominates and the design estimate holds in
direction if not in size. Above it the account choice dominates. **The app prints
δ = 10.** The four crossings sit within one point of each other, so the inversion
is structural rather than a property of the one cell quoted.

**δ is not a model parameter.** It is the assumed size of the user's miss — how
wrong their guess about their own future marginal rate turns out to be — and
nothing in the model constrains it. It was fixed at 10 **before** the sweep ran,
on the grounds that a two-point miss is optimistic for a fifty-year forecast.
That choice, made blind to the result, is what inverted the headline.

**I did not move δ afterward and I did not switch objectives.** Either would have
produced a sentence that reports the parameter I picked rather than the model I
built. All four objectives ship at both deltas and the crossing is published, so
a reader sees the choice instead of inheriting its result.

**The 4× is retired, not restated. And the claim it was built to carry survives
on a different instrument** — the dot plot in §8.1 shows the same lesson with no
arithmetic and no parameter I had to choose.

*Source — `scripts/measure_4a.py` §3 and §5, captured in
`scripts/out_measure_4a_20260819-2237.txt`. Recorded in D-17, D-23. The
retirement of the 4× is in `DESIGN.md` 3.1.*

## 8.4 One objective reads slightly low, and it is the solver, not the model ✅

Objective 5 sits about **0.08 points below `t_now`** across the whole slab. That
is a sampling artifact in the search, not a modelling result, and here is the
measurement that says so.

`P(not running out)` counts a discrete event over 2,000 paths, so it takes 2,001
values and its step is exactly `1/2000`. **The difference is not zero at a point —
it is zero across an interval:**

```
t_later    P_trad   P_roth      diff
0.32420    0.5135   0.5130    +0.000500
0.32430    0.5130   0.5130     0.000000   <- plateau opens
0.32500    0.5130   0.5130     0.000000   <- t_now, 48.4% of the way across
0.32550    0.5130   0.5130     0.000000
0.32600    0.5125   0.5130    -0.000500   <- plateau closes
```

Bisected edges: **[0.324218010830, 0.325834192065]**, width **0.1616 pp**.

`breakeven()` tests whether the sign changed. An exact zero reads as *not
positive*, so the interval closes from the right and the solver returns the
**left edge** every time — deterministically, reproducibly.

**The underlying claim is exact and is asserted directly instead:**

```
f(t_now) == 0.0  EXACTLY, on all 9 objective-5 slab cells.
```

Verified bit-exact on all nine. The other 27 slab cells are continuous in the
rate, so bisection lands within a few ulps — worst measured, **9**.

**So the slab check is two assertions over two operands rather than one over 36
cells.** No bound on `breakeven` would be honest at any width, because it would be
sized against a sampling artifact that shrinks as `n_paths` grows.

*Source — taken by hand at the Sprint 4A assessment, calling `engine.breakeven()`
and `engine.outcome()` directly with no sweep code in between. Recorded in D-51.
The split is enforced by `spike_grid.validate_cube()` and captioned in
`cube.json`'s header.*

### 8.4b The engine fix that was measured and rejected ✅

The obvious repair is to bisect to the plateau's midpoint instead of its left
edge. Measured before deciding:

| | Deviation from `t_now` |
|---|---|
| Today — plateau left edge | **−0.0782 pp** |
| After the fix — plateau midpoint | **+0.0026 pp** |
| Exact | 0.0000 pp |

**A 30× improvement that is still not exact.** The gate would still need a
tolerance, that tolerance would still be sized against a sampling artifact, and
the artifact still shrinks with `n_paths` and moves with the seed. **The fix buys
a smaller wrong number, not a right one** — for two bisections instead of one, a
branch three objectives never take, and a re-verification of the whole suite.

**The reason underneath is the real one.** The plateau is a property of the
*sample*, not of the model. Over the population `P(not running out)` is a smooth
curve crossing cleanly at `t_now`. Changing the solver to chase a step edge treats
a sampling artifact as a bug in the search.

**If it ever becomes a product problem rather than an assertion problem, the cheap
lever is `n_paths`, not the solver.** The width falls roughly as `1/n_paths`, so
20,000 paths puts it under a basis point without touching a line of `engine.py`.

*Source — same assessment. Recorded in D-51 and in `remaining-sprints.md` Tech
Debt as Phase N.*

## 8.5 Every cell crosses, so the no-crossing path is untested at cube scale ✅

All 48 cells return a break-even. **No cell in this cube exercises the sentinel.**

That is recorded rather than repaired: a sprint cannot assert the presence of a
case the model does not contain. The sentinel is green at a different archetype —
a $185,000 flat profile where both contributions bind at the cap — so the code
path is tested, but the guarantee rests on a profile the cube does not hold.

**Sprint 6 can be handed a profile that does not cross, and the app is forbidden
to print nothing.** That is the live exposure.

*Source — `python spike_grid.py --check cube.json`, `0 non-crossing`. Asserted as
T4 in `tests/test_engine.py`. Recorded in R3 and D-42.*

---

# 9 — What the model gets wrong on purpose

⚠️ **UNSOURCED — and this is the section I would least like a reviewer to ask
about, because it is the one where the argument depends most on the numbers.**

**The claim.** Two simplifications bend the answer in opposite directions, and
both are stated with their size and direction rather than discovered by a reader.

| Simplification | Direction | Size |
|---|---|---|
| Over-65 deductions omitted | **understates** Traditional | marker 15.2% → **13.5%**, so 1.7 points |
| SALT deductibility ignored | **overstates** Traditional | `t*` 32.5% → **30.5%**, so 2.0 points |

They point opposite ways and roughly cancel. **That is a convenience, not the
defence.** The defence is that both are stated: *a model whose author cannot say
which way its stubs bend the answer is a model nobody should trust with a
thirty-year decision* — which is, in a smaller way, the same argument this project
makes about the escalator hiding in a spreadsheet cell.

**The objection.** Nothing computes either number. `tax.py` carries both as
comments; `ADDITIONAL_DEDUCTION_65` and `OBBB_SENIOR_DEDUCTION` are present as
constants and **deliberately unwired**, so no code path produces the 13.5%. No
test asserts either figure.

**Both are cheap to close.** The over-65 side is one conditional on age. The SALT
side is applying the state rate inside the federal calculation rather than beside
it: `0.24 + 0.085 × (1 − 0.24)` = 30.5%, and it bites only on itemizers — state
income tax alone is $14,025 at the archetype against a $16,100 standard deduction,
so it takes about $2,075 more of mortgage interest, property tax or charity to
cross.

- [ ] Compute the over-65 marker by wiring `ADDITIONAL_DEDUCTION_65` behind a
      flag, and record the delta — do **not** hard-code 13.5%
- [ ] Compute the SALT `t*` the same way, behind an itemize flag
- [ ] Assert both deltas in `tests/test_tax.py`, literals restated by hand per
      that file's own rule
- [ ] Replace the four cited copies with a pointer here
- [ ] Decide whether the $6,000 OBBB senior deduction is in scope at all — it
      phases out and it sunsets, and applying it across a 35-year retirement
      asserts something the statute does not say

**Also unsourced and smaller:** D-21's straddle-band worst-error columns
(9.92 / 1.99 / 7.99 at the sample, supremum 10.0 / 2.0 / 8.0). Nothing computes
them, though `tests/test_tax.py` uses the rounded sample points. Flagged here
rather than fixed, because it may belong in the tax contract rather than in a
results file.

---

# 10 — Reproducibility

Not results about retirement, but results about whether the results survive
being moved.

## 10.1 The cube is byte-reproducible from an integer ✅

Two runs at the same seed produce byte-identical files, and the same cube written
on a different operating system is byte-identical to the committed one.

Every header field is deterministic — a `generated_at` field was removed for
making byte-identity unpassable by construction. Two digests make the artifact
checkable from the outside:

| Field | Covers | Value |
|---|---|---|
| `paths_digest` | Everything upstream of the path array — seed, path count, horizon, kind, block length, the return series itself | `48f9c1b9…` |
| `constants_fingerprint` | Everything downstream — seven model constants plus two derived probes that reach the whole of `tax.py` without importing it | `c00a6211…` |

The two cover disjoint halves. Changing the shock amount moves every cell and
leaves `paths_digest` untouched, because shocks are applied long after the array
exists — which is exactly why the second field exists.

**`--check` re-derives rather than re-reads.** It rebuilds the array from the
header and compares it against the digest before checking a single cell. Until
Sprint 4A nothing in the repo did that, so the digest was a header field no code
verified.

```
uv run python spike_grid.py --out /tmp/cube_a.json
uv run python spike_grid.py --out /tmp/cube_b.json
sha256sum /tmp/cube_a.json /tmp/cube_b.json cube.json cube_reference.json
uv run python spike_grid.py --check cube.json
```

*Source — `spike_grid.py --check`, which prints both digests and the invariant
count. Recorded in D-41, D-49, D-51, D-52.*

## 10.2 A same-machine gate cannot see the failure that actually happened ✅

The cube came out **23,216 bytes on Linux and 24,280 on Windows** — exactly 1,064
bytes against 1,064 lines. A line-ending conversion on checkout: content
survives, `sha256` does not, and nothing in the repo would notice.

**Two runs on one machine agree with each other whichever convention that machine
uses.** So `cube_reference.json` exists — the same cube written on a different OS,
committed so the local run can be hashed against it. It is the half a same-machine
comparison cannot see.

Both sides need pinning and either alone still loses: `write_cube()` writes bytes
rather than text, and `.gitattributes` pins the checkout side to `eol=lf`.

*Source — `.gitattributes`'s own header comment, and
`docs/design/sha-diff-pc-unix.PNG`. Found at the Sprint 4A review.*

## 10.3 The generator was chosen against current practice, for a product reason ✅

`np.random.RandomState(20260815)` — MT19937, the legacy generator. NEP 19 freezes
that stream permanently and explicitly declines to freeze `default_rng`, which may
change in a minor release.

The cube has to be reproducible **from its header** — from an integer, by a reader
who has neither this environment nor its lockfile. Only the frozen stream delivers
that. **The modern generator is the faster and the less reproducible one**, and
nothing here is performance-bound.

Two sampling choices go with it. Block starts are drawn from **overlapping**
windows, which gives 94 distinct blocks against a fixed partition's 19 — and a
partition anchored at 1928 cannot emit 1937–41 at all, because deck index 9 is not
a multiple of 5. **No wrap**, because wrapping would manufacture a 2025 → 1928
adjacency that never happened; the cost is that edge years are undersampled, and
that is named rather than hidden.

*Source — `engine.py`'s `3A OK` line prints the digest on every run. Recorded in
D-43.*

## 10.4 The suite and the sweep ✅

| | |
|---|---|
| Test suite | **250 collected items** from **168 test functions** — the gap is `parametrize` |
| The eight engine claims, selected | `pytest -k "T1 or … T8"` → **59 passed, 191 deselected** |
| Backward pass | **17 `test_T*` functions against 8 claims**, all mapped with a role |
| Cube sweep | **17.1 s** for 48 cells, twelve cached accumulations, 0.28 s per cell warm |
| `--check` on a committed cube | **2.1 s**, of which most is the path rebuild |

**The suite asserts its own size**, in functions rather than collected items — a
collected-count assertion fails under `pytest -k` and would have to skip itself,
and a guard that skips itself is the object the item existed to remove.

*Source — `uv run pytest`. Recorded in D-57. Timings recorded in
`remaining-sprints.md` Tech Debt.*

## 10.5 ⚠️ The suite-runtime decision has no dated measurement — UNSOURCED

D-53 wired `validate_cube()` into the default test run and accepted the cost:
**1.67 s → 4.05 s** in the agent's container, **1.17 s → ~3.7 s** locally. The
slow half is nine cold accumulations plus the path rebuild, and the rebuild is
what the test buys — it is the only code anywhere that verifies `paths_digest`.

**D-53 is an explicit standing reversal point**: when the suite crosses the
threshold where someone stops running it locally, the marker option is the answer.

---

# 11 — Known limits

What the model does not settle, and two things not yet done.

## Not yet done

| | Result | Where | Cost |
|---|---|---|---|
| [ ] | The two known biases, 13.5% and 30.5% | §9 | wire two flags in `tax.py`, assert in `tests/test_tax.py` |
| [ ] | The preset's frozen allowance and modelled draw | §3 | one self-test line, or two asserted literals |

## Deliberately not closed

| Item | Why it stays open |
|---|---|
| The no-crossing sentinel is unexercised at cube scale (§8.5) | A sprint cannot assert the presence of a case the model does not contain. Sprint 6 is where it becomes real |
| The block-structure assumption cannot be validated at n ≈ 20 (§5.5) | Stating it is the only honest move available |
| Objective 5's plateau (§8.4) | The fix was measured and rejected. `n_paths` is the lever if it ever matters |
| Whether the cloud is insensitive to profile within a segment | Testable with the machinery already here — run the cube at two archetypes and report how far the dots move. **Not measured** |
