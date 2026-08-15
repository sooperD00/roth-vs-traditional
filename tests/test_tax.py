"""Sprint 1's assertions. Each defends a number published in DECISIONS.md.

These are NOT among the eight engine tests in DECISIONS section 6 -- those live
in test_engine.py and are collected at the tail of Sprint 4. DoD item 5 covers
this file.

THE LITERALS HERE ARE DELIBERATE. D-21's rule is that no tax number appears
anywhere else in the repo, and tests/ is its one exemption: a hand-verification
that imports the constant it is verifying tests nothing. Every number below was
computed by hand from the published 2026 single-filer table and is restated
rather than imported. That is the point of the file.

Float note: bracket arithmetic is exact in decimal and not in binary, so
equalities that hold mathematically are asserted with pytest.approx. Where a
value IS exactly representable -- a rate looked up from a table, a rounded
display figure -- it is asserted with ==.
"""

import ast
import inspect

import pytest

import tax

# Hand-computed from the 2026 single table. Restated, not imported.
SD = 16_100                    # standard deduction
CAP = 24_500                   # 402(g) deferral cap
ARCHETYPE_GROSS = 165_000      # D-19 income at 35
PRESET_GROSS = 60_000          # D-40 early-career preset
MARKER_GROSS = 127_804         # D-24, published (rounded)
MARKER_NET = 108_397           # D-39, published (rounded)


# --- taxable() ---------------------------------------------------------------
def test_taxable_subtracts_the_standard_deduction():
    """D-21: gross minus deduction gives taxable, and the table is read in
    taxable terms."""
    assert tax.taxable(127_804) == pytest.approx(111_704)
    assert tax.taxable(165_000) == pytest.approx(148_900)


def test_taxable_floors_at_zero():
    """Negative taxable income is not a thing the tax code has. This floor is
    not D-38's prohibited clamp -- that one is about balances in decumulation."""
    assert tax.taxable(0) == 0.0
    assert tax.taxable(10_000) == 0.0
    assert tax.taxable(SD) == 0.0


# --- tax_on() ----------------------------------------------------------------
def test_tax_on_archetype_withdrawal_band_by_band():
    """Sprint 1 gate. Taxable 111,704 against the published 2026 single table:

        10% on 12,400            =  1,240.00
        12% on 50,400 - 12,400   =  4,560.00
        22% on 105,700 - 50,400  = 12,166.00
        24% on 111,704 - 105,700 =  1,440.96
                                   ----------
                                   19,406.96
    """
    bands = [
        0.10 * 12_400,
        0.12 * (50_400 - 12_400),
        0.22 * (105_700 - 50_400),
        0.24 * (111_704 - 105_700),
    ]
    assert sum(bands) == pytest.approx(19_406.96)
    assert tax.tax_on(MARKER_GROSS) == pytest.approx(19_406.96)


def test_tax_on_is_zero_below_the_deduction():
    assert tax.tax_on(SD) == 0.0
    assert tax.tax_on(11_160) == 0.0


def test_net_of_tax_at_the_marker():
    """D-24: $127,804 gross funds $108,397 net. The unrounded value is
    108,397.04 -- the published figure is that value rounded for display."""
    assert tax.net_of_tax(MARKER_GROSS) == pytest.approx(108_397.04, abs=1e-6)
    assert round(tax.net_of_tax(MARKER_GROSS)) == MARKER_NET


# --- effective_rate() --------------------------------------------------------
def test_effective_rate_is_the_published_marker():
    """D-24: an effective 15.2% on the modeled withdrawal. Unrounded 15.185%."""
    assert tax.effective_rate(MARKER_GROSS) == pytest.approx(0.15185, abs=5e-6)
    assert round(tax.effective_rate(MARKER_GROSS) * 100, 1) == 15.2


def test_effective_rate_at_zero_gross_returns_zero():
    """It is a demo. A ZeroDivisionError in front of a panel is worse than a
    rate that means nothing."""
    assert tax.effective_rate(0) == 0.0


