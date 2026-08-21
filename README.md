# Roth vs. Traditional — solve for the threshold, don't guess the input

A scenario-planning demo for the Traditional-vs-Roth 401(k) choice. Most
calculators return a recommendation. This one returns the **future marginal tax
rate at which the two choices tie**, and lets you locate yourself against it.

Built as a design spike for an energy-analytics panel. The brief is in
[`docs/assignment/ASSIGNMENT.md`](docs/assignment/ASSIGNMENT.md).

---

## Status

| | |
|---|---|
| **Live demo** | **https://roth-vs-traditional-production.up.railway.app/ — the Sprint 6 app, live.** Confirmed 2026-08-20 against the local run. P3a's probe is gone from the repo and off the deployment. **Sprint 9 stays open on its own three done-whens** — cold load under five seconds, and the URL opening from a phone — which are measurements rather than a push |
| **Progress** | Sprint 6 complete — **10 of 13 sprint units.** Done: 1, 2A, 2B, 2C, P3a, 3A, 3B, 4A, 4B, 6. Remaining: 8, 9, 10. *(P3a counts. Sprint 5 folded into 4B and Sprint 7 was cut, and neither is counted — cuts 4 and 6 had already removed everything in Sprint 7 that Sprint 6 did not build, and D-35's verdict suppression moved to Sprint 8. 2 split into 2A / 2B / 2C, 3 into 3A / 3B, 4 into 4A / 4B; 10 is closeout.)* |
| **Runs today** | `tax.py`, `return_series.py`, `engine.py` end to end — accumulation, the retirement draw, both decumulation loops, the policy branch, the four objective reductions and the bisection that solves for the threshold, plus the block bootstrap, `paths_digest()` and `path_drawdown()` as of Sprint 3A, and all three rung mechanisms as of Sprint 3B. No path in the engine raises any more. **`spike_grid.py` writes the 48-cell `cube.json` as of Sprint 4A**, validates it against ten invariants, and re-derives it from the header under `--check`. **`app.py` is the real Streamlit app as of Sprint 6** — top strip, threshold axis, the two-rates sentence and the balance-graph pair, reading `cube.json` and computing exactly one number. 281 passing tests |
| **Not yet written** | The three fragility panels and the objective control (Sprint 8), plus D-35's verdict suppression, which landed there when Sprint 7 was cut. **The app ships their region and their caption, not their contents** — seven cleanup tags mark the sites, and the one at `app.py:1085` is written to render on the page on purpose |

**Where the numbers in this file come from.** Design gate two was a cold read: a
fresh agent, no access to the design conversation, asked to reproduce the
headline figures from the documents alone. It reproduced two of three, built a
working deterministic engine to do it, and found the third impossible as
specified. Every figure below came out of that engine.

**Sprints 2A, 2B and 2C have since brought the engine into this repo.** The four
age-65 balances, `t_now`, both year-20 allowances, D-15's proxy, the modeled draw
and the today's-law marker all reproduce from `uv run python engine.py` and are
asserted by tests. **So do both thresholds, as of Sprint 2C** — 58.4064% and
29.1% come out of `breakeven()`'s own bisection now rather than a hand-bisection
of `outcome()`, so nothing in this file is a cold-read figure any more. Two
figures were withdrawn during review and restored in 2A as labeled proxies.
**Sprint 3A supplied the bootstrap distribution they stand in for** — D-15's T65
Traditional runs p10 $997,415, median $2,123,538, mean $2,618,218 against the
$2,028,066 proxy. **Sprint 6's caption carries the median, $2,123,538**, on the
grounds D-23 already set out: the ensemble average is not what any one household
lives. Decided and recorded in D-15.

---

## Why this problem shape

The brief asks for 401(k) dynamics. The math object is the Energy Analytics
group's own.

A tariff and the tax code are the same thing: a piecewise,
jurisdiction-specific, customer-class-dependent rule that converts a quantity
into a cost, imposed on the user rather than chosen by them. Marginal brackets
are tiered block rates. An RSU vest is a demand charge — the peak sets the bill,
not the average.

But the pair that decides the answer in both domains is this one:

| DER / solar ROI | This model |
|---|---|
| 25-year utility rate escalator | 30-year future marginal tax rate |
| Payback year, IRR | Break-even future marginal rate |

Both escalators are unknowable. Both usually hide as one scalar in one
spreadsheet cell. Both dominate the output. A DER ROI model and a Roth
calculator fail the same way — by naming a number nobody has.

Hadamard's 1902 conditions for a well-posed problem are existence, uniqueness,
and stable dependence on the inputs. A problem with an unknowable input does not
have a unique solution; it has a solution family. Reporting the threshold is how
you answer it anyway without inventing precision you don't have.

The other seven analog pairs are in [`docs/CONTEXT.md`](docs/CONTEXT.md) part A.

**MVP highlight: net metering ≡ Roth.** Both ask you to pay a known cost today in
exchange for favorable treatment under a rule that may change. Retroactive net
metering rollbacks are not hypothetical, and neither are the retirement-account
changes in [References](#references).

---

## What it teaches

Four lessons. Every control on the page delivers one — if a feature can't be
traced to a row here, it gets cut.

| # | Lesson | Delivered by |
|---|---|---|
| **L1** | The investment return rate never affects the choice | 7 / 9 / 12% buttons |
| **L2** | Tax rates do affect the choice | Income shape, state toggles, bracket accordion |
| **L3** | Fragility matters more than this choice, for most people | Ten-stop ladder driving three dot panels |
| **L4** | You are not in control of the tax law | Two thresholds side by side, plus the nevermind toggle |

**L1 and L2 are taught by contrast.** The return-rate buttons sit physically
beside the tax controls. One set moves the answer and the other cannot, and the
two lessons land harder next to each other than either does alone.

### The identity L1 rests on

`(1−t)·(1+r)ⁿ` and `(1+r)ⁿ·(1−t)` are the same expression. The growth factor
divides out. Whether the market returns 7% or 12% cannot change which account
wins. Measured at the reference archetype, `t*` comes out to **32.5000% at every
`r ∈ {4, 7, 9, 12}%`.**

One convention makes the cancellation exact, and the app states it: the
comparison is **same pre-tax dollars** — $X into Traditional against $X·(1−t)
into Roth. Comparing same nominal dollars quietly favors Roth, which is where
most calculators go wrong.

The derivation and the four other choices that change an answer are in
[`docs/ENGINE.md`](docs/ENGINE.md). Why the model has this shape at all is in
[`docs/DESIGN.md`](docs/DESIGN.md).

---

## Quick start

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/). `.python-version`
pins 3.13 to match the deploy target.

```bash
uv sync                          # installs from uv.lock
uv run pytest                    # 294 tests, all green
uv run python engine.py          # engine self-test — 2A, 2B, 2C, 3A and 3B's published scalars
uv run python return_series.py   # return-series self-test
uv run streamlit run app.py      # the app — strip, threshold axis, balance graph
uv run python scripts/measure_3a.py   # 3A — block-vs-IID, block length, R9, D-15
uv run python scripts/measure_3b.py   # 3B — placement toggle, shock magnitude, D-22's Low pair
uv run python spike_grid.py           # 4A — sweeps 48 cells, validates, writes cube.json (~17 s)
uv run python spike_grid.py --check cube.json   # re-derives the committed cube from its header
uv run python scripts/measure_4a.py   # 4A — the L3 collapse, ruin at t_now, the $X/$Y grid, δ
```

Without uv:

```bash
pip install -e . && pip install pytest
python -m pytest                 # run from the repo root
```

**Byte-identity is a property of two runs, so it is two commands.** Write the
cube twice and compare; `cube_reference.json` is the same cube written by a
different OS, which is the half a same-machine comparison cannot see.

```bash
uv run python spike_grid.py --out /tmp/cube_a.json
uv run python spike_grid.py --out /tmp/cube_b.json
sha256sum /tmp/cube_a.json /tmp/cube_b.json cube.json cube_reference.json
```

---

## Repo map

| Path | | What it holds |
|---|---|---|
| `tax.py` | ✅ | Every number that came from outside the model — 2026 single-filer brackets, standard deduction, deferral cap, state rate, early-withdrawal penalty. No tax number appears anywhere else in the repo, and `tests/` is the one stated exemption |
| `return_series.py` | ✅ | 98 annual real total returns, 1928–2025. Damodaran + CPI from the same workbook, Fisher-deflated on load. Self-tests on run |
| `tests/test_tax.py` | ✅ | 35 tests. Literals are restated by hand rather than imported — a hand-verification that imports the constant it is verifying tests nothing |
| `engine.py` | ✅ | Sprint 2A landed the profile, income curve, contributions, accumulation, the D-33 ladder and the constant-path builder. Sprint 2B landed the retirement draw, both decumulation loops, the D-26 policy branch, the four objective reductions, ruin detection and `outcome()`, and deleted `marker_withdrawal` — it was a pure alias for `tax.gross_for_net`. Sprint 2C landed `breakeven()` — the bisection, the D-06 degeneracy guard, the no-crossing sentinel and the `Result` shape — and pinned the three search parameters no document had decided: the bracket `(0.01, 0.95)`, float exhaustion as the stopping rule, and the rate `ruin` is read at. Sprint 3A landed the block bootstrap inside `make_paths` — the D-43 generator, sampling scheme and truncation rule — plus `paths_digest()` for D-41's cube header and `path_drawdown()` for D-44's vocabulary. Sprint 3B landed the three rung branches inside `accumulate(..., shocks>0)` without changing the signature 2A's 54 tests sit on: `underwater_depth()` for D-45's placement reading, the D-46 stable tie-break, `forced_sale_gross()` with D-47's deferral-net base, and the D-48 module constants `SHOCK_PLACEMENT` and `SHOCK_AMOUNT` — both carried in `_accumulations()`'s cache key. **Nothing in the engine raises any more.** Specified in [`docs/ENGINE.md`](docs/ENGINE.md) |
| `spike_grid.py` | ✅ | Sprint 4A. Sweeps 48 cells — 3 rungs × 4 objectives × 4 shock counts — writes `cube.json` and prints the markdown grid. **Contains no math (D-11):** every published number comes back from `engine.outcome()` or `engine.breakeven()`, and `--audit` walks the AST and reports 32 arithmetic expressions, five of which name a cell value or a rate; the rest are counters, string joins and indices. `validate_cube(cube, paths=None)` holds the ten invariants D-49 assigns it, split by operand per D-51 — 27 cells within 128 ulps of `t_now`, 9 objective-5 cells asserting the after-tax difference is exactly `0.0`. With `paths=None` it rebuilds the path array from the header and checks it against `paths_digest` before using it, which is what makes `--check` re-derive rather than re-read |
| `cube.json` | ✅ | Sprint 4A. The 48 cells the app reads, plus a thirteen-field header: the seed and the two digests that make it reproducible, the archetype minus `stops`, the swept rung axis, and four `captions` carrying sentences that must travel with the artifact. **Byte-reproducible from the header alone** — `.gitattributes` pins it to `eol=lf`, because a checkout conversion breaks the sha without touching the content |
| `cube_reference.json` | ✅ | The same cube written on a **different OS** — the agent's Linux container — and committed so the local run can be hashed against it. Two runs on one machine agree with each other whichever line-ending convention that machine uses, so the same-machine gate cannot see the failure that actually happened; this file is the half that can. Byte-identical to `cube.json` today, and the day it is not, one of the two machines has moved |
| `tests/test_engine.py` | ✅ | Opened at Sprint 2A — 207 tests: 54 over the profile, ladder, contributions and accumulation, 47 added at Sprint 2B over the draw, decumulation, the policy branch, the objective reduction and ruin, 3 added post-2B over `geometric_mean`'s overflow (D-39), 24 added at Sprint 2C over the search, the bracket, the sentinel and the `Result` fields, 19 added at Sprint 3A over the bootstrap, the D-43 parameters, the digest, `path-drawdown` and the three measurement records, 59 added at Sprint 3B over the three rung branches, the placement reading and its tie-break, Low's inversion, D-22's slab, the cache key D-48 widened and one recorded measurement, and 3 added at Sprint 4B — 4A's two handover wires (`validate_cube` against the committed cube, and the `constants_fingerprint` recompute) plus one test asserting the suite's own size. **Two tests were deleted rather than skipped** — `test_block_paths_still_raise` at 3A and `test_a_nonzero_shock_count_raises_...` at 3B, both asserting a `NotImplementedError` that no longer exists. 209 written minus 2 deleted is the 207. **Sprint 4B mapped T1–T8 within it rather than creating it: each docstring now QUOTES the sentence it defends with its document and section, and all seventeen `test_T*` functions are named with a role in [`ENGINE.md`](docs/ENGINE.md)'s mapping table.** All eight green — T1 and T2 as of 2B, T3, T4 and T5 as of 2C, T6, T7 and T8 as of 3B |
| `app.py` | ✅ | Sprint 6. The Streamlit app: top strip → `Profile`, the threshold axis, the two-rates sentence, and the balance-graph pair. **It computes one number and reads all the others** — the deterministic line comes from `engine.breakeven()` on a one-row constant array, and every other figure is a control's own state or an index into `cube.json`. No stochastic code (D-12), and the grep that says so is a test rather than a habit. **Five departures from DECISIONS §7 are deliberate and §7 now records them.** Six `[SPRINT-7-CLEANUP]` sites and one `[SPRINT-8-CLEANUP]` hold the copy and the regions Sprint 8 fills — **the tags name sites rather than a schedule, so they outlived Sprint 7's cut unrenamed.** The `[SPRINT-8-CLEANUP]` one is inside a string rather than a comment and renders on the live page, which is a decision: a PoC shown week over week should say what is coming next. The name is kept deliberately, so this sprint changed no deploy config |
| `railway.toml` | ✅ | P3a. Builder, start command, healthcheck, restart policy. Config-as-code overrides the dashboard, so this file is the source of truth |
| `.streamlit/config.toml` | ✅ | Sprint 6, build order step 1. **Theme only.** `base = "dark"`, with the marker's orange as `primaryColor` so the widgets and the today's-law line share one colour on purpose: both of them are the user, as against the two bars, which are the two bets. **Nothing server-side lives here** — port, address, headless, `fileWatcherType` and `gatherUsageStats` are flags in `railway.toml`'s start command, and the deploy test reads that command rather than this file |
| `tests/test_deploy_config.py` | ✅ | 8 tests on `railway.toml`. No assertion names the entry file — the one test that checks it reads the name out of the start command and asserts that file exists. **Sprint 6 rewrote `app.py` wholesale and this file needed no edit, which was verified rather than assumed.** The rename it was built to absorb never happened; the plan forbids it, because the filename is the one thing keeping the app sprints out of deploy config |
| `scripts/measure_3a.py` | ✅ | Sprint 3A. Not the engine, and nothing imports it. Five documents cite one block-vs-IID measurement taken at gate two by code that was **not in this repo**; this file makes all five checkable by one command. It also carries the IID arm, which lives here rather than as a third `make_paths` kind because nothing in the model consumes an IID path set |
| `scripts/measure_4a.py` | ✅ | Sprint 4A. Five runs over the finished cube, each landing in a named document: the L3 collapse (D-22, `## Results` below), ruin at a common `t_now` — the one reading the cube deliberately does not carry (D-50) — the `$X`/`$Y` grid at both δ, the two risk gates, and the δ at which `$Y` and `$X` cross on each objective. Not a deliverable, which is why it may call `engine._outcome_paths` and `spike_grid.py` may not |
| `scripts/measure_3b.py` | ✅ | Sprint 3B, extended at the results pass to **six runs**. Each lands in a named document: the correlated/uncorrelated placement toggle (`ENGINE.md`), the $25,000 / $80,000 shock-magnitude sensitivity and its bisected crossing (`## Results` below), and D-22's published Low ratios, which do **not** reproduce — the run identifies the rule that produced them rather than guessing. Its stdout names the destination of every figure it prints |

---

## Documentation

| File | What it is | Open it when |
|---|---|---|
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | **The build contract.** Wins over every other document | You want the authoritative answer |
| [`docs/RESULTS.md`](docs/RESULTS.md) | **Measurements a claim rests on** — every published figure with the run behind it, including the objective-5 plateau D-51 rests on and the engine fix that was measured and rejected. *(`EVIDENCE.md` was folded in here at Sprint 4B. There is no separate evidence file)* | You want the number under a decision rather than the decision |
| [`docs/USER_LESSONS.md`](docs/USER_LESSONS.md) | The four lessons as a reader meets them — L1 to L4, the ones carrying no number, a 90-second path through the app, and what it does not claim | You want what the app teaches, without the machinery |
| [`docs/TRADEOFFS.md`](docs/TRADEOFFS.md) | Every option considered, what each is good and bad at, which one shipped | You want to know what else was on the table |
| [`docs/DESIGN.md`](docs/DESIGN.md) | Design rationale — the model, the five mockups, and what gate two overturned | You want the reasoning and the pictures |
| [`docs/ENGINE.md`](docs/ENGINE.md) | How the math works, and the five choices inside it that change an answer | You want the numerical dynamics |
| [`docs/CONTEXT.md`](docs/CONTEXT.md) | Requirements synthesis, audience derivation, the option space as it stood at design phase | You want the framing from before decisions closed |
| [`docs/remaining-sprints.md`](docs/remaining-sprints.md) | Sprint plan, budget, done-whens, cut ladder | You want to know what's left and what gets cut first |
| [`docs/review/GATE-1.md`](docs/review/GATE-1.md) · [`GATE-2.md`](docs/review/GATE-2.md) | Cold-read design reviews by fresh agents | You want to see what the reviews caught |
| [`docs/sprints/`](docs/sprints/) | Per-sprint execution records, commit plans, verification batteries | You want commit-level detail |
| [`prompts/`](prompts/) | The prompt given to each agent session | You want the AI disclosure to be checkable |
| [`docs/sprints/DEVLOG.txt`](docs/sprints/DEVLOG.txt) | Working log | — |

---

## Headline numbers

Reproducible from [`docs/DECISIONS.md`](docs/DECISIONS.md) alone. Every figure
comes out of the deterministic engine at 7% real.

| | Reference archetype | Early-career preset |
|---|---|---|
| Income now | $165,000 | $60,000 |
| State while working / in retirement | taxed / untaxed | untaxed / untaxed |
| `t_now` = `t*`, rules hold | **32.5%** | **12.0%** |
| Today's-law effective marker | **15.2%** | **15.9%** |
| Verdict | Traditional by 17.3 points | **Roth** by 3.9 points |
| `t*` if treatment moves at year 20 | **58.4%** | **29.1%** |
| Verdict under the policy | Traditional, by more | **Traditional** — flipped |
| Traditional balance at 65 | $2,108,867 | $1,749,149 |
| Roth balance at 65 | $1,423,485 | $1,539,251 |
| Frozen allowance at year 20 | $607,475 — about six of thirty-five retirement years | $631,049 |
| Modeled draw | $108,397/yr, 54% of final income | $117,212/yr, 59% |

**The second threshold moves the way nobody expects.** A policy that harms only
Roth *raises* the rate at which Roth becomes worthwhile. Both thresholds sit far
to the right of the marker, so the scenario you were told makes Roth safe is the
one that widens Traditional's lead. The design deck had this drawn backwards; the
reversal is in [`docs/DESIGN.md`](docs/DESIGN.md) part 4 and
[`GATE-2.md`](docs/review/GATE-2.md).

*Both thresholds are computed with balances allowed to go negative — the engine
records ruin rather than enforcing a floor, which is what keeps the difference
monotone enough to solve. Traditional's terminal balance goes negative above a
33.45% future rate, so the 58.4% figure is a crossing between two already-ruined
paths. That is what makes it computable; it is not a retirement anyone funds. See
`DECISIONS.md`, D-26's subsection.*

The flip is real, but it belongs to someone else. The early-career preset reads
Roth under current rules and Traditional once the rule moves. **The rule change
costs the low-bracket saver Roth was supposed to be for.**

---

## Results

Claims the design made and fudge factors it named, measured against the built
engine. Some did not survive; two survived and turned out to be carrying more
weight than the document that named them admitted. Recorded here rather than
quietly rewritten — the convention is the project's own and D-05 and D-15 are the
earlier instances. **Each entry closes with the sprint that measured it and the
file you can re-run**, so no figure here is an assertion.

### Income shape — the deck's 1.4 points measure zero, and the deferral cap is why

**The income shape's end point never reaches the archetype.** The design deck's
income mockup states that ending flat at $200,000 rather than declining to
$165,000 *"costs Traditional 1.4 points of its advantage,"* and D-19 carried the
qualitative half of it: ending high raises retirement spending and narrows
Traditional's lead, so it is the conservative case. Measured at Sprint 2B, both
shapes return `t_now` 32.50%, a 15.18% marker, a 17.32-point advantage and a
$108,397 draw — identical to the dollar, with the policy threshold at 58.4064%
either way. **The deferral cap is the reason.** A 20% savings rate passes $24,500
above an income of $122,500, and the declining profile is still earning $168,500
at age 64, with $33,700 of capacity against a $24,500 cap. Every year of the
55→65 leg is capped under both shapes, so the terminal income cannot reach the
balance at 65 and nothing downstream of it can move. The estimate was not wrong
by 1.4 points; the mechanism it named is invisible at this income. **Nor does the
early-career preset rescue it** — the preset starts under the cap but ends at
$200,000, so its end point is capped too and moves nothing either. The effect
needs a profile whose *final* leg stays under $122,500, and there it is a
fraction of the claimed size: ending at $90,000 rather than $110,000 moves the
marker by **0.13 points**. That is the correction, rather than a defense of the
original number.

*Measured at Sprint 2B. This is the one entry here with no runnable source in
`scripts/` — it predates the measurement-script convention Sprint 3A introduced,
and re-deriving it means re-running the two profiles by hand.*

### D-39's 15% margin — the base case ruins about half the time regardless

**A named margin was measured and its justification did not survive.** D-39 sizes
the retirement draw to leave 15% of the Roth's age-65 balance at 100, so the base
case is not sitting exactly at zero where any shock ruins every objective at
once. Over 2,000 block-bootstrap paths, shock-free, **the Roth balance goes
negative before 100 about half the time.** That is sequence risk rather than a
tuning error: a level real draw against a 19.30% standard deviation over 35 years
ruins about half the time by construction, and no plausible margin closes it.
Sprint 4A's gate had read *ruin is 0.0 across the 0-shock slab*, which cannot
pass; R9 closed on option 1 and replaced it with *ruin is measured and reported
on the slab, and rises with shock count*. **Both halves ran at 4A.** The slab
came in at 48.70%, and at the Low rung ruin climbs 48.70% → 55.95% → 65.40% →
74.20% across zero to three shocks.

**The figure was re-measured at Sprint 3A rather than inherited, and it moved the
way that would have flattered us.** The original 53.1% was taken with the draw
sized at the 7% deterministic solve; Sprint 2B pinned the bootstrap draw at the
series' own compounded rate, which is a smaller draw and therefore less ruin. On
3A's own bootstrap, 2,000 paths, three seeds: **48.7%, 48.2%, 49.4%**, with the
draw at about $99,000 against the $108,397 deterministic solve. It fell four
points and it did not fall far enough to matter. **D-39 records OPTION 1** —
report the ruin rate as a finding and drop Sprint 4A's absolute gate — with the
other three options costed at the re-measured number.

*Measured at Sprint 3A by `scripts/measure_3a.py` §3; output in
`scripts/out_measure_3a_20260818-1502.txt`. Closes R9.*

### Block bootstrap — chosen to fatten the tail, and it thins it

**The block bootstrap was picked for a reason that failed measurement.** It was
chosen to fatten the tail against an IID draw and it thins it slightly — p10
`path-drawdown` −59.6% against −63.7%, measured over the 30-year accumulation
window. **The tail is the finding and the middle is not.** Across five seeds the
p10 pair says *block thinner* five times out of five; the median pair splits three
to two at a gap of a few tenths of a point, which is sampling noise. The pick
survives on a different argument than the one it was chosen for, which Scope &
Branches below states in full.

*Measured at Sprint 3A by `scripts/measure_3a.py` §1 and §1b, 4,000 paths
averaged over five seeds; output in `scripts/out_measure_3a_20260818-1502.txt`.
**The −59.6% is the five-seed figure and is the one to quote** — two other
sample sizes of the same quantity circulate, and `docs/ENGINE.md` reconciles
all three.*

### Block length — the larger of the two fudge factors, and it gates nothing

**Block length 5 has no measurement behind it, and the modeling choice it sits
inside does.** Sprint 3A ran the sensitivity at 3, 5 and 10. It is monotone: a
shorter block breaks history's runs into smaller pieces and deepens the tail, a
longer one averages over more of the record and shallows it. Five sits between
them.

**The p10 spread across that range is about ten points, which is wider than the
block-versus-IID gap the entry above is about.** The arbitrary number moves the
tail more than the modeling choice does. Nothing published moves with it — the
cube ran at five, and the direction is what the sensitivity was for.

*Measured at Sprint 3A by `scripts/measure_3a.py` §5, 4,000 paths at seed
20260815; output in `scripts/out_measure_3a_20260818-1502.txt`. The three-row
table and the full reading are in [`docs/ENGINE.md`](docs/ENGINE.md).*

### Shock magnitude — $40,000 is a fudge factor, and it is load-bearing

`SHOCK_AMOUNT = $40,000` was chosen at 1.6x a contribution year (D-39), so the
forced sale and the skipped contribution would be the same order of magnitude.
Sprint 3B measured $25,000 and $80,000 against it, at the Low rung, three
shocks, 2,000 bootstrap paths.

| Shock | Gross sale at 55 | All-in cost | `trad_65` median | `roth_65` median |
|---|---|---|---|---|
| $25,000 | $43,657 | 42.7% | $1,613,286 | $1,135,589 |
| $40,000 | $73,960 | 45.9% | $1,217,364 | $925,751 |
| $80,000 | $158,506 | 49.5% | **$295,296** | **$390,411** |

**At $80,000 the account ordering reverses.** Traditional finishes below Roth,
and `trad_65` is a pre-tax balance while `roth_65` is already after tax — so on
the median path there is no retirement tax rate, including zero, at which
Traditional recovers. The breakeven does not move. It stops existing.

Two multipliers produce it, one fixed and one growing. Traditional starts ahead
by `1 / (1 - t_now)` = 1.481x, because the deferral buys more shares. But each
forced sale costs Traditional 1.98x what it costs Roth, so Traditional loses
1.34x as much *of itself* per shock. That second multiplier is the one that
moves: the gross sale runs 1.75x, 1.85x, 1.98x across the three shock sizes,
because the withdrawal climbs the bracket table as it grows. A fixed head start
against a growing per-shock penalty, and enough shocks consume it.

**This is the finding the deterministic model cannot produce.** With no shocks
`roth/trad` is pinned at `1 - t_now` exactly, at every rung and every return
rate (D-22, tests T7 and T8). The reversal is reachable only through the single
asymmetric mechanism in the cube — the 10% penalty plus the incremental
bracket on a forced sale. Tax deferral is leverage, and leverage amplifies both
directions.

**Read it with its limits.** Both outcomes at $80,000 are bad — those are
near-ruin balances after a career of $24,500/year contributions. It is a median
rather than a distribution. And whether the cell resolves to `always_roth`
(D-42) is a Sprint 4A question; this run establishes it for the median path
only.

**The crossing is at $67,471** — 2.75x a contribution year, against the 1.63x
D-39 chose. Below it Traditional's `1 / (1 - t_now)` head start survives three
shocks; above it the penalty plus bracket-climb has consumed the whole 1.481x.
Bisected over 2,000 paths at the Low rung, three shocks; the precision is the
bisection's rather than the sample's.

*Measured at Sprint 3B by `scripts/measure_3b.py` §2, 2,000 paths at seed
20260815; output in `scripts/out_measure_3b_20260818-1607.txt`, which is the run
that carries the bisected crossing. The reasoning that promoted this from a
sensitivity row to a `## Results` entry is in
`scripts/learning_3b_20260818-1502.txt`.*

### The sentence, and the parameter that decides it

I estimated during design that moving up a resilience rung would be worth about
four times getting the account right. The reasoning was L3 itself: if the
break-even only moves for people without a buffer, the buffer should dominate
the arithmetic. The cube rejects that, at the setting the app prints.

At the cell the app's sentence reads — objective 4, one shock, the Low rung:

| | δ = 2 points | δ = 10 points |
|---|---|---|
| **$X** — getting the account right | $264,662 | $1,602,313 |
| **$Y** — moving up one rung | $756,988 | $756,988 |
| ratio | 2.86× | **0.47×** |

**$Y does not move.** That is not a rounding artifact, and it is the same fact
one of the cube's invariants already rests on: under current rules a Roth
terminal value does not depend on the future tax rate at all. Roth is the better
account on every cell in this grid, so $Y is a difference between two Roth
outcomes and the rate never enters it. $X is a difference between Roth and
Traditional, and Traditional's after-tax terminal falls as the rate rises — so
$X grows with δ while $Y sits still. It grows 6.05× for a 5× increase in δ,
slightly faster than linear because the withdrawal gross-up is 1/(1 − t).

So δ chooses which magnitude is larger. I solved for the crossing on all four
objectives:

| objective | δ where $Y = $X |
|---|---|
| 1 — mean terminal | 6.10 points |
| 3 — median terminal | 5.58 points |
| 4 — p10 terminal | 4.82 points |
| 5 — P(not running out) | 5.56 points |

Below roughly five points the buffer dominates and the design estimate holds in
direction if not in size. Above it the account choice dominates. **The app
prints δ = 10.** The crossing is tight across all four objectives, so this is
structural rather than a property of the one cell the sentence quotes.

**δ is not a model parameter.** It is the assumed size of the user's miss — how
wrong their guess about their own future marginal rate turns out to be — and
nothing in the model constrains it. I fixed δ at 10 before running the sweep, on
the grounds that a two-point miss is optimistic for a forecast reaching fifty
years out. That choice, made for a defensible reason and made blind to the
result, is what inverted the headline.

I did not move δ afterward and I did not switch objectives. Either would have
produced a sentence that reports the parameter I picked rather than the model I
built. All four objectives ship in `cube.json` at both deltas and the crossing
is published here, so a reader sees the choice instead of inheriting its result.

**The claim the sentence was built to carry survives, and a different instrument
carries it.** The break-even at the Low rung:

| rung, objective 4 | 0 shocks | 1 | 2 | 3 |
|---|---|---|---|---|
| Low | 32.5000% | 30.8987% | 28.0158% | 24.4070% |
| Mid | 32.5000% | 32.5000% | 32.5000% | 32.5000% |
| High | 32.5000% | 32.5000% | 32.5000% | 32.5000% |

**8.13 points of movement at one rung and none at the other two** — not
approximately none, exactly none, at every shock count on objectives 1, 3 and 4,
for a reason the engine can derive rather than measure. That is the account
question being contested for people without a buffer and settled for everyone
else. The dot panel shows it without arithmetic and without a parameter I had to
choose.

**Objective 5 reads about 0.08 points low across the whole slab, and that is the
solver rather than the model.** `P(not running out)` counts a discrete event over
2,000 paths, so its difference is a staircase and its zero set has width — 0.1616
points at the archetype — and the bisection closes on the plateau's left edge.
The claim underneath is exact and is asserted directly instead: the after-tax
difference is `0.0` at `t_now`, on all nine of those cells, with no tolerance.
D-51 carries the reading and `cube.json`'s header carries the caption.

One note on the magnitudes in the first table. Objective 4 is the tenth
percentile of the after-tax terminal value, and nothing in the engine floors a
balance at zero: a path that runs out at 72 keeps compounding a negative number
for 28 more years. The p10 figures behind that $1,602,313 are −$9,506,737 for
Roth and −$11,109,050 for Traditional. The spread is not wealth gained. It is
depth of hole avoided at the tenth percentile, which is a second reason the
dollar sentence is the weaker of the two instruments on this page.

*Measured at Sprint 4A by `scripts/measure_4a.py` — the collapse table in §1, the
`$X`/`$Y` pairs in §3, the four crossings in §5, all read off `cube.json` at seed
20260815 over 2,000 paths. Output in
`scripts/out_measure_4a_20260819-2237.txt`, which captures all five sections. The
earlier `out_measure_4a_20260819-2128.txt` predates §5 and is kept as the run the
§1–§4 figures were first read off.*

---

## Two known biases, both deferred, both measured

Neither changes a verdict. What matters is that each one's size and direction are
known rather than discovered by a reader.

| Simplification | Direction | Size |
|---|---|---|
| Over-65 deductions omitted | **understates** Traditional | marker 15.2% → 13.5%, so 1.7 points |
| SALT deductibility ignored | **overstates** Traditional | `t*` 32.5% → 30.5% for an itemizer, so 2.0 points |

They point opposite ways and roughly cancel, which is a convenience rather than a
defense. The defense is that both are stated. A model whose author cannot say
which way its stubs bend the answer is a model nobody should trust with a
thirty-year decision — which is, in a smaller way, the same argument this project
makes about the escalator hiding in a spreadsheet cell.

---

## Scope & Branches

What was cut, why, and what it would take. The alternatives that were *rejected*
rather than deferred are in [`docs/TRADEOFFS.md`](docs/TRADEOFFS.md).

| Cut | Why | What it would take |
|---|---|---|
| **Certainty preference** — choosing Roth knowing the expected value is worse, because you'd rather not hold an open position | All four objectives are about wealth outcomes. None can express *I want it settled*. This is a real preference and the model does not contain it | A utility formulation over outcome *variance* rather than level, or an explicit premium the user names. Neither fits the threshold framing, which is why it is a branch rather than a sixth objective |
| **Objective 2 — max after-tax lifetime spending** | Cut, not deferred. Its precondition was *spending is an output*; D-39 made spending a fixed common input sized off the Roth, so both accounts fund identical spending on every path and the difference is identically zero. Neither repair survives: spending-until-first-shortfall is still degenerate wherever the accounts stay proportional, and maximum-sustainable-spending is algebraically the same test as objective 1 | Spending would have to become an output again — a per-account sustainable-draw solve — which reopens the assumption D-39 exists to close |
| **Bracket rise as a modeled scenario** | Already on the axis. A higher future rate is a position to the right of `t*` | Nothing. Naming it is the work, and the two-threshold headline does that |
| **Symmetric "nevermind"** — the rule change hitting Traditional's deduction too | The design deck's original words were "all tax benefits go away." Making it symmetric deletes the asymmetry the whole policy branch rests on, and it still doesn't flip the archetype toward Roth | A Traditional branch in the decumulation loop. ~20 minutes and one lost argument |
| **Two-bar asymmetry chart** (p90 gain vs p10 loss, both against median) | Teaches a real lesson — outcomes are left-skewed, the bad case is bigger than the good one — but not L3. L3 is *fragility beats the account choice*, carried by the dot collapse and the $X/$Y sentence. Adjacent, not the same | A `p90` field in the cube and one chart. ~10 minutes |
| **Block length sensitivity** | Block length 5 is a stated fudge factor. **Run at Sprint 3A, and it is monotone** — a shorter block deepens the tail and a longer one shallows it, over a 10-point p10 range from block 3 to block 10. The three-row table is in [`docs/ENGINE.md`](docs/ENGINE.md) | Nothing further. It gates nothing: 5 sits between the two and the direction is what the sensitivity was for |
| **Block bootstrap over IID** | Kept, but its original justification failed measurement — block *thins* the tail rather than fattening it (p10 `path-drawdown` −59.6% vs −63.7%), because annual real returns have a lag-1 autocorrelation of −0.035. It survives on the recovery-forgone channel, and on reproducing history's own worst five-year run. At ~19.6 independent blocks the structure claim cannot be validated, only stated | Switching to IID would have deleted one fudge factor and saved Sprint 3A about five minutes. The reason not to is that block is the more conservative tail and keeps real sequences intact — but that is a preference, not a result, and this row says so |
| **Shock magnitude sensitivity** | $40,000 is the same kind of fudge factor. **Run at Sprint 3B, and it is load-bearing** — at $80,000 the account ordering reverses and the breakeven stops existing, with the crossing bisected at $67,471. The finding is in `## Results` above, not here, because it changed a conclusion rather than sizing one | Nothing further. $40,000 sits at 59% of the flip point, which is inside the safe regime but not by an order of magnitude, and that is now a number rather than a hope |
| **Over-65 deductions** — the permanent $2,050 additional standard deduction, and the OBBB senior deduction of up to $6,000 | Deferred, not overlooked. Together they move the marker from 15.2% to **13.5%**, which *widens* Traditional's lead — so omitting them **understates** the recommendation. Neither changes a verdict, and the preset's flip survives at 14.4% against a 12.0% threshold. The $6,000 also sunsets, and applying it across a 35-year retirement would assert something the statute doesn't say | The $2,050 is one conditional on age in `tax.py` and is the honest one to wire first. The $6,000 needs a phaseout and an expiry |
| **SALT deductibility** — state tax is added flat to the federal marginal rate | **The larger of the two known biases, and it points the other way.** For a filer who itemizes the true combined rate is `0.24 + 0.085 × (1 − 0.24)` = **30.5%, not 32.5%** — two points on the headline itself, in the direction that flatters Traditional. It bites only on itemizers: state income tax alone is $14,025 at the archetype against a $16,100 standard deduction, so it takes about $2,075 more of mortgage interest, property tax or charity to cross | An itemize-or-not branch, and the state rate applied inside the federal calculation rather than beside it |
| **Real per-state tax data** | One boolean at 8.5% carries the whole state effect | A state table and a second lookup. The `TODO` is in `tax.py` |
| **MFJ and Head of Household** | Single only — the UI models one income curve and one age, so a household is something the controls cannot represent. *(The earlier reason given here, overlapping HoH bracket edges, does not survive checking: the published 2026 HoH column is contiguous.)* | Two more bracket tables, verified against the same primary source |
| **Employer match, and the taxable side account** | Both are Traditional-flavored money that arrives whether or not you choose it. Grayed in the accordion as evidence of completeness | A second contribution stream and a taxable-account model. This is where the next hour would go |

---

## AI disclosure

> **⚠ PLACEHOLDER — this section gets replaced before the repo goes public.**
> The table below was written when this was going to be two or three agent
> sessions. It became nine sprints, several of them split, and each one carries a
> build session plus a docs pass plus whatever the assessment turned up — on top
> of the design conversations, which are not sprints at all. A row per session
> stopped being a useful disclosure somewhere around Sprint 2C, and the table has
> been behind ever since. **What replaces it is a short statement of how AI was
> used across the project**, with the research session kept as the one linked
> artifact. Until then the table is accurate for the rows it has and silent about
> the ones it doesn't. Tracked in `remaining-sprints.md` housekeeping.

Each phase ran as a separate agent session with a written prompt. The prompts are
committed in [`prompts/`](prompts/), so the disclosure is checkable rather than
asserted.

| # | Phase | Prompt | Record |
|---|---|---|---|
| 1 | Research | — | (kept private) |
| 2 | Design | `prompt1.txt`, `prompt2.txt` | (kept private) |
| 3 | Design gate one | `prompt3.txt` | [`GATE-1.md`](docs/review/GATE-1.md) |
| 4 | Design gate two | `prompt4.txt` | [`GATE-2.md`](docs/review/GATE-2.md) |
| 5 | Sprint planning + Sprint 1 | `prompt5.txt` | [`docs/sprints/Sprint1.txt`](docs/sprints/Sprint1.txt) · _(link)_ |
| 6 | Sprint 2A | `prompt5.txt` _(reused)_ | [`docs/sprints/Sprint2A.txt`](docs/sprints/Sprint2A.txt) · _(link)_ |
| 7 | P3a — Railway deploy | `prompt5.txt` _(reused)_ | [`docs/sprints/P3a.txt`](docs/sprints/P3a.txt) · _(link)_ |
| 8 | Docs assessment | `prompt6.txt` | _(link)_ |
| 9 | Sprint 2B | `reading-list-archive/reading-list-sprint-2B.txt` | [`docs/sprints/Sprint2B.txt`](docs/sprints/Sprint2B.txt) · _(link)_ |
| 10 | Sprint 2C | `reading-list-archive/reading-list-sprint-2C.txt` | [`docs/sprints/Sprint2C.txt`](docs/sprints/Sprint2C.txt) · _(link)_ |
| 11 | Sprint 3A | `reading-list-archive/reading-list-sprint-3A-paths.txt` | [`docs/sprints/Sprint3A.txt`](docs/sprints/Sprint3A.txt) · _(link)_ |
| 12 | Sprint 3B | `reading-list-archive/reading-list-sprint-3B-rungs.txt` | [`docs/sprints/Sprint3B.txt`](docs/sprints/Sprint3B.txt) · _(link)_ |
| 13 | Sprint 4A planning | `planning-archive/Sprint-4A-planning-round-2.txt` | [`docs/sprints/Decisions-Gating-4A.txt`](docs/sprints/Decisions-Gating-4A.txt) · [`RESULTS.md`](docs/RESULTS.md) |
| 14 | Sprint 4A | `reading-list-archive/reading-list-sprint-4A-cube.txt` | [`docs/sprints/Sprint4A.txt`](docs/sprints/Sprint4A.txt) · _(link)_ |

`prompts/` also holds `readinglist.sh`, which builds a reading list from a sprint
name, and `designing-a-read-policy.txt`, the session that decided what a reading
list should contain. A reading list moves to `reading-list-archive/` once its
sprint has run. `planning-archive/` holds the plan-tightening sessions — the
passes that decided a sprint's shape before its reading list was built, which is
why they sit beside the lists rather than in them. **Every closed sprint's list is
now in `reading-list-archive/`**, 4A's and 4B's included — 4A's moved at this docs
pass and 4B's followed it when that sprint closed. `prompts/` itself holds only the
numbered prompts, the script and the read-policy session.

Sessions 3 and 4 were deliberately cold: a fresh agent with no access to the
design conversation, given the documents only. **Gate two is the reason three
headline numbers changed.**

---

## References

1. **r/personalfinance flowchart** — [`docs/design/reddit_personal_finance_flowchart.jpeg`](docs/design/reddit_personal_finance_flowchart.jpeg) ·
   [source](https://www.reddit.com/r/personalfinance/comments/4gdlu9/how_to_prioritize_spending_your_money_a_flowchart/)
   The ten-stop ladder is this flowchart's ordering, including the detail that
   the employer match comes before clearing medium-interest debt.

2. **Hadamard's uniqueness condition.** A problem with an unknowable input
   doesn't have a unique solution; it has a solution family. Reporting the
   threshold is how you make an ill-posed question answerable without lying
   about it.

3. **Decades-long bets on a rule that moved.**
   - Argentina 2008 — private pension funds nationalized into the state system
   - Hungary 2010–11 — effectively forced transfers back to the state pillar
   - Ireland 2011–14 — an annual levy on private pension *assets*, not income
   - Poland 2013–14 — the bond portion of private pension accounts cancelled outright
   - Spain — drew heavily on its social security reserve fund
   - US SECURE Act 2019 — eliminated the stretch IRA, retroactively changing the
     inheritance math for accounts people had spent decades building. Nobody's
     money was seized, but the rule moved under people who had already committed.

4. **2026 brackets and limits — primary source, R1 CLOSED.**
   [IRS IR-2025-103](https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill),
   Oct. 9, 2025, and [Revenue Procedure 2025-32](https://www.irs.gov/pub/irs-drop/rp-25-32.pdf).
   All seven single-filer edges and the $16,100 standard deduction verified
   against it on 2026-08-15, and corroborated independently by the Tax
   Foundation's 2026 table — the two agree on every edge. Deferral limit
   $24,500, combined employee-plus-employer limit $72,000:
   [COLA increases](https://www.irs.gov/retirement-plans/cola-increases-for-dollar-limitations-on-benefits-and-contributions).

5. **Bengen (1994), Journal of Financial Planning**, and the Trinity Study
   (Cooley/Hubbard/Walz, 1998). Rolling 30-year windows over US data. The binding
   case isn't 1929, it's 1966 — stagflation ate real withdrawals while nominal
   returns went nowhere for sixteen years. Bengen has since revised upward
   (~4.7%) on a broader asset mix, and Wade Pfau's international work found much
   lower safe rates outside the US, so the original number is partly survivorship
   on the best-performing market of the twentieth century. Translated for the
   panel: **the 4% rule is a backtest with n ≈ 5** — which is exactly the critique
   of "our ROI model is validated on twenty years of one utility's rate history."

6. **Markowitz, Portfolio Selection (1959).** He says outright that downside-only
   risk is the better measure and picks variance because it was computationally
   tractable in 1959. The entire standard risk framework is a punch-card-era
   compute compromise nobody revisited, so the critique of the instrument ladder
   has a 65-year-old co-signer.

7. **Ergodicity** — Ole Peters, and Kelly earlier. The expected value across
   10,000 simulated households is not what any one household experiences over a
   lifetime, because ruin is an absorbing state. Monte Carlo tools report the
   ensemble average. You live the time average.

---

## License

None. This is a research spike, not a distributed package.
