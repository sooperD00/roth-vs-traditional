"""The eight engine tests of DECISIONS section 6, collected across Sprints 2A-4.

No sprint CREATES this file -- Sprint 2A opened it. SPRINT 4 CLOSES BY checking
that eight tests are green and writing the docstring-to-README mapping that is
the panel-facing artifact. (That was Sprint 5 until the P3a docs review folded
it into Sprint 4's tail; the sprint numbers past 4 did not move.) So the tests
arrive here as the sprints that need them are built:

    Sprint 2A  (this pass)  the accumulation gates. NOT numbered T-anything --
                            they defend Sprint 2A's done-when, not section 6
    Sprint 2B               T1, T2
    Sprint 2C               T3, T4, T5
    Sprint 3                T6, T7, T8

THE LITERALS HERE ARE DELIBERATE, same rule tests/test_tax.py states: a
hand-verification that imports the constant it is verifying tests nothing. Every
published figure below is restated from DECISIONS and remaining-sprints rather
than imported from the module under test.

Float note: these balances come out of a 30-step compounding loop, so the
published figures are asserted as ROUNDINGS. Two things are asserted with `==`
and both are deliberate -- D-22's ratio identity, which is exact by construction
and is the cheapest place in the project to catch a broken contribution rule,
and the ladder derivation, which is integer logic.

SPRINT 2B'S ULP BOUNDS ARE A DIFFERENT SHAPE FROM 2A'S, AND THE DIFFERENCE IS
MEASURED RATHER THAN GUESSED. 2A bounded a ratio at 4 ulps of the ratio itself.
T1 cannot be bounded that way: it differences two terminal values after 35 more
years of compounding, and 2A's own 0-to-3 ulp seed mismatch in
roth_65/trad_65 == 1 - t_now is AMPLIFIED by (1+r)**35 -- 52.8x at 12% -- before
the subtraction happens. Measured against the RESULT that reads 1,191 ulps at
12%, which invites a generous round tolerance. Measured against the mechanism it
is small and stays small:

    T1  resid <= K * ulp(roth_65) * (1+r)**35        measured worst K = 5.64
    T2  spread <= K * ulp(peak balance)              measured worst K = 2.75

T2 is the clean one because the draw cancels BEFORE any amplification. That
asymmetry is L1 showing up in the float arithmetic rather than in the algebra.
Both bounds below carry ~3x headroom, and the failures they exist to catch move
the numbers by dollars -- something like 1e9 ulps of these scales.
"""

import ast
import math
import pathlib

import numpy as np
import pytest

import engine
import return_series
import tax

# --- Published, restated by hand ---------------------------------------------
ARCH_TRAD_65 = 2_108_867        # D-15, remaining-sprints Sprint 2A
ARCH_ROTH_65 = 1_423_485
PRESET_TRAD_65 = 1_749_149
PRESET_ROTH_65 = 1_539_251
ALLOWANCE_YEAR_20 = 607_475     # D-26. Balance AFTER the age-54 contribution
ALLOWANCE_AGE_55 = 666_536      # D-26's named misreading. Off by 59,061
ANNUITY_DUE_TRAD_65 = 2_256_487  # D-20's rejected reading. +7.0%
D15_PROXY_T65 = 2_028_066       # D-15, restored in this sprint
D15_PROXY_GAP = 0.0383
INCOME_AT_45 = 126_470.59       # on D-19's 38 -> 55 leg
ARCH_T_NOW = 0.325              # D-19/D-30: 24% federal + 8.5% state
PRESET_T_NOW = 0.12
CAP = 24_500                    # 402(g), restated per the tests/ exemption
RATES = (0.04, 0.07, 0.09, 0.12)  # D-04a's buttons plus 4%, per T2's sweep

# --- Sprint 2B, restated by hand from DECISIONS and remaining-sprints ---------
DRAW = 108_397                  # D-39. Level real after-tax, 54% of final income
DRAW_ANNUITY_DUE = 101_305      # D-20's rejected reading of the draw. -6.5%
MARKER_GROSS = 127_804          # D-24. Gross today's brackets need for the draw
MARKER_RATE = 0.152             # D-24. EFFECTIVE, against t*'s MARGINAL
ROTH_MARGIN = 0.15              # D-39. What the draw leaves at 100
POLICY_N = 20                   # D-09/D-26 default. Year 1 is current_age
T1_ULP_K = 16                   # measured worst 5.64 -- see the module docstring
T2_ULP_K = 8                    # measured worst 2.75
T2_DRAWS = (0.0, 108_397.0, 250_000.0)   # T2's sweep, per section 6
TRAD_RUIN_ABOVE = 0.3345        # D-26. Traditional's terminal turns negative here


def accum(profile, rate=0.07):
    """One deterministic accumulation. The shape IS the deterministic mode."""
    paths = engine.make_paths("constant", 1, profile.n_years, rate)
    return engine.accumulate(profile, paths[0])


# --- income() -----------------------------------------------------------------
@pytest.mark.parametrize(
    "age, expected, why",
    [
        (35, 165_000, "D-19 knot 1 -- what a Staff SWE recognizes"),
        (38, 75_000, "D-19 knot 2 -- the parental-leave trough"),
        (55, 200_000, "D-19 knot 3 -- the peak"),
        (65, 200_000, "D-19 knot 4 -- FLAT from the peak, the conservative case"),
    ],
)
def test_income_returns_the_four_points_exactly(age, expected, why):
    """D-19's four points are the income shape. If one moves, the marker moves."""
    assert engine.ARCHETYPE.income(age) == pytest.approx(expected), why


def test_income_interpolates_linearly_between_knots():
    """Sprint 2A gate: income(45) sits on the 38 -> 55 leg.

    Hand computation, restated rather than imported:
        75,000 + (200,000 - 75,000) * (45 - 38) / (55 - 38)
      = 75,000 + 125,000 * 7 / 17  =  126,470.59
    """
    assert engine.ARCHETYPE.income(45) == pytest.approx(INCOME_AT_45, abs=0.01)


def test_income_is_flat_outside_the_stated_range():
    """The curve is a shape the user draws, not an extrapolation."""
    assert engine.ARCHETYPE.income(30) == pytest.approx(165_000)
    assert engine.ARCHETYPE.income(99) == pytest.approx(200_000)


