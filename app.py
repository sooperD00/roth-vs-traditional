"""Traditional or Roth: the Streamlit app. DECISIONS section 7 is the layout.

The app computes one number and reads all the others. The two thresholds
and the today's-law marker come from engine.breakeven() at a fixed return,
solved live. Every other number on the page is a control's own state or a
value read from cube.json (D-12).

Keep out of this file:
  - stochastic code; spike_grid.py writes cube.json            (D-12)
  - tax literals; they live in tax.py                          (D-21)
  - copies of engine constants; import them or read the cube

Keep this file at the repo root, named app.py:
  - `import engine` works because Streamlit puts this file's folder on
    sys.path. The deploy does not install the project as a package.
  - railway.toml's start command names app.py, and
    tests/test_deploy_config.py reads the name from there.

The live solve takes about 54 ms per rerun. st.cache_data is insurance,
and Profile is frozen so the cache can hash it.
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
RUNG_MECHANISM = {"low": "no buffer", "mid": "some buffer", "high": "deep buffer"}
                                                # D-16's three mechanisms, in the
                                                # deck's own words.  Low sells at
                                                # the bottom, Mid fails to buy at
                                                # the bottom, High does neither.

# D-35.  TWO GATES SUPPRESS THE VERDICT AND A THIRD STOP GETS ITS OWN LINE, and
# the difference between those two sentences is D-61.  The corpus said this
# three ways -- D-35 names the first two gates, D-33's reason column reads as
# all three, and section 7 reads as the whole Low rung, which is any of stops
# 1-3 cleared.  D-35 is the decision and section 0 gives it precedence.
GATE_STOPS = (0, 1)             # $400 and $2,000.  Zero-indexed against
                                # engine.LADDER_STOPS, which is bottom-up.
DEBT_STOP = 2                   # High-interest debt.  Adds a line; suppresses
                                # nothing (D-61).

# ---- FIXED AXIS DOMAINS.  BOTH ARE FIXED AND FOR OPPOSITE REASONS ----------

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

# THE RATE AXIS IS FIXED BECAUSE THE NUMBER DOES NOT MOVE.  A dynamic domain
# rescaled when the nevermind year changed, so 32.5% slid across the screen
# while reading 32.5% -- the first lesson, taught backwards.  An axis that moves
# under a number that does not is the chart lying about the thing it exists to
# show.  0-100 is also the honest range for "what could a future tax rate be".
RATE_AXIS = [0.0, 100.0]

# D-24's sentence, and it lives HERE rather than inside the chart.  Two units
# share that axis -- t* is a future MARGINAL rate and the orange marker is an
# EFFECTIVE one -- and the axis is required to say so.  As a Vega title it got
# clipped at narrow viewports; as a caption it wraps.
RATE_AXIS_CAPTION = (
    "**future tax rate** — the bar's edge is a MARGINAL rate (t\\*), the "
    "orange line is your EFFECTIVE rate today"
)

# THE BALANCE AXES ARE FIXED BECAUSE THE NUMBER DOES MOVE.  Auto-scaling hid the
# L1 gesture completely: at 7% and at 12% the curve is the SAME SHAPE and only
# the tick labels change, so clicking appeared to do nothing.  Pinned, the curve
# visibly climbs.
#
# BOTH PANELS SHARE A CEILING ON PURPOSE.  $6M clears the highest reachable
# value among the shipped presets -- the archetype at 12% real tops out at
# $5,278,624 -- and a shared ceiling is what makes the two panels comparable
# rather than merely adjacent.  The log floor is $10,000: below the lowest
# first-year contribution either preset produces ($12,000 at early-career).
BALANCE_AXIS_LINEAR = [0.0, 6_000_000.0]
BALANCE_AXIS_LOG = [10_000.0, 6_000_000.0]

# EXPLICIT LOG TICKS, AND THE CEILING IS THE WHOLE REASON.  A log axis left to
# itself ticks at 1-3-10 multiples, so a $6M ceiling gets NO tick -- the top
# label reads $3M and the shared ceiling becomes invisible, which makes the two
# panels look like they are drawn to different scales when they are not.  Naming
# the values also kills the minor-gridline hatching a log axis draws by default,
# and it anchors both panels at the same three reference points: $1M, $2M, $6M.
BALANCE_TICKS_LOG = [10_000, 30_000, 100_000, 300_000,
                     1_000_000, 2_000_000, 6_000_000]
MILESTONES = (1_000_000.0, 2_000_000.0)   # The two numbers people cite as
                                          # "when you can retire".  Debatable as
                                          # targets, excellent as checkpoints.


TRAD_BLUE = "#2E7BC4"
ROTH_GREEN = "#1F8A5F"
MARKER_ORANGE = "#E8912A"
RAIL_GREY = "#8B949E"

# THE PANEL AXIS IS THE THIRD PINNED ONE AND IT IS THE WORST CASE OF THE THREE.
# The other two protect a lesson from being DELETED.  This one protects the
# reader from a lesson that is not there.
#
# Objective 5's break-even is the LEFT EDGE OF A PLATEAU rather than a point
# (D-51): P(not running out) counts a discrete event over 2,000 paths, so its
# difference is zero across an interval and the bisection lands ~0.08 points
# below t_now on every upper-panel cell.  Auto-scaled, the Mid panel turns
# 0.1757 points into its full width and draws four columns with one of them
# offset -- every number on screen correct, and a finding fabricated out of a
# solver artifact.  Pinned, Mid and High collapse to a visual point, which is
# D-22 and which is the truth.
#
# 0-40 IS THE DECK'S OWN DOMAIN (DESIGN 3.4), drawn before the trap that needs
# it was written.  It is a LITERAL and never a read of the cube: a domain sized
# to today's data is exactly the habit the two axis tests exist to punish.  Low
# spans 8.1346 points, a fifth of the width; Mid 0.1757 and High 0.0782.
PANEL_RATE_AXIS = [0.0, 40.0]
PANEL_RATE_TICKS = [0, 10, 20, 30, 40]

# D-34's encoding, REBUILT FOR FOUR OBJECTIVES.  The row assigned gray to (1, 2)
# and objective 2 is CUT (D-06), so "gray dots" is ONE dot and every plural
# attached to it described a panel that cannot be drawn.  Four groups, named
# here rather than left to a legend key: the reader has to be able to say which
# definition of "optimal" each colour is.  Objectives 4 and 5 share orange
# BECAUSE THEY ARE ONE FAMILY -- colour is the family, not the objective.
PANEL_OBJECTIVES = (1, 3, 4, 5)
OBJECTIVE_LABEL = {
    1: "1 · mean — expected value",
    3: "3 · median",
    4: "4 · 10th percentile — tail",
    5: "5 · P(not running out) — tail",
}
OBJECTIVE_COLOR = {1: "#6E7681", 3: "#C9D1D9",
                   4: MARKER_ORANGE, 5: MARKER_ORANGE}

# D-04a.  7 / 9 / 12, ALL REAL, default 7.  Each labelled with its nominal
# equivalent, and 12 labelled implausible ON PURPOSE: it is the button a skeptic
# reaches for first, and watching t* hold still there is L1 at full force.
RETURN_BUTTONS = {
    "7% real  (~10% nominal)": 0.07,
    "9% real  (~12% nominal)": 0.09,
    "12% real  (~15% nominal, implausible)": 0.12,
}


def escape_dollars(text: str) -> str:
    """`$` IS A KaTeX DELIMITER IN st.markdown, AND THIS PAGE IS ABOUT MONEY.

    Streamlit renders LaTeX between dollar signs, so any rendered string
    carrying TWO of them hands the span between them to the maths renderer.
    "crosses **$1M at age 56** and **$2M at age 64**" came out as one run of
    italic maths -- in the sentence that puts L1 in years, which is the most
    quotable line on the page.  Ten strings were affected and five of them
    paired.

    A LONE `$` IS HARMLESS, WHICH IS EXACTLY WHY THIS SURVIVED REVIEW.  The
    defect only appears when a SECOND one arrives, usually in a different edit
    months later, and it lands in whichever sentence happened to be nearby.  So
    the rule is every dollar sign rather than every pair, because a rule about
    pairs cannot be checked one string at a time.

    TWO ROUTES, ONE INVARIANT.  Literals this file owns escape inline as `\\$`;
    text arriving from outside -- `engine.LADDER_STOPS` carries "$400" and
    "$2,000" and the seam forbids editing it -- comes through here.
    `test_no_rendered_copy_hands_a_dollar_sign_to_the_maths_renderer` enforces
    the outcome and does not care which route was taken.
    """
    return text.replace("$", "\\$")


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
    accumulation = engine.accumulate(profile, paths[0], 0)

    # ---- TWO GUARDS, AND THEY RUN BEFORE breakeven() FOR A REASON -----------
    # THE ENGINE RAISES ON INPUTS THESE CONTROLS CAN REACH.  The module
    # docstring's "nothing raises" is a statement about the SEARCH under a valid
    # profile; it is not a promise about every profile a number_input can build.
    # Measured at Sprint 6 round 3:
    #
    #   current income 0, state tax OFF   ValueError: t_later 0.0 outside (0, 1)
    #   all income 0, either state        AssertionError: the difference is
    #                                     constant at 0.0 across the bracket
    #
    # `t_now` keys off the CURRENT-AGE income alone, so zeroing the one visible
    # "Current income" box is enough -- and the early-career preset sets
    # state_while_working=False, which makes preset-then-zero a TWO-CLICK path
    # to a traceback on screen. Guarding here rather than at the chart, because
    # the chart never gets reached.
    #
    # THE SEAM FORBIDS FIXING THIS IN engine.py (the app is a consumer), and it
    # is the right place for the guard anyway: these are control-range
    # questions, not model questions.
    if accumulation.trad <= 0:
        return {"blocked": "no_contributions"}
    if profile.t_now <= 0:
        return {"blocked": "no_deferral", "t_now": profile.t_now}

    try:
        rules_hold = engine.breakeven(profile, SENTENCE_OBJECTIVE, 0, None,
                                      paths)
        treatment_moves = engine.breakeven(
            profile, SENTENCE_OBJECTIVE, 0, policy_year, paths
        )
    except (ValueError, AssertionError) as exc:
        # BELT AND BRACES, AND IT NAMES WHAT HAPPENED RATHER THAN SWALLOWING IT.
        # A traceback on screen in front of a panel is the worst outcome this
        # app has; a caught raise that reports nothing is the second worst.
        return {"blocked": "engine", "detail": str(exc)}
    draw = engine.retirement_draw(
        accumulation.roth,
        profile.n_decumulation_years,
        engine.draw_return_rate(paths),
    )
    marker_gross = tax.gross_for_net(draw)

    return {
        "blocked": None,
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
def threshold_axis(readings: dict, policy_on: bool, policy_year: int):
    """ONE bar -- the scenario the toggle has selected -- and a ghost tick.

    CHANGED AT ROUND 2, AND THE ARGUMENT IS ABOUT WHAT TEACHES RATHER THAN WHAT
    IS TRUE.  Two stacked bars showed both thresholds honestly and nobody could
    read them: the rows share an axis, a marker and a palette, so a viewer has
    to construct the comparison out of one differing boundary.  Juxtaposition
    asks the reader to do the work.  MOVEMENT DOES THE WORK FOR THEM -- a
    boundary that slides when you click is attributed causally and instantly,
    which is the whole reason the toggle exists.

    D-10 STILL HOLDS AND THAT IS WHY THE GHOST TICK IS HERE.  Both thresholds
    are computed every rerun and both are on screen always; the inactive one is
    a dimmed tick with its own label rather than a second bar.  That keeps the
    panelist who never touches the toggle from seeing only one exposure -- the
    exact failure D-10 was written to correct -- and it does something two rows
    could not: it shows WHERE THE BOUNDARY IS ABOUT TO GO, so the movement is
    anticipated, and a movement you saw coming reads as a mechanism rather than
    as an animation.

    THE DOMAIN IS FIXED AT 0-100 (see RATE_AXIS).  Nothing about this chart
    rescales, ever.

    THE SECOND THRESHOLD IS TO THE RIGHT.  58.4% against 32.5% (D-40).  The
    design deck drew it at 14% with Roth winning beyond it and the algebra
    cannot do that: a policy that harms only Roth strictly RAISES the rate at
    which Roth becomes worthwhile.

    TWO UNITS SHARE THIS AXIS AND IT SAYS SO (D-24).  t* is a future MARGINAL
    rate; the today's-law marker is an EFFECTIVE rate.
    """
    if policy_on:
        active, inactive = readings["treatment_moves"], readings["rules_hold"]
        active_label = f"if tax rules change at year {policy_year}"
        inactive_label = "if rules hold instead"
    else:
        active, inactive = readings["rules_hold"], readings["treatment_moves"]
        active_label = "assuming tax rules hold"
        inactive_label = f"if rules change at year {policy_year}"

    lo, hi = RATE_AXIS
    marker = readings["marker"] * 100.0

    if active.status == "crosses":
        edge = active.breakeven * 100.0
        bars = [{"lo": lo, "hi": edge, "who": "Traditional wins"},
                {"lo": edge, "hi": hi, "who": "Roth wins"}]
        edge_text = f"{edge:.1f}%"
    else:
        # NO BOUNDARY IS DRAWN BECAUSE THERE IS NO CROSSING.  D-35 forbids
        # printing nothing, so the verdict block carries the sentence and the
        # bar carries one colour end to end.
        who = "Traditional wins" if active.status == "always_trad" else "Roth wins"
        bars = [{"lo": lo, "hi": hi, "who": who}]
        edge = None
        edge_text = "no break-even"

    frame = pd.DataFrame([dict(b, row=active_label) for b in bars])
    scale = alt.Scale(domain=RATE_AXIS, nice=False)
    row_axis = alt.Axis(labelLimit=260, labelFontSize=13)
    x_axis = alt.Axis(values=list(range(0, 101, 10)), format=".0f",
                      labelExpr="datum.value + '%'", grid=True)

    chart = alt.Chart(frame).mark_bar(height=42).encode(
        x=alt.X("lo:Q", title=None, scale=scale, axis=x_axis), x2="hi:Q",
        y=alt.Y("row:N", title=None, axis=row_axis),
        color=alt.Color(
            "who:N", title=None,
            scale=alt.Scale(domain=["Traditional wins", "Roth wins"],
                            range=[TRAD_BLUE, ROTH_GREEN]),
            # LEGEND AT THE BOTTOM.  At the top it lands in the same 40px band
            # as the boundary label and the marker label, and in a narrow
            # container all three overprint -- which is what a review screenshot
            # caught.  Nothing above the bar now except the two value labels.
            legend=alt.Legend(orient="bottom", direction="horizontal"),
        ),
    )

    def _mark(value):
        """A one-row frame carrying the SAME band key as the bar.

        EVERY ANNOTATION ENCODES y ON THE BAR'S OWN BAND SCALE, and that is the
        round-3 review fix rather than a style choice.  These layers previously
        used absolute pixel offsets -- y=alt.value(121) and friends -- which
        assumed the plot area was the 200px passed to .properties(height=...).
        IT IS NOT.  Streamlit sends autosize {"type": "fit"}, which fits the
        WHOLE view into that height, so the title, the axis and the legend all
        come out of it and the drawable area is nearer 120px.  The annotations
        landed below the axis, past the legend, hanging off the bottom of the
        chart -- while every number in them was correct.
        """
        return alt.Chart(pd.DataFrame([{"at": value, "row": active_label}]))

    def _place(dy):
        # dy is relative to the band centre, so it survives any plot height
        # autosize decides on. Nothing here may be an absolute pixel again.
        # THE SAME y SPEC AS THE BAR, NOT axis=None. Vega-Lite MERGES axes
        # across a layered chart, so one layer suppressing the axis suppresses
        # it for all of them -- which silently deleted the row label naming
        # which scenario is on screen.
        return dict(x=alt.X("at:Q", scale=scale, axis=x_axis),
                    y=alt.Y("row:N", title=None, axis=row_axis),
                    tooltip=alt.value(None)), dy

    def _text(value, text, dy, **mark):
        enc, dy = _place(dy)
        return _mark(value).mark_text(text=text, dy=dy, **mark).encode(**enc)

    def _rule(value, **mark):
        # x only: a full-height locator, which needs no y arithmetic at all.
        return _mark(value).mark_rule(**mark).encode(
            x=alt.X("at:Q", scale=scale, axis=x_axis), tooltip=alt.value(None))

    # THE LABEL IS A MARK PROPERTY, NOT AN ENCODING, and that is deliberate:
    # text carried in a data column travels to the browser in the arrow payload
    # rather than in the spec, which renders identically and is invisible to a
    # test.  A literal is in the spec, so the boundary reading 32.5% is
    # assertable -- and this is the sprint's cheapest detector.
    chart += _text(edge if edge is not None else (lo + hi) / 2.0, edge_text,
                   dy=-36, fontSize=16, fontWeight="bold", color="#E6EDF3")

    # THE MARKER LABEL IS LEFT-ALIGNED OFF THE LINE.  Centred, the dashed rule
    # runs straight through the digits.
    chart += _rule(marker, strokeDash=[6, 4], strokeWidth=2.5,
                   color=MARKER_ORANGE)
    chart += _text(marker, f"you: {marker:.1f}%", dy=-58, align="left", dx=6,
                   fontSize=12, color=MARKER_ORANGE)

    # ---- THE OTHER SCENARIO, DRAWN AS MOVEMENT RATHER THAN AS A POSITION ----
    # THIS WAS A MEANING BUG, NOT A LAYOUT ONE.  A bare tick at the inactive
    # threshold inherits the colour it is drawn on, and that colour belongs to
    # the OTHER scenario.  At the early-career preset the inactive threshold is
    # 29.1%, which lands in the green "Roth wins" band -- so the chart said
    # "29.1% is Roth territory" when crossing it is exactly what puts that user
    # on the TRADITIONAL side.  The most counterintuitive result in the project,
    # drawn backwards.
    #
    # It is also the design deck's own error in a new costume: 3.5 drew the
    # second threshold so that Roth appeared to win beyond it.  D-40 corrected
    # the number and the direction; this corrects the READING.
    #
    # The fix is words, because WORDS CANNOT BE RECOLOURED BY THE BAND UNDER
    # THEM. The arrow carries the direction of travel; the clause carries the
    # consequence.
    if inactive.status == "crosses":
        ghost = inactive.breakeven * 100.0
        side = "Traditional" if marker < ghost else "Roth"
        arrow = "\u2192" if (edge is None or ghost > edge) else "\u2190"
        chart += _rule(ghost, strokeWidth=2, color=RAIL_GREY, opacity=0.6,
                       strokeDash=[2, 3])
        # ANCHORED AT THE RIGHT END OF THE SPAN, not at the ghost. Anchored at
        # the ghost, a leftward movement puts the label underneath the span it
        # describes and the orange marker rule prints through it.
        anchor = ghost if edge is None else max(edge, ghost)
        # THE SENTENCE IS ~55 CHARACTERS AND THE AXIS IS 100 UNITS WIDE, so it
        # spans roughly half of it and cannot be anchored blindly: at the
        # early-career preset the span ends at 29.1% and a right-aligned label
        # runs off the left edge of the chart. Anchor away from the near wall.
        right = anchor > 50.0
        chart += _text(anchor,
                       f"{arrow} {ghost:.1f}% {inactive_label} \u2014 "
                       f"you would be on the {side} side",
                       dy=42, align="right" if right else "left",
                       dx=-6 if right else 6, fontSize=11.5, color=RAIL_GREY)

    # THE TITLE IS NOT A VEGA TITLE ANY MORE, AND THAT IS THE FIX FOR A DEFECT
    # THAT ONLY APPEARED SOMETIMES.  It read as one line at a wide viewport and
    # wrapped at a narrow one, and `autosize: fit` spends `height` on the title,
    # the axis AND the legend before the plot gets any -- so the second line had
    # nowhere to go and Vega clipped the text through the middle of the letters.
    # Every number was correct; the sentence explaining the units was sheared in
    # half, which is D-24's whole contribution to this chart.
    #
    # A Streamlit caption cannot clip.  It wraps, it reflows, and it is the same
    # instrument the rest of the page already uses for chart prose.  Rendered
    # from RATE_AXIS_CAPTION at the call site, immediately above the chart.
    return chart.properties(
        # Autosize "fit" spends this on the axis and the legend as well as the
        # plot, so it is a TOTAL, not a drawable area.  The title no longer
        # comes out of it, which is the whole 24px this went up by.
        height=264,
    )


def _active(readings: dict, policy_on: bool):
    """The threshold the verdict is measured against.  The toggle selects it."""
    return readings["treatment_moves"] if policy_on else readings["rules_hold"]


def binding_gate(stops: tuple) -> int | None:
    """The lowest of D-35's two gates the user has not cleared, or None.

    TWO BOOLEANS, AND WHICH TWO IS D-61.  D-35 names the first two stops -- $400
    and $2,000 -- and nothing else suppresses.  Stop 3 gets its own line and
    takes the verdict away from nobody, which is the reading that keeps this
    function returning a GATE rather than a rung: `rung` is already on screen
    three feet away and it answers a different question.

    It is deliberately not `highest_contiguous_stop() < 2`.  D-37's contiguity
    rule is about where the rung sits; this is about which specific gate is
    binding, and the copy has to name it.
    """
    for stop in GATE_STOPS:
        if not stops[stop]:
            return stop
    return None


def verdict_block(readings: dict, policy_on: bool, policy_year: int,
                  stops: tuple) -> None:
    """THE ANSWER, AND NOTHING ELSE.  One line, above the chart that argues it.

    D-35 REPLACES THIS LINE AND ONLY THIS LINE.  The suppression outranks every
    branch below it, including the two sentinels: a profile can be both
    always_trad and standing under an unmet $400 gate, and the gate is the more
    urgent true thing.  `t*`, both thresholds, the two-rates sentence and the
    $X/$Y pair all survive one function down -- hiding numbers would make the
    page read as a lockout, and this app has never once printed nothing.

    SPLIT FROM ITS OWN EXPLANATION AT ROUND 2.  The verdict was rendering below
    the threshold axis, so the page asked a reader to interpret a bar before it
    told them what the bar concluded.  A page whose answer arrives after its
    evidence is a page that reads as a proof rather than as an answer.

    THE WASH BAND IS +/- 2 POINTS (D-02).  Inside it the headline says it is a
    wash; outside it names the winner.  At the archetype the gap is 17.3 points
    so the band never fires there -- it exists for the profiles a panelist types
    in, which is exactly what happens at a demo.

    A NON-CROSSING PROFILE PRINTS COPY, NEVER A NULL (D-35).  The reachable case
    is always_trad: drag the nevermind year to 1 or 2 and the frozen allowance
    is one or two years of contributions, so Roth never catches up at any rate
    on the axis.  D-40 at full strength rather than an error state.
    """
    active = _active(readings, policy_on)
    marker = readings["marker"] * 100.0

    # D-35, AND IT RUNS FIRST.  Section 7 supplies the replacement sentence
    # verbatim; verdict_detail names which gate is binding, which is the whole
    # reason Sprint 6 reserved the room down there rather than up here.
    if binding_gate(stops) is not None:
        st.markdown("### This election is not your binding constraint yet.")
        return

    if active.status == "always_trad":
        st.markdown("### No future tax rate rescues Roth here.")
    elif active.status == "always_roth":
        st.markdown("### No future tax rate rescues Traditional here.")
    else:
        gap = active.breakeven * 100.0 - marker
        if abs(gap) <= WASH_BAND_POINTS:
            st.markdown("### It's a wash.")
        else:
            st.markdown(f"### {'Traditional' if gap > 0 else 'Roth'}, by "
                        f"{abs(gap):.1f} points.")


def verdict_detail(readings: dict, policy_on: bool, stops: tuple) -> None:
    """The sentences that describe the chart, and they sit beneath it.

    THE NUMBERS SURVIVE THE SUPPRESSION.  D-35's point is that the verdict line
    is REPLACED while t*, both thresholds and the $X/$Y sentence stay -- hiding
    them would make the page read as a lockout rather than as an answer.
    """
    active = _active(readings, policy_on)
    marker = readings["marker"] * 100.0

    if active.status == "always_trad":
        st.markdown(
            f"A rule change this early freezes "
            f"**\\${readings['allowance']:,.0f}**"
            " tax-free and taxes everything after it as ordinary income. "
            "Traditional wins at every rate on the axis. There is no line here "
            "to be on the wrong side of."
        )
    elif active.status == "always_roth":
        # UNREACHABLE FROM THESE CONTROLS TODAY and written anyway.  Under
        # D-01's convention roth_65 is exactly trad_65 * (1 - t_now), so the
        # difference is trad_65 * (t_now - t_later) and its sign always flips
        # inside the bracket.  It stops being unreachable the day the accordion's
        # D2 row becomes editable, which is Sprint 7's.
        st.markdown(
            "This profile fills the Roth to the contribution cap, so both "
            "accounts receive the same nominal dollars and the Roth's are "
            "already taxed. Roth wins at every rate on the axis."
        )
    else:
        side = "left" if active.breakeven * 100.0 > marker else "right"
        st.markdown(
            f"Your withdrawal rate today is {marker:.1f}%. The future marginal "
            f"rate that would tie them is {active.breakeven:.1%}. You are to "
            f"the {side} of it."
        )

    if active.status != "crosses" and readings["rules_hold"].status == "crosses":
        st.markdown(
            "**Under current rules the break-even is still "
            f"{readings['rules_hold'].breakeven:.1%}**, and your withdrawal "
            f"rate today is {marker:.1f}%."
        )

    # D-10's label.  It is a statement about TWO simultaneous exposures, which
    # is why the inactive threshold stays on the axis as a ghost tick rather
    # than disappearing with the toggle.
    st.caption(
        "**Roth bets the treatment holds. Traditional bets the rates do.** "
        "Neither is the neutral choice — pick which rule you'd rather be "
        "exposed to."
    )

    # ---- D-35'S SLOT, FILLED.  The room Sprint 6 reserved here is now the copy.
    # THE COPY IS AN ANSWER, NOT A LOCKOUT, and blocked_notice() set that
    # precedent three branches ago: each of these is a true statement about the
    # profile rather than an apology for the software.  Nothing above is hidden.
    gate = binding_gate(stops)
    if gate is not None:
        st.markdown(
            f"**{escape_dollars(engine.LADDER_STOPS[gate])} sits below this "
            "question on the "
            "flowchart.** Without it a life event forces a sale, which is the "
            "Low-rung mechanism the panels below draw — and it moves the "
            "outcome further than the account election can at any rate on this "
            "axis. The break-even is still true. It is just not the number "
            "doing the most work for you yet."
        )

    if not stops[DEBT_STOP]:
        # STOP 3 GETS ITS OWN COPY AND SUPPRESSES NOTHING (D-61).  Arithmetic
        # rather than advice: no 401(k) election returns 20% guaranteed, so this
        # comparison needs no model and no rate.
        st.markdown(
            f"**Paying off {escape_dollars(engine.LADDER_STOPS[DEBT_STOP])} "
            "beats either "
            "account, at any tax rate.** That is arithmetic rather than "
            "advice — no 401(k) election returns 20% guaranteed."
        )


def blocked_notice(readings: dict) -> None:
    """Copy for a profile the deterministic line cannot be computed for.

    D-35's principle, applied one layer out: the page never prints nothing, and
    it never prints a traceback. Each of these is a real statement about the
    profile rather than an apology for the software.
    """
    reason = readings["blocked"]

    if reason == "no_deferral":
        # THIS IS AN ANSWER, NOT AN ERROR, AND IT IS THE STRONGEST FORM OF ONE.
        # At t_now = 0 the difference is trad_65 * (0 - t_later), which is
        # negative for every rate in the bracket -- so Roth wins everywhere, and
        # it wins for the plainest possible reason. The engine cannot SAY it:
        # its search runs over (0.01, 0.95) and evaluates at t_now, so a t_now
        # of exactly 0 is outside its own bracket. The algebra is unambiguous
        # even where the search is not, so the app states the conclusion and is
        # explicit about not having drawn it.
        st.markdown("### Roth, at every rate.")
        st.markdown(
            "Your marginal rate today is **0%**, so a Traditional contribution "
            "defers no tax at all. There is nothing to trade away, and so "
            "nothing to trade it for — Roth wins at every future rate."
        )
        st.caption(
            "No axis is drawn because there is no break-even to draw: the "
            "search runs over rates from 1% to 95% and the answer here sits "
            "outside it. Raise the current income, or turn on state income tax "
            "while working, and the chart returns."
        )
    elif reason == "no_contributions":
        st.markdown("### Nothing to compare yet.")
        st.markdown(
            "At this income the model contributes nothing, so there is no "
            "balance in either account and no rate at which the two could tie."
        )
        st.caption("Raise the current income and the whole page returns.")
    else:
        st.markdown("### This profile can't be evaluated.")
        st.markdown(
            "The engine declined it rather than returning a number, which is "
            "the behaviour you want from it. Change a control and the page "
            "returns."
        )
        st.caption(f"Reported: {readings.get('detail', 'no detail given')}")


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
def milestone_ages(series, current_age: int) -> dict:
    """First age at which the balance clears each milestone.  None if never.

    THE POINT OF THIS IS TO PUT L1 IN YEARS RATHER THAN IN DOLLARS.  Dollars at
    65 are abstract -- $2.1M and $5.3M are both "a lot" and the difference does
    not land.  Ages land: eight working years to go from the first million to
    the second at 7% real, five at 12%.  Same gesture, a unit a person feels.
    """
    return {
        target: next((current_age + i for i, v in enumerate(series)
                      if v >= target), None)
        for target in MILESTONES
    }


def _balance_panel(frame, order, ages, scale_type: str, title: str,
                   legend: bool):
    """One balance panel.  The pair differs ONLY in the y scale."""
    log = scale_type == "log"
    domain = BALANCE_AXIS_LOG if log else BALANCE_AXIS_LINEAR
    y = alt.Y("d:Q", title=None,
              scale=alt.Scale(type=scale_type, domain=domain, nice=False),
              # alt.Undefined, not None: Altair validates the schema at
              # construction and `None` is not a legal `values`, so the linear
              # panel has to OMIT the property rather than null it.
              axis=alt.Axis(format="$,.0s", grid=True,
                            values=(BALANCE_TICKS_LOG if log
                                    else alt.Undefined)))

    lines = alt.Chart(frame).mark_line(strokeWidth=2.5).encode(
        x=alt.X("age:Q", title="age",
                scale=alt.Scale(domain=[ages[0], ages[-1]], nice=False)),
        y=y,
        color=alt.Color(
            "series:N", title=None, sort=order,
            scale=alt.Scale(domain=order,
                            range=[TRAD_BLUE, ROTH_GREEN, MARKER_ORANGE]),
            legend=(alt.Legend(orient="top", direction="horizontal", columns=1)
                    if legend else None),
        ),
        strokeDash=alt.StrokeDash(
            "series:N", sort=order,
            scale=alt.Scale(domain=order, range=[[1, 0], [1, 0], [7, 4]]),
            legend=None,
        ),
    )

    # THE TWO CHECKPOINTS, DRAWN ON BOTH PANELS.  They are the clearest place to
    # SEE the difference between the two scales: on the linear panel the $1M and
    # $2M rules crowd the top, and on the log panel they are evenly spaced,
    # because a doubling is a doubling wherever it happens.
    marks = pd.DataFrame([{"d": m} for m in MILESTONES])
    rules = alt.Chart(marks).mark_rule(
        color=RAIL_GREY, opacity=0.45, strokeDash=[3, 4],
    ).encode(y=alt.Y("d:Q", scale=alt.Scale(type=scale_type, domain=domain,
                                            nice=False)))

    return (lines + rules).properties(
        width=300, height=300,
        title=alt.TitleParams(title, fontSize=12, color=RAIL_GREY,
                              anchor="start"),
    )


def balance_graphs(readings: dict, profile: engine.Profile):
    """THE SAME DATA TWICE -- linear on the left, logarithmic on the right.

    THE PAIR IS THE LESSON AND NEITHER PANEL CARRIES IT ALONE.  Measured at the
    archetype: the Traditional-to-Roth gap is a CONSTANT RATIO, 1.481481..., to
    nine decimal places at every one of the thirty years -- it is exactly
    1 / (1 - t_now) and it never budges, which is D-22's identity.  On the LOG
    panel that reads as what it is: two dead-parallel lines, 0.170696 decades
    apart, from the first contribution to the last.

    ON THE LINEAR PANEL THE IDENTICAL RATIO LOOKS LIKE A GAP THAT EXPLODES --
    $7,962 at 35, $685,382 at 64, an eighty-six-fold widening of a number that
    did not change.  That is not a drawing error; it is what a linear axis does
    to a ratio, and it is the visual root of "the account choice matters more
    later, so I will decide later."  IT DOES NOT MATTER MORE LATER.  The ratio
    was fixed the day the first contribution was made.

    WHY BOTH PANELS AND NOT JUST THE HONEST ONE.  The linear panel is how
    everyone's brokerage statement draws this, so it is the picture the audience
    arrives holding.  Deleting it wins the argument against nobody.  Showing the
    two side by side makes the misreading visible AS a misreading, which is the
    only way to retire it.

    BOTH PANELS ARE PINNED AND SHARE A CEILING, so the L1 gesture works on both:
    click a return rate and the curves climb rather than the labels changing.

    A LOG AXIS CANNOT DRAW A NON-POSITIVE NUMBER, so non-positive points are
    dropped from BOTH panels rather than clamped -- keeping the two panels drawn
    from exactly the same rows matters more here than showing one extra point on
    the left.  The gap in the curve is honest; a clamp would not be (D-38).

    NOTE THE UNITS (the G4 trap drawn).  trad_by_year is PRE-TAX and
    roth_by_year is ALREADY AFTER TAX.  The dashed orange curve is Traditional
    after tax and lies exactly on Roth -- worst deviation across all thirty
    years is 1.16e-10 dollars, which is float noise.
    """
    t_now = readings["t_now"]
    ages = [profile.current_age + i for i in range(len(readings["trad_by_year"]))]
    rows = []
    for age, trad, roth in zip(ages, readings["trad_by_year"],
                               readings["roth_by_year"]):
        after_tax = trad * (1.0 - t_now)
        if min(trad, roth, after_tax) <= 0:
            continue
        rows.append({"age": age, "series": "Traditional (pre-tax)", "d": trad})
        rows.append({"age": age, "series": "Roth (after tax)", "d": roth})
        rows.append({"age": age, "series": "Traditional after tax",
                     "d": after_tax})
    if not rows:
        return None
    frame = pd.DataFrame(rows)
    order = ["Traditional (pre-tax)", "Roth (after tax)",
             "Traditional after tax"]

    left = _balance_panel(frame, order, ages, "linear",
                          "linear — how a statement draws it", legend=True)
    right = _balance_panel(frame, order, ages, "log",
                           "logarithmic — what the ratio does",
                           legend=False)
    return alt.hconcat(left, right, spacing=40).resolve_scale(
        color="shared", strokeDash="shared")


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
# THE FRAGILITY PANELS.  48 cells, indexed.  THIS SPRINT COMPUTES NOTHING --
# every dot is cells[(rung, objective, shocks)]["breakeven"], read and scaled to
# percent for display.  There is no breakeven() call here and no second x_and_y.
# =============================================================================
def panel_frame(cells: dict) -> pd.DataFrame:
    """The whole cube, long-form, ready to plot.  One row per dot, 48 of them.

    SEPARATE FROM THE CHART ON PURPOSE.  A test that wants to know what the
    panels DRAW should not have to parse a Vega spec to find out -- the two axis
    tests already do that and their docstrings say why it is a last resort.
    This function is the same data the spec carries, in a shape a test can
    assert on directly.
    """
    return pd.DataFrame([
        {"rung": rung,
         "objective": OBJECTIVE_LABEL[objective],
         "shocks": shocks,
         "rate": cells[(rung, objective, shocks)]["breakeven"] * 100.0}
        for rung in RUNG_LABEL
        for objective in PANEL_OBJECTIVES
        for shocks in range(4)
        if cells[(rung, objective, shocks)]["breakeven"] is not None
    ])


def _fragility_panel(frame, rung: str, user_rung: str, line, order, legend):
    """One rung's panel.  The three differ ONLY in which rows they draw.

    THE SHARED DOMAIN IS THE WHOLE ARGUMENT AND IT IS NOT A STYLE CHOICE.  Let
    either upper panel size itself to its own data and 0.08 points of solver
    artifact becomes the full panel width: four columns, one of them offset,
    with every number on screen correct.  That is the third occurrence of the
    defect the two axis tests upstairs were written for, and the first that
    would INVENT a finding rather than delete one.
    """
    active = rung == user_rung
    scale = alt.Scale(domain=PANEL_RATE_AXIS, nice=False)
    x_axis = alt.Axis(values=PANEL_RATE_TICKS, format=".0f",
                      labelExpr="datum.value + '%'", grid=False,
                      labelFontSize=10)

    dots = alt.Chart(frame).mark_circle(
        # THE USER'S RUNG IS HIGHLIGHTED AND THE OTHER TWO ARE DIMMED, NEVER
        # DROPPED (DESIGN 3.1).  The collapse is the lesson and a trend needs
        # three points; showing only the user's rung deletes the comparison L3
        # is made of.
        # SIZED DOWN AFTER LOOKING AT IT.  At size 120 the four objectives in a
        # Low row merged into one blob: the within-row spread is 1.4656 points
        # at three shocks, which on a domain pinned for Low's 8.1346 is under
        # ten pixels.  Smaller dots plus partial opacity let an overlap read as
        # an overlap, which is what "no jitter" (D-34) depends on -- dots on top
        # of each other are supposed to MEAN the objectives agree, and that
        # cannot be read off a shape that is opaque and too big to resolve.
        size=68 if active else 44,
        opacity=0.88 if active else 0.34,
    ).encode(
        x=alt.X("rate:Q", title=None, scale=scale, axis=x_axis),
        # ROW = SHOCK COUNT, 0 AT TOP (D-34).  An ordinal y sorted ascending
        # puts 0 at the top, which is the deck's own reading order: the
        # undisturbed life first and the descent below it.
        # THE Y TITLE RIDES ON THE LEFTMOST PANEL ONLY.  Repeated across three
        # panels it reads as three separate charts, which is the opposite of
        # what one shared domain is for.
        y=alt.Y("shocks:O", title=("life events" if legend else None),
                sort="ascending",
                axis=alt.Axis(labelFontSize=11, titleFontSize=10, grid=False)),
        color=alt.Color(
            "objective:N", title=None, sort=order,
            scale=alt.Scale(domain=order,
                            range=[OBJECTIVE_COLOR[o] for o in PANEL_OBJECTIVES]),
            legend=(alt.Legend(orient="bottom", direction="vertical",
                               columns=1, labelFontSize=10)
                    if legend else None),
        ),
        tooltip=[alt.Tooltip("objective:N", title="definition of optimal"),
                 alt.Tooltip("shocks:O", title="life events"),
                 alt.Tooltip("rate:Q", title="break-even t*", format=".4f")],
    )

    layers = dots
    if line is not None:
        # D-15 DRAWN.  User inputs move the LINE; they never move the dots.  The
        # dots are the archetype's and the line is the user's own break-even, so
        # setting the state toggle slides the line through a cloud that stays
        # where it is -- which is the mismatch stated as an interaction rather
        # than buried in a caption.
        rule = alt.Chart(pd.DataFrame([{"at": line}])).mark_rule(
            color=TRAD_BLUE, strokeWidth=2, opacity=1.0 if active else 0.45,
        ).encode(x=alt.X("at:Q", scale=scale, axis=x_axis),
                 tooltip=alt.value(None))
        layers = dots + rule

    return layers.properties(
        width=196, height=186,
        title=alt.TitleParams(
            f"{RUNG_LABEL[rung]} — {RUNG_MECHANISM[rung]}"
            + ("  ·  your rung" if active else ""),
            fontSize=12, anchor="start",
            color="#E6EDF3" if active else RAIL_GREY,
        ),
    )


def fragility_panels(cells: dict, user_rung: str, line):
    """Three panels, ONE shared pinned domain.  L3 shown rather than asserted.

    THREE, NEVER TWO.  The cut ladder refuses a two-rung version in writing: it
    saves five minutes and costs L3, which needs three points to read as a
    trend.  The design deck drew two because the third had not been named yet.

    WHAT THE READER IS SUPPOSED TO SEE.  Low's four definitions of "optimal"
    fan out across 8.1346 points of tax rate as the life events stack up.  Mid
    and High do not move -- 0.1757 and 0.0782 points, which at this scale is one
    dot.  That is D-22 and it is derived rather than observed: only Low's
    penalty is asymmetric, so 36 of 48 cells equal `t_now` exactly.

    ONE hconcat, NOT THREE CHARTS IN THREE COLUMNS, for the reason the balance
    pair already records: three charts carry three legends and their plot areas
    start at three different heights, so the panels stop lining up and a reader
    compares them wrongly.
    """
    frame = panel_frame(cells)
    order = [OBJECTIVE_LABEL[objective] for objective in PANEL_OBJECTIVES]
    panels = [
        _fragility_panel(frame[frame["rung"] == rung], rung, user_rung, line,
                         order, legend=(rung == "low"))
        for rung in RUNG_LABEL
    ]
    return alt.hconcat(*panels, spacing=18).resolve_scale(color="shared")


# =============================================================================
# THE LADDER FOLLOWS THE SCROLL.  One CSS block, and it is the only one.
# =============================================================================
# WHY THIS EXISTS.  The ten checkboxes drive the rung, the rung drives which
# fragility panel is highlighted, and the panels are at the BOTTOM of the page.
# A control you have to scroll away from in order to see its own effect is the
# same defect DESIGN 3.1 named when it put the ladder in a rail at all: *a
# control you have to scroll to cannot outrank anything.*
#
# WIDENED AT D-66 TO EVERY CONTROL, and the argument generalised the moment it
# was written down.  The return buttons move the balance graphs in the middle of
# the page; the state toggle moves the line through the dot cloud at the bottom.
# Both were in a strip across the top that scrolled away from every graph they
# move.  The ladder was the loudest instance, not the only one.
#
# THE ONE COST, AND IT IS REAL.  A rail holding every control can be taller than
# the viewport, and then the rail scrolls INSIDE itself -- with the ladder at
# the bottom, it is the ladder that goes.  That internal scroll persists while
# the page scrolls, so it is a one-time adjustment rather than a fight, but on a
# short viewport it is the first thing to feel wrong.  `gap="xxsmall"` on the
# container is the density lever; the checkbox list is the tallest block.
#
# THE ANCHOR IS STREAMLIT'S OWN, NOT A GUESSED SELECTOR.  `st.container(key=x)`
# emits `class="st-key-x"`, which is a documented hook.  `:has()` then finds the
# COLUMN that contains it, so this does not depend on the rail being the first
# column or on how many `st.columns()` calls the page makes -- and the top strip
# makes two more, which a `:first-child` rule would have caught by accident.
#
# THE THREE NUMBERS, AND THE MIDDLE ONE IS THE KNOB.
#   4.5rem   floor.  Clears Streamlit's own fixed header.
#   24rem    HALF THE RAIL'S HEIGHT.  RE-MEASURED AT D-66, when the rail went
#            from ten checkboxes to every control on the page: four income
#            boxes, three toggles, a radio, a year box, ten checkboxes and the
#            rung readout, ~48rem in total.  This is what centres it, and it is
#            the only value worth touching -- raise it to sit higher, lower it
#            to sit lower.
#   6rem     ceiling, DOWN FROM 12rem AT D-66 FOR THE SAME REASON.  `top` also
#            applies at scroll zero, where the rail's natural position is
#            already near the top, so an uncapped centring offset pushes the
#            rail visibly DOWN on first paint.  A rail this tall barely has
#            room to centre at all, so the cap does most of the work now and
#            the rail effectively pins just under the header.
#
# WHAT IT CANNOT DO.  Sticky has ONE threshold, so an element cannot be both
# flush at scroll zero and centred while scrolling.  This picks centred, because
# scrolling is when the rail has a job.  Set the middle number to 0rem and it
# pins to the top instead.
STICKY_RAIL_CSS = """
<style>
  /* A flex item is stretched to the row's full height by default, and a
     full-height element has nothing to stick to.  Both properties say the same
     thing from the two sides; either alone is enough, and saying it twice
     costs nothing and survives one of them being overridden. */
  [data-testid="stHorizontalBlock"]:has(.st-key-resilience_rail) {
    align-items: flex-start;
  }
  [data-testid="stColumn"]:has(.st-key-resilience_rail) {
    position: sticky;
    align-self: flex-start;
    top: clamp(3rem, calc(50vh - 24rem), 6rem);
    /* If the rail is taller than the viewport it scrolls INSIDE itself rather
       than running off the bottom.  A laptop at 768px is the case that needs
       this and it is the case a demo happens on. */
    max-height: calc(100vh - 4.5rem);
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 0.5rem;
    scrollbar-width: thin;
    z-index: 5;
  }
  /* THE SILENT KILLER.  `position: sticky` does nothing at all if any ancestor
     between it and the scroll container establishes its own scroll context.
     Nothing in Streamlit 1.62 sets one here -- checked -- but the rule that
     protects against it is one line and the failure it prevents is invisible. */
  [data-testid="stVerticalBlock"]:has(.st-key-resilience_rail) {
    overflow: visible;
  }
</style>
"""


# =============================================================================
# LAYOUT
# =============================================================================
st.set_page_config(page_title="Traditional vs Roth", layout="wide")
seed_state()

cube = load_cube()
header = cube["header"]

# THE STYLESHEET GOES HERE, IN THE SETUP BLOCK, AND THAT IS A SCAR.
# It used to sit two lines under st.title(), and the D-66 layout pass rewrote
# everything from that title down to the old settings strip -- which swallowed
# this call.  The rail silently stopped following the scroll and the SOURCE
# still contained the whole stylesheet, its comment block, and a test asserting
# every selector in it.  All of that was true and none of it reached a browser.
#
# Two changes so it cannot happen the same way twice: the call lives in the
# page-setup block, which no layout edit has a reason to touch, and
# `test_the_sticky_rail_stylesheet_actually_reaches_the_page` asserts DELIVERY
# rather than definition.  D-52's sentence, one layer out -- a guard nobody
# runs reads as coverage and is not.
st.html(STICKY_RAIL_CSS)

# --- TITLE ROW.  The two buttons ride beside the title (D-66) --------------
# NEITHER IS A SETTING.  The preset writes four income boxes and two booleans in
# one click, and the model box is DISABLED and always has been -- it is a
# statement about the option space rather than a control.  Both were sitting in
# the settings strip taking width from controls that change on every click, and
# both are now beside the title where a masthead action belongs.
title_col, preset_col, model_col = st.columns(
    [5, 1.25, 1.4], vertical_alignment="center", gap="small"
)
with title_col:
    st.title("Traditional vs Roth retirement investing")
with preset_col:
    st.button("Early-career preset", on_click=load_early_career,
              width="stretch",
              help="D-40's flip: Roth under current rules, Traditional once "
                   "the rule moves. Income (35, $60,000) · (38, $54,000) · "
                   "(55, $200,000) · (65, $200,000), neither state taxing.")
with model_col:
    # THE DISABLED MODEL BOX (section 7).  Disabled rather than absent: the
    # option space was mapped and two were built, and a disabled control says so
    # without implying the other seven exist.  The label is read off the
    # artifact rather than typed, so it cannot drift from the cube.
    # [SPRINT-7-CLEANUP] section 7 wants the tooltip to list all nine return
    # models from CONTEXT part D; part D was not in Sprint 6's reading list nor
    # in Sprint 8's, so the tooltip names the two IMPLEMENTED models and the
    # count only.  Deferred to Sprint 10, which reads part D anyway.
    st.button(
        f"Model ({header['return_model']} resampling, "
        f"length {header['block_length']})",
        disabled=True, width="stretch",
        help="Nine return models were mapped and two are implemented: "
             "#2 fixed real rate, which draws the page's headline, and #6 "
             f"{header['return_model']} resampling over the historical "
             "series, which produced the committed grid.",
    )

rail, main = st.columns([1.2, 4.0], gap="large")

# EVERY CONTROL LIVES IN THE STICKY RAIL NOW (D-66).  The strip across the top
# was a settings bar that scrolled away from every graph it moved, and the page
# grew two more regions below it this sprint.  `gap="xxsmall"` is the density
# knob and it is Streamlit's own parameter rather than a CSS bet -- the widget
# testids this build emits do not include a checkbox or a number input, so
# there is nothing honest to select on.
rail_box = rail.container(key="resilience_rail", gap="xxsmall")

with rail_box:
    # --- INCOME.  D-19's four knots, linearly interpolated ------------------
    # LABEL BESIDE THE BOX RATHER THAN ABOVE IT.  Four stacked inputs with
    # labels above cost ~110px of a rail that has to hold ten checkboxes too.
    # The box keeps the LARGER share of the row because the reported defect was
    # a clipped VALUE -- "540" where 54000 was typed -- and a number input
    # spends about 56px of its width on stepper buttons before a digit is drawn.
    st.markdown("**Income shape**")
    for age, label in ((35, "At 35 (now)"), (38, "at 38"),
                       (55, "at 55"), (65, "at 65")):
        lab_col, box_col = st.columns([0.8, 1.2], vertical_alignment="center",
                                      gap="small")
        lab_col.markdown(label)
        box_col.number_input(f"income at {age}", min_value=0, step=1_000,
                             key=f"income_{age}", format="%d",
                             label_visibility="collapsed")

    st.toggle("State income tax (while working)", key="state_while_working",
              help="Default assumes you earn in a taxing state and retire in "
                   "one that doesn't. Both are toggles.")

    st.radio("Investment return rate", list(RETURN_BUTTONS),
             key="return_button",
             help="This input drives the picture, not the answer — the "
                  "break-even under current rules is the same 32.5% at all "
                  "three rates. The nevermind threshold DOES move with it "
                  "(58.4% to 66.5%), because a frozen allowance is a smaller "
                  "share of a bigger portfolio.")

    pol_col, year_col = st.columns([1.05, 1], vertical_alignment="bottom",
                                   gap="small")
    with pol_col:
        st.toggle("Tax law changes", key="policy_on")
    with year_col:
        st.number_input("in year", min_value=1,
                        max_value=engine.RETIREMENT_AGE
                        - engine.Profile.current_age - 1,
                        step=1, key="policy_year",
                        help="You can still contribute — it just stops being "
                             "worth it. Direct taxation of Roth withdrawals is "
                             "the least likely form this takes; what has "
                             "repeatedly happened instead is that tax-free "
                             "money stops being invisible — counted toward a "
                             "Medicare premium, the taxable share of Social "
                             "Security, or an ACA subsidy. Poland 2013 · "
                             "Ireland 2011 · US SECURE Act 2019.")

    st.divider()

    # --- THE LADDER.  L3 claims fragility outranks the account choice, and a
    # control you have to scroll to cannot outrank anything.
    st.markdown("**Resilience ladder**")
    st.caption("Ten stops. Check what you have cleared, bottom up.")
    # CUT 4, PRE-APPROVED: colour bands become a single neutral rail and both
    # markers stay.  Rendered top-down so the picture matches the mockup, while
    # engine.LADDER_STOPS stays bottom-up because contiguity is a MODELING rule.
    for i in range(len(engine.LADDER_STOPS) - 1, -1, -1):
        st.checkbox(f"{i + 1}. {escape_dollars(engine.LADDER_STOPS[i])}",
                    key=f"stop_{i}")

profile = profile_from_state()
rung = profile.rung
cleared = engine.highest_contiguous_stop(profile.stops)

with rail_box:
    st.markdown(f"Rung: **{RUNG_LABEL[rung]}**  ·  {cleared} of 10 cleared")
    # D-37.  Non-contiguous checks render top-heavy and the app names the gap.
    # The copy points at the flowchart rather than issuing advice, because the
    # top stops are mostly illiquid or penalised -- telling a 401k-heavy user to
    # sell is the forced-liquidation branch this model treats as the bad outcome.
    if cleared < len(engine.LADDER_STOPS) and any(profile.stops[cleared:]):
        st.warning(
            "You have assets above a gap — the flowchart would prioritize "
            f"**{escape_dollars(engine.LADDER_STOPS[cleared])}** first."
        )

with main:
    st.divider()

    # --- THE COMPUTED HALF ---------------------------------------------------
    readings = deterministic_readings(
        profile, RETURN_BUTTONS[st.session_state["return_button"]],
        st.session_state["policy_year"]
    )
    if readings["blocked"]:
        blocked_notice(readings)
        # st.stop() rather than an indent over the whole computed half: the
        # strip and the ladder are already on screen above, which is everything
        # a reader needs in order to change the input that caused this.
        st.stop()

    dollars = x_and_y(cube["cells"], rung)

    # D-40 again, defensively: the axis has to reach past the second threshold
    # or it draws the deck's error by cropping instead of by placement.
    reach = [readings["marker"] * 100.0]
    for result in (readings["rules_hold"], readings["treatment_moves"]):
        if result.status == "crosses":
            reach.append(result.breakeven * 100.0)
    axis_max = min(100.0, max(70.0, 10.0 * (int(max(reach) / 10.0) + 2)))

    # --- THE ANSWER, FIRST -------------------------------------------------
    # MOVED AT ROUND 2.  The verdict is what the page is FOR, and it was sitting
    # below the chart that argues for it -- a reader had to interpret the bar
    # before being told the conclusion the bar supports.  Answer first, evidence
    # under it: the explainer sentences stayed where they were, which now reads
    # correctly because they describe the chart they now sit beneath.
    verdict_block(readings, st.session_state["policy_on"],
                  st.session_state["policy_year"], profile.stops)

    st.caption(RATE_AXIS_CAPTION)
    st.altair_chart(
        threshold_axis(readings, st.session_state["policy_on"],
                       st.session_state["policy_year"]),
        width="stretch",
    )

    verdict_detail(readings, st.session_state["policy_on"], profile.stops)
    two_rates_sentence(readings)

    st.divider()

    # --- THE BALANCE GRAPH ---------------------------------------------------
    st.markdown("#### What the two accounts hold while you save")
    t_display = f"{readings['t_now']:.1%}"
    charts = balance_graphs(readings, profile)
    if charts is None:
        st.info("No balance to draw — every year of this profile contributes "
                "nothing. Raise the income or clear a ladder stop.")
    else:
        st.altair_chart(charts)
        st.caption(
            "**Same data, both panels.** On the left the gap between "
            "Traditional and Roth grows from about \\$8,000 to about "
            "\\$685,000 — "
            "and the ratio behind it never changed. It is fixed at "
            f"1 ÷ (1 − {t_display}) for all thirty years, which is why the "
            "right-hand panel draws two parallel lines. **The account choice "
            "does not start mattering later. It mattered identically from the "
            "first contribution.**"
        )

    # THE YEARS SENTENCE.  L1 in a unit a person feels.  The account threshold
    # above does not move when the rate changes; these ages move by YEARS.
    reached = milestone_ages(readings["trad_by_year"], profile.current_age)
    first, second = reached[MILESTONES[0]], reached[MILESTONES[1]]
    rate_now = RETURN_BUTTONS[st.session_state["return_button"]]
    if first and second:
        st.markdown(
            f"At {rate_now:.0%} real, the Traditional balance crosses "
            f"**\\$1M at age {first}** and **\\$2M at age {second}** — "
            f"**{second - first} more working years** for the second million. "
            "Change the return rate and those ages move by years. The "
            "break-even above does not move at all."
        )
    elif first:
        st.markdown(
            f"At {rate_now:.0%} real, the Traditional balance crosses "
            f"**\\$1M at age {first}** and does not reach \\$2M by "
            f"{engine.RETIREMENT_AGE}."
        )
    else:
        st.markdown(
            f"At {rate_now:.0%} real, this profile does not reach \\$1M by "
            f"{engine.RETIREMENT_AGE}."
        )

    # --- $X, MOVED HERE AT ROUND 2 ------------------------------------------
    # It belongs to the ACCOUNT question, and this is the account graph. Above
    # the threshold axis it competed with the verdict for the same glance.
    if dollars["x"] is not None:
        ratio_clause = (
            f" — about {1 / dollars['ratio']:.1f}× what moving up a rung is worth"
            if dollars["ratio"] else ""
        )
        st.markdown(f"#### Getting this right is worth ~\\${dollars['x']:,.0f}"
                    f"{ratio_clause}")
        st.caption(
            f"10th-percentile outcome (objective 4) at one shock, if you miss "
            f"the break-even by δ = {SENTENCE_DELTA} points. "
            f"Modeled for the reference profile at the **{RUNG_LABEL[rung]}** "
            "rung — your controls choose the rung, not the dollars."
        )

    st.caption(
        f"**Units differ on purpose.** Traditional is a PRE-TAX balance and "
        f"Roth is ALREADY AFTER TAX — the dashed line is Traditional after tax "
        f"at your {readings['t_now']:.1%} deferral rate, and it sits on the "
        "Roth curve at every year, not just at 65. Same pre-tax dollars in "
        "(D-01); the divergence is the share the deferral is holding for the "
        "government. Both y-axes are pinned and share a \\$6M ceiling, so a "
        "click on the return rate moves the curves rather than the labels."
    )
    st.caption(
        "**Nothing is clamped.** Balances are allowed to go negative and ruin "
        "is recorded rather than floored (D-38). At the Low rung a forced sale "
        "is not affordability-checked, so a saver with \\$8,000 in the account "
        "can 'sell' \\$73,959 of it — right for the grid, wrong as a sentence "
        "about a person. A log axis cannot draw a non-positive number, so such "
        "a year leaves a gap in the line rather than being clamped to the floor."
    )

    st.divider()

    # --- $Y AND THE RESERVED DOT-PANEL REGION --------------------------------
    st.markdown("#### How fragile you are")
    if dollars["y"] is not None:
        st.markdown(
            f"#### Moving from {RUNG_LABEL[rung]} to "
            f"{RUNG_LABEL[NEXT_RUNG[rung]]} is worth ~\\${dollars['y']:,.0f}"
            + (f" — about {dollars['ratio']:.1f}× what getting the account "
               "right is worth" if dollars["ratio"] else "")
        )
    else:
        # D-36.  UNDEFINED at High, and the app says so rather than printing a
        # zero that would read as "moving up is worth nothing."
        st.markdown("#### There is no rung above High.")
        st.caption("\\$Y compares one step up, and High is the top of the "
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
        f"median of \\${SERIES_MEDIAN_T65:,} under the series, "
        f"{SERIES_MEDIAN_GAP} against the deterministic proxy. The median "
        "rather than the mean, because the ensemble average is not what any "
        "one household lives (D-15, D-23)."
    )
    # --- THE PANELS.  The region Sprint 6 reserved, consumed. ----------------
    # THE LINE IS READ UNDER CURRENT RULES EVEN WHEN THE NEVERMIND TOGGLE IS ON,
    # and that is D-63 rather than an oversight.  Every cell in the cube carries
    # `policy: null` (D-26 keeps policy off the cube axes), so a policy
    # threshold drawn against a no-policy cloud would put two different
    # questions on one axis -- the exact defect D-24 named upstairs when two
    # units shared the rate axis.
    panel_line = (readings["rules_hold"].breakeven * 100.0
                  if readings["rules_hold"].status == "crosses" else None)

    st.altair_chart(fragility_panels(cube["cells"], rung, panel_line))

    st.caption(
        "**The collapse is the lesson, and it is derived rather than "
        "observed.** Only the Low rung's mechanism is asymmetric — a forced "
        "sale grosses up through the early-withdrawal penalty while Roth basis "
        "comes out free — so 36 of these 48 cells equal your current combined "
        f"rate exactly (D-22). Low spans **8.13 points** of break-even; Mid "
        "spans 0.18 and High 0.08. **All three panels are pinned to one "
        "0–40% domain**, which is why the upper two collapse to a point: that "
        "is the finding, not a rendering failure. Let either of them scale to "
        "its own data and a tenth of a point becomes the full panel width."
    )
    st.caption(
        "**Four definitions of \"optimal,\" and the loud lesson is the "
        "descent.** Reading down a Low column, the mean falls 6.67 points and "
        "the 10th percentile falls 8.09 — expected value travels 82% as far as "
        "the tail, so it is not blind to shocks. The quieter lesson is the "
        "spread ACROSS a row: 0.00, 0.36, 0.76 and 1.47 points at zero, one, "
        "two and three life events. The definition of optimal is contested for "
        "exactly the population the fragility argument is about, and settled "
        "for everyone else."
    )
    # WRITTEN AS TWO WHOLE SENTENCES PER BRANCH RATHER THAN AS ONE STRING WITH
    # A CONDITIONAL SPLICED INTO THE MIDDLE.  The first version opened `**` in
    # the shared head, closed it inside the shared tail, and put a branch
    # between them -- so the bold ran across the join, the tail's own `**` pair
    # was read as the closer, and the paragraph shipped with a stray `**` in
    # front of it.  A markup pair that opens in one fragment and closes in
    # another is a pair nobody can see is unbalanced.
    if rung == "low":
        rung_line = (
            f"**Your rung is {RUNG_LABEL[rung]}, so the highlighted panel is "
            "the contested one.** This is where the four definitions disagree, "
            "and where the ladder outranks the account election."
        )
    else:
        rung_line = (
            f"**Your rung is {RUNG_LABEL[rung]}, so the highlighted panel is "
            "already settled.** At your rung this question is decided and the "
            "argument is happening below you. Uncheck a bottom stop to drop to "
            "Low and watch the four definitions come apart."
        )
    st.caption(
        rung_line
        + " **The dots are modeled for the reference profile** (D-15): your"
        " controls choose which rung is highlighted and where the blue line"
        " sits, not where the dots are. The line is your own break-even under"
        " current rules."
    )
    st.caption(
        "**Why the P(not running out) column sits slightly left of the "
        f"others.** {header['captions']['breakeven_objective_5']}"
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
        # ALL EIGHT ROWS, AND THREE LEANS ARE CORRECTED RATHER THAN CARRIED.
        # Sprint 6 sourced this table from the page rather than from section 4,
        # and shipped D3 and D8 as leaning TRADITIONAL and D7 as leaning ROTH.
        # Section 4 says Roth, Roth and EITHER DIRECTION, and it is the
        # disposition table -- section 0 gives it precedence over the deck.
        #
        # THE TWO INVERSIONS ARE THE SAME MISREADING TWICE, and DESIGN 3.3
        # already named it: a row states its LEAN, not its verdict.  D3 and D8
        # are Traditional-FLAVORED money, which is what Sprint 6's own caption
        # says -- and money that already arrives pre-tax is precisely what makes
        # deferring MORE of it worth less.  The flavour of the dollar and the
        # direction of the effect point opposite ways.
        #
        # D7 IS THE ONE THAT MATTERED MOST.  Labelled "Roth," it reproduces the
        # design deck's retired claim that the rule moving makes Roth safer.
        # D-40 is the algebra that reversed it: a policy harming only Roth
        # strictly RAISES the rate at which Roth becomes worthwhile, so at the
        # archetype it widens Traditional's lead -- and it flips the other way
        # at the early-career preset.  Either direction, and the preset is why.
        # THE STATUS COLUMN READS AS A SYSTEM RATHER THAN AS AN EXCEPTION,
        # AND THAT IS TWO FIXES IN ONE CELL SHAPE.
        #
        # REGISTER.  The column was reporting scope in product words -- yes,
        # off by default, the toggle above -- and then said `TODO` twice.
        # `TODO` is a word from a codebase, so it imports a codebase meaning:
        # UNFINISHED.  D3 and D8 are not unfinished.  They are real effects
        # left out on purpose, which is a stronger thing to say and the exact
        # opposite of what the borrowed word says.
        #
        # SALIENCE.  Backticks were the only styling in the column, so the two
        # ABSENCES were the loudest content in a table of eight presences -- the
        # eye landed on the two things the model does not do.  Chipping every
        # cell costs the same edit and makes status a column rather than a
        # flag.  Three values, and the third is real: D2 is implemented in the
        # engine and reachable from no control, because cut 3 took the
        # accordion read-only.
        st.markdown(
            "| # | Departure | Leans | Modeled |\n"
            "|---|---|---|---|\n"
            "| D1 | You withdraw across brackets, not at one rate | Traditional"
            " | `modeled` — always on, and it is the orange marker |\n"
            "| D2 | Contribution limit binds — Roth shelters more real money | "
            "Roth | `modeled · off` — in the engine, reachable from no control"
            " |\n"
            "| D3 | Below the limit, the tax saving sits in a taxable side "
            "account | Roth | `not modeled` — arrives either way |\n"
            "| D4 | You retire to a state that also taxes income | Roth | "
            "`modeled` — the toggle above |\n"
            "| D5 | A shock forces withdrawal — Traditional penalty vs. Roth "
            "basis | Roth | `modeled` — the panels below |\n"
            "| D6 | \"Optimal\" isn't expected value | either | `modeled` — "
            "always on, the four colours below |\n"
            "| D7 | The rule moves | either direction | `modeled` — the toggle "
            "above |\n"
            "| D8 | Employer match pushes withdrawals into higher brackets | "
            "Roth | `not modeled` — arrives either way |\n"
        )
        st.caption(
            "Each row names its **lean**, not its verdict — a departure that "
            "leans Roth is not an argument for Roth. The threshold is the "
            "argument. **`not modeled` is a scope report, not a backlog "
            "item** — D3 and D8 are real effects left out on purpose: "
            "both are Traditional-flavored money that arrives whether or not "
            "you choose it — which is exactly why they lean Roth, since a "
            "dollar already coming out pre-tax makes deferring the next one "
            "worth less. Almost nobody is a pure case, and saying that is "
            "worth more than modeling it badly."
        )
        # D-42, AND IT IS THE CAP LESSON FROM THE OTHER SIDE.  The row above
        # says the limit binds and Roth shelters more; this says the archetype
        # cannot reach that shelter, for the same reason.
        st.caption(
            "**D2, and why it ships off by default.** The archetype cannot "
            "afford to max a Roth: 20% of \\$165,000 is \\$33,000 of "
            "capacity against the \\$36,296 pre-tax cost of filling a "
            "\\$24,500 Roth. The "
            "cap is denominated in dollars that cost you more, so it binds "
            "before it looks like it should — which is the same lesson the row "
            "above states from the side where the cap helps (D-42, D-25)."
        )
