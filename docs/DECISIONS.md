# DECISIONS

Status: **design gate two closed.** This file is the build contract.

---

## Changelog — Gate 2

Twenty-six defects found. Twenty-three resolved here, three were decisions and
are recorded as such. Numbers in this file are now reproduced from a working
deterministic engine rather than asserted.

| # | Was | Now | What it breaks if you skip it |
|---|---|---|---|
| C1 | D-33 appeared **twice** with different ladders and different bands | One D-33. Flowchart ladder, Low 1–3 / Mid 4–6 / High 7–10 | Sprint 7 has no ladder to wire |
| C2 | D-32 gave **six** checkboxes; D-37 and Sprint 7 assumed **ten** | Ten stops, ten checkboxes, defaults 1–6 on | The archetype cannot reach Mid — contiguity breaks at stop 1 |
| C3 | `t_now` was **24%** in D-19/D-24/D-25 and **32.5%** in D-18/D-30 | 32.5% is live. D-24 relabeled *federal only* | Three dollar figures and both headline numbers |
| C4 | D-25's $18,620 / $32,237 / "$763 spare" computed at 24% | Recomputed at 32.5%. **T3 moves to a $185,000 test profile** | T3's premise is false at the archetype — capacity $33,000 vs $36,296 needed |
| C5 | D-19 gave the income shape's *shape* but no **values** | Four points in D-19, linear interpolation stated | The marker is unreproducible from this file |
| C6 | D-28's 80% replacement **bankrupts both accounts** — Roth at 79, Traditional at 92 | D-28 rewritten: the draw is sized off the Roth (D-39) | Objective 1 returns $0 = $0 and the base case has no crossing |
| C7 | The year-20 toggle was specified to **flip the verdict to Roth** | It cannot. The threshold moves *right*, to 58.4%. See D-40 | Sprint 2 and Sprint 6 both had unpassable done-whens |
| C8 | No **shock magnitude** anywhere in any document | D-39: $40,000 real | Sprint 3 cannot run at all |
| C9 | §5 held **one** `roth_dollars`/`trad_dollars` pair; D-17 needs two δ | `dollars` keyed by δ | Sprint 4's cross-δ invariant is uncheckable |
| C10 | No **absorbing-floor** rule | D-38: no clamp. Ruin is a flag | The terminal difference stops being monotone and D-22's gate can't hold |
| C11 | `seed`, `n_paths`, return series all unspecified | D-41 | The cube is not reproducible |
| C12 | 8.5% state rate and the 10% penalty had no home | Both in `tax.py`, per D-21 | Sprint 1's "no tax number elsewhere" rule was unsatisfiable |
| C13 | Return buttons were **7/10/12** in §1 and README, **7/9/12** in D-04a | 7 / 9 / 12 everywhere | — |
| C14 | DoD said "the **four** tests in §6"; §6 has eight | Eight | — |
| C15 | §8 budget (130) and remaining-sprints (160) disagreed, with different cut lists | One table, in remaining-sprints. §8 points at it | Two different cut #1s, one of which deletes L1's only gesture |
| C16 | §7 caption said the mockup shows **8 rungs** | It shows ten, correctly banded | — |
| C17 | §0's DESIGN.md grid-column row superseded nothing | Deleted | — |
| C18 | README carried five stale numbers the panel would read | Propagated | §0 calls these defects, not notes |

**The three that were decisions, not defects:**

1. **The flip.** Kept, reversed, and moved to a preset. See D-40.
2. **The draw rule.** Sized to what the Roth sustains. The published marker moves from ~17% to **15.2%**. See D-39.
3. **The return series.** Stubbed for Sprints 1–2; real series is a gate on Sprint 3. See D-41.

---

## 0. Precedence

Where this file and `CONTEXT.md` disagree, **this file wins.** `CONTEXT.md` is
the tradeoff reference — it records the option space that was considered, and its
option tables carry two marker sets: `← initial pick` for the choice made during
synthesis, `← design-phase pick` for what survived design.

`README.md` is a working surface, not a source. It is reconciled against this
file at each gate — so between gates it may disagree, and this file wins by
default. **Except** where the README states a number or a claim the panel will
read, in which case the disagreement is a defect and gets fixed in the same pass.

`remaining-sprints.md` is a **source, not a working surface — but only for the
budget table and the cut ladder**, both of which §8 delegates to it. On anything
else this file wins. Gate two's HoH correction landed in D-21 and in `tax.py` and
did *not* land in Sprint 1's goal paragraph, where it then propagated forward into
a sprint brief. That gap is what this row closes.

`TRADEOFFS.md` is a **compressed restatement, not a source.** It reorganizes the
option space against the brief's own Focus and Evaluation language so it can be
read aloud. It restates rather than links because a presentation touchpoint that
sends the reader to another file is not a touchpoint. **This file wins over it,
and `CONTEXT.md` holds the fuller design-phase framing it was compressed from.**
Where a compression drops a qualification that changes an answer, that is a
defect and gets fixed here first.

`ENGINE.md` is the **numerical specification** — the engine's contract, the five
choices that change an answer, the return series, the shock branches, the cube
and the tests. It is where the README's PoC essay went. This file still wins:
§5 holds the contract and §6 holds the eight engine tests, and `ENGINE.md`
explains them rather than defining them. **One exception worth naming:** the
block-vs-IID measurement lives there in full, and D-05 carries the summary. If
those two ever disagree, the measurement is the fact and D-05 is the stale copy.

`DESIGN.md` is the **design rationale and the mockup gallery.** The five `*.PNG`
files now live there with captions saying what each one decides and what moved
afterwards. It is still a working surface and this file still wins — §7 remains
the layout contract — but the deck is no longer loose: a mockup that disagrees
with a decision now disagrees *in writing, next to the decision*, rather than
inside an image nobody opened.

Design deck (`*.PNG`) — working surface, captioned in `DESIGN.md` part 3. This
file wins. Where the deck carries a number that exists nowhere else, that number
gets promoted into a decision rather than left in an image. **Two have not been
promoted and are labeled design-phase estimates in the gallery:** the income
shape's *"ending at $200k costs Traditional 1.4 points"*, and the layout's *"$Y —
about four times the account choice."* Neither is verifiable before Sprints 2 and
4, and Sprint 4's third gate warns `$Y` may land near `$X`.

Conflicts that markers can't express:

| Says | Superseded by |
|---|---|
| CONTEXT part B — PoC is "deliberately throwaway" | D-11. The PoC *is* the engine `app.py` imports |
| CONTEXT part B — "Cost in the budget" includes research and design | §8. Both are outside the implementation budget |
| CONTEXT part G3 — model the employer match | D8 disposition. Grayed, `TODO` |
| CONTEXT part D — app buttons are 7 / 10 / 12 | D-04a. 7 / 9 / 12, all real |
| DESIGN.md — rung slider, 8–10 stops, feeding shock *severity* | D-16. Three rungs; the rung selects a *mechanism* |
| DESIGN.md — tail visual "Pick 3, with 2 under it" | Cut. The $X/$Y sentence survives; the two-bar chart is a Scope & Branches row |
| DESIGN.md — "Recommended output stack ≈ 75 min" | §8 |
| DESIGN.md — the nine-stop resilience ladder | D-33. The ten-stop flowchart ladder replaces it |
| DESIGN.md — flat file of design-phase notes | Restructured into four parts: insight, model, interface gallery, gate-two reversals. All superseded text and its banners are preserved |
| README — the PoC/engine essay | Moved to `ENGINE.md`. README is now a standard repo README |
| README — the four-lesson prose | Moved to `DESIGN.md`. The L1 identity stays in the README because it is five lines and everything rests on it |
| Deck `withdrawal-rate-graphic` — second threshold at 14%, Roth wins | D-40. It is 58.4%, and the verdict does not flip at the archetype |
| Deck `accordion-input` D7 — "all tax benefits go away" | D-09. Roth only. Traditional needs no branch, and that absence is the asymmetry |
| Deck `fragility-graph` — "Rung 2", "Rung 3", eight rungs, 160 floats | D-16. Three rungs, named never numbered, 48 cells |

---

## 1. What the user learns

Four lessons. Every control on the page exists to deliver one. If a feature
can't be traced to a row here, cut it.

