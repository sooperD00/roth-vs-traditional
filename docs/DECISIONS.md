# DECISIONS

Status: design phase closed. This file is the build contract.

## 0. Precedence

Where this file and `CONTEXT.md` disagree, **this file wins.** `CONTEXT.md` is
the tradeoff reference — it records the option space that was considered, and its
option tables now carry two marker sets: `← initial pick` for the choice made
during synthesis, `← design-phase pick` for what survived design. Where a row
carries both, the choice held.

`README.md` is a working surface, not a source. It carries notes taken while
thinking and is reconciled against this file at each design gate — so between
gates it may disagree, and this file wins by default. Disagreements found in the
README are treated as unreconciled notes rather than conflicts, **except** where
the README states a number or a claim the panel will read, in which case the
disagreement is a defect and gets fixed in the same pass. Both files are stale
until a gate closes; this one is stale by omission, the README by draft.

Three conflicts remain that markers can't express, plus two in `DESIGN.md`:

| Says | Superseded by |
|---|---|
| CONTEXT part B — PoC is "deliberately throwaway" | D-11. The PoC *is* the engine the app imports |
| CONTEXT part B — "Cost in the budget" includes research and design | Section 8. Both are declared outside the implementation budget |
| CONTEXT §G3 — model the employer match | D8 disposition. Grayed, `TODO` |
| DESIGN.md — grid columns are a "shock count" | D-08. Columns are shock count; *timing* is correlated with drawdown |
| DESIGN.md — rung slider, 8–10 stops, feeding shock severity | D-16. Three rungs, and the rung selects a *mechanism*, not a severity |
| DESIGN.md — tail visual "Pick 3, with 2 as the visual under it" | Cut. The exchange-rate sentence survives as the $X/$Y sentence; the two-bar asymmetry chart is a Scope & Branches row |
| DESIGN.md — "Recommended output stack ≈ 75 min" | Section 8. Predates the cube, the rung mechanisms, and the ladder graphic |

Design deck — working surface, reconciled at gates. DECISIONS.md wins.

---

## 1. What the user learns

Four lessons. Every control on the page exists to deliver one of them. If a
feature can't be traced to a row here, cut it.

| # | Lesson | Delivered by | Mechanism |
|---|---|---|---|
| L1 | The return rate never affects Roth vs. Traditional | 7 / 10 / 12% buttons | The knob that doesn't work. Balance graph swings, headline number does not |
| L2 | Tax rates do affect it | Income shape, state toggle, "nevermind" toggle | Headline number moves |
| L3 | Fragility matters more than this decision, for most users | Rung control → three-panel dot plot; the $X/$Y sentence | Dots collapse as the rung rises. Dollar sentence puts both effects in one unit |
| L4 | You are not in control of the tax law | "Nevermind" toggle + historical line | Roth's bet is named as a bet |

**L1 and L2 are taught by contrast.** The return-rate buttons sit physically
beside the tax controls. One moves the answer, one can't.

---

## 2. Definition of done

Shipped when all seven exist:

1. `tax.py` — 2026 brackets and deferral limit, one module, source comment
2. `engine.py` — pure functions, no Streamlit import
3. `spike_grid.py` — CLI; writes `cube.json` and prints the markdown grid
4. `test_engine.py` — the four tests in §6
5. `app.py` — Streamlit, layout per §7
6. Deployed, reachable by URL
7. `## Scope & Branches` in README — Cut / Why / What-it-would-take

Not done, and labeled as such in the UI: historical sequence replay, spending
model, RMDs, Social Security taxation, real per-state tax data.

---

## 3. Decisions

### Conventions

| ID | Decision | Why |
|---|---|---|
| D-01 | **Contribution convention: same pre-tax dollars.** $X to Traditional vs. $X·(1−t_now) to Roth | The identity is exact only under this convention, so L1 depends on it. Same-nominal-dollars silently favors Roth — that is the G4 trap. Name the convention in one sentence in the app |
| D-02 | **Wash band: ±2 percentage points.** Inside it the headline reads "It's a wash"; outside it names the winner | The headline is the sentence the app exists to print |
| D-03 | **Income shape is independent of the resilience rung.** The user sets both; the rung is a three-way pick, not a slider position — see D-16 | Deriving a rung from an income curve needs a savings model and a spending model. Neither is in budget. Also keeps L2 and L3 on separate controls |

