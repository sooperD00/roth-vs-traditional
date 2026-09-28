# CONTEXT

Design-phase reasoning, kept as written. `DECISIONS.md` wins over this file
wherever the two disagree; sections H and I record every row where they now do.

---

## A. Origin, and the three questions

I asked an AI what my own retirement would look like. I expected a few
paragraphs of blog-grade advice. It wrote a Python Monte Carlo, handed me the
script in about five minutes, and then gave me confident reasons that approach
wasn't the best choice.

The script was one file. I thought: how hard could it be.

Three questions came out of that, and they are what this repo is built to
answer.

| # | Question | What it forces |
|---|---|---|
| 1 | What should I choose for myself, now? | A mid-career profile — real balances, a high marginal rate, a horizon short enough that sequence matters |
| 2 | What should I have chosen at twenty-five, with much less money? | The same question at a low bracket and a long horizon, where the textbook answer is confident, and where the stakes are small in dollars and enormous in years |
| 3 | Does the choice matter at all, next to fragility? | **The one that reframed the project.** |

The first two are the question every calculator answers. The third is the one I
could not find answered anywhere, and it turned out to dominate the other two.

**Roth versus Traditional is the decision you are invited to make.** It is the
lever the interface gives you, the one the articles are written about, and the
one you feel responsible for getting right. What the engine measures is that the
lever has a short throw. A job loss in the wrong decade, a forced sale in a down
year, an ordering of events you did not pick — these move the outcome further
than the election does, and none of them appear on the form.

So the project is not a calculator that answers the question. It is a
measurement of how much smaller that question is than it looks.

<!-- Sections C, D and E are the three halves of that argument: what "optimal"
     can even mean, what a return model has to do before fragility is visible at
     all, and who I scoped the answer to. -->

## B. Design vocabulary

The activity definitions I worked to. Budget accounting for these moved to
`DECISIONS` section 8, which declares research and design outside the
implementation budget and reports actuals separately — see section H.

| Term | What it is | Output artifact |
|---|---|---|
| **Research spike** | Timeboxed question-answering about the *domain*, not the code. "What's in the tax code that matters? What's the historical return record actually made of?" | README section + a bounded list of degrees of freedom |
| **Design spike** | Timeboxed question-answering about the *shape*. Interfaces, contracts, what's stubbed. Ends with a decision, not code. | Contract sketch + scope/branch section |
| **PoC** | Proves one risky thing works. Deliberately throwaway. <!-- design-phase: NOT throwaway here. It became the engine app.py imports — see DECISIONS D-11 --> | Ugly, working, single-purpose |
| **Prototype** | Proves the *experience* works. Real UI, stubbed math. | Demo-able |
| **Application design** | Production shape: modules, contracts, ops. | Doc + diagrams. Out of scope here — becomes README branches |

## C. Requirements synthesis — `Help` / `the` / `optimal`

| Word | Options (simple → complex) | Good at | Bad at |
|---|---|---|---|
| **Help** | 1. Compute and tell | Fast, unambiguous | Black box; user learns nothing; can't defend it to a spouse |
| | 2. Teach, then compute | Educational | Slow; condescends to an analytical audience |
| | 3. Elicit beliefs → reflect → they decide | Honest about who owns the risk | Feels like homework |
| | **4. Surface the threshold; let them self-locate** ← initial pick · design-phase pick | Respects the audience; no false precision | Requires them to hold *one* belief, which is a real ask |
| **the** | 1. Accept it; pick a default scenario | Ships in 20 min | Lies |
| | 2. Reject it; show a region/frontier | Truthful | "Just tell me what to do" |
| | **3. Split: modal answer + where it flips** ← initial pick · design-phase pick | Both | Costs one more chart |
| **optimal** | 1. Max expected after-tax terminal wealth | Simplest | Ignores that you spend it, not stack it |
| | 2. Max after-tax lifetime spending | Right unit | Needs a spending model |
| | 3. Max median outcome | Robust to tails | Hides the tail |
| | 4. Max 10th percentile (regret-minimizing) | Matches how people actually feel | Conservative-looking |
| | 5. P(not running out) | Intuitive | Binary; loses magnitude |
| | *No initial pick.* **All five ship as grid rows — the pick is the user's** ← design-phase pick | Same inputs, swap the objective, watch the answer flip. That divergence is the demo — *measured at 4A, and it flips at the Low rung only; see section I* | Needs a distribution: rows 3–5 are undefined at a fixed return rate |

