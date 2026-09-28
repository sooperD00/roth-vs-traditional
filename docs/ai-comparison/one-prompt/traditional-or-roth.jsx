import { useState } from "react";

// ── Traditional or Roth? ───────────────────────────────────────────
// The whole decision is one bet: your marginal tax rate now vs. in
// retirement. Everything else is a tiebreaker. This app makes the bet
// visible: same dollar, two timelines, one stamp.

const BRACKETS = [10, 12, 22, 24, 32, 35, 37];

const usd = (n) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);

function Chips({ value, onChange, accent }) {
  return (
    <div className="chips">
      {BRACKETS.map((b) => (
        <button
          key={b}
          className={"chip" + (value === b ? " on" : "")}
          style={value === b ? { borderColor: accent, color: accent } : {}}
          onClick={() => onChange(b)}
        >
          {b}%
        </button>
      ))}
    </div>
  );
}

function Field({ label, value, onChange, suffix, min, max, step }) {
  return (
    <label className="field">
      <span className="fieldLabel">{label}</span>
      <span className="fieldBox">
        <input
          type="number"
          value={value}
          min={min}
          max={max}
          step={step}
          onChange={(e) => {
            const v = Number(e.target.value);
            if (!Number.isNaN(v)) onChange(v);
          }}
        />
        {suffix && <span className="suffix">{suffix}</span>}
      </span>
    </label>
  );
}

