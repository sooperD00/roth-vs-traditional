# Method: one reading list per session

Every build session started with an empty context and a repo full of long documents.
A session that read everything spent its context budget (how much text a model can hold at once) before it wrote any code.
I added one step between sessions.
A planning session wrote the next build session a reading list: what to read in full, which sections to read, what not to open, and when to stop and ask.

| File | What it is |
|---|---|
| [readinglist.sh](readinglist.sh) | The script that drafts a list |
| [reading-list-sprint-8-draft.txt](reading-list-sprint-8-draft.txt) | Its draft for Sprint 8, the sprint that built the three panels |
| [reading-list-sprint-8-panels.txt](reading-list-sprint-8-panels.txt) | The list Sprint 8 got |

## What the script does

It cuts one sprint's section out of the plan and collects the decision, test and risk IDs that section names.
It also works backwards, from the sprint's tests to the decision rows that name them.
It maps each decision to the section of DECISIONS that holds it, so the list names sections instead of IDs.
Everything else goes under DO NOT READ.
Then it prints eight notes on what it cannot see, and each note names the sprint that taught it.

## The draft beside the final list

The draft is the script's output for Sprint 8, run against the plan and DECISIONS as they stood on August 20, 2026, the day the final list was written.

The draft chose well among the decisions.
Nine of its eleven made the final list.
The final list added five more and marked two long ones to skip.

On files, the draft was backwards.
It put `app.py`, `DESIGN.md`, `RESULTS.md` and `tests/test_app.py` under DO NOT READ, and the session needed all four.
It put `engine.py` and `tests/test_engine.py` under READ IN FULL, and the final list dropped both.
`engine.py` alone is 86k characters, and the session used three names from it.
The final list came to about 44k tokens.

The final list also holds what no script writes: two traps where the plan's own acceptance criteria contradict the committed results file, `cube.json`, three decisions to bring to me before drawing anything, and the order to build in.

## What is not here

The session prompts, the plan and the design reviews stay private.
The script reads the plan from `docs/remaining-sprints.md`, so it does not run in this repo as published.
(It uses only grep, sed, awk, sort and comm, so it also runs in Git Bash on Windows.)

[Back to the README](../README.md)
