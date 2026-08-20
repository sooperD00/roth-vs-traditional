"""Traditional vs Roth -- the app.  DECISIONS section 7 is the layout contract.

THE SEAM, AND IT IS ONE SENTENCE: THE APP COMPUTES ONE NUMBER AND READS ALL THE
OTHERS.  The deterministic line -- both thresholds and the today's-law marker --
comes from engine.breakeven() on a ONE-ROW CONSTANT array.  Everything else on
this page is either a control's own state or an index into cube.json.  A loop
over paths means the seam is crossed (D-12).

WHAT MUST NOT APPEAR IN THIS FILE
  - stochastic code of any kind; the cube ships committed and is read     (D-12)
  - a tax literal; they live in tax.py and arrive through engine           (D-21)
  - a second copy of any engine constant; import it or read it off the cube

WHAT SPRINT 6 KEPT FROM THE P3a PROBE THIS FILE REPLACES.  The probe proved six
things about the container and one of them shapes this file: ROOT-LEVEL MODULES
IMPORT BECAUSE STREAMLIT PUTS THE SCRIPT'S DIRECTORY ON sys.path, NOT because
they are installed as a package -- Railpack installs with --no-install-project.
So `import engine` works in the container for a reason that has nothing to do
with packaging, and moving this file into a subdirectory would break it.
Path(__file__).resolve().parent is the same reason cube.json resolves.

THE FILENAME IS LOad-BEARING.  railway.toml's start command names app.py and
tests/test_deploy_config.py reads the entry point OUT of that command rather
than hard-coding it.  Keeping the name is what lets this sprint touch no deploy
config at all.  Do not rename this file.

THE ONE THING THAT COULD HAVE FAILED WAS TIMING, AND IT DOES NOT.  breakeven()
runs a bisection to float exhaustion inside every rerun.  MEASURED at Sprint 6,
on the (1, 65) constant array, both thresholds together: ~54 ms.  Sprint 9's
gate is a cold load under five seconds.  st.cache_data is kept anyway -- it is
one decorator and Profile is frozen and hashable for exactly this reason (D-48
makes the same argument one layer down) -- but it is insurance, not a fix.
"""

import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

import engine
import tax

REPO_ROOT = Path(__file__).resolve().parent
CUBE_JSON = REPO_ROOT / "cube.json"

# --- Display constants.  NONE OF THESE IS A MODEL NUMBER ----------------------
# Every one is a presentation choice with a decision behind it.  Model numbers
# are imported from engine or read off the cube; nothing is restated here.

WASH_BAND_POINTS = 2.0          # D-02.  Inside it the headline reads "a wash";
                                # outside it names a winner.  At the archetype
                                # the gap is 17.3 points so the band never fires
                                # there -- it exists for the profiles a panelist
                                # types in, which is what happens at a demo.
SENTENCE_DELTA = "10"           # D-17.  The app uses 10 and NAMES it.  delta is
                                # the assumed size of the user's miss, not a
                                # model parameter.
SENTENCE_OBJECTIVE = 4          # D-23.  10th percentile -- where fragility is
SENTENCE_SHOCKS = 1             # visible, and it keeps both magnitudes in
                                # dollars.  Zero shocks makes $Y identically 0.
NEXT_RUNG = {"low": "mid", "mid": "high"}       # D-36.  One step, and High has
                                                # no next rung -- the app says
                                                # so rather than printing zero.
RUNG_LABEL = {"low": "Low", "mid": "Mid", "high": "High"}   # DESIGN 3.4: named,
                                                            # never numbered.

# D-15, decided 2026-08-18.  The balance graph and the dot panels run on
# different return models and the caption says by how much.  THE MEDIAN, not the
# mean -- D-23 already rejected the ensemble average as a gauge, in this
# project's own words, because it is not what any one household lives.  Not the
# $2,028,066 deterministic proxy and not the withdrawn 3.4%.
SERIES_MEDIAN_T65 = 2_123_538
SERIES_MEDIAN_GAP = "+4.7%"
SERIES_GEOMETRIC_MEAN = 6.8   # D-15.  The historical series' own geometric
                              # mean, which return_series.py forbids rescaling.
                              # A display figure with a citation, not a
                              # recomputation -- the app does no math on the
                              # deck (D-12).

TRAD_BLUE = "#2E7BC4"
ROTH_GREEN = "#1F8A5F"
MARKER_ORANGE = "#E8912A"
RAIL_GREY = "#8B949E"

# D-04a.  7 / 9 / 12, ALL REAL, default 7.  Each labelled with its nominal
# equivalent, and 12 labelled implausible ON PURPOSE: it is the button a skeptic
# reaches for first, and watching t* hold still there is L1 at full force.
RETURN_BUTTONS = {
    "7% real  (~10% nominal)": 0.07,
    "9% real  (~12% nominal)": 0.09,
    "12% real  (~15% nominal, implausible)": 0.12,
}


