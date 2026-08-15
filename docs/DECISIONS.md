# DECISIONS

Status: design phase closed. This file is the build contract.

## 0. Precedence

Where this file and `CONTEXT.md` disagree, **this file wins.** `CONTEXT.md` is
the tradeoff reference — it records the option space that was considered, and its
option tables now carry two marker sets: `← initial pick` for the choice made
during synthesis, `← design-phase pick` for what survived design. Where a row
carries both, the choice held.

Two conflicts remain that markers can't express, plus two in `DESIGN.md`:

| Says | Superseded by |
|---|---|
| CONTEXT §B — PoC is "deliberately throwaway" | D-11. The PoC *is* the engine the app imports |
| CONTEXT §G3 — model the employer match | D8 disposition. Grayed, `TODO` |
| DESIGN.md — grid columns are a "shock count" | D-08. Columns are shock count; *timing* is correlated with drawdown |
| DESIGN.md — rung slider, 8–10 stops, feeding shock severity | D-16. Three rungs, and the rung selects a *mechanism*, not a severity |

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
| D-07 | **Common random numbers.** Draw the `(n_paths, n_years)` array once; reuse across every cell, both choices, every bisection step | The quantity of interest is a small difference between two large numbers. Pairing removes sampling noise from that difference, makes the cube reproducible from a seed, and makes 160 cells cheap |
| D-08 | **Shock columns are a count (0–3); shock *timing* is correlated with drawdown.** Correlated is the default; an uncorrelated toggle exists for contrast | Forced liquidation lands when prices are worst. The toggle makes the fat tail appear and disappear in one click |
| D-09 | **Policy scenario is "nevermind," prospective.** After year N (default 20), withdrawals are ordinary income regardless of account type — applied to growth after year N, not retroactively to existing balance | Simpler than a haircut: no rate parameter. Prospective is what actually tends to happen when rules move |
| D-10 | **"Nevermind" is labeled as what Roth is betting, not as a neutral scenario** | It is one-sided — Traditional already banked its deduction. Honest framing. README carries one line noting a bracket rise cuts the other way |

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

---

## 4. Departure dispositions

The mechanisms behind the model. Accordion shows all eight; grayed rows show
what was scoped out and stay visible as evidence of completeness.

| # | Departure | Leans | Disposition |
|---|---|---|---|
| D1 | You withdraw *across* brackets, not at one rate | Traditional | **Real.** Accordion, editable |
| D2 | Contribution limit binds — Roth shelters more real money | Roth | **Real.** Hard-coded 2026 values, `TODO` source |
| D3 | Below the limit, the tax saving sits in a taxable side account | Roth | **Grayed.** `TODO`. See D-01 — the convention absorbs the trap without the model |
| D4 | You retire in a different state than you earned in | either | **Boolean tax / no-tax toggle**, top area. `TODO` real per-state data |
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

Four. Each asserts a claim the README makes, which is the point of having them.

| # | Test | Claim it defends |
|---|---|---|
| T1 | `t_now == t_later` → the two outcomes are equal under D-01 | The identity is real |
| T2 | Break-even is unchanged across `r ∈ {4, 7, 10, 12}%` | **L1** |
| T3 | At the deferral cap, Roth shelters strictly more | D2 / the G4 trap |
| T4 | A no-crossing cell returns a sentinel and does not raise | The demo doesn't die on the interesting cases |

---

## 7. App layout

Top strip, left to right: current income · income shape · state tax toggle ·
**return rate buttons** · "nevermind" toggle + year.

The return-rate buttons sit beside the tax controls deliberately (L1 × L2
contrast). Caption under them: *this input drives the picture, not the answer.*

| Region | Contents |
|---|---|
| Left rail | Resilience ladder figure, all ten stops, with the three modeled rungs marked + a three-position control: low / mid / high |
| Headline | Break-even rate `t*` + verdict. **At the low rung the verdict is replaced by:** *this election is not your binding constraint yet* |
| Under headline | The $X / $Y sentence |
| Under that | Balance graph — two curves diverging during saving, landing together after tax |
| Personalize | Accordion, all eight departures, grayed where scoped out |
| Model | Three dot-plot panels in a row — low, mid, high. The user's rung is highlighted, the other two dimmed but **always visible**: the collapse is the lesson, and a trend needs three points. Each panel is a cube slice |
| Numbers behind the picture | The objective × events grid, same data as the dot plot |

Historical line beside the "nevermind" toggle: *Poland 2013, Ireland 2011, US
SECURE Act 2019.*

**Notation:** `t*` is the break-even future marginal rate. `r` is the market
return. Do not reuse `r` for both.

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
| "Nevermind" toggle | 10 |
| Deploy | 15 |
| | **130 — over by 10, slack is gone** |

The PoC line carries 5 minutes for the block resampler over a parametric draw.
Sourcing the return series is *not* in here — it belongs to the research phase,
which is declared outside the 120. That accounting is legitimate but it has a
condition: the data must exist before the clock starts (R5).

Cuts, in order, recovering roughly 10. First: the state toggle. Second: the
accordion goes read-only — the eight departures still display, they just stop
being editable.

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