### Model

| ID | Decision | Why |
|---|---|---|
| D-04 | **Return rate is a three-way choice: 7 / 10 / 12%, real.** Default 7% | These are the exact numbers people argue about. Clicking all three while the answer holds still *is* L1 |
| D-05 | **Return path model: block bootstrap over a historical return series. Block length 5 years.** Shocks placed into each path's worst years by drawdown `argsort` | Bad years must arrive in *runs* or the forced-liquidation argument is mechanical only — you sell at the bottom and next year is fine. IID and lognormal both scatter them. Block length is stated, and its sensitivity at 3 and 10 goes in Scope & Branches: a measured fudge factor beats an unexamined distribution. `argsort` placement means no correlation coefficient to calibrate or defend |
| D-06 | **`optimal` is a parameter, not a choice.** All five objectives ship as grid rows | Same inputs, swap the objective, watch the recommendation flip. This is the demo |
| D-07 | **Common random numbers.** Draw the `(n_paths, n_years)` array once; reuse across every cell, both choices, every bisection step | The quantity of interest is a small difference between two large numbers. Pairing removes sampling noise from that difference, makes the cube reproducible from a seed, and makes 60 cells cheap |
| D-08 | **Shock columns are a count (0–3); shock *timing* is correlated with drawdown.** Correlated is the default; an uncorrelated toggle exists for contrast | Forced liquidation lands when prices are worst. The toggle makes the fat tail appear and disappear in one click |
| D-09 | **Policy scenario is "nevermind," prospective.** After year N (default 20), withdrawals are ordinary income regardless of account type — applied to growth after year N, not retroactively to existing balance | Simpler than a haircut: no rate parameter. Prospective is what actually tends to happen when rules move |
| D-10 | **Both thresholds display, always. The headline holds two numbers: `t*` under current rules and `t*` with the "nevermind" policy applied.** Labeled: *Roth bets the treatment holds. Traditional bets the rates do. Neither is the neutral choice — pick which rule you'd rather be exposed to* | The toggle as originally specified showed only Roth's exposure, while the offsetting case — brackets rise, Roth wins — sat in a README branch nobody at a demo will read. That asymmetry is what makes a one-sided toggle read as a strawman. The correction costs nothing to model, because the bracket-rise case is *already on the axis*: a higher future rate is a position to the right of `t*`, and the user is being asked to locate themselves there regardless. Showing both thresholds applies the CONTEXT part C option-4 stance twice instead of once. Cost: one extra `breakeven()` call. Layout unchanged except the headline carries two numbers |

### Architecture

| ID | Decision | Why |
|---|---|---|
| D-11 | **One engine module, two entry points.** `spike_grid.py` and `app.py` both import `engine.py`. No duplicated math | The PoC is not throwaway. Reviewable-standalone-script value survives — it is a script that imports a module and prints a table |
| D-12 | **The app contains no stochastic code.** It reads `cube.json` | Deploys smaller, cannot be slow in front of a panel, no seed in production |
| D-13 | **Deterministic path is the same function at `n_paths=1, sigma=0`** | The headline and the cube can never disagree about the underlying math |
| D-14 | **The cube is computed at the reference archetype, not at the user's profile** | It is precomputed. Consequence in D-15 |
| D-15 | **User inputs move the vertical line, not the dots.** The dot plot is labeled "modeled for the reference profile" | The interaction still lands — set the state toggle and the line slides through the cloud — but the app must not imply the dots are personalized |

### D-16 — Resilience rungs

**Three rungs, not eight.** `DESIGN.md` describes three *mechanisms*; eight would
have meant inventing six intermediate severities with nothing behind them, and a
reviewer asking what separates rung 5 from rung 6 would get a shrug.

**The rung selects which branch of the shock code runs.** It is not a multiplier.

| Rung | What a shock does | Implementation |
|---|---|---|
| **Low** — no buffer | Forces liquidation | Sell at the shocked year's price to cover the gap. Traditional takes the early-withdrawal penalty; Roth basis comes out free |
| **Mid** — some buffer | Pauses contributions | No sale. Contributions stop for the shock year, resume after. The cost is the shares not bought |
| **High** — deep buffer | Absorbed by cash | Portfolio untouched. The control case |

