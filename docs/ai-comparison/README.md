# Two AI builds of the same question

Exhibits for [FINDINGS, section 4](../FINDINGS.md#4-what-a-one-prompt-ai-build-got-right-and-what-it-put-last).
Both runs used Claude Fable 5 at high effort, on the morning of August 21, 2026.

## One prompt

> Traditional or Roth? Make an app to answer. Decide everything yourself. Don't read any of my memories.

| File | What it is |
|---|---|
| [traditional-or-roth.jsx](one-prompt/traditional-or-roth.jsx) | The app as generated, in one React file. It imports only React and loads its fonts from Google Fonts |
| [prompt-and-response.txt](one-prompt/prompt-and-response.txt) | The exchange, with the chat link removed |
| [above-the-fold.png](one-prompt/above-the-fold.png) | The rate chips, the ledger and the verdict stamp |
| [below-the-fold.png](one-prompt/below-the-fold.png) | The tiebreakers |

## A longer prompt

The second prompt added instructions about presenting the answer and about what a simple answer leaves out.
The run built one page in five parts.
Three of the parts are here, with its list of simplifications.

| File | What it shows |
|---|---|
| [part-1-the-identity.png](longer-prompt/part-1-the-identity.png) | Growth cancels out of the comparison |
| [part-2-the-two-rates.png](longer-prompt/part-2-the-two-rates.png) | Contributions come off the top of income, and withdrawals fill the brackets from zero |
| [part-3-where-the-symmetry-breaks.png](longer-prompt/part-3-where-the-symmetry-breaks.png) | The contribution cap, and the retirement rate as a forecast |
| [assumptions.png](longer-prompt/assumptions.png) | What the run simplified |

[Back to FINDINGS](../FINDINGS.md)