# =============================================================================
# THE ARTIFACT.  Read, never computed.
# =============================================================================
@st.cache_data
def load_cube() -> dict:
    """cube.json off disk, keyed by (rung, objective, shocks).

    The path pattern is the probe's: Path(__file__).parent resolves inside the
    container, which P3a proved rather than assumed.  D-12 -- the cube ships
    committed and is READ, never recomputed, which is what keeps this file free
    of a seed and free of anything that could be slow in front of a panel.
    """
    cube = json.loads(CUBE_JSON.read_text(encoding="utf-8"))
    cells = {(c["rung"], c["objective"], c["shocks"]): c for c in cube["cells"]}
    return {"header": cube["header"], "cells": cells}


# =============================================================================
# THE ONE COMPUTED THING.  Everything below reads it; nothing recomputes it.
# =============================================================================
@st.cache_data(hash_funcs={engine.Profile: hash})
def deterministic_readings(profile: engine.Profile, rate: float,
                           policy_year: int) -> dict:
    """Both thresholds, the marker, and the accumulation curves.  One call.

    THE ENTIRE COMPUTED HALF OF THIS APP IS THIS FUNCTION.  make_paths with
    kind="constant" and n_paths=1 IS deterministic mode -- a shape, not a flag
    (D-22) -- so the engine cannot tell it apart from the array that built the
    cube, which is what keeps the headline and the dots from ever drifting.

    TWO breakeven() CALLS, ALWAYS, AND THAT IS D-10 RATHER THAN AN OPTION.  Both
    thresholds are on screen at once and neither sits behind a click: showing one
    and hiding the other makes a bet look like a default.  The nevermind toggle
    selects which one the VERDICT is measured against; it does not decide whether
    the second one is computed.

    THE MARKER IS AN EFFECTIVE RATE AND t* IS A MARGINAL ONE (D-24).  Two units
    on one axis, and the axis says so.  The marker's withdrawal is defined
    non-circularly -- the gross amount today's brackets require to fund the
    modelled net draw, in closed form, no solver.

    Objective 4 is passed for the deterministic line and the choice costs
    nothing: at n_paths == 1 objectives 1, 3 and 4 collapse onto the same number
    (D-22), so the headline is objective-independent by construction.  Objective
    5 would RAISE here, correctly -- P(not running out) over one path is a step
    function with one step.
    """
    paths = engine.make_paths("constant", 1, profile.n_years, rate=rate)

    rules_hold = engine.breakeven(profile, SENTENCE_OBJECTIVE, 0, None, paths)
    treatment_moves = engine.breakeven(
        profile, SENTENCE_OBJECTIVE, 0, policy_year, paths
    )

    accumulation = engine.accumulate(profile, paths[0], 0)
    draw = engine.retirement_draw(
        accumulation.roth,
        profile.n_decumulation_years,
        engine.draw_return_rate(paths),
    )
    marker_gross = tax.gross_for_net(draw)

    return {
        "rules_hold": rules_hold,
        "treatment_moves": treatment_moves,
        "marker": tax.effective_rate(marker_gross),
        "marker_gross": marker_gross,
        "draw": draw,
        "t_now": profile.t_now,
        "trad_by_year": accumulation.trad_by_year,
        "roth_by_year": accumulation.roth_by_year,
        "trad_65": accumulation.trad,
        "roth_65": accumulation.roth,
        "allowance": engine.policy_allowance(accumulation, policy_year),
    }


# =============================================================================
# CONTROLS -> A Profile.  The whole app is a function of this object.
# =============================================================================
FIELD_DEFAULTS = {
    "income_35": 165_000, "income_38": 75_000,          # D-19's four knots.
    "income_55": 200_000, "income_65": 200_000,
    "state_while_working": True,                        # D-30, default yes.
    "state_in_retirement": False,                       # D-30 / D4, default no.
    "return_button": "7% real  (~10% nominal)",         # D-04a, default 7.
    "policy_on": False,                                 # D-09.
    "policy_year": engine.POLICY_YEAR,                  # D-26's N, default 20.
}


def seed_state() -> None:
    """First-paint defaults.  D-19's archetype, so the line sits on the dot."""
    for key, value in FIELD_DEFAULTS.items():
        st.session_state.setdefault(key, value)
    for i, on in enumerate(engine.DEFAULT_STOPS):     # D-32: 1-6 on, 7-10 off,
        st.session_state.setdefault(f"stop_{i}", on)  # so the archetype lands
                                                      # at Mid, contiguously.