| # | Lesson | Delivered by | Mechanism |
|---|---|---|---|
| L1 | The return rate never affects Roth vs. Traditional | **7 / 9 / 12%** buttons | The knob that doesn't work. Balance graph swings, headline number does not |
| L2 | Tax rates do affect it | Income shape, state toggles, the accordion | Headline number moves |
| L3 | Fragility matters more than this decision, for most users | Rung control → three-panel dot plot; the $X/$Y sentence | Dots collapse as the rung rises. Dollar sentence puts both effects in one unit |
| L4 | You are not in control of the tax law | "Nevermind" toggle + the early-career preset | Roth's bet is named as a bet, and priced |

**L1 and L2 are taught by contrast.** The return-rate buttons sit physically
beside the tax controls. One moves the answer, one can't.

---

## 2. Definition of done

Shipped when all eight exist:

1. `tax.py` — 2026 brackets, deferral limit, state rate, early-withdrawal penalty. One module, source comments
2. `engine.py` — pure functions, no Streamlit import
3. `spike_grid.py` — CLI; writes `cube.json` and prints the markdown grid
4. `test_engine.py` — **the eight tests in §6**
5. `tests/test_tax.py` — **Sprint 1's assertions**, listed in that sprint's done-when. Not among §6's eight, which are engine tests
6. `app.py` — Streamlit, layout per §7
7. Deployed, reachable by URL
8. `## Scope & Branches` in README — Cut / Why / What-it-would-take

Not done, and labeled as such in the UI: historical sequence replay, a real
spending model, RMDs, Social Security, real per-state tax data, the employer
match.

---

## 3. Decisions

### Conventions

| ID | Decision | Why |
|---|---|---|
| D-01 | **Contribution convention: same pre-tax dollars.** $X to Traditional vs. $X·(1−`t_now`) to Roth | The identity is exact only under this convention, so L1 depends on it. Same-nominal-dollars silently favors Roth — that is the G4 trap. Name the convention in one sentence in the app |
| D-02 | **Wash band: ±2 percentage points.** Inside it the headline reads "It's a wash"; outside it names the winner | The headline is the sentence the app exists to print. At the archetype the gap is 17.3 points, so the band is not load-bearing there — it exists for the profiles a panelist will type in |
| D-03 | **Income shape is independent of the resilience rung.** The user sets both | Superseded reason — see D-31. The conclusion stands on the stronger argument: income is a fourth instrument ladder, and same income / different fragility is the entire project |

### Model

| ID | Decision | Why |
|---|---|---|
| D-04a | **Return buttons are 7 / 9 / 12%, all real.** Default 7%. Each labeled with its nominal equivalent; 12% is labeled implausible on purpose | D-27 puts the model in real dollars, so nominal buttons would misread. 7 and 10 collapse under conversion — 10% nominal *is* ~7% real — so a straight translation loses a button. The implausible button is the one a skeptic reaches for first, and watching `t*` hold still there is L1 at full force. Caption: *this input drives the picture, not the answer.* **Supersedes D-04** |
| D-05 | **Block bootstrap over a historical real return series. Block length 5.** Shocks placed into each path's worst accumulation years by drawdown `argsort`. **The reason for this pick was measured at gate two and did not hold; the pick survives on a different one** | Block length 5 keeps history's own bad sequences intact as sequences — 1929–32, 1937–41, 1973–74 arrive as units, and the median path's worst five-year run lands exactly on history's own, −10.26% annualized. **What it does not do is fatten the tail.** Measured against an IID draw on the same series: median maximum drawdown −42.6% against −43.0%, p10 −59.7% against −64.3%. Block is the *thinner*-tailed, more conservative model here, which is the opposite of what this decision originally claimed. One number explains it — the lag-1 autocorrelation of annual US real returns is **−0.035**, so at annual frequency there is no persistence to preserve, and the crashes in this record came packaged with their own rebounds (1931 sits in a block with 1933, 1974 with 1975, 2008 with 2009). **The forced-liquidation mechanism survives through a different channel:** a Low-rung shock sells $40,000 at a depressed price and the cost is the compounding forgone, so a *faster* rebound makes that cost larger. Measured, the year after the worst year returns +17.0% under block against +9.5% under IID. Block length remains a stated fudge factor with sensitivity at 3 and 10 in Scope & Branches, and `argsort` placement still means no correlation coefficient to calibrate or defend. **This row is the project's own methodology applied to itself** — a named fudge factor got measured, its justification failed, and the failure is written down rather than the reason quietly rewritten |
| D-06 | **`optimal` is a parameter, not a choice. FOUR objectives ship as grid rows.** Objective 2, max after-tax lifetime spending, is **CUT** | Same inputs, swap the objective, watch the recommendation flip. That is still the demo. **Objective 2's precondition is gone:** `DESIGN.md`'s bad-at column for it read *needs a spending model*, and D-39 made spending a fixed common input, which deleted the thing the objective measured. Under a common draw and D-38's no-clamping rule, both accounts pay the same amount every year on every path *including ruined ones* — so lifetime spending is `35 × S` for both and the difference is **identically zero, at every `t_later`, every rung, every shock count.** Not small. Zero. Bisection has nothing to bracket. **Both repairs fail.** Spending-until-first-shortfall is a step function and is still degenerate at Mid and High. Maximum-sustainable-spending is *algebraically the same test as objective 1* — `S*_T > S*_R ⟺ trad₆₅(1−t_later) > roth₆₅`, the compounding factor and the annuity factor dividing out — so it can never produce a different row at any cell, verified including at Low where nothing is proportional. **This is a gate-two regression, recorded rather than quietly dropped:** D-39 changed a precondition and the objective ladder was not re-checked against it. Scope & Branches carries the row |
| D-07 | **Common random numbers.** Draw the `(n_paths, n_years)` array once; reuse across every cell, both choices, every bisection step | The quantity of interest is a small difference between two large numbers. Pairing removes sampling noise from that difference, makes the cube reproducible from a seed, and makes 48 cells cheap |
| D-08 | **Shock columns are a count (0–3); shock *timing* is correlated with drawdown.** Correlated is the default; an uncorrelated toggle exists for contrast. Shocks land in the **accumulation phase only** (ages 35–64), placed at the `n` deepest drawdown years of each path | Forced liquidation lands when prices are worst. Restricting to accumulation is not a simplification of convenience: all three rung mechanisms are defined on a contribution stream, and Mid's "contributions pause" has nothing to pause after 65 |
| D-09 | **Policy scenario is "nevermind," prospective and Roth-only.** After year N (default 20), Roth withdrawals above the frozen allowance are ordinary income. Traditional is unchanged | Simpler than a haircut: no rate parameter. Prospective is what actually tends to happen when rules move. The deck said "all tax benefits go away"; making it symmetric would delete the asymmetry that D-26 depends on |
| D-10 | **Both thresholds display, always.** The headline holds `t*` under current rules and `t*` with the nevermind policy applied. Labeled: *Roth bets the treatment holds. Traditional bets the rates do. Neither is the neutral choice — pick which rule you'd rather be exposed to* | The toggle as originally specified showed only Roth's exposure while the offsetting case sat in a README branch nobody at a demo will read. The correction costs one extra `breakeven()` call, because the bracket-rise case is *already on the axis*: a higher future rate is a position to the right of `t*` |

### Architecture