Mid is the one that carries the argument and the one a reviewer will look at
first. Pausing contributions during a drawdown means you stop buying at exactly
the moment prices are lowest — a real cost that appears nowhere on a statement.
Low sells at the bottom; mid fails to buy at the bottom; high does neither.

Rungs are **named in the UI, never numbered.** The ladder figure in the left rail
keeps all ten stops and marks which three are modeled: the figure is the
argument, the three are the model.

### GAPS SURFACED IN DESIGN REVIEW, CLOSED HERE

| D-17 | **Dollar fields are evaluated at `t* + δ`, δ = 10 percentage points**, not at the break-even. Emit `roth_dollars` / `trad_dollars` at δ ∈ {2, 10}; the app uses 10 and the README reports both. Null for non-crossing cells | At `t*` the two outcomes are equal by construction, so `$X` would be zero. δ is the assumed size of the miss, and it sets `$X` outright while leaving `$Y` nearly untouched — so it must be chosen *against* the L3 claim rather than for it. Ten points is about a bracket and a half, the generous case. The wash band was rejected as the anchor precisely because it minimizes `$X`. Sensitivity at 2 and 10 goes in Scope & Branches; δ is named in the app's sentence, not hidden |

| D-23 | **The $X / $Y sentence reads objective 4 (max 10th percentile) at 1 shock.** Rung comes from the user's control; $Y compares that rung to the next one up, same objective and shock count. **The README reports the pair at all five objectives.** The sentence names its objective in-line | Zero shocks makes $Y identically zero — the rung selects a shock branch, and with no shock all three branches run the same code. Expected value is the wrong gauge for fragility: a halving and a doubling cancel in the mean, and ruin is absorbing, so the ensemble average is not what any one household lives. Objective 4 is where fragility is visible and it keeps both magnitudes in dollars, which is the only reason the sentence works at all. It is also the choice that flatters L3 most — it shrinks $X and grows $Y — so the full five-objective spread is published rather than the single quoted pair. Objectives 2 and 5 need the spending model and cannot serve here |

| D-27 | **Everything is in real 2026 dollars. Brackets are treated as inflation-indexed**, so the 2026 table applies at every year of the run | Returns are declared real (D-04) while the bracket table is nominal 2026. Running both unstated models a world where brackets never index — bracket creep would push the future rate up on its own and `t*` would be an artifact of the mismatch. Real throughout is internally consistent and matches the law. **R5's return series must be real or deflated on load.** The 7/10/12 buttons are labeled as the figures people quote, since 12% real is not a claim |

| D-19 | **Reference archetype:** age 35, retires 65, dies 100, filing single, no-income-tax state (D4 default), income $165,000 real, savings rate 20%, replacement rate 80%. Income shape has one start, one trough, one peak, one end | Filing single because the UI models one income curve and one age — an MFJ archetype is a household the controls cannot represent. $165k is what a Staff SWE recognizes; the panel will reset income to their own the way part E predicts they will reset the state toggle. Consequences: `t_now` = 24% with no bracket straddle, and savings capacity ($33,000) just clears the cost of maxing a Roth ($32,237), so D2 and T3 are live at the archetype rather than hypothetical |

| D-20 | **Horizon runs to age 100; `n_years = 100 − current_age`.** Two phases: accumulate to 65, decumulate 65→100. All objectives evaluate at 100 | Planning past median longevity is the standard convention, because outliving the money is the failure that matters. Retirement at 65 was already implicit in the income shape's right endpoint. Splitting the phases is what puts `t*` where it belongs — in the withdrawal years. "Terminal wealth" therefore means bequest at 100, not balance at 65, so all five objectives share one horizon. Guard needed for `current_age >= 65` |

| D-21 | **`tax.py` implements SINGLE only: 2026 bracket edges, seven rates, standard deduction $16,100.** MFJ and HoH are `TODO` stubs with a source comment | Source: Tax Foundation / IRS 2026 release. Deduction applies to withdrawals, so gross minus deduction gives taxable and the bracket table is read in taxable terms. HoH is stubbed rather than half-entered because the published HoH column has overlapping edges at the 24/32 boundary. Additional standard deduction for filers over 65 is a `TODO` — it lowers the effective retirement rate and therefore moves `t*` slightly toward Traditional. **R1 closes when the single column and the deduction are verified by hand against irs.gov, not against a secondary source** |

