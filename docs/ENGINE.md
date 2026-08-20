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

**Status: the engine is complete and no path inside it raises.** Sprint 2A
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
R9's ruin question (D-39, option 1) and D-15's reconciliation. **Sprint 3B landed
the three rung mechanisms behind `accumulate(..., shocks>0)`** — the last stub in
the module — inside the signature §5 publishes and 2A's 54 accumulation tests sit
on. `underwater_depth()` implements D-45's placement reading, the `argsort`
tie-break is D-46's stable one, `forced_sale_gross()` carries D-47's
deferral-net base, and D-48 puts the placement toggle and the shock amount in
module constants that `_accumulations()`'s cache key now reads.

**What is left is not engine work.** `spike_grid.py` and the cube shipped at
Sprint 4A and the real `app.py` is Sprint 6. Both import this module rather than
extending it, and 4A closed without changing a line of it — the sweep reads
`breakeven()` and `outcome()` through the public signatures §5 publishes.

**Three parameters more were decided nowhere in this corpus and are now D-43.**
The generator is `RandomState(20260815)`, MT19937 — picked *against* current
numpy practice because NEP 19 freezes the legacy stream and declines to freeze
`default_rng`, and D-41 needs reproduction from an integer rather than from a
lockfile. Block starts are drawn from overlapping windows with no wrap. A
trailing partial block is truncated.

**The digest is reproducible on three conditions, and only one of them is a decision.**

| Condition | Status |
|---|---|
| The generator stream is frozen | **Decided.** D-43 chose `RandomState`/MT19937 against current numpy practice for exactly this reason |
| The array is C-contiguous | **Handled in the function.** `ascontiguousarray` normalises stride before the bytes are taken, so a view or a transpose cannot change the hash of the same values |
| `float64` is in the machine's native byte order | **An assumption, and it is unstated anywhere else** |

The third one is the one to know about. `tobytes()` takes native order, so an 
identical array on a big-endian machine hashes differently. Every machine this 
project has run on is little-endian and the published digest holds across them; 
pinning `dtype='<f8'` would close the gap and has not been done, because the 
failure requires hardware nobody is going to point at this. **Named here rather 
than fixed, so that a digest mismatch on strange hardware reads as a known limit 
instead of a corrupted deck.**

**What the digest actually guarantees**

`paths_digest()` is a blake2b-128 fingerprint of the path array, and Sprint 
4A writes it into the cube's header. It is the fast failure: a reader who 
rebuilds the array and gets a different digest knows they are not looking at 
the same experiment before comparing a single cell. **`spike_grid.py --check` 
performs that rebuild.** Until 4A nothing in the repo did, so the digest was a 
header field no code verified — the reader this paragraph describes was 
hypothetical and is now a command.

**It fingerprints the inputs, not the cube.** Everything upstream of the array 
is inside it — seed, `n_paths`, `n_years`, the kind, the block length, the 
contents of `return_series.py`. Everything downstream is outside it. Changing 
`SHOCK_AMOUNT` from $40,000 to $80,000 moves every cell in the cube and leaves 
the digest byte-identical, because shocks are applied inside `accumulate()`, 
long after the array exists. That boundary is the reason the header carries a 
separate fingerprint over the model constants: the two cover disjoint halves 
of what makes two runs differ, and neither is redundant with the other.

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

Block length is five years — a choice rather than a derivation. **Measuring the
fudge factor is what caught the bad reason.** That is the whole argument for
naming them.

**The sensitivity, run at Sprint 3A.** 4,000 paths, same seed, same 30-year
window as the table above.

| Block length | Median `path-drawdown` | p10 `path-drawdown` |
|---|---|---|
| 3 | −44.7% | −65.1% |
| **5** (D-05) | **−42.6%** | **−59.4%** |
| 10 | −41.8% | −54.8% |

**It is monotone and it gates nothing.** A shorter block breaks history's runs
into smaller pieces and deepens the tail; a longer one averages over more of the
record and shallows it. Five sits between the two. The p10 spread across the
range is about ten points, which is larger than the block-versus-IID gap the
whole section above is about — so **block length is the bigger fudge factor of
the two**, and it is the one with no measurement behind its value. That is the
honest reading, and it is why the number stays named rather than derived. The
Sprint 4A cube ran at five; nothing published moves.

**One quantity, three published values, and the difference is the sample.** `p10
path-drawdown` at block 5 appears three times in this project at three slightly
different numbers, and none of them supersedes another:

| Value | Where it appears | What produced it |
|---|---|---|
| **−59.6%** | The block-versus-IID table above, and DECISIONS, DESIGN, CONTEXT, TRADEOFFS and the README | `measure_3a.py` §1 — 4,000 paths **averaged over five seeds** |
| **−59.4%** | The block-length table directly above | `measure_3a.py` §5 — 4,000 paths at **seed 20260815 only** |
| **−59.3%** | `uv run python engine.py`, the `3A OK` line | 2,000 paths (D-41's `N_PATHS`) at seed 20260815 |

**Quote the five-seed figure.** It is the one the sensitivity in §1b actually
tested for direction, and it is the one every document already carries. The
self-test's −59.3% is a different job: it runs at the cube's own path count so
that a change in the deck or the generator shows up in the line a developer sees
on every run. A reader who finds two of these and assumes one is a typo has found
the reason this note exists.

# Shock timing and size

Life events land in each path's worst accumulation years, found by sorting on
drawdown. There is no correlation coefficient — the placement is the correlation,
and there is nothing to calibrate or defend.

**Which drawdown, though. RESOLVED AT SPRINT 3B: it is `underwater-depth`**, how
far below its running peak the index sits at the end of a year (D-45). D-44 splits
the word into three quantities and D-08's rule admitted two — the other candidate
was `worst-year-return`, the annual return itself, which was never a drawdown at
all. **This paragraph was deliberately ambiguous until the pick and is not any
more.** Neither is `path-drawdown`, which is one number per path and is what the
table above measures.

The two readings were not close: **at three shocks they agree on the year set for
8.1% of paths.** `underwater-depth` was chosen because it carries the word
honestly, because year 0 becomes structurally unshockable under it — the index at
year 0 is its own running peak — and because it puts a quarter as many shocks in
the early years where cumulative Roth basis is short of the $40,000 sale. The
`argsort` tie-break is `kind="stable"`, which resolves to the earlier year and is
named rather than inherited (D-46): **numpy's default is introsort and is not
stable**, and on this deck a tie decides the shock year on up to 11% of paths.

An uncorrelated toggle scatters them randomly instead, seeded from each path's own
content so the answer does not depend on call order.

**Flipping it deflates the tail, and this sentence is now measured rather than
asserted.** It used to read *deflates the tail visibly* with nothing behind it, and
the Sprint 3B plan hedged the same claim on purpose — the document asserted, the
plan hedged, and they could not both be right. Measured at Low over 2,000 paths,
`trad₆₅` at the 10th percentile:

| Shocks | Correlated | Uncorrelated | Difference |
|---|---|---|---|
| 1 | $851,000 | $893,087 | **−4.71%** |
| 3 | $576,048 | $666,761 | **−13.60%** |

So the claim survives, and it is the cheapest demonstration in the project that
the mechanism does real work — but note what it demonstrates now. **The
block-vs-IID comparison already failed its own prediction** (D-05, R8): block does
not fatten the tail relative to an IID draw, it thins it slightly. The toggle's
job is therefore narrower than it was written. It shows that **shock placement**
matters, not that the return model does. `scripts/measure_3b.py` is the source.

A shock is $40,000 real. That is a named fudge factor, chosen at 1.6× a
contribution year so that the forced sale and the skipped contribution are the
same order of magnitude; sensitivity at $25,000 and $80,000 goes in Scope &
Branches, the same treatment block length gets.

What a shock costs depends on the rung, and these are three code branches rather
than three settings of a severity dial:

| Rung | What happens |
|---|---|
| Low | Sell at the shocked year's price. Traditional takes the 10% early-withdrawal penalty plus ordinary income at the **exact incremental** rate (D-16's PIN), on a base net of that year's deferral (D-47); Roth basis comes out free, **in full and untracked** (D-16, 3B) |
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

The status field exists because the tail objectives can genuinely have no
crossing point inside a plausible range. That is an answer, not an error, and the
demo should not die on the interesting cases.

**Measured at Sprint 4A: every one of the 48 cells crosses, so no cell in this
cube exercises the field.** The sentinel path is not untested — T4 is green at
Sprint 2C on D-42's `$185,000` flat profile, which is a different archetype — but
the non-crossing case is a property of a profile this cube does not contain. The
field stays, and the reason moves from *the tail objectives do not cross here* to
*a profile the app can be handed will not cross, and the demo must survive it*.
Recorded rather than repaired: a sprint cannot assert the presence of a case the
model does not contain.

### Scaling past one profile

The cube is computed at the reference archetype (D-14), which is what makes it a build artifact rather than a request. A production version does not delete that property. It multiplies it, and it splits the answer in two.

The two halves have different profile sensitivity. `breakeven()` is a bisection over a deterministic identity, dominated by the user's own tax position, and cheap. The spread — the dots, the fan, the collapse across rungs — is dominated by rung and shock count, and it costs a path set. So the production shape is the shape this app already has (D-15): the line is computed live per user, the cloud is served from the nearest precomputed cell. What changes is only the number of cubes behind the cloud.

