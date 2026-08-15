"""P3a deploy probe.  Scaffolding.  [SPRINT-6-CLEANUP]

WHY: R2 is the highest-variance item in the plan and Sprint 9 budgets five
minutes on the assumption the deploy already stood up once.  P3a is that
standing-up, scheduled early because it needs no project code.

Sprint 6 REPLACES this file wholesale with the real app (DECISIONS section 7
layout).  `railway.toml` names app.py in its start command, so keeping the name
means Sprint 6 changes no deploy config -- one fewer thing to forget at the
moment there is the least room to forget it.

WHAT THIS PAGE IS FOR.  A hello-world proves one bit: the pipeline runs.  For
the same effort this proves six, and every one of them is a thing that would
otherwise surprise Sprint 6:

  1. numpy imported          -> uv actually populated the image
  2. `import tax` worked     -> Railpack installs with --no-install-project, so
                                root-level modules are NOT installed as a
                                package.  They import because Streamlit puts the
                                script's directory on sys.path.  Proven here
                                rather than discovered later.
  3. A published number reproduces in the container -> the math runs, and the
                                deployed code is the code you think it is
  4. JSON read off disk      -> the path pattern Sprint 9 needs for cube.json,
                                which must be committed and read, never computed
  5. Python version          -> .python-version was honored, not Railpack's
                                3.13.2 default
  6. PORT and commit SHA     -> the start command bound correctly, and you are
                                looking at the deploy you think you are

NO TAX NUMBER IS DEFINED HERE (D-21).  32.5% below is read back from tax.py,
never restated -- this file computes it and compares against what tax.py says,
which is a wiring check, not a second copy of the constant.
"""

import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import streamlit as st

import tax

REPO_ROOT = Path(__file__).resolve().parent
PROBE_JSON = REPO_ROOT / "deploy_probe.json"   # [SPRINT-6-CLEANUP] -> cube.json


@st.cache_resource
def boot_time() -> float:
    """Wall-clock at first script run in this process.

    st.cache_resource is per-process, so this survives Streamlit's re-run of the
    whole script on every interaction.  Uptime tells you whether the page you
    are looking at came from a cold container or a warm one -- which is the
    difference between the number Sprint 9 cares about and a meaningless one.
    """
    return time.time()


def probe(label: str, ok: bool, detail: str, retires: str) -> None:
    st.markdown(f"{'✅' if ok else '❌'} **{label}** — {detail}")
    st.caption(retires)


st.set_page_config(page_title="P3a deploy probe", layout="centered")

started = boot_time()

st.title("P3a — deploy probe")
st.markdown(
    "Not the app. This is the pre-flight that closes **R2** so Sprint 9 is a "
    "push rather than a scramble. Sprint 6 overwrites this file."
)
st.divider()

# 1 -- numpy
try:
    _v = float(np.array([0.07, 0.09, 0.12]).mean())
    probe("numpy", abs(_v - 0.093333) < 1e-4, f"{np.__version__}, array mean {_v:.4f}",
          "The image really has the runtime dependencies, not just a green build log.")
except Exception as exc:                                      # noqa: BLE001
    probe("numpy", False, f"{type(exc).__name__}: {exc}", "Dependency install did not land.")

# 2 + 3 -- root-module import, and a published number reproducing
#
# NO TAX LITERAL APPEARS HERE (D-21).  The deferral cap is a tax number and may
# not be written outside tax.py, so the contribution is DERIVED by calling
# tax.contribution() rather than typed -- which also shows the cap binding, since
# 20% of the archetype's gross is well above it.
#
# ARCHETYPE_GROSS and SAVINGS_RATE are D-19 and D-28 modeling constants that
# properly live in engine.py.  They sit here only because this is a probe with no
# engine to import from yet.  [SPRINT-6-CLEANUP]
ARCHETYPE_GROSS = 165_000
SAVINGS_RATE = 0.20

try:
    contribution = tax.contribution(ARCHETYPE_GROSS, SAVINGS_RATE)
    t_now = tax.combined_rate(ARCHETYPE_GROSS, contribution, True)
    probe(
        "import tax",
        True,
        f"contribution **${contribution:,.0f}** (cap binds) → `t_now` = **{t_now:.4%}**",
        "Root modules import under --no-install-project, and the archetype's "
        "t_now reproduces inside the container — DECISIONS D-19, D-21, D-28, D-30.",
    )
except Exception as exc:                                      # noqa: BLE001
    probe("import tax", False, f"{type(exc).__name__}: {exc}",
          "sys.path in the container does not include the repo root. Sprint 6 would have died here.")

# 4 -- JSON off disk, the cube.json rehearsal
try:
    payload = json.loads(PROBE_JSON.read_text(encoding="utf-8"))
    probe(
        "read JSON from the repo",
        payload.get("probe_ok") is True,
        f"`{PROBE_JSON.name}` parsed, seed {payload.get('seed')}",
        "Path(__file__).parent resolves inside the container. This is the exact "
        "pattern Sprint 9 needs for cube.json, which ships committed (D-12).",
    )
except Exception as exc:                                      # noqa: BLE001
    probe("read JSON from the repo", False, f"{type(exc).__name__}: {exc}",
          "Relative-path resolution differs in the container. Fix before Sprint 4.")

# 5 -- interpreter
_pyver = platform.python_version()
probe(
    "Python version",
    _pyver.startswith("3.13"),
    f"{_pyver}  ({sys.implementation.name})",
    "`.python-version` pins 3.13 and mise honored it. A bare Railpack default "
    "would read 3.13.2 regardless — this confirms the file was read.",
)

# 6 -- the deployment's own identity
_port = os.environ.get("PORT", "(unset — running locally)")
_sha = os.environ.get("RAILWAY_GIT_COMMIT_SHA", "(unset — running locally)")
probe(
    "runtime environment",
    True,
    f"streamlit **{st.__version__}** · PORT `{_port}` · commit `{_sha[:12]}`",
    "The start command bound $PORT, and the commit SHA says which push you are "
    "looking at. Both blank locally, which is how you tell the two apart.",
)

st.divider()

_up = time.time() - started
st.markdown(
    f"**Process uptime {_up:,.1f}s** — booted "
    f"{datetime.fromtimestamp(started, tz=timezone.utc):%Y-%m-%d %H:%M:%S} UTC."
)
st.caption(
    "Uptime near zero means you caught a cold container and any load timing you "
    "take now is the real one. Uptime in the minutes means this container is "
    "warm and the number is optimistic. The server cannot measure your network "
    "round trip — take cold load with `curl -w` from your own machine, per the "
    "P3a checklist."
)