| D-28 | **Spending stub: save 20% of income during accumulation, spend 80% of final working income in retirement.** Modeled contribution is `min(0.20 × income, deferral cap)`; the remainder is declared out of model and displayed grayed | Source: BLS household budget data. One number serves both phases — savings rate on the way up, replacement rate on the way down — which is why one stub unlocks objectives 2 and 5. 80% sits at the conservative end of the 70–80% planning band. The grayed excess ($8,500 at the archetype) shares a row with D3: both are money outside the 401k that the model does not follow. **This voids D-03's stated reason** — a savings model and a spending model now exist, so the income-shape-to-rung question needs a new justification or a flip |

| D-04a | **Return buttons are 7 / 9 / 12%, all real.** Each is labeled with what it corresponds to nominally; 12% is labeled implausible on purpose. Default 7% | D-27 puts the model in real dollars, so nominal buttons would misread. But 7 and 10 collapse under conversion — 10% nominal *is* ~7% real — so a straight translation loses a button. Keeping 12% real preserves D-04's reason (these are the figures people argue about) and improves on it: the implausible button is the one a skeptic reaches for first, and watching `t*` hold still there is L1 at full force. Caption under the row: *this input drives the picture, not the answer* |

| D-29 | **The grayed excess-savings row carries the solar-capex analog in its label, with no outbound link.** Suggested: *"excess savings — in the energy analog, this is the year you buy the panels."* The phrase links to the domain-analog table in the README | It is the one place in the app that addresses the panel rather than the user, so it should spend that attention on the analog rather than on an ask. A careers link is the wrong mapping — part A pairs solar capex with Roth tax paid up front, and a hiring page is neither capex nor a rate schedule. Linking inward routes a curious reader to the nine-pair table |

| D-24 | **Departures do not perturb the deterministic headline. D1 is reclassified from a model change to a reference marker:** the app computes the effective rate today's brackets produce on the modeled withdrawal and draws it as a second line beside `t*`. Accordion-editable means the user overrides that computed number, not the bracket model | Under a flat future rate the after-tax Traditional trajectory is the Roth trajectory scaled by `(1−t_later)` — identical for any `r`, any income shape, any spending path. T2 therefore holds by construction and needs no default to switch off. What breaks the scalar multiple is a mechanism that hits the accounts asymmetrically: the early-withdrawal penalty, the cap (D2), the rule change (D7). D1 is not one of those. As a marker it costs one function already needed, keeps `t*` a single interpretable scalar, and supplies D-18's operand at no extra input — preserving the CONTEXT part C option-4 stance. At the archetype it yields `t*` = 24% against ~17% effective under today's law: Traditional by ~7 points, because you defer at marginal and withdraw across the whole structure from zero |

| D-25 | **D-01 applies at `min(capacity, cap)` in PRE-TAX terms.** Base case: $24,500 to Traditional, $18,620 to Roth — the Roth deliberately under-fills. **D2 ON** fills the Roth to $24,500 after-tax ($32,237 pre-tax) and is the only place the cap effect enters. T3 tests D2 ON | The cap is denominated in nominal contribution dollars, which are pre-tax for Traditional and after-tax for Roth, so at the boundary the two choice sets differ and the convention has nothing to equalize. Reading D-01 as a comparison device rather than a behavior model resolves this: the base case isolates the *timing* effect, D2 adds the *capacity* effect back as a named step. Under-filling the Roth is artificial and is labeled so in the app. **Correction to D-19:** the archetype's $33,000 capacity is ABOVE the $24,500 cap, so this is the base case, not an edge case. Capacity covers the $32,237 cost of maxing the Roth with $763 spare, so T3 exercises something the reference user experiences |

| D-30 | **State tax is two booleans sharing one rate: 8.5%, DC's marginal rate at the archetype income.** Top strip — *"State income tax — while working,"* default **yes**. Accordion D4 — *"You retire to a state that also taxes income,"* default **no**. Rate is added to the federal marginal rate; real per-state data stays `TODO` | Split because the earning state and the retirement state are different assumptions and the gap between them is the whole effect. Defaults are earn-taxed / retire-untaxed, which is the widest honest case and the demo: `t_now` = 32.5% against ~17% federal effective, Traditional by ~15.5 points. Turning the accordion half on narrows it back toward baseline — that is the correction most users should apply, and it must stay reachable, so **D4's row is exempt from the accordion read-only cut**. 8.5% rather than a round 10 because DC's top rate applies above ~$1M and the panel files DC returns: a rate rounded up flatters the Traditional case by 1.5 points in a number they can check. Simplification: state tax is treated as additive to the federal marginal rate, ignoring SALT deductibility — `TODO`, and it slightly overstates the combined rate |

