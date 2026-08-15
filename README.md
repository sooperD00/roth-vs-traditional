# Process

- [x] init
- [x] discovery
- [x] research
- [x] synthesis
- [x] design
- [x] final scope — design gate two closed
- [ ] plan
- [ ] deliver

## Domain Analogs

This project models a 401k Roth-vs-Traditional decision, but the problem shape is
an energy analyst's. A tariff and the tax code are the same math object: a piecewise,
jurisdiction-specific, customer-class-dependent rule structure that converts a
quantity into a cost, imposed on the user rather than chosen by them. Marginal
brackets are tiered block rates. A Roth conversion or an RSU vest is a demand
charge — the peak sets the bill, not the average. And the assumption that decides
the answer in both domains is the one nobody can know: a 25-year utility rate
escalator and a 30-year future tax rate are the same scalar hiding in the same
spreadsheet cell.

The full mapping — nine analog pairs, including load profile ↔ contribution
schedule and payback year ↔ break-even marginal rate — is in
[docs/DESIGN.md](docs/DESIGN.md).

MVP highlight: **net metering ≡ Roth.** Both ask you to pay a known cost today in
exchange for favorable treatment under a rule that may change. Retroactive net
metering rollbacks are not a hypothetical, and neither are the tax-treatment
changes that have hit retirement accounts elsewhere — see References.

---

## Design

I built this around a threshold instead of a recommendation. Most
Roth-vs-Traditional calculators return a number. This one returns the future
marginal tax rate at which the two choices tie, and lets the user locate
themselves against it.

The threshold exists because the input that decides the answer is your tax rate
thirty years from now, and nobody knows it. A problem with an unknowable input
has a solution family rather than a solution. Reporting where the answer flips is
how you stay useful without inventing precision you don't have.

Four lessons follow. Every control on the page delivers one.

| Lesson | What delivers it |
|---|---|
| The return rate never affects the choice | 7 / 9 / 12% buttons |
| Tax rates do affect the choice | Income shape, state toggles, bracket accordion |
| Fragility matters more than the choice, for most people | Ten-stop ladder driving the three dot panels |
| You are not in control of the tax law | Two thresholds side by side, plus the nevermind toggle |

### The investment return rate never affects the choice

`(1−t)·(1+r)ⁿ` and `(1+r)ⁿ·(1−t)` are the same expression. The growth factor
divides out. Whether the market returns 7% or 12% cannot change which account
wins.

The app gives three buttons: 7%, 9%, 12%, all real. These are the figures people
argue about, and 12% real is labeled implausible on purpose — it is the button a
skeptic reaches for first. Clicking through them swings the balance chart hard
and leaves the break-even rate sitting still. Measured at the archetype, `t*`
comes out to 32.5000% at every one of `r ∈ {4, 7, 9, 12}%`. The user proves the
claim by trying to break it.

One convention makes the cancellation exact, and the app states it: the
comparison is same pre-tax dollars, $X into Traditional against $X·(1−t) into
Roth. Comparing same nominal dollars quietly favors Roth, which is where most
calculators go wrong.

### Tax rates do affect the choice

Current income, the shape of that income across a career, state tax while
working, state tax in retirement, and the brackets you withdraw across all move
the threshold. The income curve is draggable, because a peak year is a
high-bracket contribution year and a trough is a conversion window.

These controls sit beside the return-rate buttons deliberately. One set moves the
answer and the other can't, and the two lessons land harder next to each other
than either does alone.

One sentence sits under the threshold axis, because it is the hardest idea on the
page and a legend won't carry it: **you defer at 32.5 cents on the dollar and
withdraw at an average of 15.2, because contributions come off the top of your
income and withdrawals fill the brackets from zero.** Both numbers are computed,
so the sentence moves with the controls. Without it the natural misreading is
*the break-even is 32.5% and I'm at 15.2%, so my taxes would have to double* —
which is wrong, and it is where a careful non-expert lands on their own.

### Fragility matters more than the choice, for most people

The standard risk ladder — stocks, ETFs, bonds, CDs — ranks the volatility of the
instrument. This one ranks the fragility of the person holding it, from $400 in
cash up through no high-interest debt, maxed contributions, and assets outside
the house. Your position decides whether a life event pauses your saving or
forces a sale.

Ten checkboxes set the position; the rung is the highest contiguous stop cleared,
and it drives three dot panels. The prediction is that at a low rung the five
definitions of "optimal" disagree across a wide span of tax points and at a high
rung they collapse onto one value — that collapse is the lesson, and Sprint 8
measures whether it happens. If the dots don't collapse, L3 isn't landing, and it
is better to find that out in the sprint than on stage.

