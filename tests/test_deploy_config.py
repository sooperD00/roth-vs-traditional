"""Guards on railway.toml.  P3a, closing R2.

WHAT THIS FILE IS AND IS NOT.  It tests the deploy CONFIG, not the deploy.  A
deploy is a property of Railway's state and no pytest can reach it; that half is
verified by hand, with curl and a phone, per the P3a checklist.  What IS testable
is the class of bug that costs twenty minutes and one confused rebuild: the start
command naming a file that is not there.

WHY IT NEEDS TO EXIST.  Railpack does not fail when the start command is wrong.
Its Python provider scans the repo root for main.py, app.py, start.py, bot.py,
hello.py, server.py -- and app.py is ours.  So a broken start command silently
degrades to `python app.py`, which for a Streamlit script starts no server and
exits ZERO.  Nothing raises.  Nothing logs an error.  The healthcheck in
railway.toml catches it at deploy time; these tests catch it before the push.

Same shape as D-06's guard before bisecting and D-38's refusal to clamp: a
degenerate state must raise rather than return something plausible.

WRITTEN TO SURVIVE SPRINT 6.  Nothing here names app.py.  Every assertion reads
the entry point OUT of the start command, so when Sprint 6 replaces the probe
with the real app -- or renames it -- these tests keep guarding instead of
needing an edit.  A test that has to be updated whenever the thing it guards
changes is not a guard.

NO TAX NUMBERS HERE, so D-21's rule and the tests/ exemption are both untouched.
"""

import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RAILWAY_TOML = REPO_ROOT / "railway.toml"

# Streamlit's own health endpoint.  Restated by hand rather than imported from
# streamlit, on the same principle tests/test_tax.py restates tax literals: a
# check that imports the value it is checking checks nothing.
STREAMLIT_HEALTH_PATH = "/_stcore/health"


@pytest.fixture(scope="module")
def config() -> dict:
    """Parsed railway.toml.

    Defends: "Config defined in code will always override values from the
    dashboard."  A file that does not parse is a file Railway ignores, and the
    deploy quietly falls back to whatever the dashboard last had.
    """
    assert RAILWAY_TOML.is_file(), f"railway.toml missing from {REPO_ROOT}"
    return tomllib.loads(RAILWAY_TOML.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def start_command(config: dict) -> str:
    cmd = config.get("deploy", {}).get("startCommand")
    assert cmd, "deploy.startCommand is absent -- Railpack would fall back to its root-file scan"
    return cmd


def test_builder_is_railpack(config: dict) -> None:
    """Defends R2's premise: we are on Railpack, not Nixpacks or a Dockerfile.

    Railway builds with a Dockerfile whenever it finds one, which would silently
    change the build path for the whole project.  Stating the builder means a
    stray Dockerfile turns this red instead of turning the deploy weird.
    """
    assert config.get("build", {}).get("builder") == "RAILPACK"


def test_the_app_is_started_by_streamlit_not_by_python(start_command: str) -> None:
    """THE central assertion.  Defends against the silent-exit fallback.

    `python app.py` on a Streamlit script prints two warnings, serves nothing,
    and returns exit code 0.  Measured, not assumed.  If this test ever goes red
    because someone "simplified" the start command, that is the whole reason the
    file exists.
    """
    tokens = start_command.split()
    assert tokens[:2] == ["streamlit", "run"], (
        f"start command must begin `streamlit run`, got: {start_command!r}"
    )


def test_the_entry_script_named_in_the_start_command_exists(start_command: str) -> None:
    """Defends the Sprint 6 handoff.

    Sprint 6 replaces the probe with the real app.  If the file is renamed and
    railway.toml is not, Railpack finds no such file, the container dies, and the
    only clue is in a build log nobody reads until the second round.  This is the
    cheapest possible place to catch that.
    """
    tokens = start_command.split()
    entry = tokens[tokens.index("run") + 1]
    assert entry.endswith(".py"), f"entry point is not a Python file: {entry!r}"
    assert (REPO_ROOT / entry).is_file(), f"start command names {entry!r}, which is not in the repo"


@pytest.mark.parametrize(
    "flag, why",
    [
        ("--server.port $PORT", "Railway injects PORT; a hardcoded 8501 is unreachable from the edge"),
        ("--server.address 0.0.0.0", "binding localhost only makes the container invisible to the proxy"),
        ("--server.headless true", "otherwise first run wants to write credentials.toml in the container"),
    ],
)
def test_start_command_carries_the_flag(start_command: str, flag: str, why: str) -> None:
    """Defends the three flags whose absence produces a URL that never answers."""
    assert flag in start_command, f"missing {flag!r} -- {why}"


def test_healthcheck_points_at_streamlits_health_endpoint(config: dict) -> None:
    """Defends the guard itself.

    Without a healthcheck, a container that exits zero reads as a successful
    deploy.  With one, Railway marks the deployment FAILED and names the reason.
    This is the single line that turns the pipeline's one silent failure loud, so
    it gets its own test rather than riding along in another.
    """
    assert config.get("deploy", {}).get("healthcheckPath") == STREAMLIT_HEALTH_PATH


def test_restart_policy_cannot_loop_on_a_clean_exit(config: dict) -> None:
    """Defends the Hobby bill, and the diagnosis.

    restartPolicyType = ALWAYS would restart a container that exited ZERO -- the
    exact thing the `python app.py` fallback does.  An unbounded loop of clean
    exits bills for compute and reports nothing.  ON_FAILURE with capped retries
    stops and waits to be read.
    """
    deploy = config.get("deploy", {})
    assert deploy.get("restartPolicyType") != "ALWAYS"
    assert isinstance(deploy.get("restartPolicyMaxRetries"), int)
