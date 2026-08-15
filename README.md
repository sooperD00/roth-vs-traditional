
# Process
- [x] init
- [x] discovery
- [x] research
- [x] synthesis
- [x] design
- [ ] final scope
- [ ] plan
- [ ] deliver

## Domain Analogs

This project models a 401k Roth-vs-Traditional decision, but the problem
shape is an energy analyst's. A tariff and the tax code are the same math object: a
piecewise, jurisdiction-specific, customer-class-dependent rule structure
that converts a quantity into a cost, imposed on the user rather than
chosen by them. Marginal brackets are tiered block rates. A Roth conversion
or an RSU vest is a demand charge — the peak sets the bill, not the
average. And the assumption that decides the answer in both domains is the
one nobody can know: a 25-year utility rate escalator and a 30-year future
tax rate are the same scalar hiding in the same spreadsheet cell.

The full mapping — nine analog pairs, including load profile ↔ contribution
schedule and payback year ↔ break-even marginal rate — is in
[docs/DESIGN.md/#domainanalogs](docs/DESIGN.md/#domainanalogs).

MVP Highlight: **net metering ≡ Roth.** Both ask you to pay a known cost 
today in exchange for favorable treatment under a rule that may change. 
Retroactive net metering rollbacks are not a hypothetical, and neither are the 
tax-treatment changes that have hit retirement accounts elsewhere [##References].

- [ ] **DELIVERABLE: put something in the prototype or PoC that
  shows the end-user what "the rules will change" can mean

## Design

I built this around a threshold instead of a recommendation. Most Roth-vs-Traditional calculators return a number. This one returns the future marginal tax rate at which the two choices tie, and lets the user locate themselves against it.

The threshold exists because the input that decides the answer is your tax rate thirty years from now, and nobody knows it. A problem with an unknowable input has a solution family rather than a solution. Reporting where the answer flips is how you stay useful without inventing precision you don't have.

Four lessons follow from that. Every control on the page delivers one.

| Lesson | What delivers it |
|---|---|
| The return rate never affects the choice | 7 / 10 / 12% buttons |
| Tax rates do affect the choice | Income shape, state toggle, bracket accordion |
| Fragility matters more than the choice, for most people | Resilience-rung slider driving the scatter plot |
| You are not in control of the tax law | Two thresholds side by side, plus the "nevermind" toggle |

### The investment return rate never affects the choice

`(1−t)·(1+r)ⁿ` and `(1+r)ⁿ·(1−t)` are the same expression. The growth factor divides out. Whether the market returns 7% or 12% cannot change which account wins.

The app gives the user three buttons: 7%, 10%, 12%. These are the numbers people argue about online. Clicking through them swings the balance chart hard and leaves the break-even rate sitting still. The user proves the claim by trying to break it.

One convention makes the cancellation exact, and the app states it: the comparison is same pre-tax dollars, $X into Traditional against $X·(1−t) into Roth. Comparing same nominal dollars quietly favors Roth, which is where most calculators go wrong.

### Tax rates do affect the choice

Current income, the shape of that income across a career, state tax, and the brackets you withdraw across all move the threshold. The income curve is draggable, because a peak year is a high-bracket contribution year and a trough is a conversion window.

These controls sit beside the return-rate buttons deliberately. One set moves the answer and the other can't, and the two lessons land harder next to each other than either does alone.

### Fragility matters more than the choice, for most people

The standard risk ladder — stocks, ETFs, bonds, CDs — ranks the volatility of the instrument. This one ranks the fragility of the person holding it, from $400 in cash up through no high-interest debt, maxed contributions, and assets outside the house. Your rung decides whether a life event pauses your saving or forces a sale.

A slider sets the rung, and the slider drives the scatter plot. At a low rung the five definitions of "optimal" disagree by about twenty tax points. At a high rung they collapse onto one value. That collapse is the lesson: with margin, the account question is the only thing left; without it, the account question was never the binding one. Below rung four the headline stops giving a verdict and says so.

One sentence puts both effects in the same unit, which is the only place on the page they can be compared: getting this right is worth about $X, and moving up two rungs is worth about $Y.

### You are not in control of the tax law

Roth is a bet that a rule holds for thirty years. Traditional is a bet that
rates don't rise. Neither is the neutral position, and the app reports both
thresholds side by side rather than making the user click to see the second one.

The bracket-rise case needs no model. It is already the axis — a higher future
rate is a position to the right of the break-even, which is what the user is
locating themselves against anyway. Only the treatment-moves case needs a
second number, and it is one more call to the same function.

After year N the Roth balance is frozen as a tax-free allowance and everything
past it is ordinary income. Traditional needs no branch at all: its withdrawals
were already ordinary income. That absence in the code is the asymmetry.

Next to the toggle: Poland 2013, Ireland 2011, US SECURE Act 2019. The likeliest
version of this is not a tax on Roth withdrawals — it is tax-free money ceasing
to be invisible, counted toward a Medicare premium or the taxable share of
Social Security. Untaxed, and expensive anyway.

# MVP Architechture

# PoC Design — The Math Engine

The engine answers one question: at what future marginal tax rate do Roth and Traditional tie? Everything else in this project is presentation.

```python
breakeven(profile, objective, shocks, policy, paths) -> Result
```

The app imports this module. The PoC is a script that imports it and prints a table. There is one implementation of the math and two ways to reach it.

## Same pre-tax dollars

$1,000 into a Roth costs more take-home than $1,000 into a Traditional, because the Roth dollar was already taxed. Comparing them as equals quietly favors Roth, and most calculators do exactly that.

So the comparison is $X into Traditional against $X·(1−t) into Roth. Under that convention the growth factor appears identically on both sides and divides out, which is what makes the return rate irrelevant to the answer. The convention is load-bearing, not cosmetic.

## The deterministic answer is the stochastic one with the noise turned off

At `n_paths=1` and `sigma=0` the engine produces the headline break-even rate. Same function, same code path. The app's number and the grid's numbers cannot drift apart, because there is nothing for them to drift from.

## Where the paths come from

The engine resamples five-year runs of historical returns rather than drawing years independently.

This is the one modeling choice that changes an answer, so it gets a reason. The project's central claim is that a life event costs you far more when it forces a sale during a downturn. That requires bad years to arrive in runs. Draw years independently — from history or from a fitted lognormal — and a crash year is followed by an ordinary one, so the forced sale happens and then the market recovers underneath it. The mechanism survives; the magnitude doesn't.

Block length is five years. That number is a choice rather than a derivation, and Scope & Branches reports what happens at three and ten. A fudge factor you named and measured is worth more than a distributional assumption nobody examined.

The alternative worth naming: a parametric Monte Carlo is the conventional pick here, and it is thin-tailed *and* memoryless. It buys smoothness at the cost of the only structure this argument needs.

## Shock timing

Life events land in each path's worst years, found by sorting on drawdown. There is no correlation coefficient — the placement is the correlation, and there is nothing to calibrate or defend.

An uncorrelated toggle scatters them randomly instead. Flipping it deflates the tail visibly, which is the cheapest demonstration in the project that the mechanism is doing real work.

What a shock costs depends on the resilience rung, and these are three different code branches rather than three settings of a severity dial:

| Rung | What happens |
|---|---|
| Low | Sell at the shocked year's price. Traditional takes the early-withdrawal penalty; Roth basis comes out free |
| Mid | No sale. Contributions stop that year and resume after |
| High | Absorbed by cash. The portfolio never notices |

Mid is the interesting one. Pausing contributions during a drawdown means you stop buying at exactly the moment prices are lowest — a real cost that appears nowhere on a statement. Low sells at the bottom, mid fails to buy at the bottom, and high does neither.

## Common random numbers

The `(n_paths, n_years)` array is drawn once and reused across every cell, both account types, and every step of the bisection.

The quantity of interest is a small difference between two large numbers. Evaluate the two sides on independent draws and sampling noise swamps the difference you came to measure; evaluate them on the same draws and the noise cancels. The comparison is paired, the cube is reproducible from a seed, and sixty cells cost almost nothing.

## Output

The PoC writes a cube: three rungs × five objectives × four shock counts. Each cell carries the break-even rate, a status field for the cells where the two choices never cross, and both dollar outcomes.

The dollar fields exist because the headline sentence compares two magnitudes — what choosing correctly is worth against what moving up a rung is worth — and a break-even expressed in tax points cannot make that comparison. They were specified before the engine was written, since adding them later means running everything again.

The status field exists because the tail objectives genuinely have no crossing point inside a plausible range. That is an answer, not an error, and the demo should not die on the interesting cases.

## Tests

Four, each asserting a claim made elsewhere in this README.

| Test | Defends |
|---|---|
| Equal rates at both ends produce equal outcomes | The identity is real |
| The break-even is unchanged across 4, 7, 10, and 12 percent | The return rate never affects the choice |
| At the deferral cap, Roth shelters strictly more | The same-dollars trap, and why the limit matters |
| A no-crossing cell returns a sentinel rather than raising | The demo survives the interesting cases |

# Tradeoffs

# Scope and Branches

- The bracket-rise case cuts the opposite way from "nevermind"
- D-15 — the dots come from the reference archetype while the line is personalized
- Some people choose Roth knowing the expected value is worse, because they'd rather not owe anything later. That preference is real and this model does not contain it — none of the five objectives can express "I want it settled."

| Cut | Why | What it would take |
|---|---|---|
| **Certainty preference** — choosing Roth knowing the expected value is worse, because you'd rather not hold an open position | All five objectives are about wealth outcomes. None can express *I want it settled*. This is a real preference and the model does not contain it | A utility formulation over outcome *variance* rather than level, or an explicit premium the user names. Neither fits the threshold framing, which is why it is a branch rather than a sixth objective |
| **Bracket rise as a modeled scenario** | Already on the axis. A higher future rate is a position to the right of `t*` | Nothing. Naming it is the work, and the two-threshold headline does that |
| Two-bar asymmetry chart (p90 gain vs p10 loss, both against median) | Teaches a real lesson — outcomes are left-skewed, the bad case is bigger than the good one — but not L3. L3 is *fragility beats the account choice*, carried by the dot collapse and the $X/$Y sentence. Adjacent, not the same | A `p90_dollars` field in the cube and one chart. ~10 minutes. The semi-variance and ergodicity notes in DESIGN.md are the argument it would draw |
# AI Disclosure

1. research
 - (kept private)

2. design
 - (kept private)

3. sprint planning
 - 

4. code execution -- with Claude Opus 5, Max Thinking
 - asdf


# References

1. reddit r/personalfinance flow doc
    - docs/reddit_personal_finance_flowchart.jpeg
    - https://www.reddit.com/r/personalfinance/comments/4gdlu9/how_to_prioritize_spending_your_money_a_flowchart/

2. Hadamard's Uniqueness Condition
    - "the" failing is exactly Hadamard's uniqueness condition — his 1902 criteria for a well-posed problem being existence, uniqueness, and stable dependence on the inputs. A problem with an unknowable input doesn't have a unique solution; it has a solution family. Reporting the threshold is how you make an ill-posed question answerable without lying about it.

3. Decades Long Bet on a Rule
    - Argentina 2008 (private pension funds nationalized into the state system)
    - Poland 2013-14 (the government cancelled the bond portion of private pension accounts outright)
    - Hungary 2010-11 (effectively forced transfers back to the state pillar)
    - Ireland's 2011-14 pension levy (an annual tax on private pension assets, not income)
    - Spain drew heavily on its social security reserve fund
    - U.S. SECURE Act (2019) eliminated the stretch IRA (retroactively changed the inheritance 
    math for accounts people had already spent decades building. Nobody's money was seized, 
    but the rule moved under people who had already committed).

4. https://www.irs.gov/retirement-plans/cola-increases-for-dollar-limitations-on-benefits-and-contributions
    - For tax year 2026, the maximum employee contribution limit for a 401(k) 
    is $24,500. The total combined limit for employee and employer contributions 
    is $72,000