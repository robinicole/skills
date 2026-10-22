"""Check eval prompts against the ml skills.

Two modes:
  keyword (default, free): a skill matches a prompt when one of the quoted trigger
      phrases in its description appears in the prompt (case-insensitive). This is
      a cheap approximation of how Claude picks skills; paraphrase cases are
      reported but do not fail it.
  cli (on demand, costs tokens): runs `claude -p` once per case with this plugin
      loaded and records the Skill tool calls in the first three turns. This is the real trigger test.

Pass rules:
  - A no-trigger case fails if any ml skill matches or is called.
  - An explicit case fails unless exactly its own skill matches (keyword) or is called (cli).
  - A paraphrase case fails in cli mode unless its own skill is called.

Usage:
  python evals/trigger_eval.py                      # keyword mode
  python evals/trigger_eval.py --mode cli -j 4      # real trigger test
  python evals/trigger_eval.py --mode cli --case no_trigger_causal_01
Results go to evals/runs/ (git-ignored).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import re
import subprocess
import tempfile
from pathlib import Path

import yaml

PLUGIN = Path(__file__).resolve().parents[1]
CASES = PLUGIN / "evals" / "cases"
RUNS = PLUGIN / "evals" / "runs"
PREFIX = "ml:"


def load_skills() -> dict[str, dict]:
    out = {}
    for f in sorted((PLUGIN / "skills").glob("*/SKILL.md")):
        text = f.read_text()
        fm = yaml.safe_load(text.split("---")[1])
        desc = fm["description"]
        phrases = [p.lower() for p in re.findall(r'"([^"]+)"', desc)]
        out[fm["name"]] = {"description": desc, "phrases": phrases}
    return out


def load_cases(pattern: str | None) -> list[dict]:
    cases = [yaml.safe_load(p.read_text()) for p in sorted(CASES.rglob("*.yaml"))]
    if pattern:
        cases = [c for c in cases if re.search(pattern, c["name"])]
    return cases


# Task skills are defined by what the user wants done (practise, audit, report),
# method skills by a topic. A prompt such as "audit the skew in my pipeline"
# names both; the task wins. This mirrors the "Not for" sentences in the descriptions.
TASK_SKILLS = {"ml-auditor"}


def keyword_match(prompt: str, skills: dict) -> list[str]:
    p = " ".join(prompt.lower().split())
    hits = sorted(n for n, s in skills.items() if any(ph in p for ph in s["phrases"]))
    tasks = [h for h in hits if h in TASK_SKILLS]
    return tasks or hits


LAST_TOOLS: dict[str, list[str]] = {}


def cli_match(prompt: str, timeout: int = 300) -> list[str]:
    cmd = ["claude", "-p", prompt, "--plugin-dir", str(PLUGIN), "--output-format", "stream-json",
           "--verbose", "--max-turns", "3",
           "--disallowedTools", "Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch", "WebSearch", "Agent"]
    called: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.Popen(cmd, cwd=tmp, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, text=True)
        try:
            for line in proc.stdout:
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("type") == "assistant":
                    tools = [c for c in ev["message"]["content"] if c.get("type") == "tool_use"]
                    LAST_TOOLS.setdefault(prompt, []).extend(t["name"] for t in tools)
                    for t in tools:
                        if t["name"] == "Skill":
                            called.append(t["input"].get("skill", ""))
                    if called:
                        break
                if ev.get("type") == "result":
                    break
        finally:
            proc.kill()
            proc.wait(timeout=timeout)
    return sorted({c.removeprefix(PREFIX) for c in called if c.startswith(PREFIX)})


def judge(case: dict, matched: list[str], mode: str) -> tuple[str, str]:
    want = case["expected"]["should_trigger"]
    if not want:
        return ("PASS", "") if not matched else ("FAIL", f"triggered {matched}")
    own = case["skill"]
    if case["kind"] == "explicit" or mode == "cli":
        if matched == [own]:
            return "PASS", ""
        return ("FAIL", f"expected [{own}], got {matched}")
    return ("PASS" if own in matched else "INFO", f"keyword got {matched}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["keyword", "cli"], default="keyword")
    ap.add_argument("--case", help="regex on case names")
    ap.add_argument("-j", type=int, default=1, help="parallel CLI runs")
    args = ap.parse_args()

    skills = load_skills()
    cases = load_cases(args.case)
    if args.mode == "keyword":
        matched = [keyword_match(c["user_message"], skills) for c in cases]
    else:
        with cf.ThreadPoolExecutor(max_workers=args.j) as ex:
            matched = list(ex.map(lambda c: cli_match(c["user_message"]), cases))

    rows, fails = [], 0
    for c, m in zip(cases, matched):
        status, note = judge(c, m, args.mode)
        fails += status == "FAIL"
        first = LAST_TOOLS.get(c["user_message"], [])
        if args.mode == "cli" and status == "FAIL" and not m:
            note += f" (first tool call: {first or 'none, answered in text'})"
        rows.append({"case": c["name"], "skill": c["skill"], "status": status, "matched": m,
                     "first_tool": first, "note": note})
        print(f"{status:5s} {c['name']:45s} {note}")
    RUNS.mkdir(exist_ok=True)
    out = RUNS / f"trigger_{args.mode}_{dt.datetime.now():%Y%m%d_%H%M%S}.json"
    out.write_text(json.dumps(rows, indent=2))
    n_info = sum(r["status"] == "INFO" for r in rows)
    print(f"\n{len(rows)} cases, {fails} failed, {n_info} informational. Saved {out}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