# --- marginal_rate() ---------------------------------------------------------
@pytest.mark.parametrize(
    "gross, expected, why",
    [
        (40_000, 0.12, "taxable 23,900 -- inside the 12% band"),
        (121_800, 0.22, "taxable 105,700 -- the 22/24 edge, LAST dollar"),
        (165_000, 0.24, "taxable 148,900 -- the archetype"),
        (105_700, 0.22, "taxable 89,600 -- mid-22%-band, NOT an edge"),
    ],
)
def test_marginal_rate_hand_verified(gross, expected, why):
    """Sprint 1 gate. All four arguments are GROSS.

    The 105,700 case is the guard against a future reader treating the argument
    as taxable. The 121,800 case tests the same confusion from the other side --
    read as gross it lands taxable exactly on the edge and returns 0.22; read as
    taxable it would return 0.24.
    """
    assert tax.marginal_rate(gross) == expected, why


def test_marginal_rate_uses_last_dollar_not_next_dollar():
    """At taxable exactly 105,700 the answer is 22%, because the 22% band runs
    THROUGH 105,700 and 24% begins at 105,701. Deferral removes income from the
    top, so the rate that matters is the one on the dollar you remove.

    This convention is what makes the 121,800 gross-vs-taxable test valid. Under
    next-dollar semantics that call returns 0.24 whichever way the argument is
    read, and the test proves nothing.
    """
    assert tax.marginal_rate(105_700 + SD) == 0.22       # taxable exactly 105,700
    assert tax.marginal_rate(105_700 + SD + 1) == 0.24   # one dollar over


# --- contribution() ----------------------------------------------------------
def test_contribution_cap_binds_at_the_archetype():
    """D-25: 20% of $165,000 is $33,000, so the cap binds at $24,500. D-28's
    20% arrives as an argument -- it is not a number this module holds."""
    assert tax.contribution(ARCHETYPE_GROSS, 0.20) == CAP


def test_contribution_savings_rate_binds_at_the_preset():
    """20% of $60,000 is $12,000, below the cap."""
    assert tax.contribution(PRESET_GROSS, 0.20) == pytest.approx(12_000)


# --- deferral_rate(): t_now --------------------------------------------------
def test_deferral_rate_at_the_archetype_is_24_percent():
    """D-19 / D-21. t_now = 24% federal.

        tax_on(165,000) = 28,334   (taxable 148,900)
        tax_on(140,500) = 22,454   (taxable 124,400)
        (28,334 - 22,454) / 24,500 = 0.24
    """
    assert tax.tax_on(165_000) == pytest.approx(28_334)
    assert tax.tax_on(165_000 - CAP) == pytest.approx(22_454)
    assert tax.deferral_rate(ARCHETYPE_GROSS, CAP) == pytest.approx(0.24, abs=1e-12)


def test_deferral_rate_at_the_preset_is_12_percent():
    """D-40. The early-career preset ships at $60,000 with neither state taxing.

        tax_on(60,000) = 5,020   (taxable 43,900)
        tax_on(48,000) = 3,580   (taxable 31,900)
        (5,020 - 3,580) / 12,000 = 0.12
    """
    assert tax.tax_on(60_000) == pytest.approx(5_020)
    assert tax.tax_on(48_000) == pytest.approx(3_580)
    assert tax.deferral_rate(PRESET_GROSS, 12_000) == pytest.approx(0.12, abs=1e-12)


@pytest.mark.parametrize("gross, contrib", [(ARCHETYPE_GROSS, 24_500), (PRESET_GROSS, 12_000)])
def test_neither_headline_profile_straddles_a_bracket_edge(gross, contrib):
    """D-19's "no bracket straddle" as a TEST, not an assumption.

    The contribution comes off the top, so no straddle means the band is the
    same before and after it is removed -- an exact equality between two table
    lookups. When that holds, deferral_rate and marginal_rate agree.
    """
    assert tax.marginal_rate(gross) == tax.marginal_rate(gross - contrib)
    assert tax.deferral_rate(gross, contrib) == pytest.approx(
        tax.marginal_rate(gross), abs=1e-12
    )


