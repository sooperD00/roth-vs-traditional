"""The app's five tests.  Opened at Sprint 6.

WHAT THIS FILE IS FOR, AND WHAT IT DELIBERATELY IS NOT.  It does not test the
math -- `tests/test_engine.py` holds the eight engine claims and this file never
opens it.  It tests the SEAM: that the app computes one number and reads all the
others, that no scaffolding survived the sprint, and that the chain from a
control to `engine.breakeven()` renders the published archetype figures.

TWO OF THESE ARE GREPS PROMOTED TO ASSERTIONS, and that is the point of them.
A done-when you run by hand is a done-when that stops being run.  D-12's
`grep -c "bootstrap|numpy.random" app.py` and Sprint 6's five-cleanup-tag
enumeration both regress SILENTLY -- the page still renders, the numbers are
still right, and nobody notices until a reviewer greps.  The other three test
things that fail loudly, and they are here because they are the sprint's own
detectors rather than because they would otherwise be missed.

THE GREPS ARE SCOPED TO CODE, AND THEY HAVE TO BE.  `remaining-sprints.md`
already solved this once, for `SPRINT-2-CLEANUP`: the unscoped grep can never
return empty, because the line that documents the grep contains the string it
greps for.  Same shape here -- three prose mentions of the Sprint 6 tag live in
`remaining-sprints.md` and are supposed to.

NO CHART INTERNALS ARE ASSERTED.  Altair specs are an implementation detail and
a test that reads one breaks when the chart is restyled, which is a test that
punishes exactly the work Sprint 8 and the cut ladder expect.  The published
figures are asserted where a PANELIST reads them -- in the verdict line and the
two-rates sentence, both of which restate `t*` and the marker in prose by design
(section 7).  Whether the bars LOOK right is a human judgment and it is in the
smoke-test checklist instead.
"""

import json
import re
from pathlib import Path

import pytest
import streamlit
from streamlit.testing.v1 import AppTest

import app
import engine

REPO_ROOT = Path(__file__).resolve().parents[1]
APP = REPO_ROOT / "app.py"

# The bisection is ~54 ms measured, and the cube read is a file open.  Ninety
# seconds is not a performance budget -- it is headroom so a loaded CI box never
# turns a timeout into a red test that says nothing.
TIMEOUT = 90


def _run(**session_state) -> AppTest:
    """One fresh app run, with session state applied before the second pass.

    Two runs rather than one: the widgets have to exist before their state can
    be set, which is the same reason `seed_state()` uses `setdefault`.
    """
    app = AppTest.from_file(str(APP), default_timeout=TIMEOUT).run()
    if session_state:
        for key, value in session_state.items():
            app.session_state[key] = value
        app.run()
    return app


def _visible(app: AppTest) -> str:
    """Everything a reader can read, as one string."""
    return " ".join(
        [m.value for m in app.markdown]
        + [c.value for c in app.caption]
        + [i.value for i in app.info]
        + [w.value for w in app.warning]
    )


def _verdicts(app: AppTest) -> list:
    return [m.value for m in app.markdown if m.value.startswith("### ")]


def _spec(app: AppTest, index: int) -> str:
    """One chart's Vega-Lite spec as text.  0 = rate axis, 1 = balance graph.

    LABELS ARE ASSERTED HERE ONLY BECAUSE THE APP WRITES THEM AS MARK
    PROPERTIES.  Text carried in a data COLUMN reaches the browser in the arrow
    payload rather than in the spec -- it renders the same and is invisible from
    here, which is a trap worth naming once.
    """
    element = app.get("vega_lite_chart")[index]
    spec = element.spec
    spec = json.loads(spec) if isinstance(spec, str) else spec
    # ensure_ascii=False, and that is not cosmetic: the panel titles carry em
    # dashes, and the default escapes them to \u2014 so a substring check for
    # the title a reader sees silently fails against text that is really there.
    return json.dumps(spec, ensure_ascii=False)


# =============================================================================
def test_the_app_contains_no_stochastic_code() -> None:
    """D-12, promoted from a done-when's grep to an assertion.

    The app reads `cube.json`; it does not draw a path.  That is what lets the
    deploy be small, keeps a seed out of production, and makes it impossible for
    the page to be slow in front of a panel.

    THE CONSTANT NAMED `SERIES_MEDIAN_T65` IS WHY THIS TEST IS WORTH HAVING.
    D-15's caption figure wants a name, the obvious name carries the forbidden
    word, and the grep that catches it is one nobody runs by hand twice.
    """
    source = APP.read_text(encoding="utf-8")
    hits = [
        line for line in source.splitlines()
        if re.search(r"bootstrap|numpy\.random", line)
    ]
    assert hits == [], (
        f"D-12: app.py must contain no stochastic code, and "
        f"`grep -c 'bootstrap|numpy.random' app.py` is the done-when. Found "
        f"{len(hits)} line(s): {hits}"
    )


def test_every_sprint_6_cleanup_tag_is_cleared() -> None:
    """Sprint 6 owned FIVE tags, not four.  Enumerated by grep, not by memory.

    Three in `app.py`, one in `deploy_probe.json`, and a fifth in
    `scripts/measure_4a.py` added at 4A after the sentence naming four was
    written.  The probe's fixture goes with the probe.

    SCOPED TO CODE for the reason `remaining-sprints.md` already recorded at
    Sprint 2: three prose mentions of this tag live in that file and are meant
    to.
    """
    # THE NEEDLE IS BUILT FROM PARTS AND THAT IS NOT CUTENESS.  A test that
    # greps for a literal contains that literal, so it finds itself and can
    # never pass -- which is exactly the trap `remaining-sprints.md` recorded
    # when it scoped Sprint 2's grep, one document over.
    needle = "SPRINT-6-" + "CLEANUP"
    code = [
        path for pattern in ("*.py", "*.json", "*.toml")
        for path in REPO_ROOT.rglob(pattern)
        if "docs" not in path.parts
        and ".venv" not in path.parts
        and "__pycache__" not in path.parts
    ]
    tagged = [
        str(path.relative_to(REPO_ROOT)) for path in code
        if needle in path.read_text(encoding="utf-8", errors="ignore")
    ]
    assert tagged == [], f"unresolved Sprint 6 cleanup tags in: {tagged}"

    assert not (REPO_ROOT / "deploy_probe.json").exists(), (
        "deploy_probe.json is the P3a probe's fixture and goes with the probe"
    )


