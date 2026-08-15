# Roth vs. Traditional — solve for the threshold, don't guess the input

A scenario-planning demo for the Traditional-vs-Roth 401(k) choice. Most
calculators return a recommendation. This one returns the **future marginal tax
rate at which the two choices tie**, and lets you locate yourself against it.

Built as a design spike for an energy-analytics panel. The brief is in
[`ASSIGNMENT.md`](ASSIGNMENT.md).

---

## Status

| | |
|---|---|
| **Live demo** | _Sprint 9 — URL pending_ |
| **Progress** | Sprint 1 of 9 complete |
| **Runs today** | `tax.py`, `return_series.py`, 35 passing tests |
| **Not yet written** | `engine.py` bodies, `spike_grid.py`, `app.py` |

**Where the numbers in this file come from.** Design gate two was a cold read: a
fresh agent, no access to the design conversation, asked to reproduce the
headline figures from the documents alone. It reproduced two of three, built a
working deterministic engine to do it, and found the third impossible as
specified. Every figure below came out of that engine. This repo's own
`engine.py` is still a skeleton, so read them as reproduced-and-pending rather
than as output of this codebase. Two figures were withdrawn during review and say
so rather than carrying a stale value.

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
uv run pytest                    # 35 tests, all green
uv run python return_series.py   # return-series self-test
```

Without uv:

```bash
pip install -e . && pip install pytest
python -m pytest                 # run from the repo root
```

Not yet runnable:

```bash
uv run python spike_grid.py      # Sprint 4 — writes cube.json
uv run streamlit run app.py      # Sprint 6
```

---

## Repo map

| Path | | What it holds |
|---|---|---|
| `tax.py` | ✅ | Every number that came from outside the model — 2026 single-filer brackets, standard deduction, deferral cap, state rate, early-withdrawal penalty. No tax number appears anywhere else in the repo, and `tests/` is the one stated exemption |
| `return_series.py` | ✅ | 98 annual real total returns, 1928–2025. Damodaran + CPI from the same workbook, Fisher-deflated on load. Self-tests on run |
| `tests/test_tax.py` | ✅ | 35 tests. Literals are restated by hand rather than imported — a hand-verification that imports the constant it is verifying tests nothing |
| `engine.py` | ⬜ | Skeleton. Signatures, invariants, and the tests that defend them. No bodies yet. Specified in [`docs/ENGINE.md`](docs/ENGINE.md) |
| `spike_grid.py` | ⬜ | Sprint 4. Writes the 60-cell cube and prints the markdown grid |
| `tests/test_engine.py` | ⬜ | Sprint 5. T1–T8, each docstring naming the claim it defends |
| `app.py` | ⬜ | Sprint 6. Streamlit. Reads `cube.json`; contains no stochastic code |

---

## Documentation

| File | What it is | Open it when |
|---|---|---|
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | **The build contract.** Wins over every other document | You want the authoritative answer |
| [`docs/TRADEOFFS.md`](docs/TRADEOFFS.md) | Every option considered, what each is good and bad at, which one shipped | You want to know what else was on the table |
| [`docs/DESIGN.md`](docs/DESIGN.md) | Design rationale — the model, the five mockups, and what gate two overturned | You want the reasoning and the pictures |
| [`docs/ENGINE.md`](docs/ENGINE.md) | How the math works, and the five choices inside it that change an answer | You want the numerical dynamics |
| [`docs/CONTEXT.md`](docs/CONTEXT.md) | Requirements synthesis, audience derivation, the option space as it stood at design phase | You want the framing from before decisions closed |
| [`docs/remaining-sprints.md`](docs/remaining-sprints.md) | Sprint plan, budget, done-whens, cut ladder | You want to know what's left and what gets cut first |
| [`docs/review/GATE-1.md`](docs/review/GATE-1.md) · [`GATE-2.md`](docs/review/GATE-2.md) | Cold-read design reviews by fresh agents | You want to see what the reviews caught |
| [`docs/sprints/`](docs/sprints/) | Per-sprint execution records, commit plans, verification batteries | You want commit-level detail |
| [`prompts/`](prompts/) | The prompt given to each agent session | You want the AI disclosure to be checkable |
| [`DEVLOG.txt`](DEVLOG.txt) | Working log | — |

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

The flip is real, but it belongs to someone else. The early-career preset reads
Roth under current rules and Traditional once the rule moves. **The rule change
costs the low-bracket saver Roth was supposed to be for.**

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
| **Certainty preference** — choosing Roth knowing the expected value is worse, because you'd rather not hold an open position | All five objectives are about wealth outcomes. None can express *I want it settled*. This is a real preference and the model does not contain it | A utility formulation over outcome *variance* rather than level, or an explicit premium the user names. Neither fits the threshold framing, which is why it is a branch rather than a sixth objective |
| **Bracket rise as a modeled scenario** | Already on the axis. A higher future rate is a position to the right of `t*` | Nothing. Naming it is the work, and the two-threshold headline does that |
| **Symmetric "nevermind"** — the rule change hitting Traditional's deduction too | The design deck's original words were "all tax benefits go away." Making it symmetric deletes the asymmetry the whole policy branch rests on, and it still doesn't flip the archetype toward Roth | A Traditional branch in the decumulation loop. ~20 minutes and one lost argument |
| **Two-bar asymmetry chart** (p90 gain vs p10 loss, both against median) | Teaches a real lesson — outcomes are left-skewed, the bad case is bigger than the good one — but not L3. L3 is *fragility beats the account choice*, carried by the dot collapse and the $X/$Y sentence. Adjacent, not the same | A `p90` field in the cube and one chart. ~10 minutes |
| **Block length sensitivity** | Block length 5 is a stated fudge factor | Run at 3 and 10, record the deltas. Sprint 3 does this and reports it here |
| **Block bootstrap over IID** | Kept, but its original justification failed measurement — block *thins* the tail rather than fattening it (p10 drawdown −59.7% vs −64.3%), because annual real returns have a lag-1 autocorrelation of −0.035. It survives on the recovery-forgone channel, and on reproducing history's own worst five-year run. At ~19.6 independent blocks the structure claim cannot be validated, only stated | Switching to IID would delete one fudge factor and simplify Sprint 3 by about five minutes. The reason not to is that block is the more conservative tail and keeps real sequences intact — but that is a preference, not a result, and this row says so |
| **Shock magnitude sensitivity** | $40,000 is the same kind of fudge factor | Run at $25,000 and $80,000. Same sprint |
| **Over-65 deductions** — the permanent $2,050 additional standard deduction, and the OBBB senior deduction of up to $6,000 | Deferred, not overlooked. Together they move the marker from 15.2% to **13.5%**, which *widens* Traditional's lead — so omitting them **understates** the recommendation. Neither changes a verdict, and the preset's flip survives at 14.4% against a 12.0% threshold. The $6,000 also sunsets, and applying it across a 35-year retirement would assert something the statute doesn't say | The $2,050 is one conditional on age in `tax.py` and is the honest one to wire first. The $6,000 needs a phaseout and an expiry |
| **SALT deductibility** — state tax is added flat to the federal marginal rate | **The larger of the two known biases, and it points the other way.** For a filer who itemizes the true combined rate is `0.24 + 0.085 × (1 − 0.24)` = **30.5%, not 32.5%** — two points on the headline itself, in the direction that flatters Traditional. It bites only on itemizers: state income tax alone is $14,025 at the archetype against a $16,100 standard deduction, so it takes about $2,075 more of mortgage interest, property tax or charity to cross | An itemize-or-not branch, and the state rate applied inside the federal calculation rather than beside it |
| **Real per-state tax data** | One boolean at 8.5% carries the whole state effect | A state table and a second lookup. The `TODO` is in `tax.py` |
| **MFJ and Head of Household** | Single only — the UI models one income curve and one age, so a household is something the controls cannot represent. *(The earlier reason given here, overlapping HoH bracket edges, does not survive checking: the published 2026 HoH column is contiguous.)* | Two more bracket tables, verified against the same primary source |
| **Employer match, and the taxable side account** | Both are Traditional-flavored money that arrives whether or not you choose it. Grayed in the accordion as evidence of completeness | A second contribution stream and a taxable-account model. This is where the next hour would go |

---

## AI disclosure

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
| 6 | Docs assessment | — | _(link)_ |

Sessions 3 and 4 were deliberately cold: a fresh agent with no access to the
design conversation, given the documents only. **Gate two is the reason three
headline numbers changed.**

---

## References

1. **r/personalfinance flowchart** — [`docs/reddit_personal_finance_flowchart.jpeg`](docs/reddit_personal_finance_flowchart.jpeg) ·
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