# --- contributions() ----------------------------------------------------------
def test_contribution_binds_at_the_cap_for_the_archetype():
    """Sprint 2A gate. 20% of $165,000 is $33,000, capped to $24,500.

    The cap binding is the whole reason D-25 exists: at the boundary the two
    choice sets differ and D-01's convention has nothing to equalize.
    """
    trad, _ = engine.contributions(engine.ARCHETYPE, 35)
    assert trad == pytest.approx(CAP)


def test_contribution_binds_at_the_savings_rate_for_the_preset():
    """Sprint 2A gate. 20% of $60,000 is $12,000, under the cap."""
    trad, _ = engine.contributions(engine.EARLY_CAREER, 35)
    assert trad == pytest.approx(12_000)


def test_d2_off_is_the_same_pre_tax_dollars():
    """D-01. $X to Traditional against $X * (1 - t_now) to Roth.

    Comparing them as equal NOMINAL dollars is the G4 trap and quietly favors
    Roth, which is what most calculators do.
    """
    trad, roth = engine.contributions(engine.ARCHETYPE, 35)
    assert roth == pytest.approx(trad * (1 - ARCH_T_NOW))


def test_d2_on_fills_the_roth_to_the_cap_after_tax_when_affordable():
    """D-25/D-42 at the $185,000 test profile. Capacity $37,000 covers the
    $36,296 pre-tax cost, so the Roth reaches the cap in AFTER-TAX dollars and
    the two nominal contributions land equal.

    That equality is D2's asymmetry: the same nominal dollars now cost
    DIFFERENT pre-tax money, which is exactly the convention D-01 forbids in the
    base case and D2 breaks on purpose.
    """
    trad, roth = engine.contributions(engine.TEST_185K, 35)
    assert 0.20 * 185_000 >= CAP / (1 - ARCH_T_NOW)      # 37,000 >= 36,296
    assert roth == pytest.approx(CAP)
    assert trad == pytest.approx(CAP)


def test_d2_on_degrades_rather_than_raising_when_unaffordable():
    """D-42 from the other side, and it is the accordion's D2 copy.

    The archetype's capacity is $33,000 against a $36,296 cost, so the Roth
    cannot reach the cap. It fills to what $33,000 buys after tax -- $22,275 --
    which is still strictly more than the $16,538 the base case puts in. The cap
    is denominated in dollars that cost you more, so it binds before it looks
    like it should.
    """
    unaffordable = engine.Profile(
        income_points=engine.ARCHETYPE.income_points, d2_roth_to_cap=True
    )
    _, roth_d2 = engine.contributions(unaffordable, 35)
    _, roth_base = engine.contributions(engine.ARCHETYPE, 35)
    assert 0.20 * 165_000 < CAP / (1 - ARCH_T_NOW)       # 33,000 < 36,296
    assert roth_d2 == pytest.approx(0.20 * 165_000 * (1 - ARCH_T_NOW))
    assert roth_d2 < CAP
    assert roth_d2 > roth_base


# --- t_now --------------------------------------------------------------------
def test_t_now_is_one_scalar_taken_at_the_current_age_income():
    """Section 5. NOT recomputed per year off that year's income.

    Forced rather than chosen -- the identity test below only exists under this
    reading. A rate that moved with the income curve turns the ratio into a
    weighted average landing on no published number.
    """
    assert engine.ARCHETYPE.t_now == pytest.approx(ARCH_T_NOW)
    assert engine.EARLY_CAREER.t_now == pytest.approx(PRESET_T_NOW)


@pytest.mark.parametrize(
    "gross, true_combined, lookup_combined, why",
    [
        (218_000, 0.325408, 0.405, "D-21 band 3 -- 24/32, and the income a "
                                   "Staff engineer types into the box first"),
        (70_000, 0.230, 0.305, "D-21 band 1 -- 12/22, the widest gap at 10.0 pts"),
    ],
)
def test_t_now_is_a_deferral_rate_at_a_straddling_income(
    gross, true_combined, lookup_combined, why
):
    """D-21, one level up from tax.py -- AND THIS TEST EXISTS BECAUSE THE
    MUTATION BATTERY FOUND ITS ABSENCE.

    Replacing Profile.t_now's deferral_rate with a marginal_rate lookup left the
    whole Sprint 2A suite GREEN. It survives because D-21 already established
    that neither headline profile straddles a band edge, so the two methods
    agree exactly at $165,000 and at $60,000 -- which means every published gate
    in this sprint is blind to the substitution by construction.

    It is not a hypothetical. The app takes gross income as a control, `t*` IS
    `t_now`, and a lookup at $218,000 reports 40.5% against a true 32.5% -- a
    headline wrong by eight points, at an income this panel will type. tax.py's
    tests assert the two methods diverge; nothing asserted which one the ENGINE
    reaches for until now.
    """
    straddler = engine.Profile(
        income_points=((35, gross), (38, gross), (55, gross), (65, gross))
    )
    assert straddler.t_now == pytest.approx(true_combined, abs=1e-6), why
    assert straddler.t_now != pytest.approx(lookup_combined, abs=1e-4)


# --- The four published balances ---------------------------------------------
def test_archetype_balances_at_65():
    """Sprint 2A gate. D-15's unaffected row and the operand for everything 2B
    computes."""
    a = accum(engine.ARCHETYPE)
    assert round(a.trad) == ARCH_TRAD_65
    assert round(a.roth) == ARCH_ROTH_65


def test_early_career_preset_balances_at_65():
    """Sprint 2A gate. D-40's preset -- the artifact that carries the flip."""
    e = accum(engine.EARLY_CAREER)
    assert round(e.trad) == PRESET_TRAD_65
    assert round(e.roth) == PRESET_ROTH_65


def test_cash_flows_land_at_period_end():
    """D-20, and the reason it is a gate rather than a comment.

    The annuity-due reading -- contribute first, then grow -- multiplies every
    balance by exactly (1 + r). Traditional at 65 becomes $2,256,487, +7.0%.
    That is far enough to fail every gate in this sprint and close enough to
    read as an interpolation bug, which is the combination worth a test.
    """
    a = accum(engine.ARCHETYPE)
    assert round(a.trad) == ARCH_TRAD_65
    assert round(a.trad * 1.07) == ANNUITY_DUE_TRAD_65
    assert round(a.trad) != ANNUITY_DUE_TRAD_65