def test_the_headline_reads_the_published_archetype_numbers() -> None:
    """THE SPRINT'S CHEAPEST DETECTOR, made permanent.

    32.5% / 58.4% / 15.2% at the archetype proves the ENTIRE chain -- session
    state to `Profile` to `make_paths(kind="constant", n_paths=1)` to
    `breakeven()` to the page.  If a control stops reaching the engine, or the
    engine's constants move, or `Profile` stops deriving its rung from `stops`,
    this is what goes red.

    THE SECOND THRESHOLD IS TO THE RIGHT AND THAT IS ASSERTED, not assumed.
    The design deck drew it at 14%, left of the first, with Roth winning beyond
    it; D-40 is the algebra that reversed both the number and the direction.  A
    regression that reproduced the deck's error would still render a plausible
    chart, which is precisely why the ordering is an assertion.
    """
    app = _run()
    assert not app.exception, app.exception
    first_paint = _visible(app)

    assert "32.5%" in first_paint, "t* under current rules is 32.5% (== t_now)"
    assert "15.2%" in first_paint, "the today's-law effective marker is 15.2%"
    assert "17.3 points" in first_paint, (
        "Traditional's lead at the D-30 defaults is 17.3 points"
    )

    moved = _run(policy_on=True)
    assert not moved.exception, moved.exception
    assert "58.4%" in _visible(moved), (
        "the nevermind threshold is 58.4% (D-40)"
    )
    assert 58.4 > 32.5, "sanity: D-40 puts the second threshold to the RIGHT"


def test_a_non_crossing_policy_year_renders_copy_rather_than_a_null() -> None:
    """D-35 forbids printing nothing, and the reachable sentinel is always_trad.

    THE PLAN NAMED THE OTHER ONE.  `remaining-sprints.md` and the sprint's
    reading list both say a user-entered profile can return `always_roth`,
    citing T3's $185,000 flat profile.  True of T3 and false of the app: T3
    carries `d2_roth_to_cap=True`, and D2 is behind the read-only accordion.
    With D2 off, D-01's convention makes `roth_65` exactly
    `trad_65 * (1 - t_now)`, so the difference is `trad_65 * (t_now - t_later)`
    and its sign always flips inside the bracket -- `always_roth` is not
    reachable, algebraically, rather than merely unobserved.

    `always_trad` IS reachable and it is one drag of a shipped control.  At the
    archetype the nevermind year crosses over between N = 2 and N = 3.

    THE NUMBERS MUST SURVIVE THE SUPPRESSION.  D-35's whole point is that the
    verdict line is REPLACED while `t*`, both thresholds and the $X/$Y sentence
    stay -- hiding them would make the page read as a lockout.
    """
    app = _run(policy_on=True, policy_year=1)
    assert not app.exception, app.exception

    verdicts = _verdicts(app)
    assert verdicts, "D-35: something must render where the verdict was"
    assert "No future tax rate rescues Roth" in verdicts[0], (
        f"expected the always_trad copy, got {verdicts[0]!r}"
    )

    still_there = _visible(app)
    assert "32.5%" in still_there, "D-35: t* stays visible"
    assert "15.2%" in still_there, "D-35: the marker stays visible"
    assert "$1,622,671" in still_there, "D-35: the $X sentence stays visible"
    assert "None" not in verdicts[0] and "0.0%" not in verdicts[0], (
        "a sentinel must not surface as a null or a zero"
    )


@pytest.mark.parametrize("button,shown,marker", [
    ("7% real  (~10% nominal)", "7% real", "15.2%"),
    ("9% real  (~12% nominal)", "9% real", "20.0%"),
    ("12% real  (~15% nominal, implausible)", "12% real", "29.0%"),
])
def test_the_return_buttons_never_move_the_current_rules_threshold(
    button: str, shown: str, marker: str
) -> None:
    """L1, AND THE SPRINT'S OWN CORRECTION TO ITS DONE-WHEN.

    `remaining-sprints.md` says clicking 7 / 9 / 12 "leaves BOTH thresholds
    still."  MEASURED AT SPRINT 6, ONE OF THE TWO MOVES:

        r      t* rules hold    t* nevermind @20    today's-law marker
        7%         32.5000%           58.4064%             15.1849%
        9%         32.5000%           61.5761%             19.9923%
        12%        32.5000%           66.4577%             28.9750%

    THE CURRENT-RULES THRESHOLD IS EXACT ACROSS EVERY RATE and that is L1 at
    full strength -- both accounts fund the same net spending, so the common
    draw cancels out of the difference, which then compounds at `(1 + r)` for
    any `r` and crosses zero at `t_later == t_now` regardless.  32.5% is not
    approximately still; it is the same float.

    THE OTHER TWO MOVE FOR ONE REASON AND IT IS D-26's FROZEN ALLOWANCE.  The
    policy snapshot is fixed in real dollars at year N and does not grow, while
    the balance compounds at `r` -- so a bigger portfolio outgrows the same
    allowance, a smaller share of the Roth stays sheltered, and the rate at
    which Roth catches up moves further right.  The marker moves for the
    ordinary reason: a bigger balance funds a bigger draw, and a bigger draw
    fills higher brackets, which is D1 working exactly as designed.

    So L1's honest statement is *the return rate never moves the break-even
    under current rules* -- which is the claim T2 actually defends.  Recorded
    here rather than smoothed, and surfaced to the plan as a done-when to amend.

    Whether the balance graph VISIBLY swings is a human judgment and it is in
    the smoke-test checklist, not here.
    """
    app = _run(return_button=button)
    assert not app.exception, app.exception
    text = _visible(app)

    assert "32.5%" in text, (
        f"the current-rules break-even must read 32.5% at {button!r}: L1 says "
        "the return rate cannot move it"
    )
    assert "You defer at 32.5 cents on the dollar" in text, (
        "t_now is a property of income and the tax code, not of r"
    )
    assert f"deterministic at {shown}" in text, (
        f"the return-model caption should name {shown}"
    )
    assert marker in text, (
        f"the today's-law marker DOES move with r and reads {marker} at "
        f"{shown} -- asserted so the done-when's 'both thresholds still' stays "
        "corrected rather than quietly re-inherited"
    )