| ID | Decision | Why |
|---|---|---|
| D-11 | **One engine module, two entry points.** `spike_grid.py` and `app.py` both import `engine.py`. No duplicated math | The PoC is not throwaway. It is a script that imports a module and prints a table |
| D-12 | **The app contains no stochastic code.** It reads `cube.json` | Deploys smaller, cannot be slow in front of a panel, no seed in production |
| D-14 | **The cube is computed at the reference archetype, not at the user's profile** | It is precomputed. Consequence in D-15 |
| D-15 | **User inputs move the vertical line, not the dots.** The dot plot is labeled *modeled for the reference profile*. **Two different mismatches separate the line from the dots, and only one of them is a labeling problem** | The interaction still lands — set the state toggle and the line slides through the cloud — but the app must not imply the dots are personalized. **Profile mismatch:** the line is the user's, the dots are the archetype's. That is what the label fixes. **Return-model mismatch:** the line is deterministic at 7% real (D-04a) while the dots come from a bootstrap whose mean path compounds at **6.78%** — the historical series' own geometric mean, which `return_series.py` forbids rescaling. **This does not move `t*`.** The scalar multiple holds per path, so the 0-shock slab lands on `t_now` at any return rate; that is T2 and D-22's validation gate, and it is why L1 survives the mismatch untouched. **It moves dollars.** So a reviewer comparing a figure on the balance graph against a figure in the $X/$Y sentence will find them a few points apart, and the answer is that they are computed on different return models deliberately. Label it where the dollar sentence lives. Do not close the gap by editing the series. **RESTORED in Sprint 2A: the deterministic proxy at the series' own geometric mean puts T65 at $2,028,066 against $2,108,867 at 7%, a 3.83% gap.** That is a proxy, not the bootstrap — Sprint 3 supplies the real distribution and decides what Sprint 6's caption carries |
| D-22 | **Deterministic mode is `paths` of shape `(1, n_years)` filled with the constant real return.** `make_paths(kind, ...)` builds either a constant array or a bootstrap array; the engine cannot tell which it received. **Supersedes D-13** | The block bootstrap has no `sigma` — that parameter belonged to the parametric model D-05 rejected. Expressing the deterministic path as a shape rather than a setting makes D-13's claim structural: one function, one code path, nothing to drift. Two consequences: at `n_paths=1` objectives 1, 3 and 4 collapse, so the headline is objective-independent by construction; and objective 5 degenerates to a step function that will not bisect, so the deterministic path must reject it. **Validation gate, and it is DERIVABLE rather than measured — see the note below** |
| D-38 | **The engine never clamps a balance at zero.** Balances are allowed to go negative; ruin is a recorded boolean, not an absorbing floor | Objectives 1–3 bisect on the *difference* between two terminal values. That difference is monotone in `t_later` and crosses zero at `t_now` — but only if the arithmetic is allowed to run. Clamping makes both sides pile up at $0 over a range of rates, the difference goes flat, and bisection returns whichever endpoint it started nearest. D-22's gate cannot hold with a floor in the code. Objectives 4 and 5 read the flag; nobody reads a clamped balance |

### D-15 — the dollar side of the return-model mismatch  ✅ PROXY RESTORED, Sprint 2A

**What was wrong.** D-15 published the bootstrap's compounding rate as ~6.81%.
The series compounds at **6.7762%**, which is what `return_series.py` measures,
what its self-test prints, and what the README carries. The row and the file
disagreed by three basis points.

**Where 6.81% came from, because it is not a typo.** Deflate the same 98 rows by
*subtraction* — `nominal − cpi` — and the geometric mean is 6.8176%. D-27
prohibits subtraction by name and `return_series.py` implements Fisher-exact,
which is the entire reason it keeps `RAW` around. So 6.81% is a pre-D-27 number
that outlived the convention that produced it. **Recording the provenance rather
than the correction alone, on the same principle D-05 records a failed reason
rather than quietly rewriting it.**

**What is still stale, and why it is blank rather than guessed.** Two figures
were computed off 6.81% and both are downstream of an engine that does not exist
yet:

| Figure | Published | Status |
|---|---|---|
| T65 under the bootstrap | ~~$2,038,611~~ | **PROXY RESTORED: $2,028,066.** Deterministic run at the series' geometric mean, Sprint 2A. Real bootstrap value still owed by Sprint 3 |
| Dollar gap, deterministic vs. bootstrap | ~~3.4%~~ | **PROXY RESTORED: 3.83%** |
| T65 at 7% deterministic | $2,108,867 | Unaffected — not a bootstrap number |

**One precision note, and it is the reason this is computed rather than typed.**
The proxy must run at the geometric mean *the series measures*, not at the
four-decimal rounding of it. `6.7762%` as a literal returns **$2,028,055.76**;
the series' own **6.776229%** returns **$2,028,066.17**, which is the published
figure. Ten dollars, on a number that is only in this document to be checked
against — so `engine.geometric_mean(return_series.REAL_RETURNS)` is the operand,
and the rounded literal appears nowhere in code.

**Two stages, because the published figure was a proxy and nobody said so.**
$2,038,611 was a *deterministic run at the series' geometric mean*, not a
bootstrap result. Sprint 2A can reproduce that object directly — expect **T65 ≈
$2,028,066 at 6.7762%, a 3.83% gap** — and clearing this row's tag is one of its
done-whens. But the proxy and the bootstrap are not the same thing: by Jensen,
the mean of terminal values need not equal the terminal of the mean-compounding
path. **Sprint 3 checks the proxy against the real distribution and reports the
difference**, whichever way it goes.

A level-contribution stream over 30 years lands about **3.9%** below the 7% case
at 6.7762%, against 3.35% at 6.81%. That is an annuity approximation, not the
model: the archetype's contributions are `min(0.20 × income, cap)` over D-19's
four-point income shape, not a level stream. **It is here to say which direction
the correction runs and roughly how far — not to be published.** Sprint 2A's
accumulation produces the proxy (~$2,028,066, a 3.83% gap) and Sprint 3 produces
the real distribution.

**Consequence for Sprint 6.** Its done-when instructs a caption reading *dollar
figures differ by about 3.4%*. That number is withdrawn; the caption is not.
Write it from Sprint 3's output — the caption is about the bootstrap, so the
Sprint 2A proxy is not the right number to publish there. The caption's job — telling a panelist the two
return models are different on purpose — is unchanged and is still load-bearing.

### D-22 — why the collapse is derivable, and how much of the cube it covers

**One fact, applied four times.** Objectives 1, 3, 4 and 5 are all monotone
functionals of the after-tax terminal *distribution* — mean, median, 10th
percentile, `P(< 0)`. When the Traditional and Roth after-tax distributions are
related by a positive scalar `(1−t_later)/(1−t_now)`, every one of them crosses
where that scalar equals 1. That is not four coincidences to be measured; it is
one property to be asserted.

**Where the multiple survives:**

| Rung | Mechanism | Multiple | Why |
|---|---|---|---|
| High | Absorbed by cash | **preserved** | Nothing is touched |
| Mid | Contribution paused | **preserved** | Removes `c` from Traditional and `c·(1−t_now)` from Roth. The paused stream scales identically |
| Low, 0 shocks | Nothing fires | **preserved** | No branch runs |
| Low, shocks ≥ 1 | Forced sale | **BROKEN** | Traditional grosses up through the penalty; Roth basis comes out free. The only asymmetric mechanism in the cube |

Measured on a constant-return path, `roth/trad` holds at `0.675000000000` for
Mid and High at 0, 1 and 3 shocks, and moves to `0.689633` and `0.708591` at Low.

**So the gate is: the entire Mid and High slabs equal `t_now` at every shock
count — 32 of 48 cells — plus Low's 0-shock row, for 36 of 48 asserted exactly.
Only 12 cells vary.** Assert it as an identity, not a tolerance.

**This is not a defect to repair.** Giving Mid an asymmetric mechanism so the
dot panels show a gradient is exactly what this project is against. The honest
reading is sharper than the gradient would have been: *the account question is
only contested for people without a buffer.* At Mid and above, every definition
of optimal returns the same number.

**Three mechanisms break proportionality, and only one is in the cube:**

| Mechanism | Where it acts |
|---|---|
| Low's early-withdrawal penalty | The cube — the 12 informative cells |
| The "nevermind" policy | Headline only. D-26 keeps policy off the cube axes |
| **D2 ON** — Roth filled to the cap after-tax | Accordion only |

D2 is the reason T3 matters more than its position in the test list suggests: it
is the only coverage of the second asymmetric mechanism.

### D-16 — Resilience rungs

**Three rungs, not eight.** `DESIGN.md` describes three *mechanisms*; eight would
have meant inventing six intermediate severities with nothing behind them.

**The rung selects which branch of the shock code runs.** It is not a multiplier.

| Rung | What a shock does | Implementation |
|---|---|---|
| **Low** — no buffer | Forces liquidation | Sell $40,000 (D-39) at the shocked year's price. Traditional takes the 10% early-withdrawal penalty plus ordinary income; Roth basis comes out free |
| **Mid** — some buffer | Pauses contributions | No sale. Contributions stop for the shock year and resume after. The cost is the shares not bought |
| **High** — deep buffer | Absorbed by cash | Portfolio untouched. The control case |