@pytest.mark.parametrize("rate", RATES)
@pytest.mark.parametrize(
    "profile_name", ["ARCHETYPE", "EARLY_CAREER"]
)
def test_the_accumulation_identity_is_exact_at_every_return_rate(profile_name, rate):
    """D-22's accumulation half: roth_65 / trad_65 == 1 - t_now.

    EXACT IN THE ONLY SENSE BINARY ARITHMETIC OFFERS -- within a few ulps of the
    target, measured at 0 to 3 across the eight cases. It is not bit-exact, and
    the done-when's word "exactly" cannot be met literally. The two balances are
    the same weighted sum of the same path with one scaled termwise by a
    constant, so the constant factors out in REAL arithmetic; in floating point
    the two recurrences round at different points, because multiplication does
    not distribute over a rounded addition.

    THE ONE WAY TO GET BIT-EXACTNESS IS THE ONE WAY THAT MUST NOT BE TAKEN.
    Computing roth_by_year as [x * (1 - t_now) for x in trad_by_year] returns
    zero ulps at every rate -- and asserts the identity by construction instead
    of testing it, so a mutant that broke the contribution rule would sail
    through. A four-ulp bound keeps the test honest; the failure it exists to
    catch moves the ratio by 1e-3 or more, which is roughly 1e12 ulps.

    D-22's "assert as an identity, not a tolerance" survives intact -- the bound
    below is a REPRESENTATION tolerance, not a modeling one. Nothing about the
    model is being given room.

    This is also why t_now has to be one scalar. Per-year rates make the ratio a
    weighted average and this test stops being an identity at all.
    """
    profile = getattr(engine, profile_name)
    a = accum(profile, rate)
    target = 1.0 - a.t_now
    assert abs(a.roth / a.trad - target) <= 4 * math.ulp(target)


@pytest.mark.parametrize("rate", RATES)
def test_the_identity_test_has_teeth(rate):
    """Companion to the above: the identity BREAKS where D-22 says it breaks.

    D2 is the second asymmetric mechanism in the model, alongside Low's penalty.
    If the test above passed here too, it would be asserting nothing.
    """
    a = accum(engine.TEST_185K, rate)
    target = 1.0 - a.t_now
    assert abs(a.roth / a.trad - target) > 4 * math.ulp(target)


# --- policy_allowance() -------------------------------------------------------
def test_year_20_allowance_is_the_balance_after_the_age_54_contribution():
    """Sprint 2A gate and D-26's off-by-one.

    Year 1 is age 35, so year 20 is age 54. Reading it as age 55 gives $666,536
    and misses by $59,061 -- large enough to move the policy threshold, small
    enough to look like a plausible number.
    """
    a = accum(engine.ARCHETYPE)
    assert round(engine.policy_allowance(a, 20)) == ALLOWANCE_YEAR_20
    assert round(engine.policy_allowance(a, 21)) == ALLOWANCE_AGE_55


def test_the_allowance_is_smaller_than_the_roth_balance_at_65():
    """D-40's inequality, which is WHY the policy threshold moves right.

    A policy that harms only Roth strictly raises the rate at which Roth becomes
    worthwhile, whenever the frozen allowance is smaller than the balance it was
    frozen out of. It always is, and this asserts it rather than assuming it.
    """
    a = accum(engine.ARCHETYPE)
    assert engine.policy_allowance(a, 20) < a.roth


def test_policy_year_outside_the_accumulation_phase_raises():
    """A snapshot of a balance that does not exist yet is not a small error."""
    a = accum(engine.ARCHETYPE)
    with pytest.raises(ValueError):
        engine.policy_allowance(a, 0)
    with pytest.raises(ValueError):
        engine.policy_allowance(a, 99)


# --- D-15's restored proxy ----------------------------------------------------
def test_d15_proxy_reproduces_at_the_series_own_geometric_mean():
    """D-15, restored in this sprint. $2,028,066 against $2,108,867, a 3.83% gap.

    NOTE WHAT THIS IS. A deterministic run at the series' geometric mean, which
    is what the stale figure always was -- a proxy for the bootstrap, not the
    bootstrap. By Jensen the mean of terminal values need not equal the terminal
    of the mean-compounding path, so Sprint 3 checks this against the real
    distribution and decides what Sprint 6's caption carries.

    The rate is COMPUTED, not typed. The four-decimal literal 0.067762 returns
    $2,028,055.76 and misses the published figure by $10.
    """
    geo = engine.geometric_mean(return_series.REAL_RETURNS)
    proxy = accum(engine.ARCHETYPE, geo)
    seven = accum(engine.ARCHETYPE, 0.07)
    assert round(proxy.trad) == D15_PROXY_T65
    assert (seven.trad - proxy.trad) / seven.trad == pytest.approx(
        D15_PROXY_GAP, abs=5e-5
    )


def test_the_rounded_literal_is_not_the_series_geometric_mean():
    """Guards the note above. If someone later hardcodes 0.067762 this fails."""
    geo = engine.geometric_mean(return_series.REAL_RETURNS)
    assert geo != 0.067762
    assert round(accum(engine.ARCHETYPE, 0.067762).trad) == 2_028_056


# --- make_paths() -------------------------------------------------------------
def test_constant_paths_are_shape_one_by_n_years():
    """D-22: deterministic mode is a SHAPE, not a flag. The engine cannot tell
    which kind it received, which is what keeps the headline and the cube from
    drifting apart."""
    paths = engine.make_paths("constant", 1, 65, 0.07)
    assert paths.shape == (1, 65)
    assert (paths == 0.07).all()


def test_constant_paths_ignore_n_paths():
    """n identical rows would collapse objectives 1, 3 and 4 onto one number
    while costing n times the arithmetic."""
    assert engine.make_paths("constant", 2_000, 65, 0.07).shape == (1, 65)


def test_block_paths_still_raise():
    """Sprint 2A gate. The bootstrap is Sprint 3.

    It RAISES rather than falling back to a constant array: a silent fallback to
    determinism would make every stochastic gate in Sprints 3 and 4 pass for the
    wrong reason.
    """
    with pytest.raises(NotImplementedError):
        engine.make_paths("block", 2_000, 65)


def test_the_stub_flag_is_what_guards_the_block_path():
    """D-41: STUB survives as the flag make_paths("block", ...) raises on, not
    as a description of the file's contents. P4 and R5 are closed."""
    assert return_series.STUB is False