# =============================================================================
# ROUND 2 -- the two axes, pinned for opposite reasons.
# =============================================================================
@pytest.mark.parametrize("state,label", [
    ({}, "defaults"),
    ({"policy_on": True}, "nevermind on at the default year"),
    ({"policy_on": True, "policy_year": 3}, "N=3, where t* reaches 93.5%"),
    ({"policy_on": True, "policy_year": 1}, "N=1, the always_trad sentinel"),
    ({"return_button": "12% real  (~15% nominal, implausible)"}, "12% real"),
])
def test_the_rate_axis_never_rescales(state: dict, label: str) -> None:
    """THE AXIS IS FIXED BECAUSE THE NUMBER IS NOT MOVING.

    Round 1 sized the domain to the data, which is the ordinary default and is
    wrong here: changing the nevermind year rescaled the axis, so the 32.5%
    boundary SLID ACROSS THE SCREEN while continuing to read 32.5%.  L1's first
    lesson is that a number holds still, and it was being taught on a chart that
    moved underneath it.

    Nicole caught this at review and it is the one regression in this file that
    would never show up as a wrong number -- every figure was correct the whole
    time.  Hence a test: correctness cannot catch it, so something else must.
    """
    assert '"domain": [0.0, 100.0]' in _spec(_run(**state), 0), (
        f"the rate axis rescaled at {label}: it must be pinned to 0-100 in "
        "every control state"
    )


@pytest.mark.parametrize("button,edge", [
    ("7% real  (~10% nominal)", "32.5%"),
    ("9% real  (~12% nominal)", "32.5%"),
    ("12% real  (~15% nominal, implausible)", "32.5%"),
])
def test_both_balance_panels_are_pinned_and_share_a_ceiling(
    button: str, edge: str
) -> None:
    """THE BALANCE AXES ARE FIXED BECAUSE THE NUMBER *IS* MOVING.

    The mirror image of the rate-axis test, and the reason both belong here.
    Auto-scaled, the 7% and the 12% curves are THE SAME SHAPE and only the tick
    labels differ -- so clicking the return buttons appeared to do nothing, and
    L1's only gesture was silently absent while the done-when that asked for
    "visibly swings" read as satisfied.

    THE SHARED $6M CEILING IS WHAT MAKES THE TWO PANELS COMPARABLE rather than
    merely adjacent.  If they drifted apart the pair would stop being the same
    data twice, which is the entire claim the caption makes.
    """
    spec = _spec(_run(return_button=button), 1)
    assert '"domain": [0.0, 6000000.0]' in spec, "the linear panel is pinned"
    assert '"domain": [10000.0, 6000000.0]' in spec, "the log panel is pinned"
    assert '"type": "log"' in spec and '"type": "linear"' in spec, (
        "both scale types must be present -- the pair IS the lesson"
    )
    # THE CEILING NEEDS A LABEL OR THE SHARED CEILING IS INVISIBLE.  A log axis
    # left alone ticks at 1-3-10 multiples, so $6M gets none: the top label
    # reads $3M with a 10.8% empty band above it, and the two panels look drawn
    # to different scales when their domains are identical.
    assert '"values": [10000, 30000, 100000, 300000, 1000000, 2000000, 6000000]' \
        in spec, "the log panel must tick at its own ceiling, and at $1M/$2M"
    assert edge in _spec(_run(return_button=button), 0), (
        "and the rate axis boundary still reads 32.5% -- L1"
    )


@pytest.mark.parametrize("state,label", [
    ({}, "defaults, user at Mid"),
    ({"stop_0": False}, "user dropped to Low"),
    ({"stop_6": True, "stop_7": True, "stop_8": True, "stop_9": True},
     "user raised to High"),
    ({"return_button": "12% real  (~15% nominal, implausible)"}, "12% real"),
    ({"policy_on": True}, "nevermind on"),
])
def test_all_three_fragility_panels_share_one_pinned_rate_domain(
    state: dict, label: str
) -> None:
    """THE THIRD PINNED AXIS, AND THE FIRST THAT WOULD INVENT A FINDING.

    The two tests above this one were written after a chart with every number
    correct drew a false picture -- once by rescaling under a number that does
    not move, once by rescaling under numbers that do.  Both were DELETING a
    lesson.  This one is the same defect pointed the other way.

    Objective 5's break-even is the LEFT EDGE OF A PLATEAU rather than a point
    (D-51): `P(not running out)` counts a discrete event over 2,000 paths, so
    its difference is zero across an interval and the bisection closes on the
    left edge, ~0.08 points below `t_now`, deterministically.  Across the whole
    Mid slab that artifact is 0.1757 points wide.

    LET THE MID PANEL SCALE TO ITS OWN DATA AND 0.1757 POINTS BECOMES 196
    PIXELS.  Four columns, one of them visibly offset, descending nowhere --
    a finding manufactured out of a sampling artifact, with every number on
    screen correct.  Pinned, it collapses to a dot, which is D-22.

    Asserted across five control states because the domain must not be
    reachable from the data by ANY route: the rung control chooses which panel
    is highlighted and the return buttons and the policy toggle move the line
    through the cloud, and none of them may touch the axis.
    """
    spec = _spec(_run(**state), 2)
    assert '"domain": [0.0, 40.0]' in spec, (
        f"a fragility panel rescaled at {label}: all three are pinned to "
        "0-40%, and an upper panel that sizes to its own data draws a finding "
        "that is not there"
    )
    assert '"domain": [24' not in spec and '"domain": [32' not in spec, (
        "a domain sized to the cube's own values is the defect, not the fix"
    )


