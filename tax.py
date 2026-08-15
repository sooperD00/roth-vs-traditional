"""Every number that came from outside the model lives here.

DECISIONS D-21. Sprint 1's rule: no tax number appears anywhere else in the
repo. That includes the state rate and the early-withdrawal penalty -- both are
tax numbers, and both were homeless before gate two.

ONE EXEMPTION: tests/. A hand-verification that imports the constant it is
verifying tests nothing, so tests/test_tax.py restates the literals by hand.
That is the only place outside this module where a tax number may appear, and
it is the reason the grep sweep excludes that directory.

R1 IS CLOSED. The seven edges, the standard deduction and the deferral cap were
verified by hand against the primary source on 2026-08-15 -- IRS IR-2025-103 and
Rev. Proc. 2025-32, not a secondary source and not a model's recollection -- and
corroborated independently by Tax Foundation's 2026 table. Both URLs and the
date are in the source comment below. If any edge moves, t_now, the marker and
both thresholds move with it.

t_now IS NOT A BRACKET LOOKUP. It is deferral_rate() -- the rate the deferred
dollars actually avoid. marginal_rate() equals it only when the contribution
stays inside one bracket. When the contribution straddles an edge, marginal_rate
overstates t_now by up to the full bracket gap, and t* IS t_now, so the error
lands on the headline. Three straddle bands, their mechanism and their measured
errors are in D-21's subsection. Neither headline profile straddles, and
tests/test_tax.py asserts that rather than assuming it (D-19).

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
EARLY_WITHDRAWAL_PENALTY = 0.10   # SOURCE: IRC 72(t). D-16 low-rung branch.
                                  # Defined here because it is a tax number and
                                  # D-21 says tax numbers live here. First USED
                                  # in Sprint 3, at the forced-liquidation
                                  # branch. Unreferenced until then, by design.
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
                              # A scalar with no bracket table, so unlike the
                              # federal half it cannot straddle. combined_rate()
                              # says so at the point of use.

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
#
# THAT 13.5% CARRIES A CONVENTION AND THIS IS IT (D-21): the gross is RE-SOLVED
# to hold D-39's net draw fixed at $108,397, falling from $127,804 to ~$125,380,
# and the $6,000 is taken IN FULL. Hold the gross at $127,804 instead and the
# answer is 13.7%; apply the OBBB phaseout and it is ~14.1%. Neither changes a
# verdict, but a reader who recomputes without the convention will not reproduce
# the published number.


# --- Derived. Not a source of numbers -- a rearrangement of BRACKETS. ---------
def _bands():
    """(lo, hi, rate, base) per bracket, in TAXABLE terms.

    `base` is the cumulative tax at `lo`, so tax(t) = base + rate * (t - lo)
    with no accumulation loop and no partial sums to drift. Derived rather than
    typed out: a second place holding the same numbers is a second place to get
    them wrong, and D-21 allows exactly one.
    """
    out, lo, base = [], 0.0, 0.0
    for hi, rate in BRACKETS:
        out.append((lo, hi, rate, base))
        if hi != float("inf"):
            base += rate * (hi - lo)
            lo = float(hi)
    return out


_BANDS = _bands()

# The NET each band tops out at. gross_for_net() selects a band by comparing
# against these, which is what makes the inverse a lookup plus one division
# rather than a search.
_NET_CEILINGS = [
    float("inf") if hi == float("inf")
    else (hi + STANDARD_DEDUCTION) - (base + rate * (hi - lo))
    for lo, hi, rate, base in _BANDS
]


# --- Conversions -------------------------------------------------------------
def taxable(gross: float) -> float:
    """Gross to taxable. The controls take gross; BRACKETS is stated in taxable,
    and this is the only place the two meet (Sprint 1 done-when).

    Floored at zero. That floor is NOT the clamp D-38 prohibits -- D-38 is about
    balances in the decumulation loop, where a floor breaks bisection. Negative
    taxable income is not a thing the tax code has, so flooring here is the model
    being correct rather than the model being protected.
    """
    return max(0.0, gross - STANDARD_DEDUCTION)


def tax_on(gross: float) -> float:
    """Total federal tax on a gross amount, summed across brackets.

    Sprint 1 gate: tax_on(127_804) is hand-verifiable. That is the archetype's
    modeled gross withdrawal under D-39 and the operand for the 15.2% marker.
    Taxable is 111,704 and the bands contribute 1,240.00 + 4,560.00 + 12,166.00
    + 1,440.96 = 19,406.96, leaving $108,397.04 net.

    No rounding here. The app rounds for display; rounding inside the module
    would push error into every rate the engine computes from it.
    """
    t = taxable(gross)
    for lo, hi, rate, base in _BANDS:
        if t <= hi:
            return base + rate * (t - lo)
    raise AssertionError("unreachable: the last band's upper edge is infinite")


def net_of_tax(gross: float) -> float:
    """Gross minus federal tax. The forward direction of gross_for_net()."""
    return gross - tax_on(gross)


def gross_for_net(net: float) -> float:
    """The gross withdrawal that funds a given net amount. Closed form, exact.

    D-39 defines spending as NET; D-24's marker needs GROSS. This function is
    that conversion, and it lives here because it is a fact about the tax code
    rather than about the model -- the same reason gross-to-taxable does (D-21).
    Making it one named object is what stops the convention drifting: at gate
    two, 17% and 15.2% were both defensible precisely because this conversion
    was happening inside something bigger.

    net(gross) is piecewise linear, so invert the piece:

        within a band:  net = g(1-rate) - base + rate*(SD + lo)
        so:             g   = (net + base - rate*(SD + lo)) / (1 - rate)

    No bisection, no tolerance argument, no iteration count. d(net)/d(gross) is
    1 - marginal_rate, and the top rate is 37%, so the slope never drops below
    0.63: net is strictly increasing everywhere and the inverse is unique. There
    is no branch where it is ambiguous.

    GUARD, below the standard deduction: there is no tax, so net == gross.
    Without it the formula extrapolates the 10% band downward and returns a
    gross BELOW the net it is supposed to fund -- gross_for_net(11_160) would
    give $10,611. Reachable in the app, because a low income gives a low balance
    gives a low draw, and the marker is computed on that draw.

    Published pair: gross_for_net(108_397) returns 127_803.95, not 127_804.
    $127,804 and $108,397 are two display roundings of one unrounded point
    (D-24). Do not assert them against each other exactly. The engine passes the
    UNROUNDED draw, which returns 127,803.64 -- a third rounding of the same
    point, and the reason those two figures must never be asserted against one
    another.

    CLOSED AT SPRINT 2B. engine.py's marker_withdrawal() was a pure alias for
    this function; it is deleted and the marker is now
    tax.effective_rate(tax.gross_for_net(draw)) at the call site. D-24's
    reasoning lives in engine.py where that function stood.
    """
    if net <= STANDARD_DEDUCTION:
        return net
    for (lo, hi, rate, base), ceiling in zip(_BANDS, _NET_CEILINGS):
        if net <= ceiling:
            return (net + base - rate * (STANDARD_DEDUCTION + lo)) / (1.0 - rate)
    raise AssertionError("unreachable: the last net ceiling is infinite")


# --- Rates -------------------------------------------------------------------
def effective_rate(gross: float) -> float:
    """tax_on(gross) / gross. This is the D-24 marker's unit -- an EFFECTIVE
    rate. t* is a MARGINAL rate. They share an axis in the app and the axis
    says so, because the gap between them is the lesson.

    Zero gross returns 0.0 rather than raising. It is a demo, and a division by
    zero in front of a panel is worse than a rate that means nothing.
    """
    if gross <= 0:
        return 0.0
    return tax_on(gross) / gross


def marginal_rate(gross: float) -> float:
    """Rate on the LAST dollar of taxable income (not the next dollar).

    Deferral removes income from the top, so the rate that matters is the one on
    the dollar you remove, not the one you would earn next. At taxable exactly
    105,700 this returns 0.22; next-dollar semantics would return 0.24.

    THIS IS NOT t_now. Use deferral_rate(). marginal_rate survives for display
    and as combined_rate's federal half, and it agrees with deferral_rate only
    when the contribution stays inside one band -- see the module docstring and
    D-21's subsection for the three bands where it does not.

    Sprint 1 gates, ALL FOUR ARGUMENTS GROSS:
        marginal_rate( 40_000) -> 0.12   taxable  23,900
        marginal_rate(121_800) -> 0.22   taxable 105,700, the 22/24 edge
        marginal_rate(165_000) -> 0.24   taxable 148,900, the archetype
        marginal_rate(105_700) -> 0.22   taxable  89,600, mid-22%-band

    The fourth exists to catch a future reader treating the argument as taxable.
    The second tests the same confusion from the other side and is valid ONLY
    under last-dollar: under next-dollar it returns 0.24 whichever way the
    argument is read, and proves nothing.

    Taxable zero returns 0.10 -- the first band starts at zero and the lookup is
    uniform. There is no last dollar at zero income, so the value is meaningless
    rather than wrong, and nothing reads it there.
    """
    t = taxable(gross)
    for hi, rate in BRACKETS:
        if t <= hi:
            return rate
    raise AssertionError("unreachable: the last band's upper edge is infinite")


def contribution(gross: float, savings_rate: float) -> float:
    """The deferred amount: savings_rate of gross, capped.

    The CAP is a tax number and lives here. The SAVINGS RATE is behavioral --
    D-28 sources 20% from BLS household budget data -- so it arrives as an
    argument from engine.py and never appears in this module. Splitting them
    this way is what keeps each module holding only its own numbers.
    """
    return min(savings_rate * gross, DEFERRAL_CAP)


def deferral_rate(gross: float, contribution: float) -> float:
    """t_now: the rate the deferred dollars actually avoid.

    Exact by construction -- it asks what the tax bill actually does, instead of
    looking up a band and assuming the whole contribution sits inside it. That
    also dissolves the last-dollar/next-dollar question rather than answering it,
    because nothing is looked up at a boundary.

    Sprint 1 gates:
        deferral_rate(165_000, 24_500) -> 0.24   the archetype
        deferral_rate( 60_000, 12_000) -> 0.12   the early-career preset

    Both are exact in arithmetic, and neither profile straddles a band edge --
    D-19's "no bracket straddle" is now a test rather than an assumption.

    (The parameter shadows the contribution() function above. Deliberate: D-21
    names this signature, and nothing in this body calls that function.)
    """
    if contribution <= 0:
        return 0.0
    return (tax_on(gross) - tax_on(gross - contribution)) / contribution


def combined_rate(gross: float, contribution: float, state: bool) -> float:
    """t_now plus the state rate when the relevant boolean is on.

    Two booleans share this rate (D-30): 'while working', default TRUE, and
    accordion D4 'you retire to a state that also taxes income', default FALSE.
    At the archetype that is 24% + 8.5% = 32.5% now, federal-only later.

    The federal half is deferral_rate, NOT marginal_rate -- otherwise the module
    would hold two definitions of t_now and Sprint 6 would pick one by accident.
    They agree at both headline profiles, so the disagreement would be invisible
    exactly where anyone would look for it. At $70,000 gross with the state on,
    a lookup reports 30.5% against a true 23.0%.

    The state half cannot straddle: D-30 defines 8.5% as a scalar with no bracket
    table, so it is the same rate on every dollar by construction.
    """
    federal = deferral_rate(gross, contribution)
    return federal + STATE_RATE if state else federal
