"""The math. Pure functions, no Streamlit import (D-11, D-12).

One question: at what future marginal tax rate do Roth and Traditional tie?
Everything else in the project is presentation.

INVARIANTS THE TESTS DEFEND
  T1  t_now == t_later  ->  equal outcomes                        (D-01)
  T2  t* unchanged across r in {4, 7, 9, 12}%, AND the common draw
      CANCELS out of the difference: after_tax_trad(100) - roth(100)
      is identical at draw = 0, 108_397 and 250_000, at every r.
      Both accounts fund the same net spending, so the draw subtracts
      the same real amount from both after-tax paths and vanishes.
      The difference is
          roth_65 * [(1 - t_later)/(1 - t_now) - 1] * (1 + r)**35
      which crosses zero at t_later == t_now for ANY r and ANY draw.
      THAT is why t* is exact, and it is a stronger claim than the
      four sampled rates.                                         (L1)

      NOT the earlier wording. "The after-tax Traditional path equals
      the Roth path scaled by (1 - t_later) at every year" is FALSE
      through decumulation once t_later != t_now: the ratio runs
      1.12 -> 1.43 -> 8.91 across ages 66, 82, 99. It holds in
      accumulation, or at t_later == t*.
  T5  IN THE BASE CASE, the today's-law marker is strictly below t*  (D-24)
      THE SCOPE IS LOAD-BEARING AND TWO DOCUMENTS DROPPED IT. Section 6 reads
      "in the base case"; remaining-sprints' 2C done-when and ENGINE.md's T5
      row did not, and unscoped the claim is FALSE BY DESIGN. At the
      early-career preset the marker is 15.9184% against t* = 12.0000% --
      D-40's own published pair, and the inversion is exactly why that preset
      carries the flip. Asserted at the archetype, with the preset as its
      teeth.                                                    (2C, CL-5)

  Validation gate, DERIVABLE not measured: objectives 1, 3, 4 and 5
  are monotone functionals of the after-tax terminal distribution,
  so wherever the two distributions are positive scalar multiples,
  all of them cross at t_now. Mid preserves the multiple (a paused
  contribution removes c from Traditional and c*(1-t_now) from Roth)
  and High preserves it trivially. So the whole Mid and High slabs
  equal t_now at every shock count -- 32 of 48 cells -- plus Low's
  0-shock row, for 36 of 48. Only Low with shocks >= 1 varies.
  Assert as an identity, not a tolerance.                         (D-22)

WHAT MUST NOT APPEAR IN THIS FILE
  - `import streamlit`                                            (D-11)
  - any tax literal; they live in tax.py                          (D-21)
  - any draw of the paths array; it is passed in                  (D-07)
  - any clamp of a balance at zero                                (D-38)

SPRINT 2B PINNED THREE THINGS THE DOCUMENTS LEFT OPEN. Each is stated at the
function that implements it; collected here because a reader looking for
"what did 2B decide" should not have to find three docstrings.

  1. THE DRAW'S RETURN RATE. outcome() receives `paths`, never a scalar return
     rate -- its own `rate` argument is t_later, a TAX rate. D-39 named two
     candidates (7% deterministic, 6.776% the series' geometric mean) and asked
     2B to pick. Neither was picked. Instead: the draw is sized at
     draw_return_rate(paths), the geometric mean of the array the engine was
     handed, on a deterministic reference accumulation at that rate. On a
     constant array that returns the rate itself to within 1e-16, so the
     deterministic gate reproduces; on a bootstrap it returns the series' own
     mean. One expression, no branch, and D-22's "the engine cannot tell which
     kind it received" survives literally rather than by convention.
     CONSEQUENCE, and it is owed to Sprint 3: R9's 53.1% ruin figure was
     measured with the draw sized at the 7% deterministic solve. Under this
     rule the bootstrap draw is smaller, so that figure needs re-measuring --
     in the direction that makes R9 less bad, not worse.
  2. RUIN'S OPERAND is the account BALANCE, not the after-tax value (Sec 5 says
     "after-tax balance"). For Traditional and for Roth under current rules the
     two agree in sign, because (1 - t_later) > 0. They can disagree for Roth
     UNDER THE POLICY, where rem*t_later + B*(1 - t_later) stays positive for a
     small negative B. Running out of money is a fact about the account; `rem`
     is a tax attribute, not money you can spend.
  3. `shocks > 0` RAISES rather than silently returning the 0-shock answer.
     Same reasoning make_paths("block", ...) already uses: a silent fallback
     would make every shocked gate in Sprints 3 and 4 pass for the wrong
     reason. The PARAMETER lands here so Sprint 3 fills a branch instead of
     moving a seam under 2A's 54 tests; only the BODY is deferred.

SPRINT 2C PINNED THREE MORE. Same accounting as the block above: each is stated
at the function that implements it, collected here so "what did 2C decide" is one
place. All three are search parameters -- none of them is a modeling choice, and
that is why they live here rather than in a decision row of their own.

  1. THE BISECTION BRACKET IS (0.01, 0.95), AND IT IS A CITATION RATHER THAN A
     PICK. Section 5 says "evaluate the difference at both bracket endpoints" and
     never says what they are; D-06, D-22, D-38 and ENGINE.md are all silent. But
     D-26's row already publishes a swept interval -- "the after-tax difference
     NEVER crosses zero anywhere in t_later in (0.01, 0.95)" -- and
     test_the_d26_terminal_rule_reproduces_all_three_readings runs exactly that
     grid today. The number was in the corpus, unlabeled.
     WHY THE LOW END CANNOT SIMPLY BE ZERO, WHICH IS THE REAL FINDING.
     _outcome_paths guards 0 < rate < 1, so lo = 0 RAISES and the "sign of zero"
     branch is unreachable there. The degenerate case is real and sits one cliff
     over: at the D-42 profile trad_65 and roth_65 are bit-identical, so the
     difference is -roth_65 * t_later * (1+r)**35 and it UNDERFLOWS TO EXACTLY
     0.0 at t_later around 1e-17. sign(f(lo)) is then 0, the no-crossing test
     sign(f(lo)) == sign(f(hi)) is False, and T4's cell reports a crossing near
     zero instead of always_roth. At lo = 0.01 that difference is -24,708.70 --
     thirteen orders above the floor -- so the zero branch cannot arise and there
     is no third case to write.
  2. THE STOPPING RULE IS FLOAT EXHAUSTION, NOT A TOLERANCE. The loop runs until
     the midpoint equals an endpoint. D-22's "assert as an identity, not a
     tolerance" and a t* published to four decimals only look opposed: the first
     governs the TEST, the second needs a rule for the SOLVER. This repo has
     already reconciled that exact pair twice -- 2A's 4-ulp bound on the
     accumulation identity and T1's K = 16 -- and Section 5 states the
     reconciliation in so many words: a REPRESENTATION tolerance, not a modeling
     one. Measured, at 54 evaluations: t* lands 3 ulps from t_now at the
     archetype and 20 at the preset, and the published 58.4064361550% reproduces
     in full. Stopping at hi - lo <= 1e-4 instead returns 58.4046% and misses a
     published figure in its fourth decimal.
  3. RUIN IS MEASURED AT THE RATE THE RESULT REPORTS. Result.ruin varies with
     t_later and nothing in the corpus said at which one: Traditional's fraction
     goes 0.0 -> 1.0 between 32.50% and 33.45%, one point either side of t*. So a
     crossing cell reports ruin at its own t*, which is what the done-when's "must
     not mean running the decumulation a second time" already points at. A
     NON-CROSSING cell has no t* and reports at t_now -- the one rate defined for
     every profile without a solve, and the rate t* equals on every crossing cell
     under current rules. That second half is the only line in this block with no
     document behind it.

OBJECTIVE ENCODING (D-06, CONTEXT part C). Four ints, and 2 is not one of them:
  1  mean of the after-tax terminal distribution   ("max expected terminal")
  3  median                                        ("max median outcome")
  4  10th percentile                               ("regret-minimizing")
  5  P(not running out) -- MAXIMIZED like the other three, so it is the
     COMPLEMENT of Result.ruin. D-22's "P(< 0)" names the same functional
     pointed the other way; every objective has to increase in the same
     direction or breakeven() has no monotone difference to bracket.
  2  REJECTED. Under a common draw and D-38 both accounts fund identical
     spending, so the difference is identically zero (D-06).

POLICY ENCODING (D-09, D-26): `None` for current rules, or an int year N for
"nevermind" applied at that year. Not a boolean -- N is D-26's snapshot index.
"""