| D-22 | **Deterministic mode is `paths` of shape `(1, n_years)` filled with the constant real return.** Replaces D-13's `n_paths=1, sigma=0`. `make_paths(kind, ...)` builds either a constant array or a bootstrap array; the engine cannot tell which it received | The block bootstrap has no `sigma` — that parameter belonged to the parametric model D-05 rejected. Expressing the deterministic path as a shape rather than a setting keeps D-13's claim intact and makes it structural: one function, one code path, nothing to drift. Two consequences: at `n_paths=1` objectives 1, 3 and 4 collapse to the same value, so the headline is objective-independent by construction; and objective 5 degenerates to a step function that will not bisect — the deterministic path must reject it. **Validation gate:** the entire 0-shock slab of the cube (3 rungs × objectives 1–4) must equal `t_now` exactly, since the scalar multiple holds per path and therefore under any objective |

| D-26 | **At year N, snapshot the Roth balance as a tax-free allowance in real dollars. It does not grow. Retirement withdrawals draw it down first; everything past it is ordinary income at `t_later`.** Traditional is unchanged. Policy is not a cube axis — the toggle moves the headline line, never the dots | D-09's "growth after year N, not retroactively to existing balance" is the harsher of two grandfathering readings, and it is the one written down: freezing the balance rather than the account. Because D-10 already commits to labeling this as Roth's bet rather than a neutral scenario, the sub-choices are modeled gently — allowance drawn first rather than pro-rated — so the effect shown is real rather than stacked. One scalar to carry, and it matches basis-recovery mechanics. Traditional needs no branch at all: its withdrawals were already ordinary income, and that absence in the code is the asymmetry. At the archetype, N=20 lands at age 55, grandfathering ≈ $763k against a $1.76M balance at 65 — about six of thirty-five retirement years |

| D-31 | **Income suggests a rung; six checkboxes set it. Both render on the ladder — income as a faint marker, checkboxes as the solid one, and the actual rung is the checkbox marker** | Deriving the rung from income would reintroduce the exact error DESIGN.md's insight paragraph names: income is a fourth instrument ladder, and same income / different fragility is the whole point. Two markers make the disagreement legible — when income says High and the checkboxes say Low, the graphic has drawn the boat and the giant house without the app asserting anything. That is the project's central claim rendered as a UI state rather than a paragraph, for the cost of one extra marker. **This supersedes D-03's stated reason**, which was voided by D-28 when the savings and spending stubs landed; the conclusion (rung is its own control) stands on the stronger reason |

| D-32 | **Six gates, from the r/personalfinance flowchart. First four default checked, last two unchecked.** Unchecking either of the first two drops to Low; all four of the first set gives Mid; both of the last two gives High | The flowchart is a behavioral checklist, not a macro claim — it stays out of contested territory in a hiring artifact. It covers only the ladder's lower half, so all-cleared lands at Mid rather than High, which is correct: the archetype at $165k should start at Mid. That is the branch D-16 says carries the argument, `$Y` is defined there, and the dots have not yet collapsed. Gates: $2,000 saved · high-interest debt cleared · employer match captured · medium-interest (~8%) debt cleared · mortgage paid off · assets outside the primary residence |

| D-33 | **Canonical ladder is the 10-stop list from DESIGN.md's "Resilience ladder as a parameter" section.** Low = stops 1–2, Mid = 3–6, High = 7–10 | DESIGN.md gives the ladder twice — 9 stops in one section, 10 in the other — and README and the mockup each give a third variant. The 10-stop version is the superset (it adds "pay for those things" after sinking funds), so it is the one D-16's "all ten stops" refers to. The spans line up with the mechanisms: the first two rungs are cash positions, so a shock forces a sale; the middle four are debt and sinking-fund positions, so a shock pauses contributions; the top four hold assets outside the emergency path, so a shock is absorbed |