**The definite article is the trap.** *The* optimal choice presumes one exists,
and the table above is the argument that it does not — five definitions of
optimal, no way to rank them without knowing whose regret is being minimized.
Saying that out loud is the work.

<!-- Sub-section it "Goals & Non-Goals." -->

## D. Return models, simplest → most complex

| # | Model | Good at | Bad at |
|---|---|---|---|
| 1 | Fixed nominal rate (the "historically 12%") | One line of code | Wrong number, and nominal hides inflation |
| 2 | **Fixed real rate (~7%)** ← initial pick (MVP) · design-phase pick (app headline, **7/9/12** selectable — gate 2, D-04a) | Removes a whole class of user confusion | Still pretends variance is zero |
| 3 | Deterministic + sensitivity band | Cheap honesty | Band is arbitrary |
| 4 | **Historical sequence replay** (rolling 30-yr windows) ← initial pick (README branch) | Real sequences, real crashes in real order | ~150 years of overlapping windows ≈ 4–5 independent samples |
| 5 | IID bootstrap (resample years) | More paths; empirical fat tails | Destroys autocorrelation and mean reversion |
| 6 | **Block bootstrap (resample *runs* of years)** ← design-phase pick (PoC / cube) | Keeps short-run sequence structure | Block length is a fudge factor |
| 7 | Parametric Monte Carlo (lognormal μ/σ) | Smooth, tunable | Famously too thin-tailed vs. reality — *and* destroys autocorrelation exactly as #5 does. Written per-row, this table never surfaced that #5 dominates #7 at similar cost |
| 8 | Regime-switching / Student-t | Fat tails | Overkill here |
| 9 | Correlated stochastic inflation + wages + tax policy paths | The honest one | Out of scope for a spike |

Design-phase note: the pick split. **#2 in the app**, with **7/9/12** selectable
(gate 2, D-04a: everything is real, and 10% nominal *is* ~7% real, so a straight
translation would have lost a button) — the point is that clicking through them
does not move the answer. **#6 in the PoC**, with life-event shocks placed into
each path's worst **accumulation** years by drawdown `argsort` rather than a
calibrated correlation coefficient. Shock magnitude is $40,000 real (D-39).

> **The reason below was measured at gate two and did not hold.** See D-05.
> Block bootstrap does *not* fatten the tail against an IID draw on this series —
> p10 `path-drawdown` (D-44) −59.6% vs −63.7% over the 30-year accumulation
> window, so block is the thinner-tailed model. **That row is the finding and the
> median row is not** — re-measured across five seeds at Sprint 3A, the p10 pair
> says block-thinner 5/5 while the median pair splits 3/2 at a few tenths of a
> point. Annual US real returns have a lag-1 autocorrelation of
> −0.035; there is no persistence at this frequency to preserve, and history's
> crashes came packaged with their rebounds. **#6 survives on a different reason:**
> it keeps history's own bad *sequences* intact, and a Low-rung forced sale costs
> the compounding forgone — so the faster post-crash recovery block produces
> (+17.0% the following year, vs +9.5% under IID) makes that cost *larger*, not
> smaller. #6 over #4 is still the Bengen critique applied to ourselves, and at
> ~19.6 independent blocks it now applies to #6 as well.

#6 over #7 because the whole fragility argument needs bad years to arrive in
*runs*. Independent draws scatter them, so a forced sale is followed by a fine
year and the margin-call story survives mechanically while dying economically.
Block length is 5 years, stated rather than hidden; the sensitivity at 3 and 10
goes in Scope & Branches. A named and measured fudge factor reads better than an
unexamined distributional assumption. #6 over #4 is the Bengen critique applied
to ourselves.

**Why #4 sits where it does, and why the critique of it is the interesting
part.** Model #4 is the 4% rule's own method — Bengen's 1994 rolling 30-year
windows over US data, popularized by the Trinity Study in 1998. The binding case
is not 1929, it is 1966: stagflation ate real withdrawals while nominal returns
went nowhere for sixteen years. Bengen has since revised the number upward on a
broader asset mix, and Wade Pfau's international work found much lower safe rates
outside the US, so the original figure is partly survivorship on the
best-performing market of the twentieth century.