def test_the_upper_panels_collapse_to_a_visual_point() -> None:
    """WHAT THE PANELS DRAW, ASSERTED ON THE DATA RATHER THAN ON THE SPEC.

    `_spec` cannot see this.  Altair sends 48 rows to the browser as a named
    dataset in the arrow payload, not inline in the Vega-Lite spec -- the same
    trap `_spec`'s own docstring names for mark text.  `app.panel_frame()`
    exists so a test can read the plotted values directly instead of parsing a
    payload that is not there.

    THE NUMBERS ARE THE SPRINT'S WHOLE CORRECTION.  Its first done-when said
    the two upper panels render as single, identical points.  Measured against
    the committed cube they are neither single nor identical: Mid spans 0.1757
    points and High 0.0782, and High's objective-5 column is flat at -0.0782 on
    every row while Mid's wobbles.  They collapse VISUALLY, on a shared domain,
    and that distinction is the reason the domain is pinned.

    The ratio is the assertion worth having: Low occupies a fifth of the panel
    and the other two occupy under half a percent of it, which at 196px is
    under a pixel -- one dot, four objectives deep.
    """
    frame = app.panel_frame(app.load_cube.__wrapped__()["cells"])
    assert len(frame) == 48, "three rungs x four objectives x four shock counts"

    spans = {
        rung: frame[frame["rung"] == rung]["rate"].max()
             - frame[frame["rung"] == rung]["rate"].min()
        for rung in ("low", "mid", "high")
    }
    width = app.PANEL_RATE_AXIS[1] - app.PANEL_RATE_AXIS[0]

    assert spans["low"] > 8.0, (
        f"Low must visibly fan -- 8.1346 points measured, got {spans['low']}"
    )
    for rung in ("mid", "high"):
        assert spans[rung] / width < 0.01, (
            f"{rung} spans {spans[rung]:.4f} points, {spans[rung] / width:.2%} "
            "of the pinned domain. Over 1% and the solver artifact has started "
            "reading as structure (D-51, RESULTS 8.4)"
        )
    assert spans["mid"] > spans["high"] > 0.0, (
        "and they are NOT identical to each other -- the done-when this test "
        "corrects said they were"
    )


@pytest.mark.parametrize("state,suppressed,extra", [
    ({}, False, False),
    ({"stop_0": False}, True, False),
    ({"stop_1": False}, True, False),
    ({"stop_2": False}, False, True),
    ({"stop_0": False, "stop_2": False}, True, True),
    ({"stop_0": False, "policy_on": True, "policy_year": 1}, True, False),
])
def test_d35_replaces_the_verdict_line_and_only_the_verdict_line(
    state: dict, suppressed: bool, extra: bool
) -> None:
    """D-35, AND THE POINT OF IT IS WHAT SURVIVES.

    Suppressing the verdict without hiding the numbers is what keeps the page
    from reading as a lockout.  `t*`, both thresholds, the two-rates sentence
    and the $X/$Y pair all stay, and this asserts their presence in exactly the
    states that remove the verdict.

    TWO GATES, NOT THREE, AND THAT IS D-61.  The corpus said this three ways --
    D-35 names the first two stops, D-33's reason column reads as all three, and
    section 7 reads as the whole Low rung.  D-35 is the decision.  Stop 3 adds
    its own line and suppresses nothing, which is the last row's shape here.

    THE SUPPRESSION OUTRANKS THE SENTINELS and the last case is why: a profile
    can be both `always_trad` and standing under an unmet $400 gate, and the
    gate is the more urgent true thing to say.
    """
    app_ = _run(**state)
    assert not app_.exception, app_.exception
    verdicts, visible = _verdicts(app_), _visible(app_)

    assert verdicts, "D-35: something must render where the verdict was"
    replaced = "This election is not your binding constraint yet" in verdicts[0]
    assert replaced == suppressed, (
        f"expected suppressed={suppressed} at {state}, got {verdicts[0]!r}"
    )
    assert (("beats either account, at any tax rate" in visible) == extra), (
        f"stop 3's own copy should be {'present' if extra else 'absent'} at "
        f"{state} -- it names an arithmetic fact and takes no verdict away"
    )

    assert "32.5%" in visible, "D-35: t* stays visible"
    assert "15.2%" in visible, "D-35: the marker stays visible"
    assert "You defer at 32.5 cents" in visible, "D-35: the sentence stays"
    assert "Getting this right is worth" in visible, "D-35: $X stays visible"
    if suppressed:
        assert engine.LADDER_STOPS[0] in visible or \
               engine.LADDER_STOPS[1] in visible, (
            "the copy must NAME the binding gate rather than announce a tier"
        )


def test_all_eight_departures_render_and_three_leans_are_corrected() -> None:
    """SECTION 4 IS THE DISPOSITION TABLE AND THE PAGE NOW AGREES WITH IT.

    Sprint 6 shipped five rows and sourced their leans from the page rather
    than from section 4.  Three disagreed, and two of the three were INVERTED:
    D3 and D8 shipped as leaning Traditional against section 4's Roth.

    THE INVERSION IS ONE MISREADING MADE TWICE.  DESIGN 3.3 already named it --
    a row states its LEAN, not its verdict.  D3 and D8 are Traditional-flavored
    money, which Sprint 6's own caption says correctly, and a dollar that
    already arrives pre-tax is exactly what makes deferring the next one worth
    LESS.  The flavour of the dollar and the direction of the effect point
    opposite ways.

    D7 IS THE EXPENSIVE ONE.  Shipped as leaning Roth, it restates the design
    deck's retired claim that the rule moving makes Roth safer -- the single
    error D-40 exists to correct, back on the page in a table cell.  A policy
    that harms only Roth strictly RAISES the rate at which Roth becomes
    worthwhile, so it widens Traditional's lead at the archetype and flips at
    the early-career preset.  Either direction.
    """
    app_ = _run()
    visible = _visible(app_)

    for row in ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"):
        assert f"| {row} |" in visible, (
            f"{row} must render -- the grayed rows are the evidence of "
            "completeness, and section 7 and DESIGN 3.3 both say eight"
        )
    # THE TOKEN CHANGED AND THE DONE-WHEN IT ANSWERS DID NOT (D-65).  The row
    # asked for a visible `TODO` on the grayed rows.  `TODO` is a word from a
    # codebase and it imports a codebase meaning -- UNFINISHED -- into a column
    # that is otherwise reporting SCOPE, and D3 and D8 are not unfinished.
    # `not modeled` keeps the done-when's intent (the page admits out loud what
    # it does not do) and drops the borrowed meaning.
    # COUNTED INSIDE THE TABLE ELEMENT, NOT ACROSS THE PAGE.  Two bites at
    # this, both on this test's own runs.  The caption under the table now
    # explains the statuses in the same words, so a page-wide count picked it
    # up -- and `_visible()` joins elements with a SPACE rather than a newline,
    # so splitting the joined page on "\n" welds that caption onto the D8 row.
    # The table is one markdown element; read it as one.
    table = next(m.value for m in app_.markdown if "| D1 |" in m.value)
    rows = [seg for seg in table.split("\n") if seg.startswith("| D")]
    assert len(rows) == 8, f"eight departure rows, got {len(rows)}"
    statuses = "".join(rows)
    assert statuses.count("`not modeled`") == 2, (
        "exactly D3 and D8 report out of scope, and they say so on the page"
    )
    assert "`TODO`" not in visible, (
        "the IDE register is gone from the page; §4 keeps it, the page does not"
    )
    # AND EVERY CELL IN THE COLUMN CARRIES A CHIP, which is the other half.
    # Backticks were the only styling in that column, so two ABSENCES were the
    # loudest content in a table of eight presences.
    assert statuses.count("`modeled`") == 5 and "`modeled · off`" in statuses, (
        "all eight status cells are chipped, so status reads as a system "
        "rather than as an exception flag on the two rows that lack something"
    )
    for row, lean in (("D3", "Roth"), ("D8", "Roth"),
                      ("D7", "either direction")):
        line = next(seg for seg in visible.split("\n") if seg.startswith(f"| {row} |"))
        assert f"| {lean} |" in line, (
            f"{row} leans {lean} per DECISIONS section 4, not what Sprint 6 "
            f"shipped: {line!r}"
        )
    assert "$36,296" in visible, (
        "D2's row carries D-42: the archetype cannot afford to max a Roth, "
        "which is the cap lesson from the other side"
    )


