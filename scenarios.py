"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    # Criterion 1 — five different queries that each match a listing.
    # Criterion 3 is scored on these same runs (the id passed to suggest_outfit
    # vs session['selected_item']['id']).
    {"name": 'match: graphic tee', "query": 'vintage graphic tee under $30', "wardrobe": 'example', "criterion": 1},
    {"name": 'match: flannel', "query": 'oversized flannel shirt', "wardrobe": 'example', "criterion": 1},
    {"name": 'match: linen trousers', "query": 'wide leg linen trousers', "wardrobe": 'example', "criterion": 1},
    {"name": 'match: denim jacket', "query": 'denim jacket under $50', "wardrobe": 'example', "criterion": 1},
    {"name": 'match: platform sneakers', "query": 'chunky platform sneakers', "wardrobe": 'example', "criterion": 1},
    # Criterion 2 — five impossible queries (both filters, size only, price only, neither, both).
    {"name": 'impossible: size+price', "query": 'designer ballgown size XXS under $5', "wardrobe": 'example', "criterion": 2},
    {"name": 'impossible: size only', "query": 'wedding tuxedo size XXL', "wardrobe": 'example', "criterion": 2},
    {"name": 'impossible: price only', "query": 'cashmere overcoat under $10', "wardrobe": 'example', "criterion": 2},
    {"name": 'impossible: neither', "query": 'quantum spaceship helmet', "wardrobe": 'example', "criterion": 2},
    {"name": 'impossible: size+price 2', "query": 'neon snowboard jumpsuit size XS under $3', "wardrobe": 'example', "criterion": 2},
    # Criterion 4 — fit card repeats: one item and one outfit, create_fit_card run
    # five times. score_criteria.py does this directly; this scenario is the item.
    {"name": 'fit card repeats', "query": 'vintage graphic tee under $30', "wardrobe": 'example', "criterion": 4},
    # Criterion 5 — five (query, max_price) pairs; every result must be <= max_price.
    {"name": 'budget: jacket', "query": 'vintage jacket under $30', "wardrobe": 'example', "criterion": 5},
    {"name": 'budget: jeans', "query": 'jeans under $25', "wardrobe": 'example', "criterion": 5},
    {"name": 'budget: sweatshirt', "query": 'sweatshirt under $15', "wardrobe": 'example', "criterion": 5},
    {"name": 'budget: blazer', "query": 'blazer under $40', "wardrobe": 'example', "criterion": 5},
    {"name": 'budget: knit', "query": 'knit top under $20', "wardrobe": 'example', "criterion": 5},
    # Diagnostic — not one of the five.
    {"name": 'empty wardrobe', "query": 'denim jacket under $50', "wardrobe": 'empty', "criterion": None},
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