Mid carries the argument and is the branch a reviewer opens first. Pausing
contributions during a drawdown means you stop buying at exactly the moment
prices are lowest — a real cost that appears nowhere on a statement. Low sells at
the bottom; mid fails to buy at the bottom; high does neither.

Rungs are **named in the UI, never numbered.** The ladder figure keeps all ten
stops and marks which three bands are modeled: the figure is the argument, the
three are the model.

**PIN — Low's withdrawal is taxed at the exact incremental rate, not a flat one.**
The sale must NET `SHOCK_AMOUNT` after both the 10% penalty and ordinary income
tax on the withdrawal. That tax is `tax_on(income(age) + W) − tax_on(income(age))`
— the actual incremental bill in that year — plus the state rate when the
working-state boolean is on. **Using `t_now` here would be D-21's error running
one direction over:** `t_now` is the rate the *contribution* avoided, in a
different year at a different income, and a withdrawal is a different event.

This is not a rounding decision. Low-with-shocks is the entire varying part of
the cube, and three flat readings of "ordinary income" span **3.5 points** of
`t*` at three shocks:

| Flat reading | `t*` |
|---|---|
| `t_now`, 32.5% combined | 29.14% |
| Federal only, 24% | 32.08% |
| Marginal rate at that year's income | 32.64% |

The exact incremental method is a fourth value and is the one to implement. It
reuses `tax.py` and adds no new tax number.

### The archetype and the numbers that come out of it