def test_the_sticky_rail_is_wired_to_the_column_the_stylesheet_targets() -> None:
    """THE LADDER FOLLOWS THE SCROLL, AND THE WIRE IS ONE STRING IN TWO PLACES.

    `rail.container(key="resilience_rail")` emits `class="st-key-resilience_rail"`
    and `STICKY_RAIL_CSS` selects the column that `:has()` it.  Rename either
    end and the rail silently stops following the scroll -- the page still
    renders, every number is still right, and nobody notices until they scroll
    to the panels in front of somebody.

    That is the same failure shape as the two axis tests above: correct output,
    wrong behaviour, invisible to correctness testing.  Asserted structurally
    because there is nothing on screen to assert.

    **THIS TEST IS NOT SUFFICIENT ON ITS OWN AND ONCE PROVED IT.** It reads the
    source, so it passed through the entire window in which D-66 had deleted
    the `st.html()` call: the constant existed, the container was keyed, every
    selector was present, and none of it reached a browser.  Both ends of the
    wire, and not the wire.  `test_the_sticky_rail_stylesheet_actually_reaches_
    the_page` is the other half and was written because of that.
    """
    source = APP.read_text(encoding="utf-8")
    key = "resilience_rail"

    # MATCHED ON THE ARGUMENT, NOT ON THE WHOLE CALL, AND IT TOOK TWO GOES.
    # First it asserted `st.container(...)` when the call is
    # `rail.container(...)` -- the container has to be created INSIDE the rail
    # column.  Then it asserted the exact two-character call `container(key=X)`
    # and went red the moment a second argument arrived (`gap="xxsmall"`, the
    # density knob the rail needed once it held every control).  BOTH FAILURES
    # WERE THE ASSERTION BEING MORE LITERAL THAN THE CLAIM: what matters is that
    # a container is created with this key, not how many arguments it takes.
    assert re.search(rf'container\([^)]*key="{key}"', source), (
        "the rail's keyed container is what the stylesheet hangs off"
    )
    assert f".st-key-{key}" in source, (
        f"STICKY_RAIL_CSS must select .st-key-{key}, which is the class "
        "Streamlit derives from the container key"
    )
    assert source.count(f".st-key-{key}") >= 3, (
        "all three rules -- the flex row, the sticky column, and the "
        "overflow guard -- key off the same class"
    )
    assert "position: sticky" in source and "align-self: flex-start" in source, (
        "a stretched flex item is already full height and has nothing to stick "
        "to; the sticky rule needs both halves"
    )
    assert "with rail:" not in source, (
        "both rail blocks must enter the KEYED container -- a leftover "
        "`with rail:` writes outside it and that content does not stick"
    )


def test_the_sticky_rail_stylesheet_actually_reaches_the_page() -> None:
    """THE TEST BESIDE THIS ONE PASSED WHILE THE FEATURE WAS DEAD.

    D-66 rewrote the layout from `st.title()` down to the old settings strip,
    and `st.html(STICKY_RAIL_CSS)` sat two lines under that title.  It was
    swallowed by the replacement.  The rail stopped following the scroll.

    NOTHING WENT RED.  The stylesheet was still defined, still carried every
    selector, still had its comment block explaining the three numbers -- and
    `test_the_sticky_rail_is_wired_to_the_column_the_stylesheet_targets` reads
    the SOURCE, so it happily confirmed that a constant existed and a container
    was keyed.  It never asked whether the two were connected at runtime.  Both
    ends of the wire were tested and the wire was not.

    **THAT IS D-52'S SENTENCE ONE LAYER OUT** -- an unpinned fingerprint *reads
    as coverage and is not* -- and it is the third instance in this project of a
    guard that describes a thing rather than checking it.

    So this asserts DELIVERY: the stylesheet is on the rendered page, and the
    class it selects is the class the rail container actually emits.  Source
    assertions cannot reach that, because a string in a file is not a byte on a
    page.
    """
    app_ = _run()
    assert not app_.exception, app_.exception

    blocks = app_.get("html")
    assert blocks, (
        "no st.html on the page -- STICKY_RAIL_CSS is defined and never "
        "injected, which is exactly how this broke the first time"
    )
    delivered = " ".join(getattr(b, "body", "") for b in blocks)

    assert "position: sticky" in delivered, (
        "the sticky rule must reach the browser, not merely exist in app.py"
    )
    assert ".st-key-resilience_rail" in delivered, (
        "the delivered stylesheet must select the class the rail emits"
    )
    assert "align-self: flex-start" in delivered, (
        "a stretched flex item is already full height and cannot stick"
    )
    # AND THE TWO ENDS MUST AGREE.  A rename on either side leaves both halves
    # individually valid and the rail unstuck -- which is the failure this whole
    # pair of tests exists for.
    source = APP.read_text(encoding="utf-8")
    key = re.search(r'container\([^)]*key="([^"]+)"', source).group(1)
    assert f".st-key-{key}" in delivered, (
        f"the page styles .st-key-... for a key the rail does not use: the "
        f"container is keyed {key!r}"
    )


