"""Annual real total returns on US equities, 1928-2025. 98 observations.

WHAT THIS IS
    The deck the block bootstrap deals from (D-05, D-41). make_paths("block", ...)
    chops REAL_RETURNS into 5-year runs and reshuffles them into synthetic
    65-year histories. Nothing else in the model reads this file.

SOURCE
    Aswath Damodaran, NYU Stern, "Historical Returns on Stocks, Bonds and Bills:
    1928-Current" (histretSP). S&P 500 annual total return, dividends reinvested,
    paired with CPI-U from the same workbook.
    Retrieved 2026-08-15 via a published machine-readable transcription of that
    workbook (eco3min.fr/dataset/sp500-historical-returns.csv).

    NOT verified against Damodaran's spreadsheet directly -- this is a secondary
    transcription. R5 sets a lower bar than R1 on purpose: a wrong deferral limit
    breaks test T3 and a stated claim; a slightly-off 1937 return is one card in
    a resampling deck. Four independent spot-checks against Damodaran's own
    published commentary all agree:
        worst year   1931  -43.84%   (he cites -43.84%)
        best year    1954  +52.56%   (he cites +52.56%)
        negative yrs 26 of 98        (he cites 26 through 2024)
        nominal CAGR 10.02%          (he cites ~10%)

REAL, NOT NOMINAL (D-27)
    Deflated on load, Fisher-exact: (1+nominal)/(1+cpi) - 1, not subtraction.
    Both input columns are kept below so the arithmetic is auditable.

DO NOT RESCALE THIS SERIES.
    The bootstrap compounds what it draws, so what it realizes is the GEOMETRIC
    mean. Measured here: 6.78% real geometric against 8.61% arithmetic -- a
    1.83-point gap, which matches sigma^2/2 = 1.86% at sd 19.30%. That is
    variance drag, not an error. "Fixing" the series to average 7% arithmetically
    would make the paths compound at roughly 5%, and the bootstrap dots would
    drift left of the deterministic line for a reason D-15's label does not
    cover.

    The 6.78% geometric sits 0.22 points under the 7% deterministic default
    (D-04a). That gap is real and small; do not close it by editing history.

n IS SMALL AND THAT IS THE POINT
    98 years at block length 5 is ~19.6 independent blocks. This is the same
    n~5 critique the README makes of Bengen's 4% rule, now pointed at this
    model. See README "What the block bootstrap does and does not buy."
"""

