# Insight

**The standard risk-tolerance ladder measures the wrong noun.** Ponzi → stocks → ETFs → bonds → CDs is an instrument ladder — it ranks the volatility of the thing you bought. Your ladder ranks the fragility of the person holding it. Same portfolio, two people, completely different risk. The instrument ladder can't see that. Yours can.

A simple grid (worst / best / a few in between) as a scenario matrix. Rows = objective, columns = shock count. Cells = the break-even rate.

## Objective ladder — "optimal" (row labels for the grid)

| # | Objective | Good at | Bad at |
|---|---|---|---|
| 1 | Max expected after-tax terminal wealth | Simplest | Ignores that you spend it, not stack it |
| 2 | Max after-tax lifetime spending | Right unit | Needs a spending model |
| 3 | Max median outcome | Robust to tails | Hides the tail |
| 4 | Max 10th percentile (regret-minimizing) | Matches how people actually feel | Conservative-looking |
| 5 | P(not running out) | Intuitive | Binary; loses magnitude |

<!-- Demo moment: same inputs, swap the objective, watch the recommendation flip.
     That IS "explain the numerical dynamics." One radio button. -->

## The scenario grid — objective × life events

Cells = the break-even future marginal rate.

|                            | 0 events | 1 event | 2 events | 3 events |
|----------------------------|----------|---------|----------|----------|
| Max expected terminal      |          |         |          |          |
| Max lifetime spending      |          |         |          |          |
| Max median outcome         |          |         |          |          |
| Max 10th percentile        |          |         |          |          |
| P(not running out)         |          |         |          |          |

<!-- Shape only. Expected pattern: rows 1-2 barely move across columns;
     rows 4-5 move a lot. Expected-value objectives are nearly blind to
     shocks because a halving and a doubling cancel in the mean. Tail
     objectives see them immediately. That divergence is the demo: people
     disagree about Roth vs Traditional not because of the math, but
     because they are silently optimizing different things. -->


## How to read the grid

| Read it… | And you learn |
|---|---|
| Down a column | How much your *definition of optimal* moves the answer |
| Across a row | How much your *fragility* moves the answer |
| Bottom-left vs. top-right | Whether the two forces compound or cancel |
| Spread of the whole grid | The honest uncertainty statement — if X ranges 18–34%, "the optimal choice" was never a scalar |

The pattern you should expect: rows 1–2 barely move across columns; rows 4–5 move a lot. Expected-value objectives are nearly blind to shocks, because a shock that halves your outcome and a boom that doubles it cancel in the mean. Tail objectives see them immediately. That divergence is your demo — it shows the audience that the reason people disagree about Roth vs. Traditional isn't the math, it's that they're silently optimizing different things.

---

# Design

Define a resilience ladder for the chosen representative median user (someone
who works as a software engineer in energy tech):

$400 → $2k → no high-interest debt → tax-advantaged → sinking funds → 
max contributions → backdoor Roth/529 → mortgage payoff → outside assets


## Resilience ladder as a parameter (not a lecture)

Rungs: $400 cash → $2k cash → no high-interest debt → tax-advantaged +
employer match → sinking funds for intended big purchases → pay for those
things → max 401k/IRA limits → backdoor Roth + 529 → mortgage payoff /
no low-interest debt → assets outside the primary residence

**Your rung determines whether a life event is a bump or a forced sale.**

| Rung | What a life event does |
|---|---|
| Low | Forces liquidation — you sell assets to eat |
| Mid | Pauses contributions — you stop buying, keep holding |
| High | Absorbed by cash — the portfolio never notices |

<!-- One slider, ~8-10 stops, feeding shock severity instead of sitting in
     the README. Converts the margin argument from a paragraph into a number
     the user watches move. Also answers "who is this tool for" INSIDE the
     tool: at rung 2 the app can say plainly that the 401k election is not
     your binding constraint yet. -->


One slider, eight stops, and it feeds the shock model instead of sitting in a README. 
That converts point 1 into a number the user can watch move.

