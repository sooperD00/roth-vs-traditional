"""Sprint 3A's measurement pass. Run it; it prints the numbers the docs cite.

WHY THIS FILE EXISTS, AND IT IS NOT "A SCRIPT WAS CONVENIENT". Five documents
carry the block-vs-IID comparison -- ENGINE.md's table, D-05, TRADEOFFS.md,
CONTEXT.md, and the README's panel-facing Scope & Branches row. All five trace to
ONE measurement, taken at gate two by code that is not in this repo. A published
number with no runnable source behind it is the same shape as a gate whose
failing input cannot be constructed: true when written, unfalsifiable afterwards.
This file makes those five documents checkable by one command.

It is NOT part of the engine and nothing imports it. The Definition of Done lists
eight artifacts and this is not among them; it is the evidence for four of the
numbers inside them.

    python scripts/measure_3a.py

IID LIVES HERE RATHER THAN AS A THIRD make_paths KIND, and that is deliberate.
Nothing in the model consumes an IID path set -- it exists only to be the thing
block is compared against. Promoting it to `kind="iid"` would put a permanent
branch in a published function to serve one table, and would need a decision row
of its own. The comparison is a measurement, so it lives with the measurements.
"""

import sys

import numpy as np

sys.path.insert(0, ".")

import engine            # noqa: E402
import return_series     # noqa: E402

DECK = np.asarray(return_series.REAL_RETURNS, dtype=float)
SEEDS = (20_260_815, 20_260_816, 20_260_817, 20_260_818, 20_260_819)
N_TABLE = 4_000          # the published table's path count
N_CUBE = engine.N_PATHS   # D-41's 2,000, for the two decisions
WINDOW = engine.ARCHETYPE.n_accumulation_years    # 30. THE WINDOW. See below.


def iid_paths(n_paths, n_years, seed):
    """The comparison arm. Same deck, same generator, blocks of one."""
    rs = np.random.RandomState(seed)
    return DECK[rs.randint(0, DECK.size, size=(n_paths, n_years))]


def worst_run(paths, length=engine.BLOCK_LENGTH, aligned=False):
    """Each path's worst `length`-year annualized run. Published: -10.26%.

    TWO READINGS AND THE SPRINT NEEDED BOTH. `aligned` reads only the drawn
    blocks, so every candidate is a sequence that really happened. The default
    is a ROLLING window, which may straddle two blocks and so may score a
    sequence history never produced. The published figure is the rolling one
    over the FULL 65-year path; see the sprint record for what that costs the
    sentence attached to it.
    """
    log = np.log1p(paths)
    if aligned:
        n = paths.shape[1] // length
        roll = log[:, : n * length].reshape(len(paths), n, length)
    else:
        roll = np.lib.stride_tricks.sliding_window_view(log, length, axis=1)
    return np.expm1(roll.mean(axis=2)).min(axis=1)


def rebound(paths):
    """The three rebound rows of ENGINE.md's table.

    For each path: find its worst-year-return, then read the year after it and
    the three years after it. Paths whose worst year sits too close to the end
    of the window have no "after" and are dropped rather than padded.
    """
    n = paths.shape[1]
    worst = paths.argmin(axis=1)
    ok1, ok3 = worst <= n - 2, worst <= n - 4
    after1 = paths[np.arange(len(paths))[ok1], worst[ok1] + 1]
    idx = worst[ok3][:, None] + np.arange(1, 4)
    after3 = np.prod(1.0 + paths[np.arange(len(paths))[ok3][:, None], idx], axis=1) - 1.0
    return after1.mean(), after3.mean(), float((after3 < 0).mean())


def drawdown_table(n_paths, seeds, window):
    """path-drawdown median and p10, block against IID, averaged over seeds."""
    out = {}
    for name, builder in (
        ("block", lambda s: engine.make_paths("block", n_paths, window, seed=s)),
        ("iid", lambda s: iid_paths(n_paths, window, s)),
    ):
        med, p10, r1, r3, neg = [], [], [], [], []
        for s in seeds:
            p = builder(s)
            dd = engine.path_drawdown(p)
            med.append(np.median(dd))
            p10.append(np.percentile(dd, 10))
            a1, a3, frac = rebound(p)
            r1.append(a1); r3.append(a3); neg.append(frac)
        out[name] = tuple(float(np.mean(v)) for v in (med, p10, r1, r3, neg))
    return out