Below the first two gates the headline stops giving a verdict and names the
binding gate instead. The thresholds and the dollar sentence stay on screen —
that is the rung where the dollar comparison proves the most.

One sentence puts both effects in the same unit, which is the only place on the
page they can be compared: getting this right is worth about $X, and moving up
one rung is worth about $Y. Both are read at objective 4, one shock, and a
10-point miss.

### You are not in control of the tax law

Roth is a bet that a rule holds for thirty years. Traditional is a bet that rates
don't rise. Neither is the neutral position, and the app reports both thresholds
side by side rather than making the user click to see the second one.

The bracket-rise case needs no model. It is already the axis — a higher future
rate is a position to the right of the break-even, which is what the user is
locating themselves against anyway. Only the treatment-moves case needs a second
number, and it is one more call to the same function.

After year N the Roth balance is frozen as a tax-free allowance and everything
past it is ordinary income. Traditional needs no branch at all: its withdrawals
were already ordinary income. That absence in the code is the asymmetry.

**And the second threshold moves the way nobody expects.** A policy that harms
only Roth raises the rate at which Roth becomes worthwhile. At the reference
profile the two thresholds are 32.5% and 58.4%, both far to the right of a 15.2%
marker — so the scenario you were told makes Roth safe is the one that widens
Traditional's lead. The design deck had this drawn backwards, with the second
threshold at 14% and Roth winning to its right. Fixing it is written up in
`GATE-2.md`.

The flip is real, but it belongs to someone else. Load the early-career preset —
$60,000 now, $200,000 at the peak, no state income tax — and the numbers read
12.0% under current rules against a 15.9% marker, which is Roth; then 29.1% once
the rule moves, which is Traditional. **The rule change costs the low-bracket
saver Roth was supposed to be for.**

Next to the toggle: Poland 2013, Ireland 2011, US SECURE Act 2019. The likeliest
version of this is not a tax on Roth withdrawals — it is tax-free money ceasing
to be invisible, counted toward a Medicare premium or the taxable share of Social
Security. Untaxed, and expensive anyway.

---

# PoC Design — The Math Engine

The engine answers one question: at what future marginal tax rate do Roth and
Traditional tie? Everything else in this project is presentation.

```python
breakeven(profile, objective, shocks, policy, paths) -> Result
```

The app imports this module. The PoC is a script that imports it and prints a
table. There is one implementation of the math and two ways to reach it.

## Same pre-tax dollars

$1,000 into a Roth costs more take-home than $1,000 into a Traditional, because
the Roth dollar was already taxed. Comparing them as equals quietly favors Roth,
and most calculators do exactly that.

So the comparison is $X into Traditional against $X·(1−t) into Roth. Under that
convention the growth factor appears identically on both sides and divides out,
which is what makes the return rate irrelevant. The convention is load-bearing,
not cosmetic.

At the archetype that is $24,500 to Traditional against $16,538 to Roth. The
Roth deliberately under-fills, and the app says so.

## Both accounts have to fund the same life

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

## The deterministic answer is the stochastic one with the noise turned off

At a `(1, n_years)` constant-return paths array the engine produces the headline
break-even rate. Same function, same code path. The app's number and the grid's
numbers cannot drift apart, because there is nothing for them to drift from.

## Nothing is clamped at zero

Balances are allowed to go negative. Ruin is a recorded flag, not an absorbing
floor.

This is not a stylistic choice. Objectives 1 through 3 bisect on the difference
between two terminal values, and that difference is monotone in the future rate
only if the arithmetic runs. Clamp it and both sides pile up at $0 across a range
of rates, the difference goes flat, and bisection returns whichever endpoint it
started nearest. Objectives 4 and 5 read the flag; nobody reads a clamped
balance.

## Where the paths come from

The engine resamples five-year runs of historical returns rather than drawing
years independently. The deck is `returns.py` — 98 annual real total returns on
US equities, 1928 through 2025, from Damodaran's series with CPI from the same
workbook, deflated on load. It compounds at 6.78% real against an 8.61%
arithmetic mean; the 1.83-point gap is variance drag and matches σ²/2 at a
19.30% standard deviation.

## What the block bootstrap does and does not buy

This is the one modeling choice that changes an answer, so it got a reason. Then
it got measured, and the reason was wrong.