# --- The ladder ---------------------------------------------------------------
@pytest.mark.parametrize(
    "cleared, expected, why",
    [
        (0, "low", "no buffer at all -- a shock forces the sale"),
        (1, "low", "D-33 band 1-3"),
        (3, "low", "top of Low"),
        (4, "mid", "employer match -- D-33 band 4-6, the contributing band"),
        (6, "mid", "20% to 401k, and where D-32's defaults land the archetype"),
        (7, "high", "max IRA -- D-33 band 7-10"),
        (10, "high", "everything cleared"),
    ],
)
def test_rung_bands(cleared, expected, why):
    """D-33's bands, and D10: zero stops cleared reads Low."""
    stops = tuple(i < cleared for i in range(10))
    assert engine.rung_from_stops(stops) == expected, why


def test_the_rung_is_the_highest_CONTIGUOUS_stop():
    """D-37. Assets checked with nothing beneath them is capital parked above a
    gap it should be filling, so it does not count.

    A lone top stop still reads Low, because the shock mechanism depends on what
    is underneath you -- not on what you own.
    """
    lone_top = tuple(i == 9 for i in range(10))
    assert engine.rung_from_stops(lone_top) == "low"
    assert engine.highest_contiguous_stop(lone_top) == 0

    gapped = (True, True, True, True, False, True, True, True, True, True)
    assert engine.highest_contiguous_stop(gapped) == 4
    assert engine.rung_from_stops(gapped) == "mid"


def test_the_archetype_lands_at_mid_contiguously():
    """D-32. The earlier six-gate version skipped stops 1, 7, 8 and 9, which
    broke contiguity at stop 1 and made the archetype unreachable at Mid BY
    CONSTRUCTION."""
    assert engine.ARCHETYPE.stops == tuple(i < 6 for i in range(10))
    assert engine.ARCHETYPE.rung == "mid"
    assert engine.highest_contiguous_stop(engine.ARCHETYPE.stops) == 6


def test_the_ladder_has_ten_stops():
    """D-33/C2. Ten stops, ten checkboxes. The six-checkbox version is deleted."""
    assert len(engine.LADDER_STOPS) == 10
    assert len(engine.DEFAULT_STOPS) == 10


def test_the_cube_sweeps_the_rung_axis_by_replacing_stops():
    """Section 5, and it is why `rung` is not on the published signatures.

    Sprint 4 needs three representative profiles, not a rung argument. If this
    ever fails, someone added a parameter that section 5 does not have.
    """
    for cleared, expected in ((3, "low"), (6, "mid"), (10, "high")):
        stops = tuple(i < cleared for i in range(10))
        p = engine.Profile(
            income_points=engine.ARCHETYPE.income_points, stops=stops
        )
        assert p.rung == expected


# --- Profile guards -----------------------------------------------------------
def test_current_age_at_or_past_retirement_is_rejected():
    """D-20's guard. There is no partial accumulation phase in this model."""
    with pytest.raises(ValueError):
        engine.Profile(income_points=engine.ARCHETYPE.income_points, current_age=65)


def test_the_horizon_is_100_minus_current_age():
    """D-20, and the only place the horizon meets a profile object."""
    assert engine.ARCHETYPE.n_years == 65
    assert engine.ARCHETYPE.n_accumulation_years == 30
    assert engine.ARCHETYPE.n_decumulation_years == 35


def test_a_short_path_is_rejected_rather_than_silently_truncated():
    """A path shorter than the accumulation phase would quietly produce a
    smaller balance that still looks plausible."""
    with pytest.raises(ValueError):
        engine.accumulate(engine.ARCHETYPE, [0.07] * 29)


def test_stops_must_carry_one_boolean_per_ladder_stop():
    with pytest.raises(ValueError):
        engine.Profile(
            income_points=engine.ARCHETYPE.income_points, stops=(True, False)
        )


# =============================================================================
# SPRINT 2B -- the draw, decumulation, outcome(), the objective reduction
# =============================================================================
def decum_slice(profile, rate=0.07):
    """(paths, decumulation columns) for one deterministic run."""
    paths = engine.make_paths("constant", 1, profile.n_years, rate)
    return paths, paths[:, profile.n_accumulation_years:profile.n_years]


# --- retirement_draw() --------------------------------------------------------
def test_the_draw_leaves_exactly_the_margin_at_100():
    """Sprint 2B gate. $108,397 at the archetype, and the residual is the point.

    D-39 defines the draw as the level real after-tax amount that leaves 15% of
    the ROTH's age-65 balance at 100 -- sized off the Roth because it is the
    smaller and therefore binding account. This asserts the definition, not just
    the published number: run the balance forward and it lands on the margin.
    """
    a = accum(engine.ARCHETYPE)
    draw = engine.retirement_draw(a.roth, 35, 0.07)
    assert round(draw) == DRAW

    balance = a.roth
    for _ in range(35):
        balance = balance * 1.07 - draw
    assert balance == pytest.approx(ROTH_MARGIN * a.roth, rel=1e-12)


def test_the_draw_rejects_the_annuity_due_reading():
    """D-20 from the decumulation side, and it is the same gate the accumulation
    side already has at $2,256,487.

    Draw first then grow divides every draw by (1+r): $101,305 instead of
    $108,397, -6.5%. Far enough to fail every published gate in this sprint,
    close enough to read as an interpolation bug.
    """
    a = accum(engine.ARCHETYPE)
    draw = engine.retirement_draw(a.roth, 35, 0.07)
    assert round(draw / 1.07) == DRAW_ANNUITY_DUE
    assert round(draw) != DRAW_ANNUITY_DUE


def test_the_draw_is_a_closed_form_not_a_search():
    """D-39's done-when. No tolerance argument, no iteration count.

    Asserted as the algebra rather than as a promise: the closed form and a
    brute-force bisection on the same definition agree to floating point, so the
    solver that is not there would have found the same answer.
    """
    a = accum(engine.ARCHETYPE)
    closed = engine.retirement_draw(a.roth, 35, 0.07)

    lo, hi = 0.0, 10 * a.roth
    for _ in range(200):
        mid = (lo + hi) / 2
        b = a.roth
        for _ in range(35):
            b = b * 1.07 - mid
        if b > ROTH_MARGIN * a.roth:
            lo = mid
        else:
            hi = mid
    assert closed == pytest.approx((lo + hi) / 2, rel=1e-9)