| D-34 | **Dot encoding: row = shock count (0 at top, 3 at bottom). Color = objective family — gray for expected-value (1, 2), neutral for median (3), orange for tail (4, 5). No jitter** | The encoding renders DESIGN.md's stated prediction directly: gray dots barely move down the rows because expected value is blind to shocks — a halving and a doubling cancel in the mean — while orange dots fan out. So the panel carries L3 (collapse across rungs) and the expected-value-vs-tail divergence at the same time, and the second one is free. No jitter because rows already separate the dots; overlap within a row means the objectives agree, which is information rather than clutter |

| D-18 | **The verdict compares `t*` against the today's-law effective rate marker from D-24.** Inside D-02's ±2-point band, "it's a wash"; outside, name the winner | D-02 defined a band with nothing to measure it against, and CONTEXT part C option 4 deliberately refuses to ask the user for a future-rate belief. The marker resolves this at no input cost: it is a computed fact — what today's brackets produce on the modeled withdrawal — not a prediction, so the threshold framing survives. At the archetype it yields 32.5% against ~17%, which is Traditional by ~15.5 points and well outside the band |

| D-35 | **The verdict is suppressed when either of the first two gates is unchecked** ($2,000 saved, high-interest debt cleared) — the same condition as the Low rung under D-32, stated as the gate rather than the tier. Copy names the binding gate: *"You're carrying high-interest debt. Paying it off beats either account, at any tax rate."* **`t*`, both thresholds, and the $X/$Y sentence all stay visible** — only the verdict line is replaced | Naming the gate is more useful than announcing a tier, and the high-interest case is arithmetic rather than advice: no 401k election returns 20%+ guaranteed. Suppressing the verdict without hiding the numbers keeps the app from reading as a lockout. `$X`/`$Y` in particular must stay — at Low, `$Y` is large against a small `$X`, which is L3's demonstration, and hiding it would gut the lesson at the exact rung that proves it. The flowchart's 15%-savings-rate guidance stays out of the model and appears only as gate labels: a rung-dependent contribution rate would couple L2 and L3, which is what keeping them on separate controls exists to prevent |

| D-36 | **`$Y` compares the user's rung to the next rung up, one step.** Undefined at High; the app says so rather than printing zero | README's "moving up two rungs" was stale. One step is the smaller and more defensible claim, and with three rungs a two-step comparison only exists for Low |

| D-33 | **Canonical ladder is the ten-stop flowchart ladder, replacing DESIGN.md's list.** Bottom to top: $400 · $2,000 · high-interest debt · employer match · medium-interest (~8%) debt · 20% to 401k · max IRA · max 401k · no mortgage · other assets. **Low = 1–3, Mid = 4–6, High = 7–10.** All ten stops are clickable | The flowchart ladder maps to the shock mechanisms tighter than DESIGN.md's list did. Low is the no-cash-plus-balance-owed band, where a shock forces a sale, and it is exactly D-35's suppression gates. **Mid is the contributing band** — employer match through 20% — which is what makes D-16's "contributions pause" mechanism land on the right stops. High is money outside the emergency path. Note the flowchart's own ordering: employer match comes *before* clearing medium-interest debt, because the match is free money |

| D-37 | **The rung is the highest CONTIGUOUS stop cleared. Non-contiguous checks render as a top-heavy shape, and the app names the gap:** *"You have assets above a gap — the flowchart would prioritize [lowest unchecked stop] first"* | Ten independent booleans make the graphic show ordering, not just position. Assets checked with nothing beneath them is misallocation — capital parked above a gap it should be filling — and the shape says so without a sentence. Contiguity keeps the rung honest: a lone top stop still reads Low, which is correct, because the shock mechanism depends on what is beneath you. Copy points at the flowchart rather than issuing advice, because the top stops here are mostly illiquid or penalized: telling a 401k-heavy user to sell is the forced-liquidation branch this model treats as the bad outcome. Cost is a contiguity check and one conditional line |

---

## 4. Departure dispositions

The mechanisms behind the model. Accordion shows all eight; grayed rows show
what was scoped out and stay visible as evidence of completeness.