| Approach | Good at | Bad at |
|---|---|---|
| One cube, one archetype (today) | Free, byte-reproducible from a seed, honest when labeled | Every user reads an illustration, not their own answer |
| One cube per named segment, nearest-match at request | Still precomputed; *modeled for a profile like yours* is defensible | Needs a stated assignment rule, and the rule becomes product surface |
| Profile axes on the lattice, interpolate between cells | One artifact, continuous-feeling | The response surface is piecewise — bracket edges, the contribution limit, the early-withdrawal penalty, the deferral cap. Interpolating across a discontinuity is wrong in a way that looks right |
| Compute per request, cache on a profile hash | Exact. No interpolation, no staleness | The app now contains stochastic code, against D-12, and a bisection over 2,000 paths is a latency budget rather than a render |

(Batch precompute does not die immediately. A coarse 180-profile lattice is 8,640 cells, roughly 45 minutes at the measured warm per-cell cost. It dies at the two axes after that.)

The claim that would have to be measured first: the segment approach is only honest if the cloud really is insensitive to profile *within* a segment. That is testable with the machinery already here — run the cube at two archetypes and report how far the dots move. If they move a lot, segments are a convenience, not a model. Not measured. `TODO`.

# Tests

**TWO COUNTS, AND THEY ARE DIFFERENT NUMBERS.** `pytest` COLLECTS **250 items**;
the suite holds **168 `def test_` FUNCTIONS**. The gap is `parametrize` — T7 and
T8 alone expand twelve ways each. Both numbers are published because the suite
now asserts one of them: `test_the_suite_asserts_its_own_size` walks the three
test files with `ast` and checks the FUNCTION counts, which is the half an AST
can see without running pytest inside pytest, and the half that survives a
filtered run (D-57).

    functions   29 · 133 · 6      = 168
    collected   35 · 207 · 8      = 250

Three suites, 250 collected. `tests/test_tax.py` — 35, each defending a number
published in `DECISIONS.md`, with the literals restated by hand rather than
imported. `tests/test_engine.py` — opened at Sprint 2A, 207: 54 over the
profile, the ladder, contributions and accumulation, 47 added at Sprint 2B over
the draw, decumulation, the D-26 policy branch, the objective reduction and ruin,
3 added post-2B over `geometric_mean`'s overflow (D-39), 24 added at Sprint
2C over the search, the bracket, the sentinel and the `Result` fields, **19
added at Sprint 3A** over the bootstrap, the D-43 parameters, the digest,
`path-drawdown`, the overflow gate D-39 called *a gate whose failing input
cannot yet be constructed*, and the three measurement records, **59 added at
Sprint 3B** over the three rung branches, the placement reading and its tie-break,
Low's inversion and its guard, D-22's slab, D-39's draw scope, Sprint 4A's ruin
monotonicity, the cache key D-48 widened, and one recorded measurement — D-22's
published Low ratios, which do not reproduce and whose cause is identified — and
**3 added at Sprint 4B**: 4A's two handover wires and the self-count above.
**A second test was DELETED at 3B**, `test_a_nonzero_shock_count_raises_...`,
for the reason 3A set the precedent for. **One test was
DELETED at 3A rather than skipped** — `test_block_paths_still_raise` asserted a
`NotImplementedError` that no longer exists, and a test of scaffolding outlives
its subject silently. 209 written minus 2 deleted is the 207.
`tests/test_deploy_config.py` — opened at P3a, 8 parsing
`railway.toml`. Those eight guard the deploy config rather than the engine, and
they are counted here because `uv run pytest` runs them; the eight numbered
tests below are a different set entirely.

No sprint creates `tests/test_engine.py` — Sprint 2A opened it. **Sprint 4B
closes by mapping** T1–T8 within it, each docstring **quoting** the sentence it
protects with the document and section it came from, so a reviewer can diff a
test against its claim without holding both in their head. **All eight are
green: T1 and T2 as of Sprint 2B; T3, T4 and T5 as of Sprint 2C; T6, T7 and
T8 as of Sprint 3B.** *(This table carried check marks on T6–T8 only, against
its own prose one paragraph up and against §6, which has marked all eight since
2C. Corrected at Sprint 4B.)*