def test_the_sticky_rail_selectors_are_ones_this_streamlit_actually_emits(
) -> None:
    """A THIRD-PARTY DOM DETAIL IS A FACT WITH A VERSION ATTACHED (D-43, D-46).

    This project has been bitten twice by trusting a library's stated behaviour
    without pinning it: `default_rng`'s stream, and `argsort`'s stability.  A
    stylesheet written against someone else's `data-testid` is the same bet in
    a third costume, and it is the worst of the three because **CSS that no
    longer matches anything fails silently.** No exception, no red test, no
    visible change until the rail scrolls away during a demo.

    So the selectors are asserted against the INSTALLED frontend bundle rather
    than against memory.  Upgrade Streamlit past a rename and this goes red and
    says which name moved -- which is the whole point, because the alternative
    is finding out from a panelist.

    Checked at streamlit 1.62.0: `stColumn` and `stHorizontalBlock` are both
    emitted as `data-testid` AND as `className`, and `st-key-` is the prefix
    the container key is mangled into.
    """
    bundle = Path(streamlit.__file__).parent / "static" / "static" / "js"
    sources = list(bundle.glob("*.js"))
    if not sources:                     # a wheel that ships no frontend
        pytest.skip("no frontend bundle in this streamlit install")

    blob = "".join(
        path.read_text(encoding="utf-8", errors="ignore") for path in sources
    )
    for needle, why in (
        ("stColumn", "the sticky rule selects the COLUMN containing the rail"),
        ("stHorizontalBlock", "the flex row that stretches its children"),
        ("stVerticalBlock", "the overflow guard's target"),
        ("st-key-", "the prefix st.container(key=...) is mangled into"),
    ):
        assert needle in blob, (
            f"streamlit {streamlit.__version__} no longer emits {needle!r} -- "
            f"{why}. STICKY_RAIL_CSS now matches nothing and the resilience "
            "ladder has silently stopped following the scroll."
        )


@pytest.mark.parametrize("state,label", [
    ({}, "defaults"),
    ({"stop_0": False}, "gate 1 unmet, D-35's copy on screen"),
    ({"stop_2": False}, "stop 3's debt line on screen"),
    ({"stop_3": False, "stop_4": False, "stop_5": False}, "Low rung"),
    ({"stop_6": True, "stop_7": True, "stop_8": True, "stop_9": True}, "High"),
    ({"policy_on": True, "policy_year": 1}, "the always_trad sentinel"),
    ({"income_35": 0, "state_while_working": False}, "the blocked notice"),
])
def test_no_rendered_copy_hands_a_dollar_sign_to_the_maths_renderer(
    state: dict, label: str
) -> None:
    """`$` IS A KaTeX DELIMITER, AND EVERY HEADLINE ON THIS PAGE IS MONEY.

    Streamlit gives the span between two dollar signs to the maths renderer.
    Found at review across TEN rendered strings, five of which paired -- and
    they paired in the most quotable sentences on the page: *crosses **$1M at
    age 56** and **$2M at age 64*** rendered as a run of italic maths, which is
    L1 stated in years, the one sentence the milestone test exists to protect.

    A LONE `$` IS HARMLESS AND THAT IS WHY THIS SURVIVED SIX SPRINTS.  Nothing
    breaks until a SECOND one arrives, usually in an unrelated edit, and then
    the damage lands in whichever sentence was nearby.  A rule about pairs
    cannot be checked one string at a time, so the rule is every dollar sign.

    ASSERTED ON THE RENDERED PAGE RATHER THAN ON THE SOURCE, because the
    source has two legitimate routes -- inline `\\$` for literals this file
    owns and `escape_dollars()` for text arriving from `engine.LADDER_STOPS`,
    which carries "$400" and "$2,000" and which the seam forbids editing.  What
    matters is what reaches the browser, and only one of these two is a grep.

    THE SECOND HALF IS THE SAME CLASS OF BUG.  An odd number of `**` markers
    means a bold that opens and never closes; the panel caption shipped with
    one, because the pair opened in a shared fragment and was supposed to close
    on the far side of a conditional.  Both defects render, both look like a
    typo to a reader, and neither is visible to any test that checks numbers.
    """
    app_ = _run(**state)
    assert not app_.exception, app_.exception

    surfaces = (
        [("markdown", m.value) for m in app_.markdown]
        + [("caption", c.value) for c in app_.caption]
        + [("info", i.value) for i in app_.info]
        + [("warning", w.value) for w in app_.warning]
        + [("checkbox", c.label) for c in app_.checkbox]
        + [("toggle", t.label) for t in app_.toggle]
        + [("radio", r.label) for r in app_.radio]
    )
    assert surfaces, "nothing rendered, so nothing was actually checked"

    unescaped = re.compile(r"(?<!\\)\$")
    offenders = [
        (kind, text) for kind, text in surfaces if unescaped.search(text)
    ]
    assert offenders == [], (
        f"unescaped $ at {label}: KaTeX will eat the span between any two of "
        f"them. Escape as \\\\$ inline, or via escape_dollars() for text from "
        f"engine. {offenders[:2]}"
    )

    unbalanced = [
        (kind, text[:70]) for kind, text in surfaces if text.count("**") % 2
    ]
    assert unbalanced == [], (
        f"an unclosed ** at {label} -- the paragraph ships with a stray marker "
        f"in front of it: {unbalanced[:2]}"
    )


def test_every_control_survived_the_move_into_the_rail() -> None:
    """D-66 RELOCATED EVERY CONTROL, AND A RELOCATION CAN DROP ONE SILENTLY.

    The settings strip across the top became the sticky rail, and the two
    buttons moved beside the title.  A widget that failed to make the trip
    leaves a page that still renders, still computes, and quietly cannot reach
    part of its own model -- `seed_state()` would keep supplying the default, so
    the number on screen would be right and unchangeable.

    Counted rather than eyeballed, because the failure is an ABSENCE and an
    absence is what nobody notices.  Every key is also checked to still exist in
    session state, since `profile_from_state()` reads them by name and a dropped
    widget takes its key with it.
    """
    app_ = _run()
    assert not app_.exception, app_.exception

    assert len(app_.checkbox) == len(engine.LADDER_STOPS) == 10, (
        "ten stops, one boolean each (D-32)"
    )
    assert len(app_.toggle) == 3, (
        "state-while-working, tax-law-changes, and D4 in the accordion"
    )
    assert len(app_.radio) == 1, "the return buttons (D-04a)"
    assert len(app_.number_input) == 5, "four income knots and the policy year"
    assert len(app_.button) == 2, "the preset and the disabled model box"

    for key in ("income_35", "income_38", "income_55", "income_65",
                "state_while_working", "state_in_retirement", "return_button",
                "policy_on", "policy_year"):
        assert key in app_.session_state, (
            f"{key} lost its widget in the move; profile_from_state() reads it "
            "by name and seed_state() would keep serving the default"
        )
    for i in range(10):
        assert f"stop_{i}" in app_.session_state, f"stop_{i} lost its widget"

    # THE AXIS SENTENCE IS ON THE PAGE AND NOT IN THE CHART.  As a Vega title it
    # clipped through the middle of the letters at narrow viewports, because
    # `autosize: fit` spends the chart's height on the title, the axis and the
    # legend before the plot gets any.  D-24 requires the axis to say that two
    # units share it; a caption says it and cannot be clipped.
    captions = " ".join(c.value for c in app_.caption)
    assert "MARGINAL rate" in captions and "EFFECTIVE rate" in captions, (
        "D-24's two-units sentence must survive leaving the Vega title"
    )
    spec = json.loads(_spec(app_, 0))
    assert "title" not in spec, (
        "the threshold axis must carry no Vega title -- that is the thing that "
        "clipped, and it clipped only at some widths, which is why it shipped"
    )