export default function App() {
  const [tNow, setTNow] = useState(22);
  const [tLater, setTLater] = useState(12);
  const [contrib, setContrib] = useState(10000);
  const [years, setYears] = useState(25);
  const [growth, setGrowth] = useState(7);

  const G = Math.pow(1 + Math.max(0, growth) / 100, Math.max(0, years));
  const gross = contrib * G;
  const trad = gross * (1 - tLater / 100);
  const rothIn = contrib * (1 - tNow / 100);
  const roth = rothIn * G;
  const diff = trad - roth;
  const best = Math.max(trad, roth);
  const deadHeat = best > 0 && Math.abs(diff) / best < 0.005;

  const winner = deadHeat ? "DEAD HEAT" : diff > 0 ? "TRADITIONAL" : "ROTH";
  const stampClass =
    winner === "TRADITIONAL" ? "stamp trad" : winner === "ROTH" ? "stamp roth" : "stamp tie";

  return (
    <div className="page">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,560&family=Libre+Franklin:wght@400;500;600&family=Spline+Sans+Mono:wght@500&display=swap');

        :root {
          --vault: #142A22;
          --vault2: #0E1F19;
          --line: rgba(239,233,218,0.14);
          --ivory: #EFE9DA;
          --muted: #8CA394;
          --trad: #A8C6D4;
          --roth: #E3B65C;
          --carmine: #C4483C;
        }
        * { box-sizing: border-box; }
        .page {
          min-height: 100vh;
          background: var(--vault);
          color: var(--ivory);
          font-family: 'Libre Franklin', system-ui, sans-serif;
          padding: 40px 20px 64px;
          display: flex;
          justify-content: center;
        }
        .col { width: 100%; max-width: 680px; }

        h1 {
          font-family: 'Fraunces', Georgia, serif;
          font-weight: 560;
          font-size: clamp(34px, 6vw, 52px);
          line-height: 1.04;
          margin: 0 0 10px;
          letter-spacing: -0.01em;
        }
        .thesis { color: var(--muted); font-size: 15px; margin: 0 0 36px; max-width: 46ch; }

        .qLabel {
          font-size: 12px;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          color: var(--muted);
          margin: 26px 0 10px;
        }
        .qLabel b { color: var(--ivory); font-weight: 600; letter-spacing: 0.14em; }

        .chips { display: flex; flex-wrap: wrap; gap: 8px; }
        .chip {
          font-family: 'Spline Sans Mono', monospace;
          font-size: 14px;
          background: transparent;
          color: var(--muted);
          border: 1px solid var(--line);
          border-radius: 999px;
          padding: 8px 14px;
          cursor: pointer;
        }
        .chip:hover { border-color: rgba(239,233,218,0.4); }
        .chip.on { background: rgba(255,255,255,0.04); font-weight: 500; }
        .chip:focus-visible, input:focus-visible, .fieldBox:focus-within {
          outline: 2px solid var(--roth); outline-offset: 2px;
        }

        .details { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px; }
        .field { display: flex; flex-direction: column; gap: 6px; flex: 1 1 140px; }
        .fieldLabel { font-size: 12px; color: var(--muted); }
        .fieldBox {
          display: flex; align-items: baseline; gap: 4px;
          border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px;
          background: var(--vault2);
        }
        .fieldBox input {
          width: 100%; background: transparent; border: none; color: var(--ivory);
          font-family: 'Spline Sans Mono', monospace; font-size: 15px; outline: none;
        }
        .suffix { color: var(--muted); font-size: 13px; }

        .ledger { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 36px; }
        @media (max-width: 540px) { .ledger { grid-template-columns: 1fr; } }
        .card {
          background: var(--vault2);
          border: 1px solid var(--line);
          border-radius: 12px;
          padding: 18px 18px 16px;
        }
        .cardName {
          font-family: 'Fraunces', Georgia, serif;
          font-size: 19px; font-weight: 560; margin: 0 0 2px;
        }
        .card.tradC .cardName { color: var(--trad); }
        .card.rothC .cardName { color: var(--roth); }
        .cardSub { font-size: 12px; color: var(--muted); margin-bottom: 14px; }
        .row { display: flex; justify-content: space-between; gap: 10px; font-size: 13px; padding: 5px 0; color: var(--muted); }
        .row .num { font-family: 'Spline Sans Mono', monospace; color: var(--ivory); white-space: nowrap; }
        .row.tax .num { color: var(--carmine); }
        .total {
          border-top: 1px solid var(--line); margin-top: 10px; padding-top: 10px;
          display: flex; justify-content: space-between; align-items: baseline;
        }
        .total .num { font-family: 'Spline Sans Mono', monospace; font-size: 22px; }
        .card.tradC .total .num { color: var(--trad); }
        .card.rothC .total .num { color: var(--roth); }

        .verdictZone { margin: 34px 0 8px; min-height: 96px; display: flex; align-items: center; gap: 18px; flex-wrap: wrap; }
        .stamp {
          font-family: 'Fraunces', Georgia, serif;
          font-weight: 560; font-size: 26px; letter-spacing: 0.06em;
          border: 3px double currentColor; border-radius: 6px;
          padding: 10px 18px; transform: rotate(-4deg);
          animation: stampIn 260ms cubic-bezier(.2,1.4,.4,1) both;
          user-select: none;
        }
        .stamp.trad { color: var(--trad); }
        .stamp.roth { color: var(--roth); }
        .stamp.tie { color: var(--muted); }
        @keyframes stampIn {
          from { transform: scale(2.2) rotate(-14deg); opacity: 0; }
          to   { transform: scale(1) rotate(-4deg); opacity: 1; }
        }
        @media (prefers-reduced-motion: reduce) { .stamp { animation: none; } }
        .verdictWhy { font-size: 14px; color: var(--muted); max-width: 34ch; }
        .verdictWhy b { color: var(--ivory); font-weight: 600; }

        .rule { border: none; border-top: 1px solid var(--line); margin: 36px 0 20px; }
        h2 { font-family: 'Fraunces', Georgia, serif; font-weight: 560; font-size: 22px; margin: 0 0 14px; }
        .tie-list { list-style: none; margin: 0; padding: 0; }
        .tie-list li { padding: 9px 0; font-size: 14px; line-height: 1.5; border-bottom: 1px dashed rgba(239,233,218,0.08); }
        .tie-list li:last-child { border-bottom: none; }
        .tie-list .paren { color: var(--muted); }
        .foot { margin-top: 28px; font-size: 12px; color: var(--muted); line-height: 1.6; }
      `}</style>

      <div className="col">
        <h1>Traditional or Roth?</h1>
        <p className="thesis">
          It's one bet: your marginal tax rate <em>now</em> versus{" "}
          <em>in retirement</em>. Pay the IRS at whichever rate is lower.
          Everything else is a tiebreaker.
        </p>

        <div className="qLabel">
          Your marginal rate <b>today</b>
        </div>
        <Chips value={tNow} onChange={setTNow} accent="var(--roth)" />

        <div className="qLabel">
          Your marginal rate <b>in retirement</b>{" "}
          <span style={{ textTransform: "none", letterSpacing: 0 }}>
            (guess from planned spending — most people drop a bracket or two)
          </span>
        </div>
        <Chips value={tLater} onChange={setTLater} accent="var(--trad)" />

        <div className="qLabel">The dollar we'll follow</div>
        <div className="details">
          <Field label="Contribution" value={contrib} onChange={setContrib} suffix="$" min={0} step={1000} />
          <Field label="Years to retirement" value={years} onChange={setYears} suffix="yrs" min={0} max={60} step={1} />
          <Field label="Growth" value={growth} onChange={setGrowth} suffix="%/yr" min={0} max={20} step={0.5} />
        </div>

        <div className="ledger">
          <div className="card tradC">
            <p className="cardName">Traditional</p>
            <p className="cardSub">Deduct now, taxed on the way out</p>
            <div className="row"><span>Goes in pre-tax</span><span className="num">{usd(contrib)}</span></div>
            <div className="row"><span>Grows ×{G.toFixed(1)}</span><span className="num">{usd(gross)}</span></div>
            <div className="row tax"><span>IRS at withdrawal ({tLater}%)</span><span className="num">−{usd(gross - trad)}</span></div>
            <div className="total"><span>Yours to spend</span><span className="num">{usd(trad)}</span></div>
          </div>

          <div className="card rothC">
            <p className="cardName">Roth</p>
            <p className="cardSub">Taxed now, free on the way out</p>
            <div className="row tax"><span>IRS today ({tNow}%)</span><span className="num">−{usd(contrib - rothIn)}</span></div>
            <div className="row"><span>Goes in after-tax</span><span className="num">{usd(rothIn)}</span></div>
            <div className="row"><span>Grows ×{G.toFixed(1)}, tax-free</span><span className="num">{usd(roth)}</span></div>
            <div className="total"><span>Yours to spend</span><span className="num">{usd(roth)}</span></div>
          </div>
        </div>

        <div className="verdictZone">
          <div key={winner + tNow + tLater} className={stampClass}>
            {winner}
          </div>
          <div className="verdictWhy">
            {deadHeat ? (
              <>
                Equal rates make the two mathematically <b>identical</b>{" "}
                (multiplication commutes) — the tiebreakers below decide.
              </>
            ) : diff > 0 ? (
              <>
                Worth <b>{usd(Math.abs(diff))}</b> more: your rate falls from{" "}
                {tNow}% to {tLater}%, so deferring the tax wins.
              </>
            ) : (
              <>
                Worth <b>{usd(Math.abs(diff))}</b> more: your rate rises from{" "}
                {tNow}% to {tLater}%, so prepaying the tax wins.
              </>
            )}
          </div>
        </div>

        <hr className="rule" />

        <h2>Tiebreakers</h2>
        <ul className="tie-list">
          <li>
            Close call? Roth quietly shelters more — the contribution limit is
            the same nominal number, but Roth dollars are already taxed.{" "}
            <span className="paren">(A maxed Roth is worth more than a maxed
            Traditional at equal rates.)</span>
          </li>
          <li>
            Traditional IRAs force withdrawals at 73+; Roth IRAs never do.{" "}
            <span className="paren">(Roth 401(k)s dropped RMDs too, as of
            SECURE 2.0.)</span>
          </li>
          <li>
            Don't trust your guess about future rates? Split contributions —
            tax diversification is a legitimate answer, not a cop-out.
          </li>
          <li>
            High income blocks direct Roth IRA contributions.{" "}
            <span className="paren">(The Roth 401(k) has no income limit, and
            the backdoor Roth exists.)</span>
          </li>
        </ul>

        <p className="foot">
          Rule of thumb: early career or a low-income year → Roth; peak earning
          years → Traditional. (Assumes the tax saved by Traditional actually
          gets invested — if it'd get spent, Roth wins by default. Not tax
          advice.)
        </p>
      </div>
    </div>
  );
}
