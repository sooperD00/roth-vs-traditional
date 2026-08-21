# User lessons

What the app is for, click by click.

`DESIGN.md` part 3 says what the interface looks like and `DECISIONS.md` §7 says
where each region goes. **This file says what a person is supposed to walk away
knowing, which control produces that moment, and which visual carries it.** It is
written to be read next to a running app.

The four numbered lessons are the ones the design deck named. Two more emerged
from building it, and they are marked as such — they are not retrofitted onto the
original claim.

---

## The map

| | The lesson | The click | The visual that carries it | The number that lands |
|---|---|---|---|---|
| **L1** | The return rate never moves the answer | `7% / 9% / 12%` | Threshold axis holds still while the balance panels leap | `32.5000%` at all three — the same float |
| **L2** | Tax rates do move it, and there are **two** of them | first paint | Bar edge (marginal) + orange line (effective), then the prose | defer at **32.5**, withdraw at **15.2** |
| **L2b** | The account gap is a **ratio**, and it was fixed on day one | first paint | Linear panel beside log panel | ratio `1.481481…` at every one of 30 years |
| **L3** | Fragility outranks the account choice | ladder checkboxes | Rung changes → `$X` and `$Y` move; dot panels *(Sprint 8)* | whole ladder `$1,234,134` vs account `$1,602,313` |
| **L4** | You are not in control of the tax law | `Tax law changes` toggle | Bar edge slides **right**, movement label names the consequence | `32.5%` → **`58.4%`** |

---

## L1 — the return rate never moves the answer

**THE CLAIM.** Whether the market returns 7%, 9% or 12% real has no bearing on
whether Traditional or Roth is the better account.

**THE CLICK.** The three return buttons. 12% is labelled *implausible* on
purpose — it is the button a skeptic reaches for first, and it is the strongest
form of the demonstration.

**THE VISUAL, AND IT IS TWO THINGS AT ONCE.** The threshold axis does not move.
The balance panels move enormously. One click, two opposite reactions, and the
contrast is the argument — a chart that held still on its own would just look
broken.

| `r` | `t*` (rules hold) | Traditional at 65 | $1M | $2M | second million |
|---|---|---|---|---|---|
| 7% | **32.5000%** | $2,108,867 | age 56 | age 64 | **8 working years** |
| 9% | **32.5000%** | $3,015,334 | age 53 | age 60 | 7 |
| 12% | **32.5000%** | $5,278,624 | age 51 | age 56 | **5** |

**WHY THE AXES ARE PINNED.** Both, for opposite reasons. The rate axis is fixed
because its number does not move — an axis that rescaled under a stationary
number would make 32.5% appear to slide, which teaches the opposite of the
lesson. The balance axes are fixed because their numbers *do* move — auto-scaled,
7% and 12% draw the same curve shape and only the tick labels change, so the
click looks like it did nothing.

**THE SENTENCE THAT LANDS IT.** Dollars are abstract; $2.1M and $5.3M are both
"a lot". Years are not. *Eight working years for the second million at 7%, five
at 12% — and the break-even above does not move at all.*

**WHERE IT IS SCOPED, AND SAY THIS OUT LOUD IF ASKED.** L1 holds for the
break-even **under current rules**. Two other numbers on the page do move with
`r`, and both are correct:

| `r` | `t*` rules hold | `t*` nevermind @20 | today's-law marker |
|---|---|---|---|
| 7% | 32.5000% | 58.4064% | 15.1849% |
| 12% | 32.5000% | 66.4577% | 28.9750% |

The policy threshold moves because the frozen allowance is fixed in real dollars
while the balance compounds, so a bigger portfolio outgrows the same shelter. The
marker moves because a bigger balance funds a bigger draw, and a bigger draw
fills higher brackets. **L1's honest statement is *the return rate never moves
the break-even under current rules*** — which is the claim the engine's own test
suite defends.

---

## L2 — tax rates do move it, and there are two of them

**THE CLAIM.** You defer at one rate and withdraw at a different one, and the
gap between them is the whole decision.

**THE MISREADING THIS EXISTS TO PREVENT.** A careful non-expert reads *my rate is
15.2%, the break-even is 32.5%* and concludes **my taxes would have to double**.
That is wrong, and it is the conclusion an intelligent person arrives at
unaided.

**THE VISUAL.** Two units share one axis and the axis says so: the bar's edge is
a **marginal** rate, the orange dashed line is an **effective** rate. Then the
prose, immediately beneath:

> **You defer at 32.5 cents on the dollar. You withdraw at an average of 15.2.**
> Those are different rates because contributions come off the top of your income
> and withdrawals fill the brackets from zero.

**THE CLICKS THAT MOVE IT.** The state income tax toggle, the income shape boxes,
and D4 in the Personalize accordion (retiring to a state that also taxes income).
These are the controls that actually change the answer — which is the point.

**THE EDGE CASE WORTH KNOWING.** Set current income low enough with state tax off
and the marginal rate is 0%. The app says **"Roth, at every rate"** — because a
Traditional contribution then defers no tax at all. Nothing to trade away, so
nothing to trade it for. It is the plainest version of L2 on the page.

---

## L2b — the gap is a ratio, and it was fixed on day one

*Not in the original four. It came out of building the linear/log pair, and it is
the most direct answer to "I'll decide later."*

**THE CLAIM.** The Traditional-to-Roth gap is a constant ratio. It does not grow.
The account choice does not start mattering more later.

**THE VISUAL, AND IT ONLY WORKS AS A PAIR.**

| | linear panel | log panel |
|---|---|---|
| what it shows | the gap "widening" | two parallel lines |
| age 35 | $7,962 apart | 0.170696 decades apart |
| age 64 | $685,382 apart | 0.170696 decades apart |
| the ratio | `1.481481…` | `1.481481…` |

**86× in dollars. Zero change in the ratio.** It is exactly `1 ÷ (1 − t_now)`,
constant to nine decimals at every one of the thirty years.

**WHY THE LINEAR PANEL IS KEPT RATHER THAN CORRECTED AWAY.** It is how every
brokerage statement draws this, so it is the picture the audience walks in
holding. Deleting it wins the argument against nobody. Showing the two side by
side makes the misreading visible *as* a misreading, which is the only way to
retire it.

**THE $1M AND $2M RULES MAKE THE SAME POINT TWICE** — crowded at the top of the
linear panel, evenly spaced on the log panel, because a doubling is a doubling
wherever it happens.

---

## L3 — fragility, and the number that argues against us

**THE CLAIM AS ORIGINALLY WRITTEN.** *Fragility affects most users much more than
this Roth vs Traditional decision.*

**THE CLICK.** The ten ladder checkboxes on the left rail. The rung is derived
from the highest **contiguous** stop, never typed — so ticking stop 10 while 7–9
are unticked changes nothing except a warning about the gap.

**THE VISUAL.** `$X` moves with the account choice; `$Y` moves with the rung. The
three fragility panels *(Sprint 8, region and caption reserved)* carry the other
half — the collapse across Low, Mid and High, which needs three points to read as
a trend.

**AND HERE IS THE PART TO SAY BEFORE ANYONE ELSE DOES.** Measured at objective 4,
one shock, δ = 10:

| | value |
|---|---|
| Account choice at Low (`$X`) | **$1,602,313** |
| One rung step, Low → Mid (`$Y`) | $756,988 |
| One rung step, Mid → High | $477,146 |
| **The whole ladder, Low → High** | **$1,234,134** |
| whole ladder ÷ account choice | **0.77×** |

**At δ = 10 the entire ladder is worth less than getting the account right.** L3,
as written, is not supported by the app's own numbers.

**AND δ IS WHY, WHICH IS THE INTERESTING PART.** δ is the assumed size of the
user's miss — how far off the break-even they land. It sets `$X` almost outright
while barely touching `$Y`:

| δ | account choice at Low | whole ladder ÷ account choice |
|---|---|---|
| 2 points | $264,662 | **4.66×** — L3 looks strong |
| 10 points | $1,602,313 | **0.77×** — L3 looks weak |

**The app publishes δ = 10, names it on the page, and therefore prints the
number that makes its own thesis look weakest.** That was chosen deliberately:
ten points is about a bracket and a half, the generous case. Switching to δ = 2
to make L3 come out better would be picking the assumption that flatters the
conclusion.

**HOW TO SAY IT.** *The dollar comparison does not support the fragility claim at
the honest δ, and we published the honest δ.* That is a stronger position in a
review than a claim that survives only at δ = 2.

---

## L4 — you are not in control of the tax law

**THE CLAIM.** Roth's advantage depends on a rule that a future legislature can
change, and you have no say in it.

**THE COUNTERINTUITIVE CORE, AND IT IS THE BEST THING IN THE APP.** A rule change
that harms **only Roth** makes **Traditional win over a wider range**, not a
narrower one. Nearly everyone predicts the opposite. The design deck itself drew
it backwards.

**THE CLICK.** The `Tax law changes` toggle, plus its year.