def test_the_two_balance_panels_are_one_chart_with_a_shared_legend() -> None:
    """ONE hconcat, NOT TWO CHARTS IN TWO COLUMNS, and the difference matters.

    Two separate charts would each carry their own legend, which duplicates the
    key and -- worse -- makes the two plot areas start at different heights, so
    the panels no longer line up.  A pair whose baselines disagree is a pair a
    reader compares wrongly.  `hconcat` with `resolve_scale(color="shared")`
    gives one legend, one colour scale, and two aligned plot areas.

    THE TITLES ARE ASSERTED BECAUSE THEY CARRY THE ARGUMENT.  "how a statement
    draws it" against "what the ratio does" is the sentence the pair
    exists to make; without them it is two charts of the same thing.
    """
    spec = _spec(_run(), 1)
    assert '"hconcat"' in spec, "the pair is one concatenated chart"
    assert "linear — how a statement draws it" in spec
    assert "logarithmic — what the ratio does" in spec


def test_the_constant_ratio_the_log_panel_exists_to_show() -> None:
    """THE MEASUREMENT BEHIND THE PAIR, asserted so the caption cannot go stale.

    trad/roth is 1.481481... to nine decimals at EVERY one of the thirty years
    -- exactly 1 / (1 - t_now), which is D-22's accumulation identity.  On a log
    axis that is two parallel lines.  On a linear axis the same unchanged ratio
    presents as a gap widening from about $8,000 to about $685,000, an
    eighty-six-fold spread in a number that never moved.

    THAT ILLUSION IS THE WHOLE REASON THE LINEAR PANEL IS KEPT.  It is how a
    brokerage statement draws this, so it is the picture the audience arrives
    holding, and the misreading it produces -- *the account choice matters more
    later, so I will decide later* -- is only retirable by making it visible.
    """
    profile = engine.ARCHETYPE
    paths = engine.make_paths("constant", 1, profile.n_years, rate=0.07)
    acc = engine.accumulate(profile, paths[0], 0)

    ratios = [t / r for t, r in zip(acc.trad_by_year, acc.roth_by_year)]
    assert max(ratios) - min(ratios) < 1e-9, (
        "the log panel draws parallel lines only because this ratio is constant"
    )
    assert abs(max(ratios) - 1.0 / (1.0 - acc.t_now)) < 1e-9, (
        "and the constant is exactly 1 / (1 - t_now), which is D-22"
    )

    gaps = [t - r for t, r in zip(acc.trad_by_year, acc.roth_by_year)]
    assert gaps[-1] / gaps[0] > 80, (
        "while in dollars the same ratio appears to widen ~86x, which is the "
        "misreading the linear panel is kept in order to expose"
    )


@pytest.mark.parametrize("state,edge,ghost", [
    ({}, "32.5%", "58.4%"),
    ({"policy_on": True}, "58.4%", "32.5%"),
    ({"policy_on": True, "policy_year": 1}, "no break-even", "32.5%"),
])
def test_both_thresholds_stay_on_screen_and_the_active_one_swaps(
    state: dict, edge: str, ghost: str
) -> None:
    """D-10 SURVIVES THE ROUND-2 REDESIGN, WHICH IS THE POINT OF ASSERTING IT.

    Round 1 drew two stacked bars and nobody could read the comparison: the rows
    share an axis, a marker and a palette, so the reader has to construct the
    difference out of one boundary.  Round 2 draws ONE bar -- the scenario the
    toggle selects -- and the movement between them does the teaching.

    THE RISK THAT CHANGE CREATES IS EXACTLY WHAT D-10 FORBIDS: showing one
    exposure and hiding the offsetting one, which is the failure D-10 was
    written to correct in the first place.  The ghost tick is the answer, so
    the invariant asserted here is that BOTH numbers are on screen in every
    state and only which one is emphasised changes.
    """
    spec = _spec(_run(**state), 0)
    assert edge in spec, f"the active bar's boundary should read {edge}"
    assert ghost in spec, (
        f"D-10: the inactive threshold {ghost} must stay on screen as a ghost "
        "tick, not disappear with the toggle"
    )


@pytest.mark.parametrize("button,first,second,gap", [
    ("7% real  (~10% nominal)", "56", "64", "8"),
    ("9% real  (~12% nominal)", "53", "60", "7"),
    ("12% real  (~15% nominal, implausible)", "51", "56", "5"),
])
def test_the_milestone_sentence_puts_l1_in_years(
    button: str, first: str, second: str, gap: str
) -> None:
    """L1 IN A UNIT A PERSON FEELS.

    $2.1M and $5.3M are both "a lot" and the difference does not land.  Eight
    working years against five does.  The sentence moves hard with the return
    rate while the break-even above it does not move at all, which is the same
    lesson the two pinned axes are drawing.
    """
    text = _visible(_run(return_button=button))
    assert f"$1M at age {first}" in text
    assert f"$2M at age {second}" in text
    assert f"{gap} more working years" in text
    assert "The break-even above does not move at all." in text


