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

from dataclasses import dataclass

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
    ever drifting apart.

    kind="block" -> block bootstrap over return_series.py, BLOCK_LENGTH=5. Bad
    years must arrive in RUNS or the forced-liquidation argument is mechanical
    only.

    P4's gate is CLEARED (D-41, R5): return_series.py holds the real 98-year
    series, STUB is False, and its self-test passes. The runtime guard that
    remains is STUB itself -- this path raises while it is True.
    """
    raise NotImplementedError


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
    """
    raise NotImplementedError


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
    contribution year and sells nothing; high does neither.

    Under policy="nevermind", the Roth balance is snapshotted at year N as a
    tax-free allowance in real dollars. It does not grow. Withdrawals draw it
    down first; everything past it is ordinary income at t_later. Traditional
    needs no branch at all -- its withdrawals were already ordinary income, and
    THAT ABSENCE IN THE CODE IS THE ASYMMETRY (D-26).

    NO CLAMPING (D-38). Balances go negative. Ruin is recorded, not enforced.
    A floor makes the terminal difference non-monotone and T1 passes for the
    wrong reason.
    """
    raise NotImplementedError


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
    raise NotImplementedError