def load_early_career() -> None:
    """D-40's preset.  THE FLIP LIVES HERE and it is the sprint's own demo.

    Roth under current rules, Traditional once the rule moves -- t* = 12.0%
    against a 15.9% marker, and the policy threshold at 29.1%.  The state toggle
    goes OFF with it: EARLY_CAREER carries state_while_working=False, and the
    preset that only moved the income curve would land on a different number
    than the one D-40 publishes.
    """
    points = dict(engine.EARLY_CAREER.income_points)
    for age in (35, 38, 55, 65):
        st.session_state[f"income_{age}"] = int(points[age])
    st.session_state["state_while_working"] = engine.EARLY_CAREER.state_while_working
    st.session_state["state_in_retirement"] = engine.EARLY_CAREER.state_in_retirement


def profile_from_state() -> engine.Profile:
    """The object everything downstream is a view of.

    THE RUNG IS NOT PASSED.  Profile.rung derives it from `stops` through
    rung_from_stops(), which is the same route Sprint 4 swept the cube's rung
    axis by -- it replaced `stops`, it never passed a rung.  These controls do
    the identical thing, so the app reaches the engine the way the cube did.
    """
    return engine.Profile(
        income_points=tuple(
            (age, float(st.session_state[f"income_{age}"]))
            for age in (35, 38, 55, 65)
        ),
        state_while_working=st.session_state["state_while_working"],
        state_in_retirement=st.session_state["state_in_retirement"],
        stops=tuple(st.session_state[f"stop_{i}"] for i in range(10)),
    )


# =============================================================================
# THE HEADLINE.  Threshold axis, verdict, two-rates sentence.
# =============================================================================
def threshold_axis(readings: dict, policy_year: int, axis_max: float):
    """Two thresholds and the marker on ONE rate scale (DESIGN 3.5).

    "Which side am I on" becomes a spatial question rather than an arithmetic
    one, and the GAP BETWEEN THE TWO LINES IS THE LESSON -- separate charts
    would hide it.

    THE SECOND THRESHOLD IS TO THE RIGHT.  58.4% against 32.5% at the archetype
    (D-40).  The design deck drew it at 14% with Roth winning to its right and
    the algebra cannot do that: a policy that harms only Roth strictly RAISES
    the rate at which Roth becomes worthwhile.  If this axis ever draws the
    second line left of the first, it has reproduced the deck's error.

    TWO UNITS SHARE THIS AXIS AND IT SAYS SO (D-24).  t* is a future MARGINAL
    rate; the today's-law marker is an EFFECTIVE rate.  You defer at marginal
    and you withdraw across the whole structure from zero.
    """
    rows = []
    boundaries = []
    scenarios = (
        ("If rules hold", readings["rules_hold"]),
        (f"If treatment moves at year {policy_year}", readings["treatment_moves"]),
    )
    for label, result in scenarios:
        if result.status == "crosses":
            edge = result.breakeven * 100.0
            rows.append({"row": label, "lo": 0.0, "hi": edge, "who": "Traditional wins"})
            rows.append({"row": label, "lo": edge, "hi": axis_max, "who": "Roth wins"})
            boundaries.append({"row": label, "at": edge, "text": f"{edge:.1f}%"})
        else:
            # NO BOUNDARY IS DRAWN BECAUSE THERE IS NO CROSSING.  D-35 forbids
            # printing nothing, so the percentage is replaced by copy rather
            # than by a null -- see verdict_block(), which carries the sentence.
            winner = ("Traditional wins" if result.status == "always_trad"
                      else "Roth wins")
            rows.append({"row": label, "lo": 0.0, "hi": axis_max, "who": winner})
            boundaries.append({"row": label, "at": axis_max / 2.0,
                               "text": "no break-even"})

    order = [label for label, _ in scenarios]
    frame = pd.DataFrame(rows)
    marker = readings["marker"] * 100.0

    bars = alt.Chart(frame).mark_bar(height=34).encode(
        x=alt.X("lo:Q", title=None,
                scale=alt.Scale(domain=[0, axis_max], nice=False),
                axis=alt.Axis(format=".0f", labelExpr="datum.value + '%'")),
        x2="hi:Q",
        y=alt.Y("row:N", title=None, sort=order,
                axis=alt.Axis(labelLimit=220, labelFontSize=13)),
        color=alt.Color(
            "who:N", title=None,
            scale=alt.Scale(domain=["Traditional wins", "Roth wins"],
                            range=[TRAD_BLUE, ROTH_GREEN]),
            legend=alt.Legend(orient="top", direction="horizontal"),
        ),
    )
    edges = alt.Chart(pd.DataFrame(boundaries)).mark_text(
        dy=-26, fontSize=14, fontWeight="bold", color="#E6EDF3",
    ).encode(x="at:Q", y=alt.Y("row:N", sort=order), text="text:N")

    rule = alt.Chart(pd.DataFrame([{"at": marker}])).mark_rule(
        strokeDash=[6, 4], strokeWidth=2, color=MARKER_ORANGE,
    ).encode(x="at:Q")
    rule_text = alt.Chart(pd.DataFrame([{"at": marker}])).mark_text(
        dy=8, dx=4, align="left", fontSize=12, color=MARKER_ORANGE,
        text=f"{marker:.1f}%  your withdrawal rate under today's law (effective)",
    ).encode(x="at:Q")

    return (bars + edges + rule + rule_text).properties(
        height=170,
        title=alt.TitleParams(
            "future tax rate  —  the two bars are MARGINAL rates (t*), "
            "the dashed line is an EFFECTIVE rate",
            fontSize=12, color=RAIL_GREY, anchor="start",
        ),
    )


def verdict_block(readings: dict, policy_on: bool, policy_year: int) -> None:
    """The verdict, and the copy that replaces it when there is no crossing.

    WHICH THRESHOLD THE VERDICT READS AGAINST IS WHAT THE NEVERMIND TOGGLE
    SELECTS.  Both thresholds are always computed and always drawn (D-10); the
    toggle moves the question, not the picture.  That is the gesture the
    early-career preset needs: at the preset the marker sits RIGHT of t* (Roth)
    and LEFT of the policy threshold (Traditional), so throwing the toggle flips
    the verdict without moving a single number on the axis.

    THE WASH BAND IS +/- 2 POINTS (D-02).  Inside it the headline says it is a
    wash; outside it names the winner.  At the archetype the gap is 17.3 points
    so the band never fires there -- it exists for the profiles a panelist types
    in, which is exactly what happens at a demo.

    A NON-CROSSING PROFILE PRINTS COPY, NEVER A NULL (D-35).  The reachable case
    is always_trad: drag the nevermind year down to 1 or 2 and the frozen
    allowance is one or two years of contributions, so Roth's advantage never
    catches up at any rate on the axis.  That is D-40 at full strength rather
    than an error state -- the scenario you were told makes Roth safe is the one
    that widens Traditional's lead, and here it widens it past the edge of the
    chart.
    """
    active = readings["treatment_moves"] if policy_on else readings["rules_hold"]
    marker = readings["marker"] * 100.0

    if active.status != "crosses":
        if active.status == "always_trad":
            st.markdown("### No future tax rate rescues Roth here.")
            st.markdown(
                f"A rule change in year {policy_year} freezes "
                f"**${readings['allowance']:,.0f}** tax-free and taxes "
                "everything after it as ordinary income. Traditional wins at "
                "every rate on this axis. There is no line here to be on the "
                "wrong side of."
            )
            st.markdown(
                "**Under current rules the break-even is still "
                f"{readings['rules_hold'].breakeven:.1%}**, and your "
                f"withdrawal rate today is {marker:.1f}%."
            )
        else:
            # UNREACHABLE FROM THESE CONTROLS TODAY and written anyway.  Under
            # D-01's convention roth_65 is exactly trad_65 * (1 - t_now), so the
            # difference is trad_65 * (t_now - t_later) and its sign always
            # flips inside the bracket.  It stops being unreachable the day the
            # accordion's D2 row becomes editable, which is Sprint 7's.
            st.markdown("### No future tax rate rescues Traditional here.")
            st.markdown(
                "This profile fills the Roth to the contribution cap, so both "
                "accounts receive the same nominal dollars and the Roth's are "
                "already taxed. Roth wins at every rate on this axis."
            )
            if readings["rules_hold"].status == "crosses":
                st.markdown(
                    "**Under current rules the break-even is still "
                    f"{readings['rules_hold'].breakeven:.1%}**, and your "
                    f"withdrawal rate today is {marker:.1f}%."
                )
    else:
        gap = active.breakeven * 100.0 - marker
        if abs(gap) <= WASH_BAND_POINTS:
            st.markdown("### It's a wash.")
            st.markdown(
                f"You are within {WASH_BAND_POINTS:.0f} points of the "
                "break-even. The account choice is not what decides this."
            )
        elif gap > 0:
            st.markdown("### Traditional, by "
                        f"{gap:.1f} points.")
            st.markdown(
                f"Your withdrawal rate today is {marker:.1f}%. The future "
                f"marginal rate that would tie them is {active.breakeven:.1%}. "
                "You are to the left of it."
            )
        else:
            st.markdown("### Roth, by "
                        f"{abs(gap):.1f} points.")
            st.markdown(
                f"Your withdrawal rate today is {marker:.1f}%. The future "
                f"marginal rate that would tie them is {active.breakeven:.1%}. "
                "You are to the right of it."
            )

    # D-10's label, and it goes BETWEEN the two thresholds because that is what
    # it is about.  Neither bar is the neutral one.
    st.caption(
        "**Roth bets the treatment holds. Traditional bets the rates do.** "
        "Neither is the neutral choice — pick which rule you'd rather be "
        "exposed to."
    )

    # D-35's slot.  The verdict above is REPLACED when either of the first two
    # gates is unchecked and t*, both thresholds and the $X/$Y sentence all
    # stay -- suppressing the verdict without hiding the numbers is what keeps
    # the page from reading as a lockout.  [SPRINT-7-CLEANUP] Sprint 7 wires the
    # ladder and fires this; Sprint 6 owes it the room, which is this block.


def two_rates_sentence(readings: dict) -> None:
    """DECISIONS section 7, in its exact words, with both figures computed.

    THIS IS THE HARDEST IDEA ON THE PAGE and the one an informed non-expert most
    needs.  Without it the natural misreading is "my rate is 15.2%, the
    break-even is 32.5%, so I need my taxes to DOUBLE" -- which is wrong, and it
    is the reading a careful non-expert arrives at on their own.  If this line
    gets cut, L2 stops teaching and starts asserting.

    Prose, not a legend, and both numbers re-render with the controls.
    """
    st.markdown(
        f"> **You defer at {readings['t_now'] * 100:.1f} cents on the dollar. "
        f"You withdraw at an average of {readings['marker'] * 100:.1f}.** "
        "Those are different rates because contributions come off the top of "
        "your income and withdrawals fill the brackets from zero."
    )


# =============================================================================
# THE BALANCE GRAPH.  L1's only gesture.
# =============================================================================
def balance_graph(readings: dict, profile: engine.Profile):
    """Two curves diverging during saving, landing together after tax.

    NOTE THE UNITS, BECAUSE THIS IS THE G4 TRAP DRAWN INSTEAD OF WRITTEN.
    trad_by_year is a PRE-TAX balance.  roth_by_year is ALREADY AFTER TAX.
    Plotting them as though they shared a unit is the same error D-01's
    convention exists to prevent -- same-nominal-dollars silently favours Roth.

    THE DASHED THIRD CURVE IS THE ARGUMENT.  Traditional multiplied by
    (1 - t_now) lies exactly on the Roth curve, and not only at 65: measured
    across all thirty years the worst deviation is 1.16e-10 dollars, which is
    float noise.  That is D-22's accumulation identity -- roth/trad == 1 - t_now
    EXACTLY -- drawn rather than captioned, and it is the strongest visual
    statement of L1 the page can make.  The divergence between the two solid
    curves is the money the deferral is holding for the government; the dashed
    line is what is left after handing it back.

    NOTHING IS CLAMPED (D-38) and the caption says so.  This is an
    ACCUMULATION-PHASE balance and it can go negative: Low's forced sale is not
    affordability-checked, so a Low-rung saver with $8,000 in the account
    "sells" $73,959 of it.  Right for the cube, wrong as a sentence about a
    person, and a graph is where someone would notice.
    """
    t_now = readings["t_now"]
    ages = [profile.current_age + i for i in range(len(readings["trad_by_year"]))]
    rows = []
    for age, trad, roth in zip(ages, readings["trad_by_year"],
                               readings["roth_by_year"]):
        rows.append({"age": age, "series": "Traditional (pre-tax)", "d": trad})
        rows.append({"age": age, "series": "Roth (after tax)", "d": roth})
        rows.append({"age": age, "series": "Traditional after tax",
                     "d": trad * (1.0 - t_now)})
    frame = pd.DataFrame(rows)
    order = ["Traditional (pre-tax)", "Roth (after tax)",
             "Traditional after tax"]

    return alt.Chart(frame).mark_line(strokeWidth=2.5).encode(
        x=alt.X("age:Q", title="age",
                scale=alt.Scale(domain=[ages[0], ages[-1]], nice=False)),
        y=alt.Y("d:Q", title=None, axis=alt.Axis(format="$,.0s")),
        color=alt.Color(
            "series:N", title=None, sort=order,
            scale=alt.Scale(domain=order,
                            range=[TRAD_BLUE, ROTH_GREEN, MARKER_ORANGE]),
            legend=alt.Legend(orient="top", direction="horizontal", columns=3),
        ),
        strokeDash=alt.StrokeDash(
            "series:N", sort=order,
            scale=alt.Scale(domain=order, range=[[1, 0], [1, 0], [7, 4]]),
            legend=None,
        ),
    ).properties(height=260)


# =============================================================================
# THE $X / $Y SENTENCE.  Arithmetic over two cube cells -- ported from
# scripts/measure_4a.py section 3, which is the worked example this inherits.
# =============================================================================
def x_and_y(cells: dict, rung: str) -> dict:
    """$X at the user's rung; $Y one rung up.  Objective 4, 1 shock, delta 10.

    $X = |roth - trad| at t* + delta, at the user's rung.
    $Y = the change in the BETTER CHOICE's outcome between that rung and the
         next rung up, same objective and shock count.

    D-23 pins the cell: objective 4 at 1 shock.  Zero shocks makes $Y
    identically zero -- with no shock all three rung branches run the same code.
    Expected value is the wrong gauge for fragility, because a halving and a
    doubling cancel in the mean while ruin is absorbing.

    D-17 SIZES delta AND THE APP NAMES IT.  Ten points is about a bracket and a
    half, the generous case, and it was chosen AGAINST the L3 claim on purpose:
    delta sets $X outright while leaving $Y nearly untouched, so at delta = 2
    the ratio reads 2.86x and L3 looks strong, and at delta = 10 -- the value
    printed here -- it reads 0.47x and L3 reads weak.  Do not switch objectives
    to make that come out better.

    $Y IS UNDEFINED AT HIGH (D-36) AND THE APP SAYS SO RATHER THAN PRINTING
    ZERO.  One step is the smaller and more defensible claim.

    THE DOLLARS ARE THE ARCHETYPE'S, NOT THE USER'S (D-14, D-15).  The cube is
    precomputed at the reference profile, so the user's controls select which
    RUNG is read; they do not move the dollars.  Labelled where it renders.
    """
    cell = cells[(rung, SENTENCE_OBJECTIVE, SENTENCE_SHOCKS)]
    if cell["dollars"] is None:                  # Non-crossing cells carry null
        return {"x": None, "y": None, "account": None, "ratio": None}
    pair = cell["dollars"][SENTENCE_DELTA]
    x = abs(pair["roth"] - pair["trad"])
    account = "roth" if pair["roth"] > pair["trad"] else "trad"

    if rung not in NEXT_RUNG:
        return {"x": x, "y": None, "account": account, "ratio": None}
    up = cells[(NEXT_RUNG[rung], SENTENCE_OBJECTIVE, SENTENCE_SHOCKS)]
    if up["dollars"] is None:
        return {"x": x, "y": None, "account": account, "ratio": None}
    y = abs(up["dollars"][SENTENCE_DELTA][account] - pair[account])
    return {"x": x, "y": y, "account": account,
            "ratio": (y / x) if x else None}


# =============================================================================
# LAYOUT
# =============================================================================
st.set_page_config(page_title="Traditional vs Roth", layout="wide")
seed_state()

cube = load_cube()
header = cube["header"]

st.title("Traditional vs Roth retirement investing")

rail, main = st.columns([1, 4.2], gap="large")

# --- LEFT RAIL: the resilience ladder ----------------------------------------
# L3 claims fragility outranks the account choice, and a control you have to
# scroll to cannot outrank anything.  Always visible, never behind a click.
with rail:
    st.markdown("**Resilience ladder**")
    st.caption("Ten stops. Check what you have cleared, from the bottom up.")
    # CUT 4, PRE-APPROVED: colour bands become a single neutral rail and both
    # markers stay.  Rendered top-down so the picture matches the mockup, while
    # engine.LADDER_STOPS stays bottom-up because contiguity is a MODELING rule.
    for i in range(len(engine.LADDER_STOPS) - 1, -1, -1):
        st.checkbox(f"{i + 1}. {engine.LADDER_STOPS[i]}", key=f"stop_{i}")

profile = profile_from_state()
rung = profile.rung
cleared = engine.highest_contiguous_stop(profile.stops)

with rail:
    st.markdown(f"Rung: **{RUNG_LABEL[rung]}**  ·  {cleared} of 10 cleared")
    # D-37.  Non-contiguous checks render top-heavy and the app names the gap.
    # The copy points at the flowchart rather than issuing advice, because the
    # top stops are mostly illiquid or penalised -- telling a 401k-heavy user to
    # sell is the forced-liquidation branch this model treats as the bad outcome.
    if cleared < len(engine.LADDER_STOPS) and any(profile.stops[cleared:]):
        st.warning(
            "You have assets above a gap — the flowchart would prioritize "
            f"**{engine.LADDER_STOPS[cleared]}** first."
        )

with main:
    # --- TOP STRIP.  DECISIONS section 7, left to right ----------------------
    strip = st.columns([1.1, 1.5, 1.0, 1.5, 1.2, 1.1])

    with strip[0]:
        st.number_input("Current income", min_value=0, step=1_000,
                        key="income_35", format="%d")

    with strip[1]:
        # DESIGN 3.2's click-into number boxes.  D-19's four knots, linearly
        # interpolated; the ages are the decision and only the values move.
        st.markdown("**Income shape**")
        shape = st.columns(3)
        for col, age in zip(shape, (38, 55, 65)):
            with col:
                st.number_input(f"at {age}", min_value=0, step=1_000,
                                key=f"income_{age}", format="%d",
                                label_visibility="visible")

    with strip[2]:
        st.toggle("State income tax (while working)",
                  key="state_while_working")
        st.caption("Default assumes you earn in a taxing state and retire in "
                   "one that doesn't. Both are toggles.")

    with strip[3]:
        st.radio("Investment return rate", list(RETURN_BUTTONS),
                 key="return_button")
        st.caption("This input drives the picture, not the answer.")

    with strip[4]:
        st.toggle("Tax law changes", key="policy_on")
        st.number_input("in year", min_value=1,
                        max_value=engine.RETIREMENT_AGE
                        - engine.Profile.current_age - 1,
                        step=1, key="policy_year")
        st.caption("**You can still contribute — it just stops being worth "
                   "it.** Poland 2013 · Ireland 2011 · US SECURE Act 2019.")

    with strip[5]:
        st.button("Early-career preset", on_click=load_early_career,
                  width="stretch")
        # THE DISABLED MODEL BOX (section 7).  Disabled rather than absent: the
        # option space was mapped and two were built, and a disabled control
        # says so without implying the other seven exist.  The label is read off
        # the artifact rather than typed, so it cannot drift from the cube.
        # [SPRINT-7-CLEANUP] section 7 wants the tooltip to list all nine return
        # models from CONTEXT part D; part D was not in Sprint 6's reading list,
        # so the tooltip names the two IMPLEMENTED models and the count only.
        st.button(
            f"Model ({header['return_model']} resampling, "
            f"length {header['block_length']})",
            disabled=True, width="stretch",
            help="Nine return models were mapped and two are implemented: "
                 "#2 fixed real rate, which draws the page's headline, and #6 "
                 f"{header['return_model']} resampling over the historical "
                 "series, which produced the committed grid.",
        )

    st.divider()

    # --- THE COMPUTED HALF ---------------------------------------------------
    readings = deterministic_readings(
        profile, RETURN_BUTTONS[st.session_state["return_button"]],
        st.session_state["policy_year"]
    )
    dollars = x_and_y(cube["cells"], rung)

    # D-40 again, defensively: the axis has to reach past the second threshold
    # or it draws the deck's error by cropping instead of by placement.
    reach = [readings["marker"] * 100.0]
    for result in (readings["rules_hold"], readings["treatment_moves"]):
        if result.status == "crosses":
            reach.append(result.breakeven * 100.0)
    axis_max = min(100.0, max(70.0, 10.0 * (int(max(reach) / 10.0) + 2)))

    # --- $X, ABOVE THE AXIS --------------------------------------------------
    if dollars["x"] is not None:
        ratio_clause = (
            f" — about {1 / dollars['ratio']:.1f}× what moving up a rung is worth"
            if dollars["ratio"] else ""
        )
        st.markdown(f"#### Getting this right is worth ~${dollars['x']:,.0f}"
                    f"{ratio_clause}")
        st.caption(
            f"10th-percentile outcome (objective 4) at one shock, if you miss "
            f"the break-even by δ = {SENTENCE_DELTA} points. "
            f"Modeled for the reference profile at the **{RUNG_LABEL[rung]}** "
            "rung — your controls choose the rung, not the dollars."
        )

    st.altair_chart(
        threshold_axis(readings, st.session_state["policy_year"], axis_max),
        width="stretch",
    )

    verdict_block(readings, st.session_state["policy_on"],
                  st.session_state["policy_year"])
    two_rates_sentence(readings)

    st.divider()

    # --- THE BALANCE GRAPH ---------------------------------------------------
    st.markdown("#### What the two accounts hold while you save")
    st.altair_chart(balance_graph(readings, profile),
                    width="stretch")
    st.caption(
        f"**Units differ on purpose.** Traditional is a PRE-TAX balance and "
        f"Roth is ALREADY AFTER TAX — the dashed line is Traditional after tax "
        f"at your {readings['t_now']:.1%} deferral rate, and it sits on the "
        "Roth curve at every year, not just at 65. Same pre-tax dollars in "
        "(D-01); the divergence is the share the deferral is holding for the "
        "government."
    )
    st.caption(
        "**Nothing is clamped.** Balances are allowed to go negative and ruin "
        "is recorded rather than floored (D-38). At the Low rung a forced sale "
        "is not affordability-checked, so a saver with $8,000 in the account "
        "can 'sell' $73,959 of it — right for the grid, wrong as a sentence "
        "about a person."
    )

    st.divider()

    # --- $Y AND THE RESERVED DOT-PANEL REGION --------------------------------
    st.markdown("#### How fragile you are")
    if dollars["y"] is not None:
        st.markdown(
            f"#### Moving from {RUNG_LABEL[rung]} to "
            f"{RUNG_LABEL[NEXT_RUNG[rung]]} is worth ~${dollars['y']:,.0f}"
            + (f" — about {dollars['ratio']:.1f}× what getting the account "
               "right is worth" if dollars["ratio"] else "")
        )
    else:
        # D-36.  UNDEFINED at High, and the app says so rather than printing a
        # zero that would read as "moving up is worth nothing."
        st.markdown("#### There is no rung above High.")
        st.caption("$Y compares one step up, and High is the top of the "
                   "ladder — so it is undefined here rather than zero (D-36).")

    # D-15.  THE TWO RETURN MODELS ARE CAPTIONED WHERE THEY MEET, and the number
    # is the MEDIAN by decision, not the deterministic proxy and not the
    # withdrawn 3.4%.  Without this caption the discrepancy is real, visible and
    # unexplained, and the person who spots it will be a panelist.
    st.caption(
        f"**Two return models meet here.** The balance graph above is "
        f"deterministic at "
        f"{RETURN_BUTTONS[st.session_state['return_button']]:.0%} real. "
        f"The panels below come "
        f"from the historical series, which compounds at about "
        f"{SERIES_GEOMETRIC_MEAN:.1f}%. "
        f"**Thresholds agree across the two** — the scalar multiple guarantees "
        f"it — **but the dollars do not**: Traditional's balance at 65 has a "
        f"median of ${SERIES_MEDIAN_T65:,} under the series, "
        f"{SERIES_MEDIAN_GAP} against the deterministic proxy. The median "
        "rather than the mean, because the ensemble average is not what any "
        "one household lives (D-15, D-23)."
    )
    st.info(
        "**Fragility panels — Low, Mid and High, your rung highlighted.** "
        "The collapse is the lesson and a trend needs three points, so all "
        "three stay visible. [SPRINT-8-CLEANUP] Sprint 8 builds the panels; "
        "Sprint 6 owns this region and the caption above it."
    )

    st.divider()

    # --- PERSONALIZE -- the accordion ---------------------------------------
    # Progressive disclosure: one sentence up front, mechanism behind a toggle.
    # All rows render INCLUDING the grayed ones -- the grayed rows are the
    # evidence of completeness, and deleting a scoped-out mechanism makes the
    # model look smaller and less considered than it is.
    with st.expander("Personalize — the departures that move this answer"):
        # CUT 3, PRE-APPROVED: read-only, EXCEPT D4's row.  D4 is the correction
        # most users should apply to the default, because the defaults are
        # earn-taxed / retire-untaxed, which is the widest honest case (D-30).
        st.toggle("**D4** — You retire to a state that also taxes income",
                  key="state_in_retirement")
        st.caption("Leans Traditional ← → Roth. Editable. The two state "
                   "booleans share one 8.5% rate; turning this on narrows the "
                   "gap back toward baseline.")
        st.divider()
        st.markdown(
            "| # | Departure | Leans | Modeled |\n"
            "|---|---|---|---|\n"
            "| D1 | You withdraw across brackets, not at one rate | Traditional"
            " | yes |\n"
            "| D2 | Contribution limit binds — Roth shelters more real money | "
            "Roth | yes, off by default |\n"
            "| D3 | Taxable side account | Traditional | `TODO` |\n"
            "| D7 | Tax treatment changes prospectively, Roth only | Roth | "
            "yes, the toggle above |\n"
            "| D8 | Employer match | Traditional | `TODO` |\n"
        )
        st.caption(
            "Each row names its **lean**, not its verdict — a departure that "
            "leans Roth is not an argument for Roth. The threshold is the "
            "argument. D3 and D8 are real effects left unmodeled on purpose: "
            "both are Traditional-flavored money that arrives whether or not "
            "you choose it, so almost nobody is a pure case, and saying that "
            "is worth more than modeling it badly."
        )
        # [SPRINT-7-CLEANUP] Section 7 and DESIGN 3.3 both say EIGHT departure
        # rows.  Five are sourced above; D5 and D6 are named nowhere in Sprint
        # 6's reading list, so they are omitted rather than invented.  Sprint 7
        # owns the accordion and should add them from the departures table.