```
point 1: the vast majority of us are always borrowing on margin. We have not paid off our house, and we don't have "all the money we will ever need" —  we are in debt to
our future needing to drink clean water and eat food. This means we are on the hook 
for a call of that debt and that timing is not in our power.
```

It also answers "who is this tool for" inside the tool without getting sensitive
— set the slider to rung 2 and the app can say plainly: **the 401k election is not 
your binding constraint yet.**

---

## The mechanism that makes the tail fat

**Life events are not independent of market drawdowns.**

| Model choice | Resulting tail |
|---|---|
| Shocks drawn independently of returns | Mild, roughly symmetric — wrong |
| Shocks correlated with drawdowns | Non-linear, fat — because forced liquidation happens exactly when prices are worst |

This is the margin call. Not levered on paper, but: a 40-year
obligation to eat, no free borrowing against future wages, and the
recall timing is set by the same process that sets asset prices.
ONE correlation coefficient carries the whole argument.

Energy analog: a financed solar customer who loses income in a
downturn must default or sell at the moment resale value is lowest.
Correlated exogenous timing, forced sale at the bottom. Same shape.

---

## Tail visual — options, simplest → most complex

| # | Design | Good at | Bad at |
|---|---|---|---|
| 1 | Percentile fan chart over time | Familiar; free from any MC run | Everyone's seen it; the eye reads the middle, not the edges. **Hides asymmetry** — the thing you want to show |
| 2 | Two bars: gain at p90 vs. loss at p10, both relative to median | Asymmetry is the whole picture, instantly | Loses time structure |
| 3 | **The exchange rate** — "safety costs $X of upside, buys $Y of downside protection" | Literally the point. One sentence, one ratio, no chart-reading required | Needs a defined "safe" comparator |
| 4 | Loss-side histogram only, upside truncated | Honest about what's fungible (upside) vs. what isn't (ruin) | Reads pessimistic; some will bounce off it |
| 5 | Full regret surface / 2D heatmap | Complete | Over budget, over-reads |

<!-- Pick 3, with 2 as the visual under it. #3 is the sentence a user
     repeats to their spouse, which is the real test. -->

DECISION: Pick 3, with 2 as the visual under it. #3 is the sentence a user repeats 
to their spouse, which is the real test.

---

## Vocabulary anchors

| Term | What it names |
|---|---|
| **Sequence-of-returns risk** | Order matters, not just average return — same returns in a different order give a different outcome once you're withdrawing |
| **Liquidity constraint** | You can't borrow freely against future wages. The formal version of the margin framing |
| **Buffer-stock saving** | Deaton / Carroll — why people rationally hold precautionary cash. The rung ladder *is* this theory, drawn |
| **Downside deviation / semi-variance** | Volatility measured only below a target, not around the mean |
| **Certainty equivalent** | The guaranteed amount you'd accept instead of the gamble. Formal version of the exchange rate |
| **Ergodicity** | Ensemble average ≠ time average when ruin is absorbing |

Details worth having in the README:

- MARKOWITZ PREFERRED SEMI-VARIANCE AND SETTLED FOR VARIANCE. In Portfolio
  Selection (1959) he says outright that downside-only risk is the better
  measure, and picks variance because it was computationally tractable in
  1959. The entire standard risk framework is a punch-card-era compute
  compromise nobody revisited. The critique of the instrument ladder has a
  65-year-old co-signer.
- ERGODICITY. The expected value across 10,000 simulated households is not
  what any one household experiences over a lifetime, because ruin is an
  absorbing state — you don't get to average across parallel lives. Ole
  Peters (and Kelly, earlier) is the formal reason "the low end is scarier
  than the high end" is correct rather than merely cautious. Monte Carlo
  tools report the ensemble average. You live the time average. -->

---

## Recommended output stack

| Layer | Artifact | Budget |
|---|---|---|
| Headline | Break-even rate — one number | 5 min |
| Under it | Objective × events grid | 20 min |
| Under that | Exchange rate sentence + two-bar asymmetry | 15 min |
| Input driving all three | Resilience-rung slider → shock severity | 15 min |
| README | Ladder figure, correlation argument, ergodicity note | 20 min |

Total ≈ 75 min, leaving room for the state-tax toggle and deploy.