**THE BACKWARD PASS WAS RUN AT SPRINT 4B AND THIS TABLE IS ITS READING.** It
returns **seventeen `test_T*` functions against eight claims**, and neither side
is wrong — the relationship was never specified. **One row per CLAIM, with every
function named inside it and carrying a role**, and the same role word opens the
function's own docstring, so the table and the file agree by construction rather
than by care. A *primary/companion* split was rejected: T2's row holds **two
halves** rather than a primary and a companion, and T4's second function defends
a 2C done-when about the `Result`'s FIELDS rather than asserting that T4's
sentinel breaks somewhere (D-55).

**WHICH COLUMN THE QUOTE COMES FROM.** §6's *Claim it defends* column is a
sentence on T1, T2 and T5 and a citation list on the rest, so the quote is taken
from **whichever cell states what must be true** and the other cell's citations
follow it (D-56). Marked below.

| §6 claim, quoted | From | The functions, and their roles |
|---|---|---|
| **T1** ✅ 2B · *"The identity is real."* | Claim | `test_T1_equal_rates_at_both_ends_produce_equal_outcomes` **primary** · `test_T1_has_teeth_away_from_t_now` **teeth** |
| **T2** ✅ 2B/2C · *"Both accounts fund the same net spending, so the draw subtracts the same real amount from both after-tax paths and vanishes."* | Claim | `test_T2_the_common_draw_cancels_out_of_the_difference` **half 1** · `test_T2_t_star_is_unchanged_across_the_return_rate` **half 2** · `test_T2_matches_the_closed_form_difference` **mechanism**. The two halves closed in different sprints and defend the same sentence — L1 as a sweep, then L1 as a solve |
| **T3** ✅ 2C · *"At the $185,000 test profile (D-42) with D2 ON, Roth shelters strictly more real dollars and the cell returns `always_roth`."* | Test | `test_T3_the_capped_roth_shelters_more_and_the_cell_returns_always_roth` **primary**. **One function, and it is not a gap** — T3 is a strict inequality rather than an identity, asserted at both bracket endpoints, so its teeth are in the same assertions as its claim |
| **T4** ✅ 2C · *"A no-crossing cell returns its sentinel and does not raise."* | Test | `test_T4_a_no_crossing_cell_returns_a_sentinel_rather_than_raising` **primary** · `test_T4s_result_is_fully_populated_and_dollars_is_none_on_purpose` **fields**. *(The second name reads `T4s` rather than `T4`, so a grep anchored on the trailing underscore misses it while `-k "T4"` does not. Left as written; noted so a later backward pass does not read 1 where there are 2.)* |
| **T5** ✅ 2C · *"The headline sentence — you defer at marginal and withdraw across the whole structure from zero."* | Claim | `test_T5_the_todays_law_marker_is_strictly_below_t_star_in_the_base_case` **primary** · `test_T5_has_teeth_because_the_preset_inverts_it` **teeth**. The scope *in the base case* is load-bearing: unscoped the claim is false by design, and at D-40's preset the marker is 15.9% against `t*` = 12.0% |
| **T6** ✅ 3B · *"Low rung: a shock realizes a $40,000 sale; Traditional takes the penalty while Roth basis comes out free."* | Test | `test_T6_a_low_rung_shock_realizes_a_sale_and_breaks_the_multiple` **primary**, which carries its own teeth — the identity holds at 0 shocks and breaks above · `test_T6_traditional_pays_the_penalty_and_roth_basis_comes_out_free` **mechanism** · `test_T6_no_balance_is_clamped_when_a_shock_exceeds_it` **guard**, D-38 reaching the accumulation phase |
| **T7** ✅ 3B · *"Mid rung: a shock skips the contribution year and the balance is never sold."* | Test | `test_T7_a_mid_rung_shock_skips_the_contribution_and_preserves_the_multiple` **primary** · `test_T7_mid_sells_nothing_and_the_cost_is_exactly_the_shares_not_bought` **mechanism**. If Mid ever sold anything the equality breaks and the branch has quietly become Low |
| **T8** ✅ 3B · *"High rung: a shock leaves the portfolio untouched."* | Test | `test_T8_a_high_rung_shock_leaves_the_portfolio_untouched` **primary** · `test_T8_has_teeth_because_the_other_two_rungs_move` **teeth**. Bit-identical to the 0-shock run, not merely proportional to it |

**Both directions, and the backward one is the one nobody runs.** Forward: every
row above names functions that exist. Backward: `grep -c "^def .*T[1-8]"` returns
**17**, and all seventeen appear above — 2 · 3 · 1 · 2 · 2 · 3 · 2 · 2. Selected,
`uv run pytest -k "T1 or T2 or T3 or T4 or T5 or T6 or T7 or T8"` is **59 passed,
191 deselected**; the 59 is the eight claims with their parametrize expansions.

T6–T8 assert the *mechanism*, not the magnitude. Three rungs are three code
branches, so three tests — a severity dial would have needed one.