# --- draw_return_rate() -- D-39's pin -----------------------------------------
@pytest.mark.parametrize("rate", RATES)
def test_the_draw_rate_is_the_constant_on_a_constant_array(rate):
    """Sprint 2B's pin on D-39. The engine has no return-rate argument -- its
    `rate` is t_later -- so the draw's rate is read off `paths`.

    D-39 named two candidates and asked 2B to pick. The geometric mean of the
    array IS both: it returns the constant on a constant array and the series'
    own compounded rate on a bootstrap. That is why there is no branch, and why
    D-22's "the engine cannot tell which kind it received" survives literally.
    """
    paths = engine.make_paths("constant", 1, 65, rate)
    assert engine.draw_return_rate(paths) == pytest.approx(rate, abs=1e-15)


def test_the_draw_is_identical_for_both_accounts():
    """Sprint 2B's draw-scope gate. D-39's PIN, consequence 1.

    outcome() runs the Roth sizing regardless of which account was asked for.
    Size the draw off Traditional instead and the Roth runs out at 79 -- every
    Roth-side objective then reports ruin, and the model measures the spending
    assumption instead of the tax question.

    (The across-SHOCKS half of this assertion is Sprint 3's. With no mechanism
    built, `shocks` changes nothing here and the assertion would pass because
    nothing happens -- the same shape as the unanchored streamlit grep 2A fixed.)
    """
    paths, _ = decum_slice(engine.ARCHETYPE)
    draw = engine._solve_draw(engine.ARCHETYPE, paths)
    for account in ("roth", "trad"):
        got = engine._solve_draw(engine.ARCHETYPE, paths)
        assert got == draw, account
    assert round(draw) == DRAW


# --- The D-24 marker ----------------------------------------------------------
def test_the_marker_is_the_gross_todays_brackets_need_for_the_draw():
    """Sprint 2B gate: $127,804 gross, a 15.2% EFFECTIVE marker.

    Non-circular by construction (D-24). The engine decumulates at the flat
    t_later, but the marker is a fact about TODAY's brackets, so its operand
    cannot depend on t_later -- it is computed on D-39's net draw instead.
    """
    paths, _ = decum_slice(engine.ARCHETYPE)
    draw = engine._solve_draw(engine.ARCHETYPE, paths)
    gross = tax.gross_for_net(draw)
    assert round(gross) == MARKER_GROSS
    assert round(tax.effective_rate(gross), 3) == MARKER_RATE


def test_the_marker_figures_are_roundings_of_one_point_not_of_each_other():
    """D-24's explicit warning, as a test rather than as a sentence.

    $127,804 and $108,397 are two display roundings of ONE unrounded point. Feed
    the rounded draw and you get 127,803.95; feed the engine's unrounded draw and
    you get 127,803.64. Both round to the published figure and neither equals it,
    which is exactly why they must not be asserted against each other.
    """
    paths, _ = decum_slice(engine.ARCHETYPE)
    exact = tax.gross_for_net(engine._solve_draw(engine.ARCHETYPE, paths))
    rounded = tax.gross_for_net(DRAW)
    assert round(exact) == round(rounded) == MARKER_GROSS
    assert exact != rounded
    assert exact != MARKER_GROSS and rounded != MARKER_GROSS


def test_marker_withdrawal_is_deleted_from_the_engine():
    """Sprint 2B's cleanup. It was a pure alias for tax.gross_for_net.

    Asserted as an absence because the tag that tracked it is also deleted, and
    an alias is the kind of thing that grows back.
    """
    assert not hasattr(engine, "marker_withdrawal")


# --- T1 -----------------------------------------------------------------------
@pytest.mark.parametrize("rate", RATES)
@pytest.mark.parametrize("profile_name", ["ARCHETYPE", "EARLY_CAREER"])
def test_T1_equal_rates_at_both_ends_produce_equal_outcomes(profile_name, rate):
    """T1 (section 6). The identity is real.

    At t_later == t_now the two after-tax terminal values tie, under D-01's
    same-pre-tax-dollars convention and for ANY return rate. The difference is
    roth_65 * [(1 - t_later)/(1 - t_now) - 1] * (1+r)**35, which is identically
    zero there.

    THE BOUND IS MEASURED AND ITS SHAPE IS THE FINDING. 2A's 4-ulp bound does not
    transfer: this differences two terminals after 35 more years of compounding,
    and 2A's own 0-to-3 ulp seed mismatch is amplified by (1+r)**35 first. Bound
    it against the mechanism -- one ulp of roth_65 carried forward 35 years --
    and the worst case over these eight pairs is K = 5.64. Bound it against the
    RESULT and the same arithmetic reads 1,191 ulps, which is the number that
    would have talked someone into a round tolerance.
    """
    profile = getattr(engine, profile_name)
    a = accum(profile, rate)
    paths, _ = decum_slice(profile, rate)
    trad = engine.outcome(profile, 1, 0, None, paths, profile.t_now, "trad")
    roth = engine.outcome(profile, 1, 0, None, paths, profile.t_now, "roth")
    scale = math.ulp(a.roth) * (1.0 + rate) ** profile.n_decumulation_years
    assert abs(trad - roth) <= T1_ULP_K * scale


def test_T1_has_teeth_away_from_t_now():
    """Companion to T1. If the tie held everywhere it would assert nothing.

    One point either side of t_now, and the sign flips -- which is also the
    statement that t* is a crossing rather than a flat region (D-06's guard).
    """
    paths, _ = decum_slice(engine.ARCHETYPE)
    t_now = engine.ARCHETYPE.t_now
    gaps = []
    for t_later in (t_now - 0.10, t_now + 0.10):
        gaps.append(
            engine.outcome(engine.ARCHETYPE, 1, 0, None, paths, t_later, "trad")
            - engine.outcome(engine.ARCHETYPE, 1, 0, None, paths, t_later, "roth")
        )
    assert gaps[0] > 0 > gaps[1]