| ID | Decision | Why |
|---|---|---|
| D-19 | **Reference archetype:** age 35, retires 65, dies 100, filing single. **Income shape, four points, linearly interpolated: (35, $165,000) · (38, $75,000) · (55, $200,000) · (65, $200,000).** Savings rate 20%. State: **taxed while working, untaxed in retirement** (D-30 defaults) | Filing single because the UI models one income curve and one age — an MFJ archetype is a household the controls cannot represent. $165k is what a Staff SWE recognizes. The trough at 38 is parental leave, which CONTEXT part E already flags as this population's low-bracket window. The end point is flat from the peak rather than declining: ending high is the *conservative* case, since it raises retirement spending and narrows Traditional's lead. **Consequence: `t_now` = 24% federal, 32.5% combined. The absence of a bracket straddle is no longer an assumption** — `deferral_rate` and `marginal_rate` agree exactly at $165,000, and `tests/test_tax.py` asserts it. See the D-21 subsection for the three incomes where they do not |
| D-20 | **Horizon runs to age 100; `n_years = 100 − current_age`.** Two phases: accumulate 35→64, decumulate 65→99. All objectives evaluate at 100. Guard on `current_age >= 65` | Planning past median longevity is the standard convention, because outliving the money is the failure that matters. Splitting the phases is what puts `t*` where it belongs — in the withdrawal years. "Terminal wealth" therefore means bequest at 100, not balance at 65. **Cash flows land at PERIOD END in both phases:** accumulation is `balance = balance × (1+r) + contribution`, so a contribution earns no return in the year it is made, and decumulation is `balance = balance × (1+r) − draw`. Stated because it is not free — the annuity-due reading puts Traditional at 65 at $2,256,487 instead of $2,108,867 (**+7.0%**) and the draw at $101,305 instead of $108,397 (**−6.5%**). Close enough to read as an interpolation bug, far enough to fail every published gate |
| D-21 | **`tax.py` implements SINGLE only:** 2026 bracket edges, seven rates, standard deduction $16,100, deferral cap $24,500, **state rate 8.5%**, **early-withdrawal penalty 10%**. MFJ and HoH are `TODO` stubs. **Over-65 deductions are DEFERRED, not omitted. `t_now` is a deferral rate, not a bracket lookup — see the subsection below** | The deduction applies to withdrawals, so gross minus deduction gives taxable and the bracket table is read in taxable terms. **The state rate and the penalty live here too**: they are tax numbers, and Sprint 1's rule is that no tax number appears anywhere else in the repo. **`tests/` is the one exemption**, stated in the module docstring, because a hand-verification that imports the constant it is verifying tests nothing. **R1 is CLOSED** — all seven single edges and the $16,100 deduction verified against IRS IR-2025-103 / Rev. Proc. 2025-32 on 2026-08-15, and corroborated by Tax Foundation's independent table. **HoH's reason changed:** the stub was justified by "overlapping edges at the 24/32 boundary," which the primary source does not support — the published HoH column is contiguous (24% ends $201,750, 32% begins $201,751). It stands on D-19's reason instead, which is the stronger one: the UI models one income curve and one age, so a household is something the controls cannot represent. **The two over-65 deductions are deferred with their cost measured** — the permanent $2,050 (IRC 63(f)) and the temporary, income-phased OBBB senior deduction of up to $6,000. Together they take the marker from 15.2% to 13.5%, which *widens* Traditional's lead, so omitting them understates the recommendation rather than inflating it. **That 13.5% carries a convention and the constants' comment must name it: the gross is RE-SOLVED to hold D-39's net draw at $108,397, falling to ~$125,380, and the $6,000 is taken IN FULL.** Holding gross fixed at $127,804 instead gives 13.7%; applying the OBBB phaseout gives ~14.1%. Neither changes a verdict; the preset's flip survives at 14.4% against a 12.0% threshold. Wiring the $2,050 is one conditional on age and is the honest one to do first; the $6,000 sunsets, and applying it across a 35-year retirement would assert something the statute does not say |
| D-25 | **D-01 applies at `min(capacity, cap)` in PRE-TAX terms.** Base case: **$24,500 to Traditional, $16,538 to Roth** — the Roth deliberately under-fills. **D2 ON** fills the Roth to $24,500 after-tax, which costs **$36,296** pre-tax | The cap is denominated in nominal contribution dollars — pre-tax for Traditional, after-tax for Roth — so at the boundary the two choice sets differ and the convention has nothing to equalize. Reading D-01 as a comparison device rather than a behavior model resolves this: the base case isolates the *timing* effect, D2 adds the *capacity* effect back as a named step. Under-filling the Roth is artificial and is labeled so in the app. **THE RULE AS CODE, since T3 needs it and no row stated it.** Let `capacity = savings_rate × income(age)`. D2 **OFF**: `trad = min(capacity, cap)` and `roth = trad × (1 − t_now)` — same pre-tax dollars, D-01. D2 **ON**: `trad` is unchanged at `min(capacity, cap)` — it cannot go higher, the cap binds — while `roth = min(cap, capacity × (1 − t_now))` in AFTER-TAX dollars. **D2 deliberately breaks D-01's same-pre-tax-dollars convention, and that break IS the asymmetric mechanism** D-22 counts alongside Low's penalty. **The unaffordable case degrades rather than raising:** at the archetype the second term binds at $22,275 against the $24,500 cap, which is D-42's lesson rendered as arithmetic instead of as an exception — the cap is denominated in dollars that cost you more, so it binds before it looks like it should |
| D-42 | **T3 runs at a `$185,000` test profile, not the archetype.** The archetype's capacity is $33,000 against the $36,296 cost of maxing the Roth — **D2 ON is unaffordable there.** $185,000 gives $37,000 of capacity and stays inside the 24% bracket after the deferral. **FULL SPEC, because "a $185,000 test profile" is not a profile:** income **FLAT at $185,000 at all four D-19 knots**, savings rate 20%, age 35, state-while-working ON and state-in-retirement OFF (the D-30 defaults), `stops` at D-32's default. **The flatness is the specification, not a convenience** — D2's affordability is tested every contribution year, and any shape with a trough fails it there: drop the archetype's $75,000 parental-leave year into this profile and capacity falls to $15,000 against a $36,296 cost, so the Roth silently under-fills in exactly the years T3 is about | The earlier claim that "T3 exercises something the reference user experiences" was arithmetic done at 24% before the state toggle landed. Rather than move the archetype to rescue the test, the test gets its own profile and says so. **The archetype's inability to max a Roth is itself the D2 lesson from the other side** — the cap is denominated in dollars that cost you more, so it binds sooner than it looks — and that sentence belongs in the accordion's D2 row |
| D-27 | **Everything is in real 2026 dollars. Brackets are treated as inflation-indexed**, so the 2026 table applies at every year of the run | Returns are declared real while the bracket table is nominal 2026. Running both unstated models a world where brackets never index — bracket creep would push the future rate up on its own and `t*` would be an artifact of the mismatch. Real throughout is internally consistent and matches the law. The return series must be real or deflated on load |
| D-28 | **Spending stub: save 20% of income during accumulation.** Modeled contribution is `min(0.20 × income, cap)`; the remainder is out of model and displayed grayed. **The retirement draw is not a replacement rate — see D-39** | Source: BLS household budget data. The grayed excess ($8,500/yr at the archetype) shares a row with D3: both are money outside the 401k that the model does not follow. **The 80% replacement rate is deleted as an input.** It bankrupted both accounts — $160,000/yr net against a $24,500 cap is not fundable at any return, and objective 1 returned $0 = $0 with no crossing |
| D-39 | **The retirement draw is the level real after-tax amount that leaves 15% of the *Roth's* age-65 balance at 100.** Computed, not input. Sized off the Roth because it is the smaller account and therefore the binding one. **Shock magnitude is $40,000 real per life event** | Two accounts are being compared as ways to fund *the same life*, so the spending path must be one both can afford. Size it off Traditional and the Roth runs out at 79 — every Roth-side objective then reports ruin and the comparison is measuring the spending assumption instead of the tax question. The 15% margin exists so the base case is not sitting exactly at zero, where any shock ruins every objective at once. **At the archetype: $108,397/yr, which is 54% of final working income** — reported as an outcome, with one sentence saying Social Security and the grayed taxable account cover the rest. $40,000 for a shock is a named fudge factor, 1.6× a contribution year, so Low's forced sale and Mid's skipped year are the same order of magnitude; sensitivity at $25k and $80k goes in Scope & Branches, the same treatment block length gets. **SCOPE PIN — the draw is solved once per `(profile, rate)`, on the SHOCK-FREE Roth accumulation, and held fixed across every path, rung and shock count.** `outcome()` therefore runs the Roth accumulation regardless of which account was asked for, which keeps §5's signature intact. **When computing a shocked cell the draw is STILL sized shock-free:** if it adapted, spending would quietly shrink to whatever the damaged balance could afford and ruin would never fire, and Sprint 4 needs ruin at 0.0 on the 0-shock slab and non-zero outside it. A draw that adapts defines away the thing being measured. The draw may vary with `r` harmlessly, since it cancels out of the difference (T2) |
| D-30 | **State tax is two booleans sharing one rate: 8.5%, DC's marginal rate at the archetype income.** Top strip — *State income tax, while working* — default **yes**. Accordion D4 — *You retire to a state that also taxes income* — default **no**. Added to the federal rate; real per-state data stays `TODO` | Split because the earning state and the retirement state are different assumptions and the gap between them is the whole effect. Defaults are earn-taxed / retire-untaxed, the widest honest case: **`t_now` = 32.5% against a 15.2% federal effective marker, Traditional by 17.3 points.** Turning the accordion half on narrows it back toward baseline — that is the correction most users should apply, so **D4's row is exempt from the accordion read-only cut.** 8.5% rather than a round 10 because DC's top rate applies above ~$1M and the panel files DC returns. **Simplification, quantified: the rate is additive to the federal rate, ignoring SALT deductibility.** For a filer who itemizes the true combined marginal rate is `0.24 + 0.085 × (1 − 0.24)` = **30.5%, not 32.5% — a 2.0-point overstatement of the headline itself**, in the direction that flatters Traditional. It bites only on itemizers: at the archetype, state income tax alone is $14,025 against a $16,100 standard deduction, so it takes roughly $2,075 more of mortgage interest, property tax or charity to cross — likely for an owner, not automatic for a renter. **This is the larger of the two known biases and it points opposite to the deferred over-65 deductions (D-21), so they roughly cancel.** `TODO` with real per-state data |
| D-24 | **Departures do not perturb the deterministic headline. D1 is a reference marker, not a model change:** the app computes the effective rate today's brackets produce on the modeled withdrawal and draws it as a second line beside `t*`. Accordion-editable means the user overrides that computed number, not the bracket model | Under a flat future rate the after-tax Traditional trajectory is the Roth trajectory scaled by `(1−t_later)` — identical for any `r`, any income shape, any spending path. T2 therefore holds by construction. What breaks the scalar multiple is a mechanism that hits the accounts asymmetrically: the penalty, the cap, the rule change. D1 is not one of those. **The marker's withdrawal is defined non-circularly as the gross amount today's brackets require to fund D-39's net draw**, computed by `tax.gross_for_net()` in closed form rather than by a solver (D-21) — $127,804 gross for $108,397 net, an effective **15.2%**. **Both published figures are display roundings of one unrounded point**: $127,804 nets $108,397.04, and `gross_for_net(108_397)` returns $127,803.95. They must not be asserted against each other exactly. Federal only at the defaults, since D4 is off. *(Read federal-only and with no state anywhere, the same comparison is 24% against 15.2% — Traditional by 8.8 points. That is the figure this decision originally carried and it was never the default.)* |
| D-26 | **At year N, snapshot the Roth balance as a tax-free allowance in real dollars. It does not grow.** Retirement withdrawals draw it down first; everything past it is ordinary income at `t_later`. **The TERMINAL BALANCE AT 100 IS TREATED THE SAME WAY** — tax-free up to whatever allowance is left, ordinary income at `t_later` beyond it. Traditional is unchanged. **Policy is not a cube axis** — the toggle moves the headline line, never the dots | D-09's "prospective, not retroactive to existing balance" is the harsher of two grandfathering readings and it is the one written down: freezing the balance rather than the account. Because D-10 already labels this as Roth's bet rather than a neutral scenario, the sub-choices are modeled gently — allowance drawn first rather than pro-rated — so the effect shown is real rather than stacked. One scalar to carry, and it matches basis-recovery mechanics. **At the archetype the allowance is $607,475 against a $1,423,485 Roth balance at 65 — about six of thirty-five retirement years. N=20 means the balance AFTER the age-54 contribution:** year 1 is age 35, so year 20 is age 54. The balance after age 55 is $666,536, and reading it that way misses by $59,061. **THE TERMINAL RULE IS NOT A DETAIL — IT IS THE DIFFERENCE BETWEEN A GATE THAT PASSES AND ONE THAT IS UNREACHABLE.** Measured at Sprint 2A's assessment: leave the age-100 bequest untaxed and the after-tax difference NEVER crosses zero anywhere in `t_later` ∈ (0.01, 0.95) — it bottoms out around +$4.8M near 40% and climbs from there, so 58.4% does not exist and `breakeven()` returns a sentinel instead of the published headline. Tax the bequest beyond the remaining allowance and it crosses at **58.4064%**. This row was silent on it, and the silence was load-bearing |
| D-40 | **The policy threshold moves RIGHT, not left. At the archetype it is 58.4% against `t*` = 32.5%, and the verdict does not flip.** The flip is carried by an **early-career preset** — income shape (35, $60,000) · (38, $54,000) · (55, $200,000) · (65, $200,000), neither state taxing — where `t*` = 12.0%, the marker is 15.9%, and the policy threshold is 29.1%: **Roth under current rules, Traditional once the rule moves** | The deck drew the second threshold at 14% with Roth winning to its right. The algebra cannot do that. A policy that harms only Roth strictly raises the rate at which Roth becomes worthwhile. **BOTH TERMS ARE FUTURE VALUES AT 100, AND THE EARLIER WORDING DID NOT SAY SO:** `t*_policy = t_now·T₆₅·(1+r)³⁵ / ( t_now·T₆₅·(1+r)³⁵ + S·A₁ )`, where `S·A₁` is the compounded value of the withdrawals the allowance funded — **$5,211,109 at the archetype, not the raw $607,475 allowance.** Read with age-65 magnitudes instead, the same expression returns **53.0130%**, and a panelist checking the headline by hand lands there and concludes the engine is wrong. The inequality is untouched: it exceeds `t_now` whenever the allowance is smaller than the Roth balance, which it always is, so *moves right* survives both readings and only the number was ever at risk. So at the archetype the honest reading is the stronger one: *the scenario you were told makes Roth safe is the one that widens Traditional's lead.* The flip is real, but it belongs to the person the policy actually costs something — the low-bracket saver Roth was supposed to be for, which is precisely CONTEXT part E's recent-hire segment. **Two artifacts, not one: the default teaches that the bet is bigger than it looked, the preset teaches that it can reverse an answer** |