import hashlib
from dataclasses import dataclass, field

import numpy as np

import return_series
import tax

SEED = 20_260_815      # D-41. Contract, not preference -- the cube must be
N_PATHS = 2_000        # byte-reproducible from the header.
BLOCK_LENGTH = 5       # D-05. Stated fudge factor; 3 and 10 measured in Sprint 3.
SHOCK_AMOUNT = 40_000  # D-39. Real. 1.6x a contribution year, so the forced
                       # sale and the skipped contribution are the same order
                       # of magnitude. $25k and $80k measured in Sprint 3.
ROTH_TERMINAL_MARGIN = 0.15   # D-39. The draw leaves this fraction of the
                              # Roth's age-65 balance at 100, so the base case
                              # is not sitting exactly at zero where any shock
                              # ruins every objective at once.

SAVINGS_RATE = 0.20    # D-28. BEHAVIORAL, sourced from BLS household budget
                       # data -- not a tax number, which is why it lives here
                       # and arrives at tax.contribution() as an argument
                       # (D-21). The CAP it is compared against lives in tax.py.
RETIREMENT_AGE = 65    # D-20. Accumulate up to it, decumulate from it.
TERMINAL_AGE = 100     # D-20. Every objective evaluates here. "Terminal wealth"
                       # means bequest at 100, not balance at 65.
POLICY_YEAR = 20       # D-09/D-26 default N. Year 1 is current_age, so N=20 is
                       # the balance AFTER the age-54 contribution, not age 55.

BRACKET = (0.01, 0.95) # 2C. breakeven()'s search interval. NOT A TAX NUMBER and
                       # so not D-21's business -- it is a bound on the search,
                       # not a fact about the code. Cited rather than chosen:
                       # D-26's row measures the untaxed reading across
                       # t_later in (0.01, 0.95), and the 2B test that
                       # reproduces its three readings sweeps that same grid.
                       # See pin 1 in the module docstring for why the low end
                       # cannot be zero.


# --- The resilience ladder (D-33) --------------------------------------------
# Bottom to top. Ten stops, ten booleans, one per stop (D-32). Named here rather
# than in the app because contiguity is a MODELING rule, not a display rule --
# spike_grid.py needs the rung and must not import Streamlit to get it (D-11).
LADDER_STOPS = (
    "$400",                    # 1  |
    "$2,000",                  # 2  |  Low  -- a shock forces a sale
    "high-interest debt",      # 3  |
    "employer match",          # 4  |
    "medium-interest debt",    # 5  |  Mid  -- the contributing band; a shock
    "20% to 401k",             # 6  |         pauses contributions
    "max IRA",                 # 7  |
    "max 401k",                # 8  |  High -- money outside the emergency path
    "no mortgage",             # 9  |
    "other assets",            # 10 |
)
_RUNG_BANDS = ((3, "low"), (6, "mid"), (10, "high"))   # D-33 upper edges
DEFAULT_STOPS = tuple(i < 6 for i in range(10))        # D-32: 1-6 on, 7-10 off


def highest_contiguous_stop(stops) -> int:
    """How many stops are cleared from the BOTTOM without a gap (D-37).

    Ten independent booleans make the ladder show ordering rather than just
    position. A stop checked with nothing beneath it is capital parked above a
    gap it should be filling, and it does not count -- the shock mechanism
    depends on what is underneath you, so a lone top stop still reads Low.

    The return value doubles as the index of the LOWEST UNCHECKED stop, which is
    what D-37's copy names: "the flowchart would prioritize [that stop] first."
    """
    n = 0
    for cleared in stops:
        if not cleared:
            break
        n += 1
    return n


def rung_from_stops(stops) -> str:
    """"low" | "mid" | "high", banded per D-33: 1-3 / 4-6 / 7-10.

    THE RUNG IS DERIVED, NEVER STORED AND NEVER A CALL ARGUMENT. That is what
    lets outcome() and breakeven() keep the signatures Section 5 publishes while
    the cube still has a rung axis: Sprint 4 sweeps that axis by REPLACING
    `stops`, not by passing a rung. One definition of "what rung am I", read by
    the engine, by D-35's verdict suppression and by D-37's gap message.

    Zero stops cleared reads "low". D-37 already rules that a lone top stop
    reads Low; the floor reads Low for the same reason -- a shock with no buffer
    forces the sale, which IS the Low mechanism.
    """
    n = highest_contiguous_stop(stops)
    for edge, name in _RUNG_BANDS:
        if n <= edge:
            return name
    raise AssertionError("unreachable: the last band's upper edge is len(stops)")


# --- Profile ------------------------------------------------------------------
@dataclass(frozen=True)
class Profile:
    """Everything the user sets. Section 5 publishes these fields.

    The income curve lives here rather than in tax.py because it is a MODELING
    assumption, not a number that came from outside (D-21) -- same reason
    savings_rate does.

    t_now IS ONE SCALAR PER PROFILE, not a per-year lookup. Forced rather than
    chosen: D-22's accumulation identity is roth_65 / trad_65 == 1 - t_now
    EXACTLY, and a rate that moved with the income curve turns that ratio into a
    weighted average landing on no published number. It is the cheapest test in
    the project and it only exists under this reading.
    """
    income_points: tuple           # four (age, gross) pairs, D-19
    savings_rate: float = SAVINGS_RATE                  # D-28
    current_age: int = 35                               # D-19
    state_while_working: bool = True                    # D-30, default yes
    state_in_retirement: bool = False                   # D-30 / D4, default no
    d2_roth_to_cap: bool = False                        # D-25 / D2, default off
    stops: tuple = DEFAULT_STOPS                        # D-32

    def __post_init__(self):
        if self.current_age >= RETIREMENT_AGE:
            raise ValueError(
                f"current_age {self.current_age} >= {RETIREMENT_AGE}: this model "
                "has no partial accumulation phase (D-20)"
            )
        if len(self.stops) != len(LADDER_STOPS):
            raise ValueError(
                f"stops must carry one boolean per D-33 ladder stop "
                f"({len(LADDER_STOPS)}), got {len(self.stops)}"
            )

    # -- derived, all of it ----------------------------------------------------
    @property
    def rung(self) -> str:
        return rung_from_stops(self.stops)

    @property
    def n_years(self) -> int:
        """D-20. The only place the horizon meets a profile object."""
        return TERMINAL_AGE - self.current_age

    @property
    def n_accumulation_years(self) -> int:
        return RETIREMENT_AGE - self.current_age

    @property
    def n_decumulation_years(self) -> int:
        return TERMINAL_AGE - RETIREMENT_AGE

    def income(self, age: float) -> float:
        return income(age, self.income_points)

    @property
    def t_now(self) -> float:
        """combined_rate at the CURRENT-AGE income. See the class docstring."""
        gross = self.income(self.current_age)
        return tax.combined_rate(
            gross,
            tax.contribution(gross, self.savings_rate),
            self.state_while_working,
        )


def income(age: float, points) -> float:
    """Gross income at an age. Four points, linearly interpolated (D-19).

    Flat outside the range in both directions: the curve is a shape the user
    draws, not an extrapolation, and D-19's fourth point is deliberately flat
    from the peak because ending high is the CONSERVATIVE case -- it raises
    retirement spending and narrows Traditional's lead.

    Sprint 2A gate: income(45) sits on the 38 -> 55 leg at $126,470.59.
    """
    pts = sorted(points)
    if age <= pts[0][0]:
        return float(pts[0][1])
    if age >= pts[-1][0]:
        return float(pts[-1][1])
    for (a0, i0), (a1, i1) in zip(pts, pts[1:]):
        if a0 <= age <= a1:
            return i0 + (i1 - i0) * (age - a0) / (a1 - a0)
    raise AssertionError("unreachable: the bracketing loop covers [first, last]")