# --- T2 -----------------------------------------------------------------------
@pytest.mark.parametrize("rate", RATES)
def test_T2_the_common_draw_cancels_out_of_the_difference(rate):
    """T2's draw-cancellation half (section 6). L1.

    Both accounts fund the same net spending, so the draw subtracts the same real
    amount from both after-tax paths and vanishes from their DIFFERENCE. Twelve
    (rate, draw) pairs; the t*-across-r half needs bisection and is 2C's.

    DO NOT ASSERT THE EARLIER WORDING. "The after-tax Traditional path equals the
    Roth path scaled by (1 - t_later) at every year" is FALSE through
    decumulation once t_later != t_now -- the ratio runs 1.12 -> 1.43 -> 8.91
    across ages 66, 82 and 99. The claim is on the difference, and that is the
    stronger one: it holds for any r and any draw, not for four sampled rates.

    WHY THIS CALLS _decumulate() AND NOT outcome(). Section 5's outcome() has no
    `draw` parameter and D-39 says the draw is computed rather than input, so
    there is no way to reach draw = 0 or $250,000 through the published
    signature. Widening a contract to admit a test is the wrong trade; the test
    goes one layer down instead.
    """
    a = accum(engine.ARCHETYPE, rate)
    _, decum = decum_slice(engine.ARCHETYPE, rate)
    t_later = 0.40
    diffs = []
    for draw in T2_DRAWS:
        trad, _, _, _ = engine._decumulate([a.trad], draw, decum, t_later, "trad")
        roth, _, _, _ = engine._decumulate([a.roth], draw, decum, t_later, "roth")
        diffs.append(float(trad[0]) - float(roth[0]))
    scale = math.ulp(max(a.trad, a.roth) * (1.0 + rate) ** 35)
    assert max(diffs) - min(diffs) <= T2_ULP_K * scale


@pytest.mark.parametrize("rate", RATES)
def test_T2_matches_the_closed_form_difference(rate):
    """The algebra behind T2, asserted rather than trusted.

    roth_65 * [(1 - t_later)/(1 - t_now) - 1] * (1+r)**35. If this drifts, the
    draw stopped cancelling and the reason T2 passes is no longer the reason
    T2 exists.
    """
    a = accum(engine.ARCHETYPE, rate)
    _, decum = decum_slice(engine.ARCHETYPE, rate)
    t_later = 0.40
    trad, _, _, _ = engine._decumulate([a.trad], DRAW, decum, t_later, "trad")
    roth, _, _, _ = engine._decumulate([a.roth], DRAW, decum, t_later, "roth")
    predicted = a.roth * ((1 - t_later) / (1 - a.t_now) - 1) * (1 + rate) ** 35
    assert float(trad[0]) - float(roth[0]) == pytest.approx(predicted, rel=1e-12)


# --- The objective reduction --------------------------------------------------
def test_objectives_1_3_and_4_collapse_at_one_path():
    """D-22's collapse, stated as a fact everywhere and asserted nowhere until
    now. It is why the deterministic headline is objective-independent BY
    CONSTRUCTION rather than by coincidence.

    Objective 5 is excluded deliberately: P(not running out) over one path is a
    step function that will not bisect, so 2C rejects it there (D-22). A forward
    evaluation of it is still well defined, which is why outcome() does not raise.
    """
    paths, _ = decum_slice(engine.ARCHETYPE)
    values = {
        objective: engine.outcome(
            engine.ARCHETYPE, objective, 0, None, paths, 0.40, "trad"
        )
        for objective in (1, 3, 4)
    }
    assert len(set(values.values())) == 1, values


def test_objective_5_is_the_complement_of_ruin():
    """Section 5 defines Result.ruin as the fraction that went negative; CONTEXT
    part C defines objective 5 as P(NOT running out).

    They are complements, and every objective has to point the same direction or
    breakeven() has no monotone difference to bracket. D-22's prose names the
    same functional as `P(< 0)`.
    """
    paths, _ = decum_slice(engine.ARCHETYPE)
    for t_later, expected in ((0.20, 1.0), (0.90, 0.0)):
        survived = engine.outcome(
            engine.ARCHETYPE, 5, 0, None, paths, t_later, "trad"
        )
        _, ruined = engine._outcome_paths(
            engine.ARCHETYPE, 0, None, paths, t_later, "trad"
        )
        assert survived == expected
        assert survived == pytest.approx(1.0 - float(np.mean(ruined)))


def test_objective_2_is_rejected_rather_than_computed():
    """D-06. Under a common draw and D-38 both accounts fund identical spending,
    so the difference is identically zero at every t_later -- not small, zero.

    Rejecting it in the reduction rather than only in breakeven()'s guard: a
    degenerate objective that returns a plausible float is worse than one that
    raises, because bisection would return whichever endpoint it started nearest,
    silently.
    """
    paths, _ = decum_slice(engine.ARCHETYPE)
    with pytest.raises(ValueError, match="CUT"):
        engine.outcome(engine.ARCHETYPE, 2, 0, None, paths, 0.40, "trad")


def test_an_unknown_objective_is_rejected():
    paths, _ = decum_slice(engine.ARCHETYPE)
    with pytest.raises(ValueError):
        engine.outcome(engine.ARCHETYPE, 6, 0, None, paths, 0.40, "trad")


# --- D-26's terminal rule -----------------------------------------------------
def d26_readings(t_later):
    """The three readings of D-26's terminal rule, at one t_later.

    The two REJECTED readings are constructed here rather than in engine.py, and
    that is the whole design: the clamped form is the one a careful reader writes
    first, so it has to be demonstrable and absent at the same time. _decumulate
    returns the raw balance and the leftover allowance so this is possible
    without a second decumulation loop living in the test file.
    """
    a = accum(engine.ARCHETYPE)
    paths, decum = decum_slice(engine.ARCHETYPE)
    draw = engine._solve_draw(engine.ARCHETYPE, paths)
    allowance = [engine.policy_allowance(a, POLICY_N)]
    signed, _, balance, left = engine._decumulate(
        [a.roth], draw, decum, t_later, "roth", allowance
    )
    trad, _, _, _ = engine._decumulate([a.trad], draw, decum, t_later, "trad")
    B, rem, T = float(balance[0]), float(left[0]), float(trad[0])
    return {
        "untaxed": T - B,
        "clamped": T - (min(B, rem) + max(0.0, B - rem) * (1 - t_later)),
        "signed": T - float(signed[0]),
    }


@pytest.mark.parametrize(
    "reading, crosses, why",
    [
        ("untaxed", False, "leave the bequest untaxed and the difference never "
                           "changes sign -- 58.4% does not exist"),
        ("clamped", False, "max(0, ...) is a clamp wearing tax logic. It stops "
                           "Roth's negative bequest being scaled while "
                           "Traditional's still is, so the two are taxed "
                           "asymmetrically in the direction of the arithmetic"),
        ("signed", True, "D-38's rule applied to the bequest instead of to the "
                         "balance. Once the allowance is spent the Roth IS an "
                         "ordinary-income account"),
    ],
)
def test_the_d26_terminal_rule_reproduces_all_three_readings(reading, crosses, why):
    """Sprint 2B gate, and it is why the policy branch is built here rather than
    beside the bisection that consumes it.

    A forward sweep, no bisection. Only the signed form changes sign, and it does
    so between t_later = 0.50 and 0.70. Under either other reading 2C's
    breakeven() returns a sentinel where the headline belongs, 200 lines from the
    cause.
    """
    grid = [0.01 + i * (0.94 / 40) for i in range(41)]
    signs = {d26_readings(t)[reading] > 0 for t in grid}
    assert (len(signs) > 1) is crosses, why
    if crosses:
        lo, hi = d26_readings(0.50)[reading], d26_readings(0.70)[reading]
        assert (lo > 0) != (hi > 0)