**The reason I wrote first.** A life event costs you far more when it forces a
sale during a downturn, and that requires bad years to arrive in runs. Draw years
independently and a crash is followed by an ordinary year, so the mechanism
survives and the magnitude doesn't.

**What 4,000 paths on the real series actually say.**

| | Block(5) | IID |
|---|---|---|
| Median maximum drawdown | −42.6% | −43.0% |
| p10 maximum drawdown | −59.7% | **−64.3%** |
| Year after the worst year | **+17.0%** | +9.5% |
| Next three years, cumulative | **+39.5%** | +32.1% |
| …of which negative | 5% | 21% |

Block bootstrap has the **thinner** left tail and the **faster** rebound. It is
the conservative model here, which is the opposite of what I claimed.

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
five-year sequence reliably: the median path's worst run lands at −10.26%
annualized, which is exactly 1937–41.

**And the honest limit.** Ninety-eight years at block length five is about
**19.6 independent blocks.** That is the same n ≈ 5 critique this README makes of
Bengen's 4% rule, now pointed at this model. The structure assumption cannot be
validated at n ≈ 20; it can only be stated.

The alternative worth naming: a parametric Monte Carlo is the conventional pick
here, and it is thin-tailed *and* memoryless. It buys smoothness, and on this
evidence it would have cost less than I assumed.

Block length is five years — a choice rather than a derivation, with sensitivity
at three and ten in Scope & Branches. **Measuring the fudge factor is what caught
the bad reason.** That is the whole argument for naming them.

## Shock timing and size

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

## Common random numbers

The `(n_paths, n_years)` array is drawn once and reused across every cell, both
account types, and every step of the bisection.

The quantity of interest is a small difference between two large numbers.
Evaluate the two sides on independent draws and sampling noise swamps the
difference you came to measure; evaluate them on the same draws and the noise
cancels. The comparison is paired, the cube is reproducible from
`seed = 20260815` at `n_paths = 2000`, and sixty cells cost almost nothing.

## Output

The PoC writes a cube: three rungs × five objectives × four shock counts. Each
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

## Tests

Eight, each asserting a claim made elsewhere in this README.

| Test | Defends |
|---|---|
| T1 · Equal rates at both ends produce equal outcomes | The identity is real |
| T2 · `t*` unchanged across 4, 7, 9, 12 percent, and the Traditional path is the Roth path scaled by `(1−t_later)` at every year | The return rate never affects the choice — the scalar-multiple assertion is why it holds for any `r`, not just the four sampled |
| T3 · At the $185,000 test profile with the cap binding, Roth shelters strictly more | The same-dollars trap, and why the limit matters |
| T4 · A no-crossing cell returns a sentinel rather than raising | The demo survives the interesting cases |
| T5 · The today's-law marker is strictly below `t*` | You defer at marginal and withdraw across the whole structure from zero |
| T6 · Low rung — a shock realizes a sale; Traditional takes the penalty, Roth basis is free | The forced-liquidation branch |
| T7 · Mid rung — a shock skips a contribution year and nothing is sold | The shares not bought |
| T8 · High rung — a shock leaves the portfolio untouched | The control case |

---

# Headline numbers

Reproducible from `DECISIONS.md` alone. Every figure here comes out of the
deterministic engine at 7% real.

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
makes about the utility rate escalator hiding in a spreadsheet cell.

---

# Scope and Branches