@pytest.mark.parametrize(
    "gross, deferral, lookup, gap",
    [
        (66_600, 0.1207507507, 0.22, 10.0),   # 12 -> 22, band floor
        (121_900, 0.2200820345, 0.24, 2.0),   # 22 -> 24, band floor
        (217_900, 0.2400816326, 0.32, 8.0),   # 24 -> 32, band floor
    ],
)
def test_straddle_bands_reproduce_d21s_table(gross, deferral, lookup, gap):
    """D-21's straddle table. Just above an edge the whole contribution comes
    out of the band BELOW, so deferral_rate converges on the lower rate while a
    lookup returns the upper one -- which makes the worst error the bracket gap
    itself, approached but never attained.

    This is the test that stops a lookup being reintroduced as t_now.
    """
    contrib = tax.contribution(gross, 0.20)
    assert tax.deferral_rate(gross, contrib) == pytest.approx(deferral, abs=1e-9)
    assert tax.marginal_rate(gross) == lookup
    error_points = (lookup - tax.deferral_rate(gross, contrib)) * 100
    assert error_points < gap                       # supremum, not attained
    assert error_points == pytest.approx(gap, abs=0.09)


def test_at_a_band_edge_the_two_methods_agree_exactly():
    """The error is discontinuous. AT the edge it is zero; one dollar above, it
    jumps to nearly the full gap. Publishing "worst error at band floor" invites
    a reader to test the floor itself, so this pins what happens there."""
    contrib = tax.contribution(121_800, 0.20)
    assert tax.deferral_rate(121_800, contrib) == pytest.approx(
        tax.marginal_rate(121_800), abs=1e-12
    )


def test_the_seventy_thousand_panelist():
    """D-21: nudge the preset income to $70,000 and a lookup gives 22.0%
    against a true 14.5%. The failure mode this whole change exists to remove."""
    contrib = tax.contribution(70_000, 0.20)
    assert tax.deferral_rate(70_000, contrib) == pytest.approx(0.145, abs=1e-12)
    assert tax.marginal_rate(70_000) == 0.22


# --- combined_rate() ---------------------------------------------------------
def test_combined_rate_at_the_archetype():
    """D-30 defaults: taxed while working, untaxed in retirement. 24% + 8.5%."""
    assert tax.combined_rate(ARCHETYPE_GROSS, CAP, state=True) == pytest.approx(0.325)
    assert tax.combined_rate(ARCHETYPE_GROSS, CAP, state=False) == pytest.approx(0.24)


def test_combined_rate_federal_half_is_the_deferral_rate():
    """Not marginal_rate. Two definitions of t_now in one module means Sprint 6
    picks one by accident, and they agree at both headline profiles so the
    disagreement would be invisible where anyone would look for it."""
    contrib = tax.contribution(70_000, 0.20)
    assert tax.combined_rate(70_000, contrib, state=True) == pytest.approx(0.23)
    assert tax.marginal_rate(70_000) + 0.085 == pytest.approx(0.305)


# --- gross_for_net() ---------------------------------------------------------
def test_gross_for_net_round_trips_across_the_range():
    """The inverse is real, not approximate. Swept $0 to $700k plus every band
    boundary and its neighbours."""
    sweep = [float(g) for g in range(0, 700_001, 500)]
    edges = [12_400, 50_400, 105_700, 201_775, 256_225, 640_600]
    for e in edges:
        for delta in (-1.0, -0.01, 0.0, 0.01, 1.0):
            sweep.append(e + SD + delta)
    for g in sweep:
        assert tax.gross_for_net(tax.net_of_tax(g)) == pytest.approx(g, abs=1e-6), g


def test_gross_for_net_is_exact_on_the_unrounded_chain():
    """The math, tested without the display roundings anywhere near it."""
    net = tax.net_of_tax(MARKER_GROSS)
    assert tax.gross_for_net(net) == pytest.approx(MARKER_GROSS, abs=1e-6)


def test_gross_for_net_reproduces_the_published_pair_as_a_rounding():
    """D-24: $127,804 and $108,397 are two display roundings of ONE unrounded
    point. Feeding the rounded net back gives 127,803.95, and asserting the two
    published figures against each other exactly fails by $0.05. This is a
    different test from the one above and neither may fail for the other's
    reason."""
    assert tax.gross_for_net(MARKER_NET) == pytest.approx(127_803.95, abs=0.01)
    assert round(tax.gross_for_net(MARKER_NET)) == MARKER_GROSS