### D-21 — `t_now` is a deferral rate, not a bracket lookup

`t_now` is the rate the deferred dollars actually avoid:

```python
def deferral_rate(gross, contribution):
    return (tax_on(gross) - tax_on(gross - contribution)) / contribution
```

Exact, one extra call to a function the module already needs, and no lookup at a
boundary — so the last-dollar/next-dollar question stops existing rather than
getting answered.

**`marginal_rate()` is not `t_now`.** It survives for display and as
`combined_rate`'s federal half, and its docstring says so. The two are equal only
when the contribution stays inside one bracket. When it straddles, `marginal_rate`
overstates `t_now` — and `t*` *is* `t_now`, so the error lands on the headline.

| Straddle band (gross) | Edge | Bracket gap **= worst error, approached not attained** | Tested at | Error there |
|---|---|---|---|---|
| $66,500 – $83,125 | 12 → 22 | 10.0 | $66,600 | 9.92 pts |
| $121,800 – $146,300 | 22 → 24 | 2.0 | $121,900 | 1.99 pts |
| $217,875 – $242,375 | 24 → 32 | 8.0 | $217,900 | 7.99 pts |

The band endpoints here are **exact**; the tested grosses are the exact lower
edge rounded up to the nearest $100, because *at* the edge the error is zero and
there is nothing to measure. `tests/test_tax.py` uses the tested column, and
`test_at_a_band_edge_the_two_methods_agree_exactly` pins the zero at $121,800.
Splitting the two columns is what stops a reader taking 9.92 for the supremum:
measured at edge + $1 the errors are 9.999, 2.000 and 8.000.

**The mechanism is derivable, which means a panelist can check it without
rerunning anything.** Just above the edge the whole contribution comes out of the
band *below*, so `deferral_rate` converges on the lower band rate while
`marginal_rate` returns the upper one — and the worst error is therefore the
bracket gap itself. It is a supremum approached as gross → the edge from above,
not a value attained: *at* the edge the two agree exactly and the error is zero.
Two different mechanisms close the bands, which is why they are not the same
width. Band 1 is uncapped and closes when 80% of gross clears the edge, at
edge ÷ 0.8. Bands 2 and 3 close a flat $24,500 above their edge, where the cap
binds instead of the savings rate.

**Neither headline profile straddles.** The archetype is 24.00% and the preset is
12.00% under either method, so 32.5% and 12.0% stand. **Band 3 is the one that
matters**: $218,000 gross reads 32% federal and 40.5% combined under a lookup,
against a true 24.04% and 32.54% — the same magnitude as band 1, sitting in the
income range a Staff engineer types first. Raise the preset from $60,000 to
$70,000 and a lookup gives 22.0% against a true 14.5%.

**The savings rate does not live in `tax.py`.** `contribution(gross,
savings_rate)` applies `min(savings_rate × gross, DEFERRAL_CAP)` — the cap is a
tax number and stays here; D-28's 20% is behavioral and arrives as an argument
from `engine.py`. Both `deferral_rate` and `combined_rate` take the contribution
rather than deriving it, which also states the cap-binding out loud at every call
site instead of burying it in a `min()`.

**`gross_for_net()` lives here too.** `net(gross)` is piecewise linear, so the
inverse is closed form — invert the piece:

```
within a bracket:  net = g(1−rate) − base + rate·(SD + lo)
so:                g   = (net + base − rate·(SD + lo)) / (1 − rate)
```

Round-trips to 1.16e-10 across $0–$700k. Bisection agrees to 1e-11 and costs 300
iterations plus a tolerance argument nobody should have to defend.
`d(net)/d(gross) = 1 − marginal_rate ≥ 0.63`, so net is strictly increasing and
the inverse is unique everywhere — there is no branch where it is ambiguous.
**Guard below the standard deduction**, where there is no tax and `net == gross`:
without it the formula extrapolates the 10% bracket downward and
`gross_for_net(11_160)` returns $10,611, a gross below the net it is supposed to
fund. Reachable in the app, since a low income gives a low balance gives a low
draw, and the marker is computed on it.

It belongs here rather than in `engine.py` for three reasons. It is a fact about
the tax code, and Sprint 1 already rules that gross↔taxable conversion lives here
— gross↔net is the same species. It is where D-39's net and D-24's gross meet,
which is the exact conversion that was ambiguous at gate two, when 17% and 15.2%
were both defensible; a named, tested primitive makes that convention one
auditable object instead of a loop inside a bigger function. And it inherits
future changes: wire the over-65 deduction or MFJ and the inverse follows, where
in `engine.py` it would keep running and quietly mean something else.
**Consequence:** `marker_withdrawal()` in the `engine.py` skeleton becomes a pure
alias. Delete it and call `tax.gross_for_net` directly, keeping the D-24
docstring at the call site.

### Ladder and gates

| ID | Decision | Why |
|---|---|---|
| D-31 | **Income suggests a rung; the checkboxes set it.** Both render on the ladder — income as a faint marker, checkboxes as the solid one. **The actual rung is the checkbox marker** | Deriving the rung from income reintroduces the exact error DESIGN.md's insight paragraph names: income is a fourth instrument ladder. Two markers make the disagreement legible — when income says High and the checkboxes say Low, the graphic has drawn the boat and the giant house without the app asserting anything. That is the project's central claim rendered as a UI state, for the cost of one extra marker |
| D-33 | **Canonical ladder is the ten-stop flowchart ladder.** Bottom to top: $400 · $2,000 · high-interest debt · employer match · medium-interest (~8%) debt · 20% to 401k · max IRA · max 401k · no mortgage · other assets. **Low = 1–3, Mid = 4–6, High = 7–10.** All ten stops are clickable | The flowchart ladder maps to the shock mechanisms tighter than DESIGN.md's list did. Low is the no-cash-plus-balance-owed band, where a shock forces a sale, and it is exactly D-35's suppression gates. **Mid is the contributing band** — employer match through 20% — which is what makes D-16's "contributions pause" land on the right stops. High is money outside the emergency path. Note the flowchart's own ordering: the employer match comes *before* clearing medium-interest debt, because the match is free money. **This is the only D-33; the earlier duplicate carrying DESIGN.md's list and a Low = 1–2 band is deleted** |
| D-32 | **Ten checkboxes, one per stop. Stops 1–6 default checked, 7–10 unchecked** — the archetype lands at **Mid**, contiguously | The earlier six-gate version skipped stops 1, 7, 8 and 9, which broke D-37's contiguity rule at stop 1 and made the archetype unreachable at Mid by construction. One boolean per stop removes the special case. The flowchart's 15%-savings-rate guidance stays out of the model and appears only as a gate label: a rung-dependent contribution rate would couple L2 and L3, which is what keeping them on separate controls exists to prevent |
| D-37 | **The rung is the highest CONTIGUOUS stop cleared.** Non-contiguous checks render top-heavy and the app names the gap: *"You have assets above a gap — the flowchart would prioritize [lowest unchecked stop] first"* | Ten independent booleans make the graphic show ordering, not just position. Assets checked with nothing beneath them is misallocation — capital parked above a gap it should be filling — and the shape says so without a sentence. Contiguity keeps the rung honest: a lone top stop still reads Low, because the shock mechanism depends on what is beneath you. Copy points at the flowchart rather than issuing advice, because the top stops are mostly illiquid or penalized — telling a 401k-heavy user to sell is the forced-liquidation branch this model treats as the bad outcome |
| D-35 | **The verdict is suppressed when either of the first two gates is unchecked** ($400, $2,000). Copy names the binding gate. **`t*`, both thresholds, and the $X/$Y sentence all stay visible** — only the verdict line is replaced | Naming the gate is more useful than announcing a tier. Suppressing the verdict without hiding the numbers keeps the app from reading as a lockout. `$X` and `$Y` in particular must stay — at Low, `$Y` is large against a small `$X`, which is L3's demonstration, and hiding it would gut the lesson at the exact rung that proves it. High-interest debt (stop 3) gets its own copy: *paying it off beats either account, at any tax rate* — arithmetic, not advice, since no 401k election returns 20% guaranteed |