# =============================================================================
# ROUND 3 -- the engine raises on inputs these controls can reach.
# =============================================================================
@pytest.mark.parametrize("state,heading", [
    ({"income_35": 0, "state_while_working": False}, "Roth, at every rate."),
    ({"income_35": 10_000, "state_while_working": False},
     "Roth, at every rate."),
    ({"income_35": 0, "income_38": 0, "income_55": 0, "income_65": 0,
      "state_while_working": False}, "Nothing to compare yet."),
    ({"income_35": 0, "income_38": 0, "income_55": 0, "income_65": 0},
     "Nothing to compare yet."),
])
def test_low_income_renders_copy_instead_of_a_traceback(
    state: dict, heading: str
) -> None:
    """THE ENGINE RAISES HERE, AND THESE ARE ALL TWO CLICKS FROM THE DEFAULTS.

    Measured at round 3, after a traceback appeared on screen:

        current income 0, state OFF   ValueError: t_later 0.0 outside (0, 1)
        all income 0, either state    AssertionError: the difference is
                                      constant at 0.0 across the bracket

    `Profile.t_now` keys off the CURRENT-AGE income alone, so zeroing the one
    visible "Current income" box is enough to reach the first -- and the
    early-career preset sets `state_while_working=False`, which makes
    preset-then-zero a TWO-CLICK PATH TO A TRACEBACK IN FRONT OF A PANEL.

    THE FIRST GUARD'S COPY IS AN ANSWER RATHER THAN AN APOLOGY.  At t_now = 0
    the difference is `trad_65 * (0 - t_later)`, negative at every rate in the
    bracket, so Roth wins everywhere -- and the reason is the plainest on the
    page: there is no tax to defer. The engine cannot SAY it, because its search
    runs over (0.01, 0.95) and evaluates at t_now, so a t_now of exactly zero
    sits outside its own bracket. The algebra is unambiguous where the search is
    not, so the app states the conclusion and says it did not draw it.

    WHY THE GUARD IS IN THE APP.  The seam makes the app a consumer and forbids
    editing `engine.py`; these are control-range questions rather than model
    questions, so this is the right side of the seam regardless.
    """
    app = _run(**state)
    assert not app.exception, (
        f"a traceback reached the page at {state}: {app.exception}"
    )
    verdicts = _verdicts(app)
    assert verdicts and heading in verdicts[0], (
        f"expected {heading!r}, got {verdicts[:1]}"
    )


def test_the_guards_sit_upstream_of_the_engine_call() -> None:
    """THE BUG WAS NOT THE MISSING GUARD.  IT WAS THE GUARD IN THE WRONG PLACE.

    Round 2 already dropped non-positive points inside `balance_graphs()` and
    the smoke checklist claimed zero income produced an info box.  It could not
    have: `deterministic_readings()` runs first, and that is where the raise
    comes from -- so the chart guard was unreachable code defending an input
    that never got that far.

    Asserted structurally, because the failure it prevents is one where every
    number in the file is still correct: the guards must come BEFORE the
    `breakeven()` calls in the source, not merely exist somewhere in it.
    """
    source = APP.read_text(encoding="utf-8")
    body = source[source.index("def deterministic_readings("):
                  source.index("# ====", source.index("def deterministic_readings("))]
    guard = body.index('return {"blocked": "no_contributions"}')
    call = body.index("engine.breakeven(")
    assert guard < call, (
        "the low-income guards must run BEFORE breakeven(), or they defend "
        "nothing -- this is the exact shape of the round-2 miss"
    )


@pytest.mark.parametrize("state,consequence", [
    ({}, "you would be on the Traditional side"),
    ({"policy_on": True}, "you would be on the Traditional side"),
])
def test_the_other_scenario_states_its_consequence_in_words(
    state: dict, consequence: str
) -> None:
    """THE ROUND-3 REVIEW BUG WAS A MEANING BUG WEARING A LAYOUT BUG'S CLOTHES.

    The inactive threshold was drawn as a bare tick on the active scenario's
    bar.  A tick INHERITS THE COLOUR IT IS DRAWN ON, and that colour belongs to
    the other scenario.  At the early-career preset the inactive threshold is
    29.1%, which lands in the green "Roth wins" band -- so the chart said
    *29.1% is Roth territory* when crossing it is precisely what puts this user
    on the TRADITIONAL side.  The single most counterintuitive result in the
    project, drawn backwards.

    IT IS ALSO THE DESIGN DECK'S OWN ERROR IN A NEW COSTUME.  DESIGN 3.5 drew
    the second threshold so Roth appeared to win beyond it; D-40 corrected the
    number and the direction, and this corrects the READING.  Every number was
    right in both cases, which is the third time this sprint that sentence has
    been the whole problem.

    The fix is words, because words cannot be recoloured by the band under
    them -- so the words are what gets asserted.
    """
    spec = _spec(_run(**state), 0)
    assert consequence in spec, (
        "the inactive threshold must state which side the user would land on, "
        "not merely where it sits"
    )


def test_no_annotation_is_positioned_in_absolute_pixels() -> None:
    """STREAMLIT'S autosize MAKES `height` A TOTAL, NOT A DRAWABLE AREA.

    `.properties(height=...)` looks like it buys that many pixels to draw in.
    It does not: Streamlit sends `autosize: {"type": "fit"}`, so the title, the
    x-axis and the legend all come out of that number and the plot area is
    roughly 120px of a nominal 200.  Annotations placed at `y=alt.value(121)`
    and `y=alt.value(152)` therefore rendered BELOW the axis, past the legend,
    hanging off the bottom of the chart -- with every number in them correct,
    which is the fourth time this sprint that has been the whole problem.

    THE STANDALONE RENDER COULD NOT SEE IT because it omitted `autosize`.  A
    harness that drops the host's layout directives is a harness that certifies
    a layout the host will never draw.

    Every annotation now encodes `y` on the bar's own band scale and offsets
    with `dy`, which is relative to the band centre and therefore survives any
    plot height autosize settles on.  Asserted structurally: a pixel `y` value
    on a layer is the defect itself, so its ABSENCE is what gets checked.
    """
    spec = _spec(_run(), 0)
    layers = json.loads(spec)["layer"]
    offenders = [
        i for i, layer in enumerate(layers)
        if isinstance(layer.get("encoding", {}).get("y"), dict)
        and "value" in layer["encoding"]["y"]
    ]
    assert offenders == [], (
        f"layers {offenders} position y in absolute pixels; under autosize:fit "
        "that lands them outside the plot area. Use the band scale and dy."
    )
    assert all(
        layer["encoding"]["y"].get("field") == "row"
        for layer in layers if "y" in layer.get("encoding", {})
    ), "every annotation shares the bar's band scale, so the row label survives"
