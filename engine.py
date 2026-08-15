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
  T5  the today's-law marker is strictly below t*                 (D-24)

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
"""

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


def accumulate(profile: Profile, path) -> Accumulation:
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

    Shocks do not appear in this function. All three rung mechanisms are defined
    on a contribution stream (D-08, D-16) and they arrive in Sprint 3; High's
    branch -- portfolio untouched -- is already exactly this code.

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
    """
    product = 1.0
    for v in returns:
        product *= (1.0 + v)
    return product ** (1.0 / len(returns)) - 1.0


@dataclass
class Result:
    breakeven: float | None
    status: str            # "crosses" | "always_roth" | "always_trad"
    dollars: dict | None   # keyed by delta: {"2": {"roth": f, "trad": f}, "10": {...}}
    ruin: dict             # {"roth": f, "trad": f}


def make_paths(kind: str, n_paths: int, n_years: int, rate: float = 0.07):
    """Build the (n_paths, n_years) real-return array.

    kind="constant" -> shape (1, n_years) filled with `rate`. This IS the
    deterministic mode (D-22) -- not a flag, a shape. The engine cannot tell
    which kind it received, which is what keeps the headline and the cube from
    ever drifting apart. n_paths is IGNORED here and that is deliberate: at
    n_paths > 1 a constant array holds n identical rows, so objectives 1, 3 and
    4 would collapse onto the same number while costing n times the arithmetic.

    kind="block" -> block bootstrap over return_series.py, BLOCK_LENGTH=5. Bad
    years must arrive in RUNS or the forced-liquidation argument is mechanical
    only.

    P4's gate is CLEARED (D-41, R5): return_series.py holds the real 98-year
    series, STUB is False, and its self-test passes. The runtime guard that
    remains is STUB itself -- this path raises while it is True.
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
        # [SPRINT-3-CLEANUP] The bootstrap itself is Sprint 3's first deliverable
        # (remaining-sprints, Sprint 3). Raising rather than returning a constant
        # array: a silent fallback to determinism would make every stochastic
        # gate in Sprints 3 and 4 pass for the wrong reason.
        raise NotImplementedError(
            "block bootstrap is Sprint 3 -- see remaining-sprints.md"
        )
    raise ValueError(f"unknown kind {kind!r}: expected 'constant' or 'block'")


def retirement_draw(roth_65: float, n_years: int, rate: float) -> float:
    """The level real AFTER-TAX draw that leaves ROTH_TERMINAL_MARGIN of
    roth_65 at age 100 (D-39).

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

    TWO NAME COLLISIONS IN THIS SIGNATURE, both inherited and both worth saying
    out loud before 2B writes the body. `n_years` here is the 35 DECUMULATION
    years, not D-20's n_years = 100 - current_age = 65. And `rate` here is the
    RETURN rate, while `rate` in outcome() is t_later, the future marginal TAX
    rate. Sprint 2B should rename both at the point it implements this.
    """
    raise NotImplementedError   # Sprint 2C


def marker_withdrawal(net_draw: float) -> float:
    """The gross amount today's brackets require to fund `net_draw`.

    Defined this way to break the circularity: the engine decumulates at the
    flat t_later, but D-24's marker is a fact about TODAY's brackets, so its
    operand cannot depend on t_later.

    Sprint 2B gate: 127_804 at the archetype, giving a 15.2% marker.
    DELETE THIS FUNCTION IN 2B -- it is a pure alias for tax.gross_for_net.
    Keep this docstring at the call site. [SPRINT-2-CLEANUP]
    """
    raise NotImplementedError


def outcome(profile, objective, shocks, policy, paths, rate, account) -> float:
    """After-tax value at 100 under one future marginal rate.

    PUBLIC. spike_grid calls it directly for the dollar fields at t* +/- delta
    (D-17) -- do not fold it into breakeven().

    Accumulate 35->64: contribution is min(0.20 * income(age), DEFERRAL_CAP) in
    PRE-TAX terms; Roth receives that scaled by (1 - t_now) (D-01, D-25).
    Decumulate 65->99: both accounts fund the same net draw; Traditional grosses
    up by 1/(1 - t_later).

    Shocks land in the ACCUMULATION phase only, at the `shocks` deepest
    drawdown years of each path (D-08). Three rung branches, three mechanisms
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
    """
    raise NotImplementedError   # Sprint 2B


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
    """
    raise NotImplementedError   # Sprint 2B


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


if __name__ == "__main__":
    _selftest()