**THE VISUAL.** The bar's edge slides from 32.5% to 58.4% — **rightward** — and
the movement is annotated in words, not left to the reader:

> `→ 58.4% if rules change at year 20 — you would be on the Traditional side`

**WHY WORDS AND NOT JUST A TICK.** A mark drawn on the bar inherits the colour
underneath it, and that colour belongs to the *other* scenario. Drawn as a bare
tick, 58.4% sat in the green "Roth wins" band and read as *Roth territory* —
precisely backwards. Words cannot be recoloured by the band beneath them.

**THE DEMO, AND IT IS THE ONLY PLACE L4 LANDS AS A FLIP RATHER THAN AN
ARGUMENT.**

1. Click **Early-career preset** → *"Roth, by 3.9 points."*
2. Throw the **Tax law changes** toggle → *"Traditional, by 13.2 points."*

Same person. Same portfolio. One rule change, and the answer inverts.

**THE EXTREME, IF SOMEONE PUSHES.** Drag the year down to 1 or 2 and the bar
loses its boundary entirely: *"No future tax rate rescues Roth here."* A change
that early freezes only $16,538 tax-free, so Roth never catches up at any rate on
the axis. It crosses back over between year 2 and year 3.

**THE PRECEDENTS ARE VERBAL RIGHT NOW.** Poland 2013 · Ireland 2011 · US SECURE
Act 2019. They were removed from the page at the round-2 review because they are
narration. **This is the one worth saying aloud without fail** — it is what stops
the scenario reading as invented, and it is the claim a skeptic challenges first.

---

## The lessons with no number

**NEITHER OPTION IS THE NEUTRAL ONE.** Printed under the axis, always:
*Roth bets the treatment holds. Traditional bets the rates do. Neither is the
neutral choice — pick which rule you'd rather be exposed to.* There is no safe
default, and the page never implies one.

**SOMETIMES IT IS A WASH.** Within ±2 points of the break-even the headline says
so outright rather than naming a winner. At the archetype the gap is 17.3 points
so it never fires — it exists for the profiles a panelist types in, which is
exactly what happens at a demo.

**SAME PRE-TAX DOLLARS IN.** Traditional is a pre-tax balance; Roth is already
after tax. The dashed orange curve is Traditional after tax and lies exactly on
the Roth curve. Comparing the raw balances would silently favour Roth, and the
dashed line is the proof that the comparison is honest.

**NOTHING IS CLAMPED.** Balances may go negative. A Low-rung saver with $8,000 in
the account can "sell" $73,959 of it — right for the model, wrong as a sentence
about a person, and said on the page rather than hidden.

**THE DOLLARS ARE THE REFERENCE PROFILE'S.** Your controls choose which *rung* is
read out of the precomputed grid. They do not move the dollar figures. The line
is yours; the dots are the archetype's.

---

## A 90-second path through it

| | Do this | They should see |
|---|---|---|
| 1 | Land on first paint | *Traditional, by 17.3 points* — then read the two-rates sentence aloud (**L2**) |
| 2 | Click **12%** | Balance curves leap; **32.5% does not move a pixel** (**L1**) |
| 3 | Point at the two balance panels | Widening gap on the left, parallel lines on the right (**L2b**) |
| 4 | Click **Early-career preset** | *Roth, by 3.9 points* |
| 5 | Throw **Tax law changes** | *Traditional, by 13.2 points* — **the flip** (**L4**) |
| 6 | Drag the year to **1** | *No future tax rate rescues Roth here* |
| 7 | Untick ladder stops | `$X` and `$Y` move with the rung (**L3**) |

Steps 4 and 5 are the demo. Everything else supports them.

---

## What this app does not claim

- **That the fragility claim survives at the published δ.** It does not, and the
  page prints the number that says so.
- **That the return model is settled.** The balance panels are deterministic at
  the chosen real rate; the fragility panels come from the historical series,
  which compounds at about 6.8%. Thresholds agree across the two — the scalar
  multiple guarantees it — **but the dollars do not.** Traditional's balance at 65
  has a median of $2,123,538 under the series, +4.7% against the deterministic
  proxy. Captioned where the two meet, because the person who spots it
  unexplained will be a panelist.
- **That every departure is modelled.** Five of eight are on the page; a taxable
  side account and an employer match are named and left unmodelled on purpose.
  Both are Traditional-flavoured money that arrives whether or not you choose it,
  so almost nobody is a pure case — and saying that is worth more than modelling
  it badly.
- **That any of this is advice.** The output is a rate and a comparison, not a
  recommendation.