**Put plainly: the 4% rule is a backtest with n ≈ 5.** That is the same critique
you would make of any model validated on twenty years of a single market's
history — and it is the reason #6 is the pick rather than #4. Full citations are
in the README's References, item 5.

## E. Who this is scoped for

A calculator has to be built for someone. I scoped to one profile rather than a
set of personas, because a set of personas is a way of not deciding.

**Scoped archetype:** a remote US knowledge worker, 28–45, household income
$120k–$250k, likely dual-income, possibly with kids, possibly holding illiquid
equity, whose state of residence is a live variable.

| Choice | Why |
|---|---|
| 28–45 | The horizon where the answer is actually contested. Earlier than that, Roth wins on nearly any assumption. Later, the balances are large enough that sequence swamps the election |
| HHI $120k–$250k | High enough that the deduction is worth arguing about, low enough that the answer isn't foreclosed by a phase-out |
| State as a variable, not a constant | 0% in WA, TX and FL against 13.3% in CA. Retiring to a different state than you earned in is a first-order input, and almost no calculator asks |
| Illiquid equity | A possible future income spike and a possible zero. Genuinely fuzzy data, and the honest move is to leave it fuzzy rather than model it precisely |

**The tactical consequence: ship a state-tax toggle.** Anyone who opens this app
sets it to their own state within seconds, because residence is the live variable
for exactly the population above. That is the show-don't-tell, and it is why the
toggle survives the cut ladder. **Section H below records that this prediction is
what D-30 acted on.**

`D-19` pins the archetype so figures reproduce: $165,000, single, working state
taxed at 8.5%, retirement state untaxed. Every published number is computed at
that pin, and the app resets it.

## F. Deliverable format

| # | Format | Est. | Good at | Bad at |
|---|---|---|---|---|
| 1 | README + one static chart | 30 min | Guaranteed to land | Not interactive |
| 2 | Jupyter notebook | 45 min | Shows the math | Readers often don't run it; GitHub renders it dead |
| 3 | **Streamlit app** ← initial pick · design-phase pick | 75–90 min | Sliders are free. Python only | Needs hosting. Railway is the known-good path |
| 4 | Single-file HTML + JS | 60–75 min | Zero install, zero host, opens from a click. Known shape | Math in JS reads less "data engineer" |
| 5 | FastAPI + React | 3–4 hr | Real service shape | Over budget |
| 6 | Real tax tables + full Monte Carlo | 6 hr+ | — | No |

**Recommendation: 3, with 1 wrapped around it.** Streamlit plus a README
carrying the design reasoning and the branch section. The only option where the
artifact itself demonstrates the interactive-analytics layer rather than
describing it.

<!-- Deploy is the risk — flag it early; #4 is the fallback if hosting eats
     more than 15 minutes. No local Docker, so Railway-from-GitHub or bust.
     Streamlit dark theme is one TOML line. -->

## G. Blanks not marked, that will bite

| # | Blank | Why it bites |
|---|---|---|
| G1 | **Time allocation** | A budget is a claim made in the README. What matters is that the pruning is visible and justified, not that the app is big. Budget it explicitly, report actuals |
| G2 | **What's stubbed vs. real** | Vote: real bracket math (it's a lookup table), stubbed returns (fixed real rate). Real tax + fake returns reads as "I know which part is the domain". *Gate 2: `tax.py` also owns the 8.5% state rate and the 10% early-withdrawal penalty — they are tax numbers and had no home* |
| G3 | **Contribution limits & the employer match** | The match is pre-tax regardless of the election. Traditional-flavored money arrives whether chosen or not — so almost nobody is a pure case. Cheap to model, surprising to the user |
| G4 | **The "same dollars" trap** | $1,000 into Roth ≠ $1,000 into Traditional. Roth costs more take-home. Most naive calculators get this wrong. Getting it right *and saying so* is the strongest single correction in the app |
| G5 | **Disruption model: what does it hit?** | Contributions (stop saving) vs. balance (withdraw). Different tax consequences — early Traditional withdrawal carries a penalty; Roth basis doesn't. *Gate 2 closed the two blanks this left: **$40,000 real** per event (D-39), landing in the **accumulation phase only** (D-08), since all three rung mechanisms are defined on a contribution stream and Mid has nothing to pause after 65* |
| G6 | **Definition of "educational triage"** | Read as: what does the user need to know *to decide*, vs. what's merely true? Progressive disclosure — one sentence up front, mechanism behind a toggle |
| G7 | **Where the README's branch section lives** | A literal `## Scope & Branches` with Cut / Why / What-it-would-take columns |