def main():
    print(f"numpy {np.__version__} | generator RandomState/MT19937 (D-43)")
    print(f"deck {DECK.size} yrs, block {engine.BLOCK_LENGTH}, "
          f"{DECK.size - engine.BLOCK_LENGTH + 1} distinct starts, no wrap\n")

    # -- 1. THE PUBLISHED TABLE. The window is the whole finding ---------------
    print(f"1. BLOCK vs IID -- path-drawdown over {WINDOW}y accumulation, "
          f"{N_TABLE} paths, {len(SEEDS)} seeds")
    t = drawdown_table(N_TABLE, SEEDS, WINDOW)
    print(f"{'':26}{'block':>10}{'IID':>10}   published")
    for i, (label, pub) in enumerate((
        ("median path-drawdown", "-42.6 / -43.0"),
        ("p10 path-drawdown", "-59.7 / -64.3"),
        ("year after worst year", "+17.0 / +9.5"),
        ("next three, cumulative", "+39.5 / +32.1"),
        ("...of which negative", "5% / 21%"),
    )):
        print(f"   {label:23}{t['block'][i]:>9.1%}{t['iid'][i]:>10.1%}   {pub}")

    print(f"\n   SAME MEASUREMENT, 65y full path -- the reading that goes stale:")
    f = drawdown_table(N_TABLE, SEEDS[:1], engine.ARCHETYPE.n_years)
    print(f"   {'median / p10':23}{f['block'][0]:>9.1%}{f['iid'][0]:>10.1%}"
          f"   {f['block'][1]:>8.1%}{f['iid'][1]:>9.1%}")

    # -- 1b. WHICH ROW CARRIES THE FINDING. Not both -------------------------
    print("\n1b. DIRECTION BY SEED -- the p10 row is the finding, "
          "the median row is noise")
    for s in SEEDS:
        b = engine.path_drawdown(engine.make_paths("block", N_TABLE, WINDOW, seed=s))
        i = engine.path_drawdown(iid_paths(N_TABLE, WINDOW, s))
        verdict = lambda f: "block thinner" if f(b) > f(i) else "BLOCK DEEPER"
        print(f"   seed {s}:  median {verdict(np.median):>13}   "
              f"p10 {verdict(lambda x: np.percentile(x, 10)):>13}")

    # -- 2. The fifth published figure, and the clause attached to it ----------
    full = engine.make_paths("block", N_TABLE, engine.ARCHETYPE.n_years,
                             seed=SEEDS[0])
    deck_worst = worst_run(DECK[None, :])[0]
    starts = np.random.RandomState(SEEDS[0]).randint(
        0, DECK.size - engine.BLOCK_LENGTH + 1,
        size=(N_TABLE, engine.ARCHETYPE.n_years // engine.BLOCK_LENGTH))
    print(f"\n2. WORST 5-YEAR RUN over the full {engine.ARCHETYPE.n_years}y path"
          f"   published -10.26%, 'which is exactly 1937-41'")
    print(f"   median path, rolling window   "
          f"{np.median(worst_run(full)):>8.2%}   <- the published figure")
    print(f"   median path, aligned block    "
          f"{np.median(worst_run(full, aligned=True)):>8.2%}")
    print(f"   the deck's own worst window   {deck_worst:>8.2%}   (1937-41)")
    print(f"   paths that actually drew it   "
          f"{(starts == 9).any(axis=1).mean():>8.1%}   <- the clause")

    # -- 3. R9. RE-MEASURED, not inherited -------------------------------------
    print(f"\n3. R9 -- 0-shock Roth ruin, {N_CUBE} paths, 3 seeds "
          f"(cited 53.1%, taken at the 7% solve)")
    for s in SEEDS[:3]:
        p = engine.make_paths("block", N_CUBE, engine.ARCHETYPE.n_years, seed=s)
        _, ruined = engine._outcome_paths(
            engine.ARCHETYPE, 0, None, p, engine.ARCHETYPE.t_now, "roth"
        )
        print(f"   seed {s}: ruin {ruined.mean():.1%}   "
              f"draw ${engine._solve_draw(engine.ARCHETYPE, p):,.0f} at "
              f"{engine.draw_return_rate(p):.4%}")

    # -- 4. D-15. Three answers, not two ---------------------------------------
    p = engine.make_paths("block", N_CUBE, engine.ARCHETYPE.n_years)
    t65 = np.array([a.trad for a in engine._accumulations(engine.ARCHETYPE, p, 0)])
    proxy = 2_028_066
    print(f"\n4. D-15 -- T65 Traditional, {N_CUBE} paths, against the "
          f"${proxy:,} deterministic proxy")
    for label, v in (("mean", t65.mean()), ("median", np.median(t65)),
                     ("p10", np.percentile(t65, 10)),
                     ("p90", np.percentile(t65, 90))):
        print(f"   {label:8}${v:>12,.0f}  {(v / proxy - 1):+7.1%}")

    # -- 5. CUT LADDER ITEM 2. Gates nothing -----------------------------------
    print(f"\n5. BLOCK LENGTH SENSITIVITY -- cut ladder item 2, gates nothing")
    keep = engine.BLOCK_LENGTH
    try:
        for L in (3, 5, 10):
            engine.BLOCK_LENGTH = L
            dd = engine.path_drawdown(
                engine.make_paths("block", N_TABLE, WINDOW, seed=SEEDS[0])
            )
            print(f"   block {L:<3} median {np.median(dd):>7.1%}   "
                  f"p10 {np.percentile(dd, 10):>7.1%}"
                  f"{'   <- D-05' if L == keep else ''}")
    finally:
        engine.BLOCK_LENGTH = keep

    print(f"\ndigest, {N_CUBE}x{engine.ARCHETYPE.n_years} at seed "
          f"{engine.SEED}: {engine.paths_digest(p)}")


if __name__ == "__main__":
    main()