| Cut | Why | What it would take |
|---|---|---|
| **Certainty preference** — choosing Roth knowing the expected value is worse, because you'd rather not hold an open position | All five objectives are about wealth outcomes. None can express *I want it settled*. This is a real preference and the model does not contain it | A utility formulation over outcome *variance* rather than level, or an explicit premium the user names. Neither fits the threshold framing, which is why it is a branch rather than a sixth objective |
| **Bracket rise as a modeled scenario** | Already on the axis. A higher future rate is a position to the right of `t*` | Nothing. Naming it is the work, and the two-threshold headline does that |
| **Symmetric "nevermind"** — the rule change hitting Traditional's deduction too | The design deck's original words were "all tax benefits go away." Making it symmetric deletes the asymmetry the whole policy branch rests on, and it still doesn't flip the archetype toward Roth | A Traditional branch in the decumulation loop. ~20 minutes and one lost argument |
| **Two-bar asymmetry chart** (p90 gain vs p10 loss, both against median) | Teaches a real lesson — outcomes are left-skewed, the bad case is bigger than the good one — but not L3. L3 is *fragility beats the account choice*, carried by the dot collapse and the $X/$Y sentence. Adjacent, not the same | A `p90` field in the cube and one chart. ~10 minutes. The semi-variance and ergodicity notes in DESIGN.md are the argument it would draw |
| **Block length sensitivity** | Block length 5 is a stated fudge factor | Run at 3 and 10, record the deltas. Sprint 3 does this and reports it here |
| **Block bootstrap over IID** | Kept, but its original justification failed measurement — block thins the tail rather than fattening it (p10 drawdown −59.7% vs −64.3%), because annual real returns have a lag-1 autocorrelation of −0.035. It survives on the recovery-forgone channel, and on reproducing history's own worst five-year run. At ~19.6 independent blocks the structure claim cannot be validated, only stated | Switching to IID would delete one fudge factor and simplify Sprint 3 by about five minutes. The reason not to is that block is the more conservative tail and keeps real sequences intact — but that is a preference, not a result, and this row says so |
| **Shock magnitude sensitivity** | $40,000 is the same kind of fudge factor | Run at $25,000 and $80,000. Same sprint |
| **Over-65 deductions** — the permanent $2,050 additional standard deduction, and the OBBB senior deduction of up to $6,000 | Deferred, not overlooked. Together they move the today's-law marker from 15.2% to **13.5%**, which *widens* Traditional's lead — so omitting them **understates** the recommendation rather than inflating it. Neither changes a verdict, and the early-career preset's flip survives at 14.4% against a 12.0% threshold. The $6,000 also sunsets, and applying it across a 35-year retirement would assert something the statute doesn't say | The $2,050 is one conditional on age in `tax.py` and is the honest one to wire first. The $6,000 needs a phaseout and an expiry |
| **SALT deductibility** — state tax is added flat to the federal marginal rate | **The larger of the two known biases, and it points the other way.** For a filer who itemizes the true combined rate is `0.24 + 0.085 × (1 − 0.24)` = **30.5%, not 32.5%** — two points on the headline number itself, in the direction that flatters Traditional. It bites only on itemizers: state income tax alone is $14,025 at the archetype against a $16,100 standard deduction, so it takes about $2,075 more of mortgage interest, property tax or charity to cross | An itemize-or-not branch, and the state rate applied inside the federal calculation rather than beside it |
| **Real per-state tax data** | One boolean at 8.5% carries the whole state effect | A state table and a second lookup. The `TODO` is in `tax.py` |
| **MFJ and Head of Household** | Single only — the UI models one income curve and one age, so a household is something the controls cannot represent. *(The earlier reason given here, overlapping HoH bracket edges, does not survive checking: the published 2026 HoH column is contiguous.)* | Two more bracket tables, verified against the same primary source |
| **Employer match, and the taxable side account** | Both are Traditional-flavored money that arrives whether or not you choose it. Grayed in the accordion as evidence of completeness | A second contribution stream and a taxable-account model. This is where the next hour would go |

---

# AI Disclosure

1. research — (kept private)
2. design — (kept private)
3. design gate two — see `GATE-2.md`
4. sprint planning — *(link)*
5. code execution, Claude Opus 5 with extended thinking — *(link)*

---

# References

1. **r/personalfinance flowchart** — `docs/reddit_personal_finance_flowchart.jpeg`
   https://www.reddit.com/r/personalfinance/comments/4gdlu9/how_to_prioritize_spending_your_money_a_flowchart/
   The ten-stop ladder is this flowchart's ordering, including the detail that
   the employer match comes before clearing medium-interest debt.

2. **Hadamard's uniqueness condition.** The failing here is exactly Hadamard's
   1902 criteria for a well-posed problem — existence, uniqueness, and stable
   dependence on the inputs. A problem with an unknowable input doesn't have a
   unique solution; it has a solution family. Reporting the threshold is how you
   make an ill-posed question answerable without lying about it.

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
   IRS IR-2025-103, Oct. 9, 2025, and Revenue Procedure 2025-32:
   https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill
   and https://www.irs.gov/pub/irs-drop/rp-25-32.pdf
   All seven single-filer edges and the $16,100 standard deduction verified
   against it on 2026-08-15, and corroborated independently by the Tax
   Foundation's 2026 table — the two agree on every edge. Deferral limit
   $24,500, combined employee-plus-employer limit $72,000:
   https://www.irs.gov/retirement-plans/cola-increases-for-dollar-limitations-on-benefits-and-contributions

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