| # | Departure | Leans | Disposition |
|---|---|---|---|
| D1 | You withdraw *across* brackets, not at one rate | Traditional | **Real.** Accordion, editable |
| D2 | Contribution limit binds — Roth shelters more real money | Roth | **Real.** Hard-coded 2026 values, `TODO` source |
| D3 | Below the limit, the tax saving sits in a taxable side account | Roth | **Grayed.** `TODO`. See D-01 — the convention absorbs the trap without the model |
| D4 | You retire to a state that also taxes income | Roth | **Boolean, 8.5%.** Paired with the top-strip "while working" toggle, per D-30. Stays editable when the accordion goes read-only. `TODO` real per-state data |
| D5 | Shock forces withdrawal — Traditional penalty vs. Roth basis | Roth | **Real, stochastic.** Becomes the correlated / uncorrelated toggle |
| D6 | Objective isn't expected value | either | **Real, stochastic.** Always on. Grid rows |
| D7 | The rule moves | either direction | **Real.** Top area, per D-09 |
| D8 | Employer match pushes withdrawals into higher brackets | Roth | **Grayed.** `TODO` |

---

## 5. Contracts

### `cube.json`

Axes: `rung` (3, per D-16) × `objective` (5) × `shocks` (4) = 60 cells.

Per cell, four fields:

| Field | Type | Notes |
|---|---|---|
| `breakeven` | `float \| null` | Break-even future marginal rate, as a percentage |
| `status` | `"crosses" \| "always_roth" \| "always_trad"` | When not `"crosses"`, `breakeven` is `null`. Objectives 4 and 5 will not always cross inside a plausible range — this must not raise |
| `roth_dollars` | `float` | Outcome under this cell's objective, Roth |
| `trad_dollars` | `float` | Outcome under this cell's objective, Traditional |

Header block alongside the cells: `seed`, `n_paths`, `return_rate`, `profile`,
`generated_at`, `engine_version`.

**The dollar fields are what the headline sentence is made of:**

- `$X` = `abs(roth_dollars − trad_dollars)` at the user's current rung
- `$Y` = change in the better choice's outcome between the user's rung and the
  next rung up, same objective and shock count. Undefined at High — the app says
  so rather than printing a zero

Sentence: *getting this right is worth about $X; moving from mid to high is worth
about $Y.* This is the only place on the page where fragility and the
Roth/Traditional decision appear in comparable units. **L3 lives here.** The
dollar fields must be in the contract before the PoC is written — retrofitting
them means re-running everything.

### `engine.py`

```
breakeven(profile, objective, shocks, policy, paths) -> Result
```

- `paths` is passed in, never drawn inside — that is what makes D-07 hold
- Solve by bisection over the future marginal rate
- Returns the `Result` shape above

---

## 6. Tests

Eight. Each asserts a claim made elsewhere in the docs, which is the point of
having them.

| # | Test | Claim it defends |
|---|---|---|
| T1 | `t_now == t_later` → the two outcomes are equal under D-01 | The identity is real |
| T2 | `t*` is unchanged across `r ∈ {4, 7, 10, 12}%`, **and** the after-tax Traditional path equals the Roth path scaled by `(1−t_later)` at every year | **L1.** The scalar-multiple assertion is why it holds for any `r`, not only the four sampled |
| T3 | With D2 ON, Roth shelters strictly more real dollars than Traditional, and the cell returns `always_roth` | D2, the G4 trap, and D-25's scoping of D-01 |
| T4 | A no-crossing cell returns its sentinel and does not raise | R3. T3's cell is one, so this is exercised rather than hypothetical |
| T5 | In the base case, the today's-law effective rate is strictly below `t*` | The headline sentence — you defer at your marginal rate and withdraw across the whole bracket structure from zero |
| T6 | Low rung: a shock realizes a sale, and Traditional takes the early-withdrawal penalty while Roth basis comes out free | D-16 low branch, D5 |
| T7 | Mid rung: a shock skips the contribution year and the balance is never sold | D-16 mid branch — the shares not bought |
| T8 | High rung: a shock leaves the portfolio untouched | D-16 high branch, the control case |

T6–T8 assert the *mechanism*, not the magnitude. Three rungs are three code
branches, so three tests — a severity dial would have needed one.

---

## 7. App layout

![App layout](ui-design.PNG)
*Mockup, post-design-gate. Superseded: ladder shows 8 rungs (D-16: three),
model box is now disabled per section 7, notation `r` → `t*` (D-24).*

Top strip, left to right: current income · income shape · **state income tax
(while working)** · return rate buttons · "nevermind" toggle + year.

