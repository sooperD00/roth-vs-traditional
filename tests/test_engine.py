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
"""

import ast
import math
import pathlib

import pytest

import engine
import return_series

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