### Cube, sentence, encoding

| ID | Decision | Why |
|---|---|---|
| D-17 | **Dollar fields are evaluated at `t* + δ`, δ ∈ {2, 10} percentage points**, not at the break-even. The app uses 10; the README reports both. Null for non-crossing cells | At `t*` the two outcomes are equal by construction, so `$X` would be zero. δ is the assumed size of the miss, and it sets `$X` outright while leaving `$Y` nearly untouched — so it must be chosen *against* the L3 claim rather than for it. Ten points is about a bracket and a half, the generous case. The wash band was rejected as the anchor precisely because it minimizes `$X`. δ is named in the app's sentence, not hidden |
| D-23 | **The $X / $Y sentence reads objective 4 (max 10th percentile) at 1 shock.** Rung comes from the user's control; `$Y` compares that rung to the next one up, same objective and shock count. **The README reports the pair at all four objectives** | Zero shocks makes `$Y` identically zero — with no shock all three branches run the same code. Expected value is the wrong gauge for fragility: a halving and a doubling cancel in the mean, and ruin is absorbing, so the ensemble average is not what any one household lives. Objective 4 is where fragility is visible and it keeps both magnitudes in dollars. It is also the choice that flatters L3 most, so the full four-objective spread is published rather than the single quoted pair |
| D-36 | **`$Y` compares the user's rung to the next rung up, one step.** Undefined at High; the app says so rather than printing zero | One step is the smaller and more defensible claim, and with three rungs a two-step comparison only exists for Low |
| D-34 | **Dot encoding: row = shock count (0 at top, 3 at bottom). Color = objective family** — gray for expected-value (1, 2), neutral for median (3), orange for tail (4, 5). No jitter | The encoding renders DESIGN.md's stated prediction directly: gray dots barely move down the rows because expected value is blind to shocks, while orange dots fan out. The panel carries L3 and the expected-value-vs-tail divergence at the same time, and the second one is free. No jitter because rows already separate the dots; overlap within a row means the objectives agree, which is information rather than clutter |
| D-29 | **The grayed excess-savings row carries the solar-capex analog in its label, with no outbound link.** Suggested: *"excess savings — in the energy analog, this is the year you buy the panels."* The phrase links inward to the domain-analog table in the README | It is the one place in the app that addresses the panel rather than the user, so it should spend that attention on the analog rather than on an ask. A careers link is the wrong mapping — part A pairs solar capex with Roth tax paid up front, and a hiring page is neither capex nor a rate schedule |
| D-41 | **`seed = 20260815`, `n_paths = 2000`. The return series is `return_series.py`, a module-level list of annual real returns with a source comment. ~~It is STUBBED for Sprints 1–2 and is a hard gate on Sprint 3~~ — the stub period is OVER. The real series landed at gate two: 98 annual real returns, 1928–2025, Damodaran + CPI, Fisher-deflated on load, `STUB = False`, self-test passes. Sprint 3's gate is CLEARED (P4, R5)** | The cube must be byte-reproducible from the header, which means both constants are contract, not preference. 2000 paths is where the p10 estimate stops moving at three significant figures under common random numbers. Stubbing the series was legitimate only because Sprints 1 and 2 are deterministic — `make_paths("constant", ...)` never touches it — and the stub rule was that it be obviously fake (a short repeating list) so that nobody shipped it by accident. That rule is now spent: the file holds the real record, and what guards it instead is `_selftest()`, which pins the 1931 and 1954 anchors, the 26 negative years, the contiguity of 1928–2025, and the variance-drag identity. **`STUB` survives as the flag `make_paths("block", ...)` raises on, not as a description of the file's contents** |

---

## 4. Departure dispositions

The mechanisms behind the model. The accordion shows all eight; grayed rows show
what was scoped out and stay visible as evidence of completeness.

| # | Departure | Leans | Disposition |
|---|---|---|---|
| D1 | You withdraw *across* brackets, not at one rate | Traditional | **Real.** Reference marker per D-24. Accordion, editable |
| D2 | Contribution limit binds — Roth shelters more real money | Roth | **Real.** Hard-coded 2026 values, `TODO` source. Row copy carries D-42: at the archetype the Roth cap is unaffordable, which is the same lesson from the other side |
| D3 | Below the limit, the tax saving sits in a taxable side account | Roth | **Grayed.** `TODO`. See D-01 — the convention absorbs the trap without the model |
| D4 | You retire to a state that also taxes income | Roth | **Boolean, 8.5%.** Paired with the top-strip toggle per D-30. Stays editable when the accordion goes read-only. `TODO` real per-state data |
| D5 | Shock forces withdrawal — Traditional penalty vs. Roth basis | Roth | **Real, stochastic.** Becomes the correlated / uncorrelated toggle |
| D6 | Objective isn't expected value | either | **Real, stochastic.** Always on. Grid rows |
| D7 | The rule moves | either direction | **Real.** Top area, per D-09 and D-40 |
| D8 | Employer match pushes withdrawals into higher brackets | Roth | **Grayed.** `TODO` |

---

## 5. Contracts

### `cube.json`

Axes: `rung` (3) × `objective` (4) × `shocks` (4) = **48 cells.** Objective 2 is cut (D-06).

Per cell:

| Field | Type | Notes |
|---|---|---|
| `breakeven` | `float \| null` | Break-even future marginal rate, as a percentage |
| `status` | `"crosses" \| "always_roth" \| "always_trad"` | When not `"crosses"`, `breakeven` is `null`. Objectives 4 and 5 will not always cross inside a plausible range — **this must not raise**. There is deliberately **no status for a degenerate cell** where the difference is flat everywhere: `breakeven()` guards against that before bisecting rather than encoding it, because a difference that never varies is a modeling error, not a result. Objective 2 was the only known instance and it is cut (D-06) |
| `dollars` | `{"2": {...}, "10": {...}} \| null` | Keyed by δ. Each value is `{"roth": float, "trad": float}`. Null for non-crossing cells |
| `ruin` | `{"roth": float, "trad": float}` | Fraction of paths where the after-tax balance went negative before 100. Recorded, never clamped (D-38) |

Header block: `seed`, `n_paths`, `return_rate`, `profile`, `deltas`,
`generated_at`, `engine_version`.

**The dollar fields are what the headline sentence is made of:**

- `$X` = `abs(roth − trad)` at δ = 10, at the user's current rung
- `$Y` = change in the better choice's outcome between the user's rung and the
  next rung up, same objective and shock count. Undefined at High — the app says
  so rather than printing a zero

Sentence: *getting this right is worth about $X; moving from mid to high is worth
about $Y.* This is the only place on the page where fragility and the
Roth/Traditional decision appear in comparable units. **L3 lives here.**

### `engine.py`

```
breakeven(profile, objective, shocks, policy, paths) -> Result
outcome(profile, objective, shocks, policy, paths, rate, account) -> float
```

**`Profile`, published because Sprint 2A had to invent it and three later sprints
read it.** Fields: `income_points` (four `(age, gross)` pairs, D-19), `savings_rate`
(D-28), `current_age`, `state_while_working` and `state_in_retirement` (D-30),
`d2_roth_to_cap` (D-25), and `stops` — **ten booleans, one per D-33 ladder stop.**

- **`rung` IS DERIVED FROM `stops`, NOT STORED AND NOT A CALL ARGUMENT.**
  `rung_from_stops()` counts the highest *contiguous* stop cleared (D-37) and bands
  it 1–3 / 4–6 / 7–10 (D-33). Keeping it off the signature is what lets §5's two
  published signatures stand unchanged while the cube still has a rung axis: **Sprint 4
  sweeps that axis by replacing `stops`, not by passing a rung.** Canonical
  representatives are first-3 (Low), first-6 (Mid, which *is* the archetype under
  D-32), all-10 (High). One definition of "what rung am I", read by the engine, by
  D-35's verdict suppression and by D-37's gap message.
- **Zero stops cleared reads Low.** D-37 already rules that a lone top stop reads
  Low; the floor reads Low for the same reason. A shock with no buffer forces the
  sale, which is the Low mechanism.