# --- The two published profiles, plus T3's ------------------------------------
ARCHETYPE = Profile(                                             # D-19
    income_points=((35, 165_000), (38, 75_000), (55, 200_000), (65, 200_000)),
)
EARLY_CAREER = Profile(                                          # D-40
    income_points=((35, 60_000), (38, 54_000), (55, 200_000), (65, 200_000)),
    state_while_working=False,
    state_in_retirement=False,
)
TEST_185K = Profile(                                             # D-42
    # FLAT is the specification, not a convenience. D2's affordability is tested
    # every contribution year, and any trough fails it there: drop the
    # archetype's parental-leave year in and capacity collapses in exactly the
    # years T3 is about.
    income_points=((35, 185_000), (38, 185_000), (55, 185_000), (65, 185_000)),
    d2_roth_to_cap=True,
)


# --- Contributions ------------------------------------------------------------
def contributions(profile: Profile, age: int) -> tuple:
    """(traditional, roth) nominal contributions for one year.

    D2 OFF -- D-01, same PRE-TAX dollars: trad = min(capacity, cap) and roth is
    that scaled by (1 - t_now). The Roth deliberately under-fills and the app
    says so. Comparing them as equal NOMINAL dollars is the G4 trap and quietly
    favors Roth.

    D2 ON -- D-25: trad is unchanged, because the cap already binds it and it
    cannot go higher. The Roth fills to the cap in AFTER-TAX dollars, limited by
    what the savings capacity can actually buy. That deliberately BREAKS D-01's
    convention, and the break is the asymmetric mechanism D-22 counts alongside
    Low's penalty.

    The unaffordable case degrades rather than raising. At the archetype the
    capacity term binds below the cap, which is D-42's lesson as arithmetic
    instead of as an exception: the cap is denominated in dollars that cost you
    more, so it binds before it looks like it should.
    """
    gross = profile.income(age)
    capacity = profile.savings_rate * gross
    trad = tax.contribution(gross, profile.savings_rate)   # min(capacity, cap)
    if profile.d2_roth_to_cap:
        roth = min(tax.DEFERRAL_CAP, capacity * (1.0 - profile.t_now))
    else:
        roth = trad * (1.0 - profile.t_now)
    return trad, roth


# --- Accumulation -------------------------------------------------------------
@dataclass
class Accumulation:
    """Both accounts at 65, plus the year-by-year balances D-26 snapshots."""
    trad: float
    roth: float
    t_now: float
    trad_by_year: list = field(repr=False)   # index i -> AFTER year i+1's flow
    roth_by_year: list = field(repr=False)


def accumulate(profile: Profile, path, shocks: int = 0) -> Accumulation:
    """Ages current_age -> 64, both accounts, one real-return path.

    CASH FLOWS LAND AT PERIOD END (D-20):

        balance = balance * (1 + r) + contribution

    so a contribution earns no return in the year it is made. This is stated
    because it is not free. The annuity-due reading -- contribute first, then
    grow -- multiplies every published balance by exactly (1 + r): Traditional
    at 65 becomes $2,256,487 instead of $2,108,867, +7.0%. Far enough to fail
    every gate in this sprint, close enough to read as an interpolation bug.

    `path` is one row of the array make_paths() built. It is passed in, never
    drawn here -- that is what makes D-07 hold (D-07 is about the CUBE, but the
    discipline has to start where the first random number would be consumed).

    `shocks` ARRIVED IN SPRINT 2B AS A DEFAULTED PARAMETER AND AN EMPTY BRANCH.
    All three rung mechanisms are defined on a contribution stream (D-08, D-16)
    and their bodies are Sprint 3's; High's branch -- portfolio untouched -- is
    already exactly this code. The parameter landed early on purpose: Sprint 3's
    two obvious routes were to change a published signature underneath 2A's 54
    tests, or to duplicate this loop inside outcome(). Defaulting it here is the
    third, and it is D-39's own argument about the draw's `rate` applied to a
    second parameter -- pin it while the function is open, not when the paths
    arrive (remaining-sprints, Sprint 2B PIN).

    IT RAISES ABOVE ZERO RATHER THAN QUIETLY IGNORING THE COUNT. Returning the
    0-shock balances under shocks=3 is the same failure make_paths("block", ...)
    already refuses: every shocked gate in Sprints 3 and 4 would pass for the
    wrong reason, and the 12 informative cells of the cube (D-22) would report
    the 36 uninformative ones' answer.

    Sprint 2A gates, at 7% real:
        ARCHETYPE     trad 2,108,867   roth 1,423,485
        EARLY_CAREER  trad 1,749,149   roth 1,539,251
        roth / trad == 1 - t_now, EXACTLY, at every r
    """
    n = profile.n_accumulation_years
    if len(path) < n:
        raise ValueError(
            f"path has {len(path)} years, accumulation needs {n} "
            f"(n_years = {TERMINAL_AGE} - current_age, D-20)"
        )
    if shocks:
        # [SPRINT-3-CLEANUP] The three rung mechanisms are Sprint 3's first
        # deliverable (D-16, remaining-sprints Sprint 3). Raising rather than
        # ignoring the count, for make_paths("block", ...)'s reason.
        raise NotImplementedError(
            f"shocks={shocks}: the rung mechanisms are Sprint 3 -- see D-16 and "
            "remaining-sprints.md. The parameter is pinned here (Sprint 2B), "
            "the branch is not"
        )
    t_now = profile.t_now
    trad = roth = 0.0
    trad_by_year, roth_by_year = [], []
    for i in range(n):
        r = float(path[i])
        c_trad, c_roth = contributions(profile, profile.current_age + i)
        trad = trad * (1.0 + r) + c_trad      # PERIOD END. D-20.
        roth = roth * (1.0 + r) + c_roth
        trad_by_year.append(trad)
        roth_by_year.append(roth)
    return Accumulation(trad, roth, t_now, trad_by_year, roth_by_year)


def policy_allowance(acc: Accumulation, n: int = POLICY_YEAR) -> float:
    """D-26's frozen allowance: the Roth balance at year N, in real dollars.

    IT DOES NOT GROW after this. Withdrawals draw it down first; everything past
    it is ordinary income at t_later, and so is whatever bequest is left at 100.

    THE OFF-BY-ONE IS THE WHOLE FUNCTION. Year 1 is current_age, so year 20 is
    age 54 and the value is the balance AFTER that year's contribution --
    $607,475 at the archetype. Reading it as age 55 gives $666,536 and misses by
    $59,061. Indexing `roth_by_year[n - 1]` is the statement of that rule.
    """
    if not 1 <= n <= len(acc.roth_by_year):
        raise ValueError(f"policy year {n} outside the accumulation phase")
    return acc.roth_by_year[n - 1]


# --- Paths --------------------------------------------------------------------
def geometric_mean(returns) -> float:
    """Compounded annual rate of a return sequence.

    Here because D-15's proxy has to run at the rate the SERIES MEASURES rather
    than at a rounding of it. The four-decimal literal returns $2,028,055.76;
    this function's value returns $2,028,066.17, which is the published figure.
    Ten dollars, on a number whose only job is to be checked against.

    COMPUTED IN LOG SPACE, AND THAT IS NOT A STYLE CHOICE. The running-product
    form this replaced overflowed float64 at about 10,800 factors. One path is
    65 of them and nobody noticed; D-41's n_paths = 2000 is 130,000 of them and
    draw_return_rate() flattens the whole array, so Sprint 3's first bootstrap
    would have returned inf -- and then nan through _solve_draw and outcome(),
    with objective 5 reporting 1.0, ZERO RUIN, which is exactly the number
    Sprint 4's 0-shock gate is looking for. exp(mean(log1p(x))) - 1 is
    bit-identical on both arrays that carry a published figure: the 7% constant
    array and the 98-year series.

    log1p rather than log(1 + x) for the small-return precision, and the guard
    below is what a total loss would otherwise do -- log1p(-1) is -inf, where
    the product form silently returned -1.
    """
    a = np.asarray(returns, dtype=float).ravel()
    if a.size == 0:
        raise ValueError("geometric_mean of an empty sequence is undefined")
    if np.any(a <= -1.0):
        raise ValueError(
            "a return of -100% or worse has no geometric mean: the compounded "
            "path is zero or negative and no annual rate reproduces it"
        )
    return float(np.exp(np.mean(np.log1p(a))) - 1.0)


@dataclass
class Result:
    breakeven: float | None
    status: str            # "crosses" | "always_roth" | "always_trad"
    dollars: dict | None   # keyed by delta: {"2": {"roth": f, "trad": f}, "10": {...}}
    ruin: dict             # {"roth": f, "trad": f}