def test_the_policy_allowance_is_roth_only():
    """D-26/D-09. Traditional needs no branch -- its withdrawals were already
    ordinary income, and THAT ABSENCE IN THE CODE IS THE ASYMMETRY.

    The deck said "all tax benefits go away"; making it symmetric would delete
    the thing D-26 depends on. Asserted as a refusal so a future symmetric
    implementation fails loudly rather than quietly halving the effect.
    """
    a = accum(engine.ARCHETYPE)
    paths, decum = decum_slice(engine.ARCHETYPE)
    with pytest.raises(AssertionError, match="asymmetry"):
        engine._decumulate([a.trad], DRAW, decum, 0.40, "trad", [1_000.0])

    untouched = engine.outcome(engine.ARCHETYPE, 1, 0, None, paths, 0.40, "trad")
    policied = engine.outcome(
        engine.ARCHETYPE, 1, 0, POLICY_N, paths, 0.40, "trad"
    )
    assert untouched == policied


def test_the_policy_crossing_brackets_the_published_58_4_percent():
    """D-26/D-40's headline, as the forward half only. 2C's bisection makes it a
    number; two evaluations either side make it a fact.

    THIS EXISTS BECAUSE THE MUTATION BATTERY FOUND ITS ABSENCE. 2A asserts
    policy_allowance(a, 20) directly, so D-26's off-by-one is covered at the
    accumulation layer -- but nothing checked which N outcome() passes THROUGH.
    Feeding year 21 instead of 20 hands the decumulation $666,536 rather than
    $607,475, an error of $59,061, and every 2B test still passed. The allowance
    is only visible downstream in where this crossing lands.

    AND THE CROSSING SITS INSIDE THE RUINED REGION, which is worth knowing before
    a panelist finds it: Traditional's terminal has been negative since 33.45%,
    so at 58.4% both accounts are about -$5.62M. That is legitimate under D-38 --
    ruin is recorded, not enforced, so the arithmetic runs and the difference
    stays monotone. It is precisely what makes the number computable.

    ROUTED THROUGH outcome(), DELIBERATELY. d26_readings() below builds the
    allowance by hand, because it has to construct two readings that do not exist
    in engine.py -- which means it never touches the line that decides WHICH YEAR
    gets snapshotted. The first version of this test used it and the off-by-one
    mutant walked straight through. A test of a value that the test itself
    supplies is not a test of the value.
    """
    paths, _ = decum_slice(engine.ARCHETYPE)

    def gap(t_later):
        return (
            engine.outcome(engine.ARCHETYPE, 1, 0, None, paths, t_later, "trad")
            - engine.outcome(
                engine.ARCHETYPE, 1, 0, POLICY_N, paths, t_later, "roth"
            )
        )

    lo, hi = gap(0.5840), gap(0.5850)
    assert (lo > 0) != (hi > 0), (lo, hi)


def test_the_reduction_distinguishes_the_tail_from_the_middle():
    """The paths axis has to be exercised with paths that DIFFER.

    FOUND BY THE MUTATION BATTERY. Every other test in this sprint runs at
    n_paths = 1, where mean, median, p10 and p90 are the same number by
    definition -- so swapping objective 4's percentile from 10 to 90 left the
    whole suite green. That is D-22's collapse working exactly as designed and
    hiding a defect inside itself.

    The array is hand-built rather than from make_paths(): the bootstrap is
    Sprint 3, and the reduction layer does not need one. outcome() takes `paths`
    and cannot tell where they came from, which is the same property D-22 relies
    on.
    """
    rates = [0.01 * i for i in range(2, 12)]        # 2% .. 11%, ten paths
    paths = np.array([np.full(65, r) for r in rates])
    args = (engine.ARCHETYPE, 0, None, paths, 0.40, "trad")
    terminals, _ = engine._outcome_paths(*args)

    p10 = engine.outcome(engine.ARCHETYPE, 4, 0, None, paths, 0.40, "trad")
    median = engine.outcome(engine.ARCHETYPE, 3, 0, None, paths, 0.40, "trad")
    mean = engine.outcome(engine.ARCHETYPE, 1, 0, None, paths, 0.40, "trad")

    assert p10 < median < mean, "terminal wealth is convex in r, so mean > median"
    assert p10 < float(np.percentile(terminals, 90))
    assert len(set([p10, median, mean])) == 3


def test_decumulation_reads_the_decumulation_years():
    """Which columns of `paths` the second phase consumes.

    FOUND BY THE MUTATION BATTERY. A constant array has identical columns, so
    slicing paths[:, 0:35] instead of paths[:, 30:65] is invisible to every other
    test in this sprint and would stay invisible until Sprint 3's bootstrap made
    the columns differ -- at which point it reads as a bootstrap bug rather than
    as a slice bug.

    Two rates in one path: 7% while accumulating, 2% while decumulating. The
    age-65 balance must still be D-19's published figure, which pins the split at
    30 years, and the terminal must come out of a 2% run.
    """
    profile = engine.ARCHETYPE
    path = np.concatenate([
        np.full(profile.n_accumulation_years, 0.07),
        np.full(profile.n_decumulation_years, 0.02),
    ])
    paths = path.reshape(1, -1)

    a = engine.accumulate(profile, path)
    assert round(a.roth) == ARCH_ROTH_65, "the split is not at 30 years"

    draw = engine._solve_draw(profile, paths)
    balance = a.roth
    for _ in range(profile.n_decumulation_years):
        balance = balance * 1.02 - draw
    got = engine.outcome(profile, 1, 0, None, paths, 0.40, "roth")
    assert got == pytest.approx(balance, rel=1e-12)