---

## H. Gate-two reconciliation

`DECISIONS.md` wins over this file. These are the rows where the two now differ,
so a reader who lands here first isn't misled:

| This file says | Superseded by |
|---|---|
| Part B — the PoC is "deliberately throwaway" | D-11. It became the engine `app.py` imports |
| Part C — `optimal` ships five objectives as grid rows | **D-06. FOUR ship.** Objective 2 is cut: its bad-at column here reads *needs a spending model*, and D-39 made spending a fixed common input, so both accounts fund identical spending and the difference is identically zero. The option stays listed above because this file records the space that was considered. Also constrained by D-22: objective 5 will not bisect on one path, so the deterministic headline rejects it |
| Part D — the app offers 7/10/12 | D-04a. 7/9/12, all real |
| Part D — #6's justification, that block bootstrap keeps bad years in runs and therefore fattens the tail | D-05, measured. It thins the tail slightly. The pick stands on the recovery-forgone channel instead |
| Part D — "a named and measured fudge factor beats an unexamined distributional assumption" | **Unchanged, and vindicated.** Measuring the fudge factor is what caught the bad reason. This is the row the methodology earned |
| Part E — archetype HHI $120k–$250k, state a live variable | D-19 pins it: $165,000, single, working state taxed at 8.5%, retirement state untaxed. The user resets it, exactly as this section predicts |
| Part F — Streamlit + README, ≈75–90 min | The budget table in `remaining-sprints.md`. This estimate predates the cube, the three rung mechanisms and the ladder graphic |
| Part G1 — budget explicitly, report actuals | Unchanged, and it is the reason the overrun is published rather than hidden |
| Part G3 — model the employer match | D8 disposition: grayed, `TODO`. The observation stands — the match is pre-tax regardless of the election, so almost nobody is a pure case — and it is the accordion row that says so |
| Part F — "#4 is the fallback if hosting eats more than 15 minutes" | **DECISIONS R2's subsection.** Written before Sprints 6–8 specified 65 minutes of Streamlit-native UI, so option 4 is a rewrite rather than a fallback. R2 now carries a five-rung ladder, and the 15-minute flag means *open the deployment details pane*, not *abandon Railway* |
| Part G4 — the same-dollars trap | D-01 and D-25. Gate 2 found the arithmetic had been done at 24% before the state toggle existed: the Roth contribution is **$16,538**, and maxing a Roth costs **$36,296** pre-tax against $33,000 of capacity, so the archetype *cannot* max one. That is the same lesson from the other side, and it is now D2's accordion copy |

## I. Sprint 4A reconciliation

Section H reconciled this file against gate two. The cube has since run, and it
measured two things this file asserts. Same rule: `DECISIONS.md` wins, and the
rows below say where.

| This file says | Measured at Sprint 4A |
|---|---|
| Part C — *same inputs, swap the objective, watch the answer flip. That divergence is the demo* | **True at the Low rung with shocks, and nowhere else.** Across objectives 1, 3 and 4 the break-even spread is **1.4656 points at Low with three shocks** and **exactly 0.0000 at Mid and High, at every shock count.** The divergence is real and it is not a property of the objective menu — it is L3 again, seen down a column instead of across a row. The radio button still earns its place, because the user who can move it is the user the answer is contested for. Objective 5 sits about 0.08 points low everywhere for a solver reason (D-51), not a modeling one |
| Part C — `optimal` ships five objectives as grid rows | Four ship (D-06, already in section H). **`dollars` on the objective-5 cells is in FRACTIONS, not money** — its reduction is `P(not running out)`, so a difference of two of them is a difference of two probabilities. Captioned in `cube.json`'s header |