def make_paths(kind: str, n_paths: int, n_years: int, rate: float = 0.07,
               seed: int = SEED):
    """Build the (n_paths, n_years) real-return array.

    kind="constant" -> shape (1, n_years) filled with `rate`. This IS the
    deterministic mode (D-22) -- not a flag, a shape. The engine cannot tell
    which kind it received, which is what keeps the headline and the cube from
    ever drifting apart. n_paths is IGNORED here and that is deliberate: at
    n_paths > 1 a constant array holds n identical rows, so objectives 1, 3 and
    4 would collapse onto the same number while costing n times the arithmetic.
    `seed` is ignored here too -- there is nothing random to seed.

    kind="block" -> block bootstrap over return_series.py, BLOCK_LENGTH=5. Bad
    years must arrive in RUNS or the forced-liquidation argument is mechanical
    only. n_paths IS honored here, which is the one place the two kinds differ
    in their reading of the same argument.

    P4's gate is CLEARED (D-41, R5): return_series.py holds the real 98-year
    series, STUB is False, and its self-test passes. The runtime guard that
    remains is STUB itself -- this path raises while it is True, BEFORE it
    raises on anything else, so a stub deck fails loudly rather than quietly.

    THE THREE PARAMETERS D-41 MAKES CONTRACT (Sprint 3A). Decided in writing
    before the first array existed, which is the done-when's own wording, and
    recorded in DECISIONS D-43. Short form, because a reader looking for "how is
    a path built" should not have to leave this file:

      GENERATOR: np.random.RandomState(seed), MT19937. Chosen AGAINST current
      numpy practice and the reason is a product reason rather than a numerical
      one. NEP 19 freezes the legacy stream permanently and explicitly declines
      to freeze `default_rng`, which may change its stream in a minor release.
      D-41 says the cube must be byte-reproducible FROM ITS HEADER -- from an
      integer, by a reader who has neither this environment nor its lockfile.
      Only the frozen stream delivers that. The modern generator is the faster
      and the less reproducible one, and nothing here is performance-bound.

      SAMPLING: overlapping starts, drawn uniformly over [0, N - 5], NO WRAP.
      Ninety-four distinct blocks against a fixed partition's nineteen. It is
      also the only scheme that can reproduce a published figure: ENGINE.md and
      D-05 both carry "the median path's worst five-year run lands at -10.26%
      annualized, which is exactly 1937-41", and 1937 is deck index 9. A
      partition anchored at 1928 cannot emit that block AT ALL -- its worst
      reachable run is -7.72%, 1928-32 -- so the partition reading falsifies a
      sentence in two documents. Wrapping was refused for the opposite reason:
      it would manufacture a 2025 -> 1928 adjacency that never happened. The
      cost is accepted and named -- edge years appear in fewer windows, so the
      oldest and most recent years are undersampled.

      TRAILING BLOCK: TRUNCATED. Free at both published profiles -- 30 and 65
      are 6 and 13 whole blocks -- but free by coincidence is not decided, and
      current_age = 36 gives 64 years, which is 12.8. One control-tweak away,
      not hypothetical.

    THE DRAW ORDER IS ROW-MAJOR AND THAT BUYS SOMETHING. One randint call fills
    (n_paths, n_blocks) in C order, so path i's blocks are consumed before path
    i+1's. Consequence: at a fixed seed and n_years, a 4,000-path array's first
    2,000 rows ARE the 2,000-path array, bit for bit. Sample sizes nest instead
    of re-randomizing, so a sensitivity run at a larger n is a superset rather
    than a different experiment. Asserted in tests/test_engine.py.
    """
    if n_years < 1:
        raise ValueError(f"n_years must be positive, got {n_years}")
    if kind == "constant":
        return np.full((1, n_years), float(rate), dtype=float)
    if kind == "block":
        if return_series.STUB:
            raise RuntimeError(
                "return_series.STUB is True -- the block bootstrap cannot deal "
                "from a stub deck (D-41)"
            )
        if n_paths < 1:
            raise ValueError(f"n_paths must be positive, got {n_paths}")
        deck = np.asarray(return_series.REAL_RETURNS, dtype=float)
        if deck.size < BLOCK_LENGTH:
            raise ValueError(
                f"the deck holds {deck.size} years and a block is "
                f"{BLOCK_LENGTH} (D-05): there is no block to draw"
            )
        n_blocks = -(-n_years // BLOCK_LENGTH)          # ceil, then truncate
        starts = np.random.RandomState(seed).randint(
            0, deck.size - BLOCK_LENGTH + 1, size=(n_paths, n_blocks)
        )
        runs = starts[:, :, None] + np.arange(BLOCK_LENGTH)
        return deck[runs].reshape(n_paths, n_blocks * BLOCK_LENGTH)[:, :n_years]
    raise ValueError(f"unknown kind {kind!r}: expected 'constant' or 'block'")


def paths_digest(paths) -> str:
    """A stable 16-byte fingerprint of a paths array, as hex.

    EXTRACTED AT SPRINT 3A FROM _accumulations(), WHICH ALREADY COMPUTED IT.
    D-41 requires the cube to be byte-reproducible from its header, so Sprint 4A
    writes this into that header -- and the expression was already living inside
    a cache key, where nothing published could reach it. Two call sites, one
    definition; the alternative was the same three lines in two places, which is
    the "second place to keep it in step" this file refuses elsewhere.

    Hex rather than bytes because a JSON header has to carry it. The cache does
    not care which it gets.
    """
    return hashlib.blake2b(
        np.ascontiguousarray(paths, dtype=float).tobytes(), digest_size=16
    ).hexdigest()


def path_drawdown(paths):
    """PATH-DRAWDOWN: one number per path. The deepest peak-to-trough decline of
    the cumulative return index, over whatever window it is handed.

    THE NAME IS THE DELIVERABLE (Sprint 3A, D-44). Three quantities in this
    project were all called "drawdown" and two of them are not this one:

        path-drawdown      deepest peak-to-trough decline of the index.
                           ONE PER PATH. What -42.6% is. This function
        underwater-depth   how far below its running peak the index sits at the
                           end of a given year. ONE PER YEAR. Sprint 3B's, and
                           path-drawdown is its minimum over the window
        worst-year-return  the annual real return itself. ONE PER YEAR. Also
                           Sprint 3B's, and NOT a drawdown -- calling it one is
                           most of why D-08's placement rule reads two ways

    Sprint 3B picks which of the last two D-08 means and owns the argsort
    tie-break D-07 needs. This function decides neither and must not be read as
    doing so.

    COMPUTED ON THE RETURN INDEX, NOT ON AN ACCOUNT BALANCE. The published
    figure is a property of the return MODEL, and a balance carries
    contributions -- which arrive every year, buy at the bottom, and mask the
    decline they are supposed to be measured against. There is no profile in
    this function's arguments and that absence is the point.
    """
    a = np.atleast_2d(np.asarray(paths, dtype=float))
    if a.shape[1] < 1:
        raise ValueError("path_drawdown needs at least one year")
    index = np.cumprod(1.0 + a, axis=1)
    peak = np.maximum.accumulate(index, axis=1)
    return (index / peak - 1.0).min(axis=1)


def draw_return_rate(paths) -> float:
    """The one scalar real return the retirement draw is sized at (D-39's pin).

    THE PROBLEM THIS SOLVES. outcome() never receives a return rate. Its `rate`
    argument is t_later, a TAX rate; the only return information it holds is
    `paths`. But retirement_draw() needs a scalar, and D-39 requires the draw to
    be ONE number held fixed across every path, rung and shock count. D-39's
    subsection named two candidates -- 7% deterministic (D-04a) or the series'
    6.776% geometric mean (D-15) -- and asked Sprint 2B to pick one.

    IT IS BOTH, AND THAT IS WHY THIS IS ONE EXPRESSION RATHER THAN A CHOICE.
    The geometric mean of the array the engine was handed returns the constant
    itself on a constant array -- measured at 5.6e-17 absolute error, which
    leaves the published $108,397 bit-identical -- and returns the series' own
    compounded rate on a bootstrap array. Both candidates fall out of the same
    sentence: the draw is sized at the geometric mean of whatever return model
    it was given.

    NO BRANCH, AND THAT IS THE POINT. Reading paths[0][0], or testing whether
    every element is equal, would reintroduce exactly the flag D-22 deleted when
    it made deterministic mode a SHAPE. The engine still cannot tell which kind
    of array it received.

    OWED TO SPRINT 3: R9's 53.1% ruin measurement was taken with the draw sized
    at the 7% deterministic solve. A bootstrap sized at 6.776% draws less, so
    that figure needs re-measuring before Sprint 3 picks among D-39's four
    options. The direction is favorable -- less ruin, not more -- which is
    precisely why it must be re-measured rather than assumed to still hold.

    Flattened over every path and every year, not per path: D-39 wants one
    number, and a per-path rate is the adaptive draw that PIN 3 forbids.
    """
    flat = np.asarray(paths, dtype=float).ravel()
    if flat.size == 0:
        raise ValueError("paths is empty: no return model to size the draw at")
    return geometric_mean(flat)


def retirement_draw(roth_65: float, n_decumulation_years: int,
                    return_rate: float, margin: float = ROTH_TERMINAL_MARGIN
                    ) -> float:
    """The level real AFTER-TAX draw that leaves ROTH_TERMINAL_MARGIN of
    roth_65 at age 100 (D-39).

    BOTH NAME COLLISIONS ARE RESOLVED HERE, which is what the Sprint 2B tech
    debt line asked for. What the stub called `n_years` is the 35 DECUMULATION
    years, NOT D-20's n_years = 100 - current_age = 65; it is now
    `n_decumulation_years`. What the stub called `rate` is the RETURN rate,
    while `rate` in outcome() is t_later, a TAX rate; it is now `return_rate`.
    Two functions one screen apart took an argument named `rate` and meant
    different quantities.

    Sized off the Roth because it is the smaller account and therefore the
    binding one. Two accounts are being compared as ways to fund the same life,
    so the spending path has to be one both can afford. Size it off Traditional
    and the Roth runs out at 79, and every Roth-side objective then reports
    ruin -- the model would be measuring the spending assumption instead of the
    tax question.

    Sprint 2B gate: returns 108_397 at the archetype.

    SCOPE (D-39): solved once per (profile, rate) on the SHOCK-FREE Roth
    accumulation, then held fixed across every path, rung and shock count.
    A draw that adapted to shocks would shrink spending to whatever the damaged
    balance could afford, and ruin would never fire.

    CLOSED FORM, NOT A SOLVER. Draws land at PERIOD END (D-20), so 35 level
    draws compound as an annuity-immediate:

        roth_65 * (1+r)**n  -  S * [((1+r)**n - 1) / r]  =  margin * roth_65

    which rearranges to the expression below. There is no tolerance argument to
    defend and no iteration count, the same reasoning tax.gross_for_net() uses
    for its own inversion (D-21).

    THE PERIOD-END CONVENTION IS NOT FREE AND THE CROSS-CHECK IS CHEAP. Read as
    an annuity-due -- draw first, then grow -- every draw divides by (1+r) and
    the archetype's answer becomes $101,305 instead of $108,397, -6.5%. That is
    D-20's named misreading, and it is asserted in the tests for the same reason
    the accumulation side asserts $2,256,487: far enough to fail every gate,
    close enough to read as an interpolation bug.
    """
    if n_decumulation_years < 1:
        raise ValueError(
            f"n_decumulation_years must be positive, got {n_decumulation_years}"
        )
    if return_rate <= -1.0:
        raise ValueError(f"return_rate {return_rate} implies total loss or worse")
    growth = (1.0 + return_rate) ** n_decumulation_years
    if return_rate == 0.0:
        annuity = float(n_decumulation_years)   # the limit of the ratio at r -> 0
    else:
        annuity = (growth - 1.0) / return_rate
    return (roth_65 * growth - margin * roth_65) / annuity


# --- The today's-law marker (D-24) -------------------------------------------
# THERE IS NO FUNCTION HERE, AND THAT IS THE DELIVERABLE. marker_withdrawal()
# stood in this spot as a one-line alias for tax.gross_for_net(). Sprint 2B
# deleted it; call tax.gross_for_net(draw) directly. Its reasoning stays here
# rather than moving, because "where does the marker come from" is a question a
# reader asks of engine.py.
#
#   THE MARKER IS  tax.effective_rate(tax.gross_for_net(draw))
#
# Defined this way to break a circularity: the engine decumulates at the flat
# t_later, but D-24's marker is a fact about TODAY's brackets, so its operand
# cannot depend on t_later. It is an EFFECTIVE rate against t*'s MARGINAL rate,
# and the gap between them is the lesson -- you defer at the margin and withdraw
# across the whole structure from zero. The app's axis says so (Sec 7).
#
# Sprint 2B gate: $127,804 gross for the archetype's $108,397 net, a 15.2%
# marker. Both published figures are display roundings of ONE unrounded point --
# gross_for_net(108_397) returns 127,803.95 while the unrounded draw returns
# 127,803.64 -- so they must never be asserted against each other exactly.
#
# CALL SITES. _selftest() below prints it, and tests/test_engine.py asserts it.
# The real consumers arrive later: T5 in Sprint 2C, and the app's second axis
# line in Sprint 6. D-24's "D1 is a marker, not a perturbation" is a claim about
# those consumers -- if the number moves when D1 toggles, something implemented
# a display marker as a model change.


# --- Accumulation cache -------------------------------------------------------
# ACCUMULATION DOES NOT DEPEND ON t_later. That was Sprint 2A's seam, and it is
# the reason this cache is correctness-neutral rather than a risk: breakeven()
# bisects over t_later, so without it every bisection step redoes 2,000 identical
# 30-year accumulation loops. Measured at n_paths = 2000: ~470 ms per outcome()
# call, ~47 s per breakeven(), ~38 minutes for Sprint 4's 48-cell cube against a
# 25-minute budget. With it, the cube reuses 12 accumulations (3 rungs x 4 shock
# counts) and lands under a minute. Vectorizing the decumulation is NOT the win
# and was measured too -- it saves 2 s of 49.
#
# Keyed on the array's CONTENTS, not its id(). D-07 says the array is drawn once
# and reused, so id() would work in practice and silently collide the first time
# it does not. The fingerprint moved OUT to paths_digest() at Sprint 3A, because
# D-41's cube header needs the same expression and it was living in a cache key.
_ACCUMULATION_CACHE: dict = {}
_ACCUMULATION_CACHE_MAX = 8


def _accumulations(profile: Profile, paths, shocks: int) -> tuple:
    """One Accumulation per row of `paths`, cached on (profile, shocks, paths).

    Returns the objects accumulate() returns, unmodified. Callers must treat
    them as read-only -- Accumulation is a plain dataclass, so a caller that
    mutated one would poison every later cache hit.
    """
    key = (profile, shocks, paths.shape, paths_digest(paths))
    hit = _ACCUMULATION_CACHE.get(key)
    if hit is None:
        hit = tuple(accumulate(profile, row, shocks=shocks) for row in paths)
        if len(_ACCUMULATION_CACHE) >= _ACCUMULATION_CACHE_MAX:
            _ACCUMULATION_CACHE.pop(next(iter(_ACCUMULATION_CACHE)))
        _ACCUMULATION_CACHE[key] = hit
    return hit


def _solve_draw(profile: Profile, paths) -> float:
    """D-39's draw for this (profile, paths). ONE number, shock-free, cached.

    Sized on a DETERMINISTIC reference accumulation at draw_return_rate(paths),
    not on the passed paths. Three things fall out of that and all three are
    D-39's requirements rather than conveniences:

      - ONE number. A bootstrap has 2,000 different roth_65 values and D-39 needs
        one; the reference accumulation has exactly one by construction.
      - SHOCK-FREE, trivially -- the reference path never sees a shock, so there
        is no branch to forget. If the draw adapted to shocks, spending would
        shrink to whatever the damaged balance could afford and ruin would never
        fire, which defines away the thing Sprint 4 measures.
      - ACCOUNT-BLIND. It is sized off the Roth whichever account was asked for,
        because the Roth is the smaller and therefore binding account. Size it
        off Traditional and the Roth runs out at 79, and every Roth-side
        objective reports ruin -- the model would be measuring the spending
        assumption instead of the tax question.

    On a constant array the reference IS the passed path to within 1e-16, so the
    deterministic gates reproduce exactly.
    """
    r = draw_return_rate(paths)
    key = (profile, r)
    hit = _DRAW_CACHE.get(key)
    if hit is None:
        reference = make_paths("constant", 1, profile.n_years, r)[0]
        hit = retirement_draw(
            accumulate(profile, reference).roth,
            profile.n_decumulation_years,
            r,
        )
        if len(_DRAW_CACHE) >= _ACCUMULATION_CACHE_MAX:
            _DRAW_CACHE.pop(next(iter(_DRAW_CACHE)))
        _DRAW_CACHE[key] = hit
    return hit


_DRAW_CACHE: dict = {}


# --- Objectives ---------------------------------------------------------------
OBJECTIVES = (1, 3, 4, 5)          # D-06. Two is cut and is not in this tuple.
OBJECTIVE_NAMES = {
    1: "mean after-tax terminal wealth",
    3: "median after-tax terminal wealth",
    4: "10th percentile of after-tax terminal wealth",
    5: "P(not running out)",
}


def _reduce(objective: int, terminals, ruined) -> float:
    """Collapse the paths axis to one float. FOUR reductions, one distribution.

    D-22's argument is that objectives 1, 3, 4 and 5 are all MONOTONE
    functionals of the after-tax terminal distribution, so wherever the two
    accounts' distributions are positive scalar multiples of one another, all
    four cross at the same rate. That is one property asserted, not four
    coincidences measured -- and it is why they all have to point the SAME
    DIRECTION. Objective 5 is therefore P(NOT running out), maximized like the
    other three. D-22's prose names the same functional as `P(< 0)`, which is
    its complement and is what Result.ruin carries.

    At n_paths == 1 objectives 1, 3 and 4 return the identical single value --
    D-22's collapse, which is why the deterministic headline is
    objective-independent by construction. Objective 5 there is a step function
    and will not bisect, so breakeven() rejects it; this function does not,
    because a forward evaluation of it is perfectly well defined.
    """
    if objective == 2:
        raise ValueError(
            "objective 2 (max after-tax lifetime spending) is CUT -- D-39 made "
            "spending a fixed common input, so under D-38 both accounts fund "
            "identical spending and the difference is identically zero at every "
            "t_later. Not small. Zero (D-06)"
        )
    if objective == 1:
        return float(np.mean(terminals))
    if objective == 3:
        return float(np.median(terminals))
    if objective == 4:
        return float(np.percentile(terminals, 10))
    if objective == 5:
        return float(np.mean(~np.asarray(ruined, dtype=bool)))
    raise ValueError(f"unknown objective {objective!r}: expected one of {OBJECTIVES}")


# --- Decumulation -------------------------------------------------------------
def _decumulate(balances, draw: float, decumulation_paths, t_later: float,
                account: str, allowance=None) -> tuple:
    """65 -> 99, vectorized across paths. Returns four arrays.

        (after_tax_at_100, ruined, balance_at_100, allowance_left)

    THE LAST TWO ARE RETURNED SO THE TESTS CAN APPLY D-26's REJECTED READINGS
    WITHOUT THOSE READINGS EXISTING IN THIS FILE. The clamped form is the one a
    careful reader writes first and D-38 forbids it, so it must be demonstrable
    and absent at the same time.

    CASH FLOWS LAND AT PERIOD END (D-20): balance = balance * (1+r) - gross.

    THREE WITHDRAWAL RULES, and Traditional's lack of a fourth is the asymmetry:
      trad                 gross = draw / (1 - t_later). Already ordinary income.
      roth, rules hold     gross = draw. Tax free, no branch.
      roth, under policy   the frozen allowance is spent FIRST and tax free; the
                           remainder is ordinary income, so it grosses up. D-26
                           models this gently -- allowance drawn first rather
                           than pro-rated -- because D-10 already labels the
                           policy as Roth's bet rather than a neutral scenario,
                           and stacking the sub-choices would overstate it.

    NO CLAMPING (D-38), AND THE ONE min() IN HERE IS NOT ONE. `minimum(rem,
    draw)` asks how much of this year's spending the allowance covers; it is a
    selection between two funding sources, and rem cannot go negative under it
    because used <= rem by construction. The clamps D-38 prohibits are a FLOOR
    ON A BALANCE -- which makes the terminal difference non-monotone so T1 passes
    for the wrong reason -- and a max(0, ...) on the BEQUEST, which deletes the
    58.4% crossing outright. Neither appears. Balances go negative and stay
    negative; ruin is recorded, not enforced.

    RUIN IS THE BALANCE'S SIGN, not the after-tax value's (Sprint 2B pin 2). It
    is absorbing without being enforced: below zero, balance * (1+r) - gross is
    strictly more negative every year, so "ever negative" and "negative at 100"
    are the same set. Recording it is not clamping it.
    """
    if account not in ("roth", "trad"):
        raise ValueError(f"account must be 'roth' or 'trad', got {account!r}")
    bal = np.array(balances, dtype=float)
    rem = None if allowance is None else np.array(allowance, dtype=float)
    if account == "trad" and rem is not None:
        raise AssertionError(
            "Traditional takes no policy branch -- its withdrawals were already "
            "ordinary income, and that absence in the code IS the asymmetry (D-26)"
        )
    ruined = np.zeros(bal.shape, dtype=bool)
    for i in range(decumulation_paths.shape[1]):
        if account == "trad":
            gross = draw / (1.0 - t_later)
        elif rem is None:
            gross = draw
        else:
            used = np.minimum(rem, draw)          # funding source, not a floor
            gross = used + (draw - used) / (1.0 - t_later)
            rem = rem - used
        bal = bal * (1.0 + decumulation_paths[:, i]) - gross
        ruined |= bal < 0.0
    if account == "trad":
        after_tax = bal * (1.0 - t_later)
    elif rem is None:
        after_tax = bal.copy()
    else:
        # D-26, THE SIGNED FORM. No min(), no max(). Once the allowance is spent
        # the Roth IS an ordinary-income account, so the terminal value scales by
        # (1 - t_later) whatever its sign -- that is D-38's rule applied to the
        # bequest instead of to the balance, and it is the same rule. Clamp it
        # and the difference never changes sign: 58.4064% stops existing and
        # breakeven() returns a sentinel 200 lines from the cause.
        after_tax = rem + (bal - rem) * (1.0 - t_later)
    return after_tax, ruined, bal, (rem if rem is not None else None)


def _outcome_paths(profile, shocks, policy, paths, rate, account) -> tuple:
    """The per-path work behind outcome(). Returns (after_tax, ruined).

    PRIVATE, AND SPRINT 2C IS ITS SECOND CALLER. Result.ruin is defined per
    account over the same run outcome() reduces, so populating it must not mean
    running the decumulation twice with a different reduction bolted on. This is
    also the seam T2 sweeps the draw through: Sec 5's outcome() signature has no
    `draw` parameter and D-39 says the draw is computed rather than input, so the
    draw-cancellation half of T2 is tested here rather than by widening a
    published signature to accommodate a test.
    """
    paths = np.asarray(paths, dtype=float)
    if paths.ndim != 2:
        raise ValueError(f"paths must be 2-D (n_paths, n_years), got {paths.shape}")
    if paths.shape[1] < profile.n_years:
        raise ValueError(
            f"paths has {paths.shape[1]} years, the run needs {profile.n_years} "
            f"(D-20: accumulate {profile.n_accumulation_years}, decumulate "
            f"{profile.n_decumulation_years})"
        )
    if not 0.0 < rate < 1.0:
        raise ValueError(f"t_later {rate} outside (0, 1): it is a marginal TAX rate")

    draw = _solve_draw(profile, paths)
    accs = _accumulations(profile, paths, shocks)
    balances = [a.roth if account == "roth" else a.trad for a in accs]

    allowance = None
    if policy is not None:
        if account == "roth":
            # Per path: D-26 snapshots YOUR balance at year N, and a shock before
            # then is part of that history. Only Roth -- Traditional is unchanged.
            allowance = [policy_allowance(a, policy) for a in accs]
    decum = paths[:, profile.n_accumulation_years:profile.n_years]
    after_tax, ruined, _, _ = _decumulate(
        balances, draw, decum, rate, account, allowance
    )
    return after_tax, ruined


def outcome(profile, objective, shocks, policy, paths, rate, account) -> float:
    """After-tax value at 100 under one future marginal rate.

    PUBLIC. spike_grid calls it directly for the dollar fields at t* +/- delta
    (D-17) -- do not fold it into breakeven().

    Accumulate 35->64: contribution is min(0.20 * income(age), DEFERRAL_CAP) in
    PRE-TAX terms; Roth receives that scaled by (1 - t_now) (D-01, D-25).
    Decumulate 65->99: both accounts fund the same net draw; Traditional grosses
    up by 1/(1 - t_later).

    Shocks land in the ACCUMULATION phase only, at the `shocks` worst years of
    each path (D-08). WHICH READING OF "WORST" IS SPRINT 3B'S -- D-08's rule
    admits both underwater-depth and worst-year-return and they are different
    year sets on the same path. Neither is path-drawdown, which is one number
    per path and is 3A's (see path_drawdown). Three rung branches, three mechanisms
    (D-16): low sells SHOCK_AMOUNT at that year's price and Traditional takes
    EARLY_WITHDRAWAL_PENALTY while Roth basis comes out free; mid skips the
    contribution year and sells nothing; high does neither. The rung comes from
    profile.stops via rung_from_stops() -- it is not an argument (Section 5).

    Under policy="nevermind", the Roth balance is snapshotted at year N as a
    tax-free allowance in real dollars. It does not grow. Withdrawals draw it
    down first; everything past it is ordinary income at t_later, AND SO IS THE
    BEQUEST AT 100 beyond whatever allowance is left (D-26). That last clause is
    load-bearing: without it the after-tax difference never crosses zero, 58.4%
    does not exist, and this function's caller returns a sentinel where the
    headline should be. Traditional needs no branch at all -- its withdrawals
    were already ordinary income, and THAT ABSENCE IN THE CODE IS THE ASYMMETRY.

    NO CLAMPING (D-38). Balances go negative. Ruin is recorded, not enforced.
    A floor makes the terminal difference non-monotone and T1 passes for the
    wrong reason.

    THIS FUNCTION SOLVES FOR NOTHING. It is a forward evaluation at a GIVEN
    t_later, which is what makes every Sprint 2B gate a scalar you can check
    standing up. Bisection is 2C.

    `objective` reduces the paths axis to one float -- see _reduce() and the
    encoding block in the module docstring. `policy` is None or an int year N.
    `rate` IS t_later, a TAX rate; the RETURN rate is read off `paths` by
    draw_return_rate(). Two arguments named `rate` one screen apart used to mean
    different things, and now only this one does.

    A CONTRACT TENSION WORTH NAMING RATHER THAN TRIPPING OVER. Sprint 4's gate
    table offers a fallback that reads objective 4 as the 10th percentile of the
    after-tax terminal DIFFERENCE. Sec 5's signature cannot produce that: this
    function takes `account` and returns one account's number, so the percentile
    is taken per account and any difference is formed afterwards --
    p10(trad) - p10(roth), which is not p10(trad - roth). The per-account reading
    is what is implemented. If anyone ever takes that fallback it needs a
    signature change, and a fallback that quietly changes the contract is not a
    fallback.
    """
    after_tax, ruined = _outcome_paths(
        profile, shocks, policy, paths, rate, account
    )
    return _reduce(objective, after_tax, ruined)


def _difference(profile, objective, shocks, policy, paths, t_later) -> tuple:
    """(trad - roth, {"roth": f, "trad": f}) at one future marginal rate.

    PRIVATE, AND IT IS THE WHOLE REASON Result.ruin COSTS NOTHING. The objective
    value and the ruin fraction are two reductions of ONE decumulation, so
    populating the field never means running the loop again with a different
    reduction bolted on -- which is what the 2C done-when asks for and what
    _outcome_paths' docstring means by naming this sprint its second caller.

    SIGN CONVENTION: trad - roth, matching _selftest's policy gap and the tests'
    d26_readings(). Positive means Traditional is ahead at this rate.

    `policy` GOES TO BOTH CALLS UNCHANGED, and Traditional's immunity is not
    re-decided here. _outcome_paths builds an allowance only for the Roth, and
    _decumulate refuses one for Traditional outright; asserting it a third time
    in this function would be a third place to keep in step. THAT ABSENCE IS
    D-26's asymmetry, and it stays where the code already carries it.

    NOT A REPLACEMENT FOR outcome(). outcome() is public and spike_grid calls it
    directly for the dollar fields (D-17); this returns a difference and a ruin
    dict, which is a shape only the search wants.
    """
    values, ruin = {}, {}
    for account in ("trad", "roth"):
        after_tax, ruined = _outcome_paths(
            profile, shocks, policy, paths, t_later, account
        )
        values[account] = _reduce(objective, after_tax, ruined)
        ruin[account] = float(np.mean(np.asarray(ruined, dtype=bool)))
    return values["trad"] - values["roth"], ruin


def breakeven(profile, objective, shocks, policy, paths) -> Result:
    """Bisect on the future marginal rate until the two outcomes tie.

    `paths` is passed in, never drawn inside -- that is what makes D-07 hold.
    The quantity of interest is a small difference between two large numbers,
    so the two sides MUST be evaluated on the same draws.

    GUARD BEFORE BISECTING (D-06). Evaluate the difference at both bracket
    endpoints and assert it is non-constant. Two evaluations, one assertion.
    A difference that is identically zero otherwise returns whichever endpoint
    bisection started nearest, SILENTLY -- worse than the no-crossing case,
    which at least has a sentinel. Objective 2 was the only known instance and
    it is cut; nothing else should trip this.

    Objectives 4 and 5 genuinely do not cross inside a plausible range for some
    cells. Return the sentinel; do not raise (T4, R3). At n_paths == 1,
    objective 5 must be REJECTED -- P(ruin) over one path is a step function
    and will not bisect (D-22).

    Archetype, rules hold:      32.5%   (== t_now, exactly)
    Archetype, nevermind @ 20:  58.4%   (RIGHT of t*, not left -- D-40)
    Early-career preset:        12.0% -> 29.1%, and the verdict flips

    THE SEARCH PARAMETERS ARE PINNED IN THE MODULE DOCSTRING, not here, because
    the bracket and the stopping rule were decided nowhere in the corpus and a
    reader looking for them should not have to know which function to open.
    Short form: BRACKET is (0.01, 0.95), the loop runs to float exhaustion, and
    ruin is measured at the rate this Result reports.

    `dollars` IS ALWAYS None OUT OF HERE AND THAT IS THE CONTRACT, not an
    omission (Sec 5, D-17). spike_grid evaluates outcome() at t* +/- delta and
    fills the slot; carrying the slot is what leaves it able to. So null has two
    causes and `status` tells them apart: status != "crosses" is a non-crossing
    cell and stays null forever, while status == "crosses" with a null here is a
    cell spike_grid has not reached yet.

    `ruin` IS POPULATED, AND IT DOES NOT CONFLICT WITH REJECTING OBJECTIVE 5 AT
    ONE PATH. The rejection is about objective 5 as a BISECTION TARGET -- P(not
    running out) over one path is a step function with one step. The FIELD is a
    report, and at n_paths == 1 it is a well-defined 0.0 or 1.0.
    """
    paths = np.asarray(paths, dtype=float)
    # The ndim clause is not belt-and-braces: on a 1-D array shape[0] is the YEAR
    # count, so testing it alone would reject a 65-year path as "one path". A
    # wrongly shaped array falls through to _outcome_paths, which owns that
    # message; duplicating it here would be a second place to keep it in step.
    if objective == 5 and paths.ndim == 2 and paths.shape[0] == 1:
        raise ValueError(
            "objective 5 (P(not running out)) cannot be bisected at n_paths == 1: "
            "over one path it is a step function, not a monotone difference "
            "(D-22). The deterministic headline is objective-independent anyway "
            "-- objectives 1, 3 and 4 collapse there"
        )

    def f(t_later):
        return _difference(profile, objective, shocks, policy, paths, t_later)

    lo, hi = BRACKET
    f_lo, _ = f(lo)
    f_hi, _ = f(hi)

    # GUARD BEFORE BISECTING (D-06). Two evaluations, one assertion. Raising
    # rather than returning a status: Sec 5 is explicit that there is deliberately
    # no status for a degenerate cell, because a difference that never varies is a
    # modeling error and not a result. AssertionError rather than `assert` for the
    # reason _decumulate's policy refusal already uses -- `python -O` deletes the
    # statement and a guard that vanishes under a flag is not a guard.
    if f_lo == f_hi:
        raise AssertionError(
            f"the difference is constant at {f_lo!r} across the whole bracket "
            f"{BRACKET}: bisection has nothing to bracket, and it would return "
            "whichever endpoint it started nearest, SILENTLY (D-06). Objective 2 "
            "was the only known instance and it is cut"
        )

    if (f_lo > 0.0) == (f_hi > 0.0):
        # No crossing in range. Objectives 4 and 5 genuinely do this for some
        # cells and so does T3's profile -- return the sentinel, do not raise
        # (T4, R3). The difference is trad - roth, so negative throughout means
        # Roth wins at every rate in the bracket.
        status = "always_trad" if f_lo > 0.0 else "always_roth"
        _, ruin = f(profile.t_now)
        return Result(breakeven=None, status=status, dollars=None, ruin=ruin)

    # Bisect to float exhaustion. No tolerance argument and no iteration count --
    # the same instinct retirement_draw() and tax.gross_for_net() apply one layer
    # up, arrived at here rather than assumed. An exact zero at the midpoint needs
    # no branch: it compares False against the sign of f_lo, so the interval keeps
    # closing on it from whichever side it is already on.
    while True:
        mid = 0.5 * (lo + hi)
        if mid == lo or mid == hi:
            break
        f_mid, _ = f(mid)
        if (f_mid > 0.0) == (f_lo > 0.0):
            lo, f_lo = mid, f_mid
        else:
            hi = mid

    t_star = 0.5 * (lo + hi)
    # One evaluation at the rate being reported, not a second sweep. _difference
    # returns ruin off the same decumulation it reduces, which is what
    # _outcome_paths' docstring means by naming this sprint its second caller.
    _, ruin = f(t_star)
    return Result(breakeven=t_star, status="crosses", dollars=None, ruin=ruin)


def _selftest():
    """Sprint 2A's published scalars, reachable without pytest.

    Same role return_series._selftest() plays: one command, no test runner, and
    it fails loudly if a paste went wrong.
    """
    paths = make_paths("constant", 1, ARCHETYPE.n_years, 0.07)
    a = accumulate(ARCHETYPE, paths[0])
    e = accumulate(EARLY_CAREER, make_paths("constant", 1, 65, 0.07)[0])
    geo = geometric_mean(return_series.REAL_RETURNS)
    proxy = accumulate(ARCHETYPE, make_paths("constant", 1, 65, geo)[0])
    assert round(a.trad) == 2_108_867, a.trad
    assert round(a.roth) == 1_423_485, a.roth
    assert round(e.trad) == 1_749_149, e.trad
    assert round(e.roth) == 1_539_251, e.roth
    assert round(policy_allowance(a)) == 607_475, policy_allowance(a)
    assert a.roth / a.trad == 1.0 - a.t_now, "D-22 accumulation identity broke"
    assert ARCHETYPE.rung == "mid" and rung_from_stops(()) == "low"
    print(
        f"engine.py 2A OK -- archetype trad {a.trad:,.0f} roth {a.roth:,.0f} "
        f"t_now {a.t_now:.4%} rung {ARCHETYPE.rung} | allowance "
        f"{policy_allowance(a):,.0f} | preset trad {e.trad:,.0f} "
        f"roth {e.roth:,.0f} | D-15 proxy at {geo:.6%} -> T65 {proxy.trad:,.2f}, "
        f"gap {(a.trad - proxy.trad) / a.trad:.4%}"
    )

    # --- Sprint 2B ------------------------------------------------------------
    draw = _solve_draw(ARCHETYPE, paths)
    gross = tax.gross_for_net(draw)          # D-24, and this is the call site
    marker = tax.effective_rate(gross)
    assert round(draw) == 108_397, draw
    assert round(gross) == 127_804, gross
    assert round(marker, 3) == 0.152, marker

    # T1 as a smoke check: at t_later == t_now the two accounts tie.
    at_t_now = [
        outcome(ARCHETYPE, 1, 0, None, paths, ARCHETYPE.t_now, acct)
        for acct in ("trad", "roth")
    ]
    assert abs(at_t_now[0] - at_t_now[1]) <= 16 * np.spacing(a.roth) * 1.07 ** 35

    # D-26's signed terminal rule: the difference changes sign between these two,
    # which is the whole reason the 58.4% headline exists (D-40).
    def _policy_gap(t_later):
        return (outcome(ARCHETYPE, 1, 0, None, paths, t_later, "trad")
                - outcome(ARCHETYPE, 1, 0, POLICY_YEAR, paths, t_later, "roth"))

    assert (_policy_gap(0.50) > 0) != (_policy_gap(0.70) > 0), "D-26 sign change"
    print(
        f"engine.py 2B OK -- draw {draw:,.2f} (annuity-due misreading "
        f"{draw / 1.07:,.0f}) | marker gross {gross:,.2f} at "
        f"{marker:.4%} | tie at t_now {at_t_now[0]:,.2f} vs {at_t_now[1]:,.2f} "
        f"| policy gap {_policy_gap(0.50):+,.0f} at 50% -> "
        f"{_policy_gap(0.70):+,.0f} at 70%"
    )

    # --- Sprint 2C ------------------------------------------------------------
    rules = breakeven(ARCHETYPE, 1, 0, None, paths)
    policy = breakeven(ARCHETYPE, 1, 0, POLICY_YEAR, paths)
    preset_paths = make_paths("constant", 1, EARLY_CAREER.n_years, 0.07)
    preset = breakeven(EARLY_CAREER, 1, 0, None, preset_paths)
    preset_policy = breakeven(EARLY_CAREER, 1, 0, POLICY_YEAR, preset_paths)
    preset_marker = tax.effective_rate(
        tax.gross_for_net(_solve_draw(EARLY_CAREER, preset_paths))
    )
    capped = breakeven(TEST_185K, 1, 0, None, paths)

    assert round(rules.breakeven, 6) == 0.325000, rules.breakeven
    assert round(policy.breakeven, 6) == 0.584064, policy.breakeven
    assert policy.breakeven > rules.breakeven, "D-40: the threshold moves RIGHT"
    assert round(preset.breakeven, 3) == 0.120, preset.breakeven
    assert round(preset_policy.breakeven, 3) == 0.291, preset_policy.breakeven
    assert preset.breakeven < preset_marker < preset_policy.breakeven, "the flip"
    assert capped.status == "always_roth" and capped.breakeven is None
    assert marker < rules.breakeven, "T5, and it is scoped to the base case"
    print(
        f"engine.py 2C OK -- t* {rules.breakeven:.4%} "
        f"({abs(rules.breakeven - a.t_now) / np.spacing(a.t_now):.0f} ulps off "
        f"t_now) -> policy {policy.breakeven:.4%}, RIGHT by "
        f"{policy.breakeven - rules.breakeven:.4%} | T5 marker {marker:.4%} "
        f"< t* | preset {preset.breakeven:.1%} < marker {preset_marker:.1%} "
        f"< {preset_policy.breakeven:.1%} FLIPS | D-42 cell {capped.status}, "
        f"ruin trad {capped.ruin['trad']:.0%} roth {capped.ruin['roth']:.0%} "
        f"| bracket {BRACKET}, dollars {rules.dollars}"
    )

    # --- Sprint 3A ------------------------------------------------------------
    # THE DIGEST IS THE POINT OF PRINTING THIS. D-41 wants the cube reproducible
    # from its header by a reader who has neither this machine nor its lockfile,
    # and MT19937 is frozen so the hex below must match on any numpy. It is the
    # cheapest cross-machine check in the project: one command, one string.
    block = make_paths("block", N_PATHS, ARCHETYPE.n_years)
    accum = block[:, :ARCHETYPE.n_accumulation_years]
    dd = path_drawdown(accum)
    assert block.shape == (N_PATHS, 65), block.shape
    assert set(np.unique(block)) <= set(return_series.REAL_RETURNS), "off-deck"
    assert np.isfinite(draw_return_rate(block)), "the D-39 overflow is back"
    print(
        f"engine.py 3A OK -- block {block.shape} seed {SEED} digest "
        f"{paths_digest(block)} | deck-real rate {draw_return_rate(block):.4%} "
        f"| path-drawdown over {ARCHETYPE.n_accumulation_years}y: median "
        f"{np.median(dd):.1%}, p10 {np.percentile(dd, 10):.1%}"
    )


if __name__ == "__main__":
    _selftest()
