
# Process
- [x] init
- [x] discovery
- [x] research
- [x] synthesis
- [ ] design
- [ ] final scope
- [ ] plan
- [ ] deliver

## Domain Analogs

This project models a 401k Roth-vs-Traditional decision, but the problem
shape is an energy analyst's. A tariff and the tax code are the same math object: a
piecewise, jurisdiction-specific, customer-class-dependent rule structure
that converts a quantity into a cost, imposed on the user rather than
chosen by them. Marginal brackets are tiered block rates. A Roth conversion
or an RSU vest is a demand charge — the peak sets the bill, not the
average. And the assumption that decides the answer in both domains is the
one nobody can know: a 25-year utility rate escalator and a 30-year future
tax rate are the same scalar hiding in the same spreadsheet cell.

The full mapping — nine analog pairs, including load profile ↔ contribution
schedule and payback year ↔ break-even marginal rate — is in
[docs/DESIGN.md/#domainanalogs](docs/DESIGN.md/#domainanalogs).

MVP Highlight: **net metering ≡ Roth.** Both ask you to pay a known cost 
today in exchange for favorable treatment under a rule that may change. 
Retroactive net metering rollbacks are not a hypothetical, and neither are the 
tax-treatment changes that have hit retirement accounts elsewhere [##References].

- [ ] **DELIVERABLE: put something in the prototype or PoC that
  shows the end-user what "the rules will change" can mean

# AI Disclosure

1. research 2 -- with Claude Opus 5, Max Thinking
 - (kept private)

2. code execution -- with Claude Opus 5, Max Thinking


# References

1. reddit r/personalfinance flow doc
    - docs/reddit_personal_finance_flowchart.jpeg
    - https://www.reddit.com/r/personalfinance/comments/4gdlu9/how_to_prioritize_spending_your_money_a_flowchart/

2. Hadamard's Uniqueness Condition
    - "the" failing is exactly Hadamard's uniqueness condition — his 1902 criteria for a well-posed problem being existence, uniqueness, and stable dependence on the inputs. A problem with an unknowable input doesn't have a unique solution; it has a solution family. Reporting the threshold is how you make an ill-posed question answerable without lying about it.

3. Decades Long Bet on a Rule
    - Argentina 2008 (private pension funds nationalized into the state system)
    - Poland 2013-14 (the government cancelled the bond portion of private pension accounts outright)
    - Hungary 2010-11 (effectively forced transfers back to the state pillar)
    - Ireland's 2011-14 pension levy (an annual tax on private pension assets, not income)
    - Spain drew heavily on its social security reserve fund
    - U.S. SECURE Act (2019) eliminated the stretch IRA (retroactively changed the inheritance 
    math for accounts people had already spent decades building. Nobody's money was seized, 
    but the rule moved under people who had already committed).