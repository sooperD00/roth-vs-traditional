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

# ---- FIXED AXIS DOMAINS.  BOTH ARE FIXED AND FOR OPPOSITE REASONS ----------
# THE RATE AXIS IS FIXED BECAUSE THE NUMBER DOES NOT MOVE.  A dynamic domain
# rescaled when the nevermind year changed, so 32.5% slid across the screen
# while reading 32.5% -- the first lesson, taught backwards.  An axis that moves
# under a number that does not is the chart lying about the thing it exists to
# show.  0-100 is also the honest range for "what could a future tax rate be".
RATE_AXIS = [0.0, 100.0]

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

    return chart.properties(
        # Autosize "fit" spends this on the title, the axis and the legend as
        # well as the plot, so it is a TOTAL, not a drawable area.
        height=240,
        title=alt.TitleParams(
            "future tax rate  —  the bar's edge is a MARGINAL rate (t*), "
            "the orange line is your EFFECTIVE rate today",
            fontSize=12, color=RAIL_GREY, anchor="start",
        ),
    )


def _active(readings: dict, policy_on: bool):
    """The threshold the verdict is measured against.  The toggle selects it."""
    return readings["treatment_moves"] if policy_on else readings["rules_hold"]


def verdict_block(readings: dict, policy_on: bool, policy_year: int) -> None:
    """THE ANSWER, AND NOTHING ELSE.  One line, above the chart that argues it.

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


def verdict_detail(readings: dict, policy_on: bool) -> None:
    """The sentences that describe the chart, and they sit beneath it.

    THE NUMBERS SURVIVE THE SUPPRESSION.  D-35's point is that the verdict line
    is REPLACED while t*, both thresholds and the $X/$Y sentence stay -- hiding
    them would make the page read as a lockout rather than as an answer.
    """
    active = _active(readings, policy_on)
    marker = readings["marker"] * 100.0

    if active.status == "always_trad":
        st.markdown(
            f"A rule change this early freezes **${readings['allowance']:,.0f}**"
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

    # D-35's slot.  [SPRINT-7-CLEANUP] Sprint 7 wires the suppression; Sprint 6
    # owes it the room, which is this block.


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
        # [SPRINT-7-CLEANUP] Section 7's caption -- "Default assumes you earn
        # in a taxing state and retire in one that doesn't. Both are toggles."
        # -- is REMOVED at Nicole's round-2 review: it is narration, and she
        # says it out loud. It is copy the deployed page loses for a panelist
        # reading alone. Decide at Sprint 7 whether it returns as a `help=`
        # tooltip, which costs no screen and survives without a narrator.
        st.toggle("State income tax (while working)",
                  key="state_while_working")

    with strip[3]:
        # [SPRINT-7-CLEANUP] Section 7's "This input drives the picture, not
        # the answer" removed, same reason. It was also the caption Sprint 6
        # measured as INCOMPLETE -- true at the defaults, but with the tax-law
        # toggle on the policy threshold moves 58.4% to 66.5% across these
        # buttons. Removing it retires that issue for now rather than fixing it.
        st.radio("Investment return rate", list(RETURN_BUTTONS),
                 key="return_button")

    with strip[4]:
        st.toggle("Tax law changes", key="policy_on")
        # [SPRINT-7-CLEANUP] Section 7's "You can still contribute — it just
        # stops being worth it. Poland 2013 · Ireland 2011 · US SECURE Act
        # 2019" removed, same reason. This is the one of the three whose loss
        # costs the most unnarrated: the three precedents are what stop the
        # nevermind scenario reading as invented.
        st.number_input("in year", min_value=1,
                        max_value=engine.RETIREMENT_AGE
                        - engine.Profile.current_age - 1,
                        step=1, key="policy_year")

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
                  st.session_state["policy_year"])

    st.altair_chart(
        threshold_axis(readings, st.session_state["policy_on"],
                       st.session_state["policy_year"]),
        width="stretch",
    )

    verdict_detail(readings, st.session_state["policy_on"])
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
            "Traditional and Roth grows from about $8,000 to about $685,000 — "
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
            f"**$1M at age {first}** and **$2M at age {second}** — "
            f"**{second - first} more working years** for the second million. "
            "Change the return rate and those ages move by years. The "
            "break-even above does not move at all."
        )
    elif first:
        st.markdown(
            f"At {rate_now:.0%} real, the Traditional balance crosses "
            f"**$1M at age {first}** and does not reach $2M by "
            f"{engine.RETIREMENT_AGE}."
        )
    else:
        st.markdown(
            f"At {rate_now:.0%} real, this profile does not reach $1M by "
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
        st.markdown(f"#### Getting this right is worth ~${dollars['x']:,.0f}"
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
        "government. Both y-axes are pinned and share a $6M ceiling, so a "
        "click on the return rate moves the curves rather than the labels."
    )
    st.caption(
        "**Nothing is clamped.** Balances are allowed to go negative and ruin "
        "is recorded rather than floored (D-38). At the Low rung a forced sale "
        "is not affordability-checked, so a saver with $8,000 in the account "
        "can 'sell' $73,959 of it — right for the grid, wrong as a sentence "
        "about a person. A log axis cannot draw a non-positive number, so such "
        "a year leaves a gap in the line rather than being clamped to the floor."
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