def test_gross_for_net_guards_below_the_standard_deduction():
    """No tax below the deduction, so net == gross. Without the guard the
    formula extrapolates the 10% band downward and returns $10,611 -- a gross
    below the net it is supposed to fund. Reachable: a low income gives a low
    balance gives a low draw, and the marker is computed on that draw."""
    assert tax.gross_for_net(11_160) == 11_160
    assert tax.gross_for_net(0) == 0
    assert tax.gross_for_net(SD) == SD


def test_gross_for_net_at_a_bracket_boundary():
    """$121,800 gross is taxable exactly 105,700 -- the same boundary the
    marginal_rate gross-vs-taxable test uses."""
    assert tax.gross_for_net(tax.net_of_tax(121_800)) == pytest.approx(121_800, abs=1e-6)


def test_the_inverse_is_continuous_at_every_band_junction():
    """Found by mutation testing: flipping gross_for_net's band selection from
    `net <= ceiling` to `net < ceiling` does not change any answer.

    That is not a hole in the suite -- it is the piecewise-linear function being
    continuous. At a junction the band below and the band above are two
    expressions for the same point, so either branch is correct there. Asserted
    here so the equivalence is a stated property rather than a coincidence a
    later reader has to rediscover.
    """
    for ceiling in (27_260, 60_700, 103_834, 176_851, 213_877):
        below = tax.gross_for_net(ceiling - 1e-6)
        exact = tax.gross_for_net(float(ceiling))
        above = tax.gross_for_net(ceiling + 1e-6)
        assert below < exact < above
        assert exact == pytest.approx(below, abs=1e-5)
        assert exact == pytest.approx(above, abs=1e-5)


def test_net_is_strictly_increasing_so_the_inverse_is_unique():
    """d(net)/d(gross) = 1 - marginal_rate, and the top rate is 37%, so the
    slope never drops below 0.63. There is no branch where the inverse is
    ambiguous, which is why no tolerance argument is needed."""
    previous = -1.0
    for g in range(0, 900_001, 2_500):
        current = tax.net_of_tax(float(g))
        assert current > previous
        previous = current


# --- deferred constants ------------------------------------------------------
def test_over_65_deductions_are_present_and_unwired():
    """Sprint 1 done-when: a grep for either name finds the constant and nothing
    calling it.

    Walks the parsed module rather than grepping text or scanning function
    bodies. A Store on the name is the definition; a Load is something reading
    it, which is the thing that must not exist. Scanning function bodies alone
    misses a module-level wiring, and grepping text cannot tell a comment from
    code -- the comments here discuss both constants at length, on purpose.
    """
    assert tax.ADDITIONAL_DEDUCTION_65 == 2_050
    assert tax.OBBB_SENIOR_DEDUCTION == 6_000

    names = {"ADDITIONAL_DEDUCTION_65", "OBBB_SENIOR_DEDUCTION"}
    tree = ast.parse(inspect.getsource(tax))

    stores = {n.id for n in ast.walk(tree)
              if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    assert names <= stores, "both constants must be defined in tax.py"

    loads = [n.id for n in ast.walk(tree)
             if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
             and n.id in names]
    assert loads == [], f"deferred constant is wired: {loads}"


def test_filing_status_stubs_are_still_stubs():
    """D-19/D-21: the UI models one income curve and one age, so a household is
    something the controls cannot represent."""
    assert tax.BRACKETS_MFJ is None
    assert tax.BRACKETS_HOH is None


def test_the_seven_published_edges_are_intact():
    """R1's payload. If any of these moves, t_now, the marker and both
    thresholds move with it -- so this is the test that fails loudest."""
    assert tax.BRACKETS == [
        (12_400, 0.10),
        (50_400, 0.12),
        (105_700, 0.22),
        (201_775, 0.24),
        (256_225, 0.32),
        (640_600, 0.35),
        (float("inf"), 0.37),
    ]
    assert tax.STANDARD_DEDUCTION == 16_100
    assert tax.DEFERRAL_CAP == 24_500
    assert tax.STATE_RATE == 0.085
    assert tax.EARLY_WITHDRAWAL_PENALTY == 0.10
