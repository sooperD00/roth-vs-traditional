"""Check that the docs still point at things that exist.

    uv run python scripts/check_docs.py

Four checks over every tracked markdown file, plus the code and tests:
  1. relative links and images resolve to a file in the repo
  2. #anchors resolve to a heading, slugged the way GitHub slugs them
  3. every decision ID (D-xx) and risk ID (Rn) cited anywhere is defined in docs/DECISIONS.md
  4. every "DECISIONS section 6" / "RESULTS 8.4"-style reference names a heading that exists

Frozen records (the showcase reading list, captured script output) are skipped
for checks 3 and 4: they describe the repo as it was when they were written.

Exit 0 when clean, 1 with a list of problems otherwise.
"""
import collections
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = {"DECISIONS": "docs/DECISIONS.md", "RESULTS": "docs/RESULTS.md",
        "ENGINE": "docs/ENGINE.md", "DESIGN": "docs/DESIGN.md"}
LINK = re.compile(r"!?\[(?:[^\]\[]|\[[^\]]*\])*\]\(([^)\s]+)\)")
FROZEN = re.compile(r"^(prompts/|method/.*\.txt$|scripts/.*\.txt$)")
SECTION_REF = re.compile(
    r"\b(DECISIONS|RESULTS|ENGINE|DESIGN)(?:\.md)?(?:'s)? (?:section |§ ?)?(\d+(?:\.\d+)?[a-z]?)\b")


def tracked(*patterns):
    out = subprocess.run(["git", "ls-files", *patterns], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    return [ROOT / p for p in out.split()]


def headings(path):
    """Heading texts outside fenced code blocks."""
    found, fenced = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and (m := re.match(r"^#{1,6} (.+?)\s*#*\s*$", line)):
            found.append(m.group(1))
    return found


def slugs(path):
    """GitHub's anchor rule: lowercase, drop everything but word characters,
    spaces and hyphens, turn each space into a hyphen, suffix repeats -1, -2."""
    seen, out = collections.Counter(), set()
    for text in headings(path):
        text = re.sub(r"<[^>]+>", "", text).lower()
        s = re.sub(r"[^\w\- ]", "", text).replace(" ", "-")
        out.add(s if not seen[s] else f"{s}-{seen[s]}")
        seen[s] += 1
    return out


def main():
    problems = []
    md_files = tracked("*.md")

    for md in md_files:
        text = md.read_text(encoding="utf-8")
        for n, line in enumerate(text.splitlines(), 1):
            for target in LINK.findall(line):
                if re.match(r"^[a-z]+:", target):          # http:, https:, mailto:
                    continue
                path_part, _, anchor = target.partition("#")
                dest = (md.parent / path_part).resolve() if path_part else md
                where = f"{md.relative_to(ROOT)}:{n}"
                if not dest.exists():
                    problems.append(f"{where}  missing file: {target}")
                elif anchor and dest.suffix == ".md" and anchor not in slugs(dest):
                    problems.append(f"{where}  missing anchor: {target}")

    decisions = (ROOT / DOCS["DECISIONS"]).read_text(encoding="utf-8")
    defined_d = set(re.findall(r"^\| (D-\d+[a-z]?) \|", decisions, re.M))
    defined_d |= set(re.findall(r"^### (D-\d+[a-z]?)\b", decisions, re.M))
    defined_r = set(re.findall(r"^\| (R\d+) \|", decisions, re.M))
    heads = {k: headings(ROOT / v) for k, v in DOCS.items()}

    for f in tracked("*.md", "*.py", "*.txt", "*.sh", "*.toml"):
        rel = f.relative_to(ROOT)
        if FROZEN.match(rel.as_posix()):
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for d in re.findall(r"\bD-\d+[a-z]?\b", line):
                if d not in defined_d:
                    problems.append(f"{rel}:{n}  undefined decision: {d}")
            for r in re.findall(r"\b(R\d)\b", line):
                if r not in defined_r:
                    problems.append(f"{rel}:{n}  undefined risk: {r}")
            for doc, num in SECTION_REF.findall(line):
                pat = re.compile(rf"^§?{re.escape(num)}(?:[.\s—]|$)")
                if not any(pat.match(h) for h in heads[doc]):
                    problems.append(f"{rel}:{n}  no heading {num} in {DOCS[doc]}")

    for p in problems:
        print(p)
    ids = f"{len(defined_d)} decisions, {len(defined_r)} risks"
    print(f"{len(md_files)} markdown files, {ids}: "
          + ("CLEAN" if not problems else f"{len(problems)} problems"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
