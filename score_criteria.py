#!/usr/bin/env python3
"""
Score the five criteria in criteria.md against the scenarios in scenarios.py.

    python score_criteria.py --label before

run_eval.py runs scenarios and records them but doesn't judge them, and
criteria 3 and 4 need instrumentation it doesn't have. This does the judging
the way each criterion is written: five different queries (criteria 1, 2, 3, 5)
or five runs of one item (criterion 4), caching off. Try N is query N.
"""

import argparse
import datetime as dt
import re

import config

config.CACHE_ENABLED = False

import agent
import scenarios
import tools
from utils.data_loader import get_example_wardrobe

TRIES = 5


def by_criterion(n):
    return [s for s in scenarios.SCENARIOS if s["criterion"] == n]


def run(query, wardrobe=None):
    """run_agent with suggest_outfit wrapped to record the id it was called with."""
    seen = []
    real = agent.suggest_outfit

    def wrapped(new_item, wardrobe_):
        seen.append(new_item["id"])
        return real(new_item, wardrobe_)

    agent.suggest_outfit = wrapped
    try:
        session = agent.run_agent(query, wardrobe or get_example_wardrobe())
    finally:
        agent.suggest_outfit = real
    return session, seen


def opening(text):
    return re.split(r"[.!?]", text.strip(), maxsplit=1)[0].strip().lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="before")
    args = parser.parse_args()

    log, rows = [], {}

    # ── criteria 1 and 3: same five matching queries ──
    c1, c3 = [], []
    for s in by_criterion(1):
        session, seen = run(s["query"])
        ok1 = session["error"] is None and bool((session["fit_card"] or "").strip())
        sel = (session["selected_item"] or {}).get("id")
        ok3 = bool(seen) and seen == [sel]
        c1.append(ok1)
        c3.append(ok3)
        log.append(f"### C1/C3 — `{s['query']}`\n\n- error: {session['error']}\n"
                   f"- selected_item id: {sel}; id passed to suggest_outfit: {seen}\n"
                   f"- fit_card: {session['fit_card']!r}\n- C1 {'PASS' if ok1 else 'FAIL'}, "
                   f"C3 {'PASS' if ok3 else 'FAIL'}\n")
    rows[1], rows[3] = c1, c3

    # ── criterion 2: impossible queries ──
    c2 = []
    for s in by_criterion(2):
        session, seen = run(s["query"])
        p = session["parsed"]
        err = session["error"] or ""
        names = []
        if p["max_price"] is not None:
            names.append(f"{p['max_price']:g}")
        if p["size"] is not None:
            names.append(p["size"])
        if names:
            named = all(n.lower() in err.lower() for n in names)
        else:
            named = "keywords" in err.lower()
        ok = bool(err) and not seen and session["outfit_suggestion"] is None and named
        c2.append(ok)
        log.append(f"### C2 — `{s['query']}`\n\n- parsed: {p}\n- suggest_outfit called: {bool(seen)}\n"
                   f"- error: {err}\n- {'PASS' if ok else 'FAIL'}\n")
    rows[2] = c2

    # ── criterion 4: same item + outfit, five fit cards ──
    s4 = by_criterion(4)[0]
    session = agent.run_agent(s4["query"], get_example_wardrobe())
    item, outfit = session["selected_item"], session["outfit_suggestion"]
    cards = [tools.create_fit_card(outfit, item) for _ in range(TRIES)]
    openers = [opening(c) for c in cards]
    c4 = []
    for i, card in enumerate(cards):
        unique = openers.count(openers[i]) == 1
        prices = [float(m) for m in re.findall(r"\$(\d+(?:\.\d+)?)", card)]
        has_price = item["price"] in prices
        has_platform = item["platform"].lower() in card.lower()
        ok = unique and has_price and has_platform
        c4.append(ok)
        log.append(f"### C4 try {i + 1} — {item['title']} (${item['price']}, {item['platform']})\n\n"
                   f"```\n{card}\n```\n- unique opening: {unique}; price ${item['price']:g} present: "
                   f"{has_price}; platform present: {has_platform}\n- {'PASS' if ok else 'FAIL'}\n")
    rows[4] = c4

    # ── criterion 5: nothing over max_price ──
    c5 = []
    for s in by_criterion(5):
        p = agent._parse_query(s["query"])
        results = tools.search_listings(p["description"], p["size"], p["max_price"])
        over = [r for r in results if r["price"] > p["max_price"]]
        ok = not over
        c5.append(ok)
        log.append(f"### C5 — `{s['query']}` (max_price {p['max_price']:g})\n\n"
                   f"- {len(results)} results, prices {[r['price'] for r in results]}\n"
                   f"- over budget: {[r['title'] for r in over]}\n- {'PASS' if ok else 'FAIL'}\n")
    rows[5] = c5

    targets = {1: 4, 2: 5, 3: 5, 4: 4, 5: 5}
    names = {1: "A matching query completes all three tools",
             2: "An impossible query stops before the second tool",
             3: "Item in session matches item passed on",
             4: "Fit card: distinct opening, price and platform",
             5: "Nothing returned over max_price"}
    table = ["| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |",
             "|---|---|---|---|---|---|---|---|"]
    for n in range(1, 6):
        marks = ["PASS" if r else "FAIL" for r in rows[n]]
        k = sum(rows[n])
        verdict = f"{'MET' if k >= targets[n] else 'MISSED'} ({k}/5)"
        table.append(f"| {n}. {names[n]} | {targets[n]} of 5 | " + " | ".join(marks) + f" | {verdict} |")

    config.RESULTS_DIR.mkdir(exist_ok=True)
    path = config.RESULTS_DIR / f"scored_{dt.datetime.now():%Y-%m-%d_%H%M}_{args.label}.md"
    text = (f"# Scored run — {args.label}\n\n- Produced by: `score_criteria.py::main`\n"
            f"- Cache off, temperature {config.TEMPERATURE}\n\n" + "\n".join(table) +
            "\n\n---\n\n" + "\n".join(log))
    path.write_text(text, encoding="utf-8")
    print("\n".join(table))
    print(f"\nWrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