# year, nominal total return, CPI inflation -- kept for auditability
RAW = [
    (1928,   0.4381, -0.0116),
    (1929,  -0.0830,  0.0058),
    (1930,  -0.2512, -0.0640),
    (1931,  -0.4384, -0.0932),
    (1932,  -0.0864, -0.1027),
    (1933,   0.4998,  0.0076),
    (1934,  -0.0119,  0.0152),
    (1935,   0.4674,  0.0299),
    (1936,   0.3194,  0.0145),
    (1937,  -0.3534,  0.0286),
    (1938,   0.2928, -0.0278),
    (1939,  -0.0110,  0.0000),
    (1940,  -0.1067,  0.0071),
    (1941,  -0.1277,  0.0993),
    (1942,   0.1917,  0.0903),
    (1943,   0.2506,  0.0296),
    (1944,   0.1903,  0.0230),
    (1945,   0.3582,  0.0225),
    (1946,  -0.0843,  0.1813),
    (1947,   0.0520,  0.0884),
    (1948,   0.0570,  0.0299),
    (1949,   0.1830, -0.0207),
    (1950,   0.3081,  0.0593),
    (1951,   0.2368,  0.0600),
    (1952,   0.1815,  0.0075),
    (1953,  -0.0121,  0.0075),
    (1954,   0.5256, -0.0074),
    (1955,   0.3260,  0.0037),
    (1956,   0.0744,  0.0299),
    (1957,  -0.1046,  0.0290),
    (1958,   0.4372,  0.0176),
    (1959,   0.1206,  0.0173),
    (1960,   0.0034,  0.0136),
    (1961,   0.2664,  0.0067),
    (1962,  -0.0881,  0.0133),
    (1963,   0.2261,  0.0164),
    (1964,   0.1642,  0.0097),
    (1965,   0.1240,  0.0192),
    (1966,  -0.0997,  0.0346),
    (1967,   0.2380,  0.0304),
    (1968,   0.1081,  0.0472),
    (1969,  -0.0824,  0.0620),
    (1970,   0.0356,  0.0557),
    (1971,   0.1422,  0.0327),
    (1972,   0.1876,  0.0341),
    (1973,  -0.1431,  0.0871),
    (1974,  -0.2590,  0.1234),
    (1975,   0.3700,  0.0694),
    (1976,   0.2383,  0.0486),
    (1977,  -0.0698,  0.0670),
    (1978,   0.0651,  0.0902),
    (1979,   0.1852,  0.1329),
    (1980,   0.3174,  0.1252),
    (1981,  -0.0470,  0.0892),
    (1982,   0.2042,  0.0383),
    (1983,   0.2234,  0.0379),
    (1984,   0.0615,  0.0395),
    (1985,   0.3124,  0.0380),
    (1986,   0.1849,  0.0110),
    (1987,   0.0581,  0.0443),
    (1988,   0.1654,  0.0442),
    (1989,   0.3148,  0.0465),
    (1990,  -0.0306,  0.0611),
    (1991,   0.3023,  0.0306),
    (1992,   0.0749,  0.0290),
    (1993,   0.0997,  0.0275),
    (1994,   0.0133,  0.0267),
    (1995,   0.3720,  0.0254),
    (1996,   0.2268,  0.0332),
    (1997,   0.3310,  0.0170),
    (1998,   0.2834,  0.0161),
    (1999,   0.2089,  0.0268),
    (2000,  -0.0903,  0.0339),
    (2001,  -0.1185,  0.0155),
    (2002,  -0.2197,  0.0238),
    (2003,   0.2836,  0.0188),
    (2004,   0.1074,  0.0326),
    (2005,   0.0483,  0.0342),
    (2006,   0.1561,  0.0254),
    (2007,   0.0548,  0.0408),
    (2008,  -0.3655,  0.0009),
    (2009,   0.2594,  0.0272),
    (2010,   0.1482,  0.0150),
    (2011,   0.0210,  0.0296),
    (2012,   0.1589,  0.0174),
    (2013,   0.3215,  0.0150),
    (2014,   0.1352,  0.0076),
    (2015,   0.0138,  0.0073),
    (2016,   0.1177,  0.0207),
    (2017,   0.2161,  0.0211),
    (2018,  -0.0423,  0.0191),
    (2019,   0.3121,  0.0229),
    (2020,   0.1802,  0.0136),
    (2021,   0.2847,  0.0704),
    (2022,  -0.1804,  0.0645),
    (2023,   0.2606,  0.0335),
    (2024,   0.2488,  0.0289),
    (2025,   0.1772,  0.0274),
]

YEARS = [y for y, _, _ in RAW]

# Fisher-exact deflation (D-27). One line, and it is why RAW is kept.
REAL_RETURNS = [(1 + nom) / (1 + cpi) - 1 for _, nom, cpi in RAW]

STUB = False   # make_paths("block", ...) raises while this is True.

FIRST_YEAR, LAST_YEAR = YEARS[0], YEARS[-1]
BLOCK_LENGTH = 5                       # D-05
N_INDEPENDENT_BLOCKS = len(REAL_RETURNS) / BLOCK_LENGTH   # ~19.6


def _selftest():
    """Run me before Sprint 3. Cheap, and it catches a bad paste."""
    import statistics as st
    assert len(RAW) == 98, len(RAW)
    assert YEARS == list(range(1928, 2026)), "years must be contiguous 1928-2025"
    assert not STUB
    geo = 1.0
    for v in REAL_RETURNS:
        geo *= (1 + v)
    geo = geo ** (1 / len(REAL_RETURNS)) - 1
    ari, sd = st.mean(REAL_RETURNS), st.stdev(REAL_RETURNS)
    assert 0.065 < geo < 0.070, f"real geometric drifted: {geo:.4%}"
    assert abs((ari - geo) - sd ** 2 / 2) < 0.005, "variance drag identity broke"
    assert sum(1 for _, n, _ in RAW if n < 0) == 26, "negative-year count moved"
    assert min(n for _, n, _ in RAW) == -0.4384, "1931 anchor moved"
    assert max(n for _, n, _ in RAW) == 0.5256, "1954 anchor moved"
    print(f"returns.py OK -- {len(RAW)} yrs {FIRST_YEAR}-{LAST_YEAR}, "
          f"real geometric {geo:.2%}, arithmetic {ari:.2%}, sd {sd:.2%}")


if __name__ == "__main__":
    _selftest()