- **`t_now` IS ONE SCALAR PER PROFILE**, `combined_rate` at the income of
  `current_age` — not recomputed per year off that year's income. Forced rather than
  chosen: D-22's accumulation identity is `roth₆₅/trad₆₅ == 1 − t_now` **exactly**,
  and a rate that moved with the income curve makes that ratio a weighted average
  that lands on no published number. The identity is the cheapest test in the
  project and it only exists under this reading.
- `n_years = 100 − current_age` (D-20). Accumulation is `65 − current_age` years,
  decumulation is a flat 35.

- `paths` is passed in, never drawn inside — that is what makes D-07 hold
- `outcome` is public; `spike_grid` calls it directly for the dollar fields
- **Guard before bisecting.** Evaluate the difference at both bracket endpoints and assert it is non-constant. Two evaluations, one assertion. A difference that is identically zero otherwise returns whichever endpoint bisection started nearest, **silently** — worse than the no-crossing case T4 covers, which at least has a sentinel. This guard would have caught objective 2 in Sprint 2B instead of Sprint 4
- Solve by bisection over the future marginal rate
- **No clamping** (D-38)
- Returns the `Result` shape above

---

## 6. Tests

Eight, and they are **engine** tests. Each asserts a claim made elsewhere in the
docs, which is the point. Sprint 1's assertions are not among them — they live in
`tests/test_tax.py` and are listed in that sprint's done-when.

| # | Test | Claim it defends |
|---|---|---|
| T1 | `t_now == t_later` → the two outcomes are equal under D-01 | The identity is real |
| T2 | `t*` unchanged across `r ∈ {4, 7, 9, 12}%`, **and** the after-tax Traditional path equals the Roth path scaled by `(1−t_later)` at every year | **L1.** The scalar-multiple assertion is why it holds for any `r`, not only the four sampled |
| T3 | At the **$185,000 test profile** (D-42) with D2 ON, Roth shelters strictly more real dollars and the cell returns `always_roth` | D2, the G4 trap, and D-25's scoping of D-01 |
| T4 | A no-crossing cell returns its sentinel and does not raise | R3. T3's cell is one, so this is exercised rather than hypothetical |
| T5 | In the base case, the today's-law effective marker is strictly below `t*` | The headline sentence — you defer at marginal and withdraw across the whole structure from zero |
| T6 | Low rung: a shock realizes a $40,000 sale; Traditional takes the penalty while Roth basis comes out free | D-16 low branch, D5, D-39 |
| T7 | Mid rung: a shock skips the contribution year and the balance is never sold | D-16 mid branch — the shares not bought |
| T8 | High rung: a shock leaves the portfolio untouched | D-16 high branch, the control case |

T6–T8 assert the *mechanism*, not the magnitude. Three rungs are three code
branches, so three tests — a severity dial would have needed one.

---

## 7. App layout

![App layout](design/ui-design.PNG)
*Mockup, reconciled at gate two. The ladder's ten stops and its Low 1–3 / Mid 4–6
/ High 7–10 bands are correct as drawn. Superseded: the model box is now
disabled, and notation `r` → `t*` (D-24).*

Top strip, left to right: current income · income shape · **state income tax
(while working)** · return-rate buttons · nevermind toggle + year · early-career
preset button.

Caption under the state toggle: *default assumes you earn in a taxing state and
retire in one that doesn't. Both are toggles.*
Caption under the return buttons: *this input drives the picture, not the answer.*

| Region | Contents |
|---|---|
| Left rail | Resilience ladder, ten stops, three bands marked, plus the three-position rung control |
| Headline | **Two break-even rates side by side: rules hold / treatment moves at year N.** Verdict beneath, measured against the today's-law effective marker. **At the Low rung the verdict is replaced by** *this election is not your binding constraint yet* |
| Under headline | The $X / $Y sentence, naming δ and its objective |
| Under that | Balance graph — two curves diverging during saving, landing together after tax |
| Personalize | Accordion, all eight departures, grayed where scoped out |
| Model | Three dot-plot panels — low, mid, high. The user's rung highlighted, the other two dimmed but **always visible**: the collapse is the lesson, and a trend needs three points |

Beside the nevermind toggle:

**You can still contribute — it just stops being worth it.**

*Direct taxation of Roth withdrawals is the least likely form this takes. What
has repeatedly happened instead is that tax-free money stops being invisible —
counted toward a Medicare premium, the taxable share of Social Security, or an
ACA subsidy. The money stays untaxed and costs you anyway, one layer over.*

Poland 2013 · Ireland 2011 · US SECURE Act 2019.

**Notation:** `t*` is the break-even future **marginal** rate. The today's-law
marker is an **effective** rate. They share an axis and the axis says so, because
the gap between them is the lesson.

**Under the axis, in prose, not a legend** — this is the hardest idea on the page
and the one an informed non-expert most needs:

> **You defer at 32.5 cents on the dollar. You withdraw at an average of 15.2.**
> Those are different rates because contributions come off the top of your
> income and withdrawals fill the brackets from zero.

Both figures are computed, so the sentence re-renders with the controls. Without
it the natural misreading is *my rate is 15.2%, the break-even is 32.5%, so I
need my taxes to double* — which is wrong, and it is the reading a careful
non-expert will arrive at on their own. `r` is the market return; do not reuse
it for either rate.

Top-right: a DISABLED control labeled **Model (block bootstrap)**. Tooltip lists
all nine return models from CONTEXT part D and marks the two implemented — #2
fixed real rate (app headline), #6 block bootstrap (cube). Disabled rather than
absent: the option space was mapped, two were built, and the control says so
without implying the other seven exist.

---

## 8. Budget

A fixed implementation budget. Research, design, and README are outside it and
reported separately. **The single budget table and the cut ladder live in
`remaining-sprints.md`** — the earlier per-item table here disagreed with it on
both the total and the order of cuts. Actuals go in the README.

---

## 9. Open risks

| # | Risk | Mitigation |
|---|---|---|
| R1 | ~~2026 bracket edges, deduction and deferral limit are unverified~~ **CLOSED 2026-08-15.** Verified against IRS IR-2025-103 / Rev. Proc. 2025-32, the primary source, and corroborated independently by Tax Foundation | Source comment in `tax.py` carries both URLs and the verification date |
| R7 | **Two known biases, both deferred, pointing opposite ways.** SALT deductibility ignored (overstates Traditional by up to 2.0 points on `t*`); over-65 deductions omitted (understates Traditional by 1.7 points on the marker) | Both are stated with their size and direction in the README, and neither changes a verdict. Roughly cancelling is not the defense — knowing which way each one bends the answer is |
| R8 | **The block bootstrap's stated reason failed measurement.** It does not fatten the tail relative to an IID draw; it thins it slightly. A reviewer who knows time-series work may reach for this | Owned, not hidden. D-05 carries the measurement, the README has a section on it, and the pick survives on the recovery-forgone channel. `n ≈ 19.6` independent blocks is the same critique the README already makes of Bengen — say it first |
| R2 | Deploy. Repo is private, ruling out Streamlit Cloud; no local Docker | Railway from GitHub. Flag at 15 minutes. **P3a is now a scheduled hard gate on Sprint 6 rather than a floating pre-flight** — it needs no project code, so it runs in parallel with Sprints 2A–5. Railpack's framework detection does not cover Streamlit, so expect to set the start command explicitly |
| R3 | Objectives 4 and 5 may not cross in range | T4 |
| R4 | Dots are archetype-based while the line is personalized | D-15 label. Owned in the README, not hidden |
| R5 | ~~Return series must exist before Sprint 3~~ **CLOSED at gate two.** `return_series.py` holds 98 real annual returns, 1928–2025, `STUB = False`, and `python return_series.py` passes its self-test | D-41. Confirmed by P4 in `remaining-sprints.md` and by the Sprint 3 gate line, both of which read *cleared*. This row stayed open one pass longer than the fact did |
| R6 | **The archetype's draw is 54% of final income**, below any published replacement band | D-39. Reported as an outcome with the reason stated: a $24,500 cap cannot fund 80% of a $200,000 income, and the gap is Social Security plus the grayed taxable account. If a panelist reads it as an error, that sentence is the answer |
