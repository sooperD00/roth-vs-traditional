"""Every number that came from outside the model lives here.

DECISIONS D-21. Sprint 1's rule: no tax number appears anywhere else in the
repo. That includes the state rate and the early-withdrawal penalty -- both are
tax numbers, and both were homeless before gate two.

R1 IS OPEN. Verify the seven edges, the standard deduction and the deferral cap
BY HAND against irs.gov before implementing. Not against a secondary source,
not against a model's recollection. If any edge moves, t_now, the marker and
both thresholds move with it.

Everything is real 2026 dollars. Brackets are treated as inflation-indexed
(D-27), so this one table applies at every year of the run.
"""

# --- 2026, single filer.
# SOURCE: IRS IR-2025-103 (Oct 9, 2025), Rev. Proc. 2025-32.
#   https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill
#   https://www.irs.gov/pub/irs-drop/rp-25-32.pdf
# Verified against the primary source 2026-08-15. R1 CLOSED.
# Corroborated independently by Tax Foundation's 2026 bracket table -- all seven
# edges and the deduction agree.
BRACKETS = [
    # (upper edge of TAXABLE income, marginal rate)
    (12_400, 0.10),
    (50_400, 0.12),
    (105_700, 0.22),
    (201_775, 0.24),
    (256_225, 0.32),
    (640_600, 0.35),
    (float("inf"), 0.37),
]
STANDARD_DEDUCTION = 16_100   # SOURCE: irs.gov, single, 2026
DEFERRAL_CAP = 24_500         # SOURCE: irs.gov COLA release, 402(g), 2026
EARLY_WITHDRAWAL_PENALTY = 0.10   # SOURCE: IRC 72(t). D-16 low-rung branch
STATE_RATE = 0.085            # D-30. DC marginal at the archetype income.
                              # ADDITIVE to the federal rate. This IGNORES SALT
                              # deductibility, and it is the larger of the two
                              # known biases: for a filer who itemizes, the true
                              # combined marginal rate is
                              #     0.24 + 0.085 * (1 - 0.24) = 30.5%
                              # not 32.5%. That is 2.0 points ON THE HEADLINE,
                              # in the direction that FLATTERS Traditional.
                              # It bites only if the filer itemizes: at the
                              # archetype, state income tax alone is $14,025
                              # against a $16,100 standard deduction, so it
                              # takes ~$2,075 of mortgage interest, property tax
                              # or charity to cross. Likely for an owner, not
                              # automatic for a renter. TODO with real per-state
                              # data.

BRACKETS_MFJ = None   # TODO
BRACKETS_HOH = None   # TODO -- stubbed because the UI models one income curve
                      # and one age, so a household is something the controls
                      # cannot represent (D-19). NOT because of overlapping
                      # edges: the published 2026 HoH column is contiguous
                      # (24% ends 201,750; 32% begins 201,751). Gate 2 found the
                      # original reason unsupported by the source.

# DEFERRED, both of them. Measured, not forgotten -- see README Scope & Branches.
# Wiring the first is one conditional on age; it is the honest one.
ADDITIONAL_DEDUCTION_65 = 2_050   # NOT WIRED. Permanent, IRC 63(f).
                                  # SOURCE: Rev. Proc. 2025-32, single.
OBBB_SENIOR_DEDUCTION = 6_000     # NOT WIRED. Up to this amount, income-phased,
                                  # and TEMPORARY -- applying it across a
                                  # 35-year retirement asserts something the
                                  # statute does not say.
# Together they move the today's-law marker 15.2% -> 13.5%, which WIDENS
# Traditional's lead. Omitting them understates the recommendation.


def taxable(gross: float) -> float:
    """Gross to taxable. The controls take gross; BRACKETS is stated in taxable,
    and this is the only place the two meet (Sprint 1 done-when)."""
    raise NotImplementedError


def tax_on(gross: float) -> float:
    """Total federal tax on a gross amount, summed across brackets.

    Sprint 1 gate: tax_on(127_804) is hand-verifiable. That is the archetype's
    modeled gross withdrawal under D-39 and the operand for the 15.2% marker.
    """
    raise NotImplementedError


def effective_rate(gross: float) -> float:
    """tax_on(gross) / gross. This is the D-24 marker's unit -- an EFFECTIVE
    rate. t* is a MARGINAL rate. They share an axis in the app and the axis
    says so, because the gap between them is the lesson."""
    raise NotImplementedError


def marginal_rate(gross: float) -> float:
    """The rate on the next dollar.

    Sprint 1 gate: hand-verified at $40,000, $105,700 (a bracket edge) and
    $165,000. At $165,000 this returns 0.24, and it still returns 0.24 after a
    full $24,500 deferral -- no straddle (D-19).
    """
    raise NotImplementedError


def combined_rate(gross: float, state: bool) -> float:
    """marginal_rate + STATE_RATE when the relevant state boolean is on.

    Two booleans share this rate (D-30): 'while working', default TRUE, and
    accordion D4 'you retire to a state that also taxes income', default FALSE.
    At the archetype that is 24% + 8.5% = 32.5% now, federal-only later.
    """
    raise NotImplementedError