def test_the_draw_rate_is_geometric_not_arithmetic():
    """D-15's lesson pointed at a new function.

    FOUND BY THE MUTATION BATTERY. On a constant array the arithmetic and
    geometric means are the same number, so every deterministic gate is blind to
    the substitution -- which is exactly how 6.81% survived in D-15: a rate
    computed the wrong way, agreeing with the right way everywhere anyone looked.

    On the real series the two differ by 1.83 points, and that gap is variance
    drag rather than rounding: it matches sigma-squared-over-two at the series'
    19.30% standard deviation. Sizing a 35-year draw at the arithmetic mean would
    fund a retirement the portfolio does not compound fast enough to pay for.
    """
    series = np.asarray(return_series.REAL_RETURNS, dtype=float).reshape(1, -1)
    geometric = engine.draw_return_rate(series)
    arithmetic = float(np.mean(series))
    assert geometric == pytest.approx(
        engine.geometric_mean(return_series.REAL_RETURNS), rel=1e-15
    )
    assert arithmetic - geometric == pytest.approx(0.0183, abs=5e-4)
    variance_drag = float(np.var(series)) / 2.0
    assert arithmetic - geometric == pytest.approx(variance_drag, abs=2e-3)


# --- Ruin ---------------------------------------------------------------------
def test_ruin_is_recorded_and_the_balance_keeps_running():
    """D-38. Ruin is a flag, not an absorbing floor.

    Traditional's terminal turns negative above 33.45% (D-26), just above
    t* = 32.5%. Below it nothing is ruined; above it the flag fires AND the
    arithmetic continues, which is what keeps the difference monotone and makes
    58.4% computable at all.
    """
    paths, _ = decum_slice(engine.ARCHETYPE)
    below, _ = engine._outcome_paths(
        engine.ARCHETYPE, 0, None, paths, TRAD_RUIN_ABOVE - 0.01, "trad"
    )
    above, ruined = engine._outcome_paths(
        engine.ARCHETYPE, 0, None, paths, TRAD_RUIN_ABOVE + 0.01, "trad"
    )
    assert float(below[0]) > 0
    assert bool(ruined[0]) is True
    assert float(above[0]) < 0, "the balance kept running past zero"


# --- D-38 as a structural rule ------------------------------------------------
def test_the_engine_never_clamps_a_balance_at_zero():
    """D-38, asserted over the SYNTAX TREE rather than by grepping for text.

    This is 2A's streamlit lesson one layer up. A grep for `max(0` matches the
    module docstring's own list of what must not appear in the file, so a gate
    that fires on the sentence prohibiting the thing is not a gate. Walking the
    AST for a call to a clamping builtin with a literal zero argument cannot see
    prose at all.

    It does NOT fire on _decumulate's np.minimum(rem, draw): that has no zero
    literal because it is a selection between two funding sources, not a floor.
    It does not look at tax.py either -- taxable()'s max(0.0, ...) is the model
    being correct, since negative taxable income is not a thing the code has, and
    D-38 is about balances in the decumulation loop.
    """
    tree = ast.parse(pathlib.Path(engine.__file__).read_text(encoding="utf-8"))
    clampers = {"min", "max", "minimum", "maximum", "clip", "fmin", "fmax"}
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if name not in clampers:
            continue
        if any(
            isinstance(arg, ast.Constant) and arg.value in (0, 0.0)
            for arg in node.args
        ):
            offenders.append(f"{name}(...) at line {node.lineno}")
    assert not offenders, offenders


# --- accumulate()'s new parameter ---------------------------------------------
def test_accumulate_gained_a_defaulted_shocks_parameter():
    """Sprint 2B's PIN. Sprint 3 fills a branch instead of moving a seam.

    Defaulted so 2A's 54 tests pass untouched, which is the whole point -- the
    two routes it replaces were changing a published signature underneath them,
    or duplicating the accumulation loop inside outcome().
    """
    a = accum(engine.ARCHETYPE)
    paths, _ = decum_slice(engine.ARCHETYPE)
    explicit = engine.accumulate(engine.ARCHETYPE, paths[0], shocks=0)
    assert explicit.trad == a.trad and explicit.roth == a.roth


def test_a_nonzero_shock_count_raises_rather_than_returning_the_zero_shock_answer():
    """The same refusal make_paths("block", ...) already makes.

    A silent fallback would make every shocked gate in Sprints 3 and 4 pass for
    the wrong reason: the 12 informative cells of the cube would report the 36
    uninformative ones' answer (D-22).
    """
    paths, _ = decum_slice(engine.ARCHETYPE)
    with pytest.raises(NotImplementedError, match="Sprint 3"):
        engine.accumulate(engine.ARCHETYPE, paths[0], shocks=1)
    with pytest.raises(NotImplementedError):
        engine.outcome(engine.ARCHETYPE, 1, 2, None, paths, 0.40, "trad")


# --- Guards on outcome() ------------------------------------------------------
def test_outcome_rejects_an_unknown_account():
    paths, _ = decum_slice(engine.ARCHETYPE)
    with pytest.raises(ValueError, match="account"):
        engine.outcome(engine.ARCHETYPE, 1, 0, None, paths, 0.40, "brokerage")


def test_outcome_rejects_a_t_later_outside_the_unit_interval():
    """`rate` here is a marginal TAX rate, not the return rate the same word
    names in retirement_draw(). Both collisions were resolved this sprint; this
    guard is what makes a leftover call site fail loudly instead of compounding
    a 7% tax rate for 35 years."""
    paths, _ = decum_slice(engine.ARCHETYPE)
    for bad in (0.0, 1.0, 1.07, -0.2):
        with pytest.raises(ValueError, match="t_later"):
            engine.outcome(engine.ARCHETYPE, 1, 0, None, paths, bad, "trad")


def test_a_path_array_too_short_for_decumulation_is_rejected():
    """A path long enough to accumulate but not to decumulate would silently
    evaluate the bequest early."""
    short = engine.make_paths("constant", 1, 40, 0.07)
    with pytest.raises(ValueError, match="years"):
        engine.outcome(engine.ARCHETYPE, 1, 0, None, short, 0.40, "trad")


# --- D-11's rule --------------------------------------------------------------
def test_engine_imports_no_streamlit():
    """D-11. Asserted as an IMPORT rather than as a grep for the word.

    The unanchored `grep -c streamlit engine.py` returns 1 -- it matches the
    module docstring's own list of what must not appear in the file. A gate that
    fires on the sentence prohibiting the thing is not a gate.
    """
    tree = ast.parse(pathlib.Path(engine.__file__).read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert "streamlit" not in imported, sorted(imported)