Caption under the state toggle: *default assumes you earn in a taxing state and
retire in one that doesn't. Both are toggles.*

The return-rate buttons sit beside the tax controls deliberately (L1 × L2
contrast). Caption under them: *this input drives the picture, not the answer.*

| Region | Contents |
|---|---|
| Left rail | Resilience ladder figure, all ten stops, with the three modeled rungs marked + a three-position control: low / mid / high |
| Headline | **Two break-even rates side by side: rules hold / treatment moves at year N.** Verdict beneath, measured against the today's-law effective marker (D-24). **At the low rung the verdict is replaced by:** *this election is not your binding constraint yet* |
| Under headline | The $X / $Y sentence |
| Under that | Balance graph — two curves diverging during saving, landing together after tax |
| Personalize | Accordion, all eight departures, grayed where scoped out |
| Model | Three dot-plot panels in a row — low, mid, high. The user's rung is highlighted, the other two dimmed but **always visible**: the collapse is the lesson, and a trend needs three points. Each panel is a cube slice |
| Numbers behind the picture | The objective × events grid, same data as the dot plot |

Beside the "nevermind" toggle:

**You can still contribute — it just stops being worth it.**

*Direct taxation of Roth withdrawals is the least likely form this takes. What
has repeatedly happened instead is that tax-free money stops being invisible —
counted toward a Medicare premium, the taxable share of Social Security, or an
ACA subsidy. The money stays untaxed and costs you anyway, one layer over.*

Poland 2013 · Ireland 2011 · US SECURE Act 2019 — the rule moved under people
who had already committed.

**Notation:** `t*` is the break-even future marginal rate. `r` is the market
return. Do not reuse `r` for both.

Top-right of the strip: a DISABLED control labeled **Model (block bootstrap)**.
Tooltip lists all nine return models from CONTEXT part D and marks the two that
are implemented — #2 fixed real rate (app headline), #6 block bootstrap (cube).
Disabled rather than absent: the option space was mapped, two were built, and
the control says so without implying the other seven exist.

---

## 8. Budget

A fixed implementation budget. Research, design, and README are declared
outside it and reported separately. Actuals go in the README.

| Item | Est. |
|---|---|
| `tax.py` + deterministic break-even | 20 |
| PoC engine, cube emit | 30 |
| Three rung mechanisms (D-16) | 15 |
| Tests | 10 |
| Streamlit app | 30 |
| Ladder graphic | 20 |
| "Nevermind" toggle | 10 |
| Deploy | 15 |
| | **130 — over by 10, slack is gone** |

The PoC line carries 5 minutes for the block resampler over a parametric draw.
Sourcing the return series is *not* in here — it belongs to the research phase,
which is declared outside the 120. That accounting is legitimate but it has a
condition: the data must exist before the clock starts (R5).

Cuts, in order, recovering roughly 26:

1. The "numbers behind the picture" grid — section 7 already calls it the same
   data as the dot plot (~8)
2. Accordion read-only — **except D4's row**, which stays editable per D-30 (~8)
3. Ladder color bands → single neutral rail, both markers kept (~5)
4. Income's suggested marker → checkbox marker only (~5)

Cut 4 costs the boat, so it is last. **Do not cut the state toggle** — CONTEXT
part E is right that every panelist sets it to their own state first.
**Do not cut to two rungs.** It saves 5 minutes and costs L3, which needs three
points to read as a trend.

**Do not cut to two rungs.** It saves 5 minutes and costs L3, which needs three
points to read as a trend.

---

## 9. Open risks

| # | Risk | Mitigation |
|---|---|---|
| R1 | **2026 bracket edges and deferral limit are unverified.** They are the one thing declared real rather than stubbed | Single module, source comment, verified by hand before build |
| R2 | Deploy. Repo is private, which rules out Streamlit Cloud; no local Docker | Railway from GitHub, known-good path. Flag at 15 minutes |
| R3 | Objectives 4 and 5 may not cross in range | T4 |
| R4 | Dots are archetype-based while the line is personalized | D-15 label. Owned in README, not hidden |
| R5 | Return series for D-05 must exist before the clock starts | Source it in the research phase, which is outside the implementation budget. **Not the same size as R1:** a wrong deferral limit breaks test T3 and a stated claim; a slightly-off 1937 return is one card in a resampling deck and breaks nothing |
