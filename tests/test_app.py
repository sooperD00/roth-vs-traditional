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

import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

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
