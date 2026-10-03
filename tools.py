"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _size_matches(query_size: str, listing_size: str) -> bool:
    """
    Token match, not substring — "s" in "us 9" and "l" in "xl" are both True,
    which is exactly the false positive a plain `in` check produces.
    """
    return bool(_tokens(query_size) & _tokens(listing_size))


def _keyword_score(description: str, listing: dict) -> int:
    """Count of unique keywords shared between the query and the listing."""
    query_tokens = _tokens(description)
    haystack = " ".join([
        listing["title"],
        listing["description"],
        listing["category"],
        " ".join(listing["style_tags"]),
        " ".join(listing["colors"]),
        listing["brand"] or "",
    ])
    return len(query_tokens & _tokens(haystack))


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    Size matching: a query size matches a listing size when they share at
    least one token, where a token is a maximal run of letters/digits (so
    "W30 L30" tokenizes to {"w30", "l30"}, and "XL (oversized)" tokenizes to
    {"xl", "oversized"}). "M" matches "S/M" (shared token "m") but not "XL"
    (no shared token) — a plain substring check would wrongly match both.

    Keyword scoring: description and listing size/price are first filtered,
    then each remaining listing is scored by the number of unique keywords
    (same tokenization) it shares with `description`, searched across the
    listing's title, description, category, style_tags, colors, and brand.
    Anything scoring zero is dropped.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    listings = load_listings()

    filtered = []
    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue
        if size is not None and not _size_matches(size, listing["size"]):
            continue
        filtered.append(listing)

    scored = [
        (listing, _keyword_score(description, listing)) for listing in filtered
    ]
    scored = [pair for pair in scored if pair[1] > 0]
    scored.sort(key=lambda pair: pair[1], reverse=True)

    return [listing for listing, _ in scored[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already own.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    item_desc = (
        f"{new_item['title']} — a {new_item['category']} in "
        f"{', '.join(new_item['colors'])}, style: {', '.join(new_item['style_tags'])}, "
        f"${new_item['price']}"
    )

    items = wardrobe.get("items") or []
    if not items:
        prompt = (
            f"A thrifter is considering buying this item:\n{item_desc}\n\n"
            "They don't have a wardrobe logged yet. Suggest one or two general "
            "outfit ideas for this piece — what kinds of pieces (by category, "
            "color, and style) would pair well with it."
        )
    else:
        wardrobe_lines = "\n".join(
            f"- {item['name']} ({item['category']}, {', '.join(item['colors'])})"
            for item in items
        )
        prompt = (
            f"A thrifter is considering buying this item:\n{item_desc}\n\n"
            f"Here is their existing wardrobe:\n{wardrobe_lines}\n\n"
            "Suggest one or two complete outfits that pair the new item with "
            "specific pieces they already own, naming those pieces directly."
        )

    return generate(
        prompt,
        system=(
            "You are a thrift-shopping stylist. Keep suggestions short, "
            "specific, and grounded only in the items given."
        ),
    )


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return (
            f"No outfit suggestion to caption yet for {new_item['title']} "
            f"(${new_item['price']} on {new_item['platform']})."
        )

    prompt = (
        "Write a short social caption (two to four sentences) for this "
        "thrifted find, meant to be posted alongside a photo.\n\n"
        f"Item: {new_item['title']}\n"
        f"Price: ${new_item['price']}\n"
        f"Platform: {new_item['platform']}\n"
        f"Outfit idea: {outfit}\n\n"
        "Mention the price and the platform once each. Make it sound like a "
        "real post from the person who found it, specific about the vibe — "
        "not a product description."
    )

    return generate(
        prompt,
        system=(
            "You write short, casual social captions for thrifted fashion "
            "finds. Avoid sounding like a product listing."
        ),
    )
