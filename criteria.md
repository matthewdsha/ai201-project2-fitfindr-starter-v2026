# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given 5 different queries, each one matching at least one listing, the agent
finishes with `session["error"]` still `None` and `session["fit_card"]` a
non-empty string — in at least 4 of the 5 queries.

**Why this target:**
`search_listings` matches on keywords, not meaning, so a real match can get
missed just from wording (e.g. "tee" vs. a listing titled "t-shirt"). That's
a limit of the search, not the loop, so I expect to miss sometimes — just
not more than once in five.

---

## 2. An impossible query stops before the second tool

Given 5 different queries, each matching no listings, the agent stops before
calling `suggest_outfit`, and the message in `session["error"]` names every
filter the query actually set (the price ceiling, the size — both, if both
were given) or, if neither was set, contains the word "keywords" — in 5 of 5.

**Why this target:**
This is just checking whether a list is empty — no model call, no scoring,
nothing left to chance. If it ever fails, that's a bug, not bad luck.

---

## 3. Something about state

Given 5 different matching queries, wrap `suggest_outfit` to record the `id`
of the `new_item` it's actually called with. That recorded `id` matches
`session["selected_item"]["id"]` from the same run — in 5 of 5.

**Why this target:**
This is just code passing a value along — no model, no matching, nothing
random about it. If the `id` ever changes, that's a bug in the loop, not
bad luck.

---

## 4. Something about the fit card

Given the same item and outfit, run `create_fit_card` 5 times. Call a run a
pass only if its opening sentence (everything up to the first `.`, `!`, or
`?`) matches no other run's, and the card contains both a dollar sign
followed by the listing's exact `price` value (e.g. "$24.99", not "twenty-
five dollars") and its platform name, case-insensitive. At least 4 of 5 runs
pass.

**Why this target:**
At `TEMPERATURE = 0.9` the cards shouldn't repeat themselves — if they do,
that's `CACHE_ENABLED` or the temperature, not the model. But remembering to
mention both the price and the platform every time means the model has to
follow instructions perfectly, and it won't always, so I leave room for one
miss.

---

## 5. Your choice

Given 5 different (query, `max_price`) pairs, every item `search_listings`
returns in each run costs `max_price` or less, with zero violations across
all 5 runs.

**Why this target:**
This is just a number comparison, done before any scoring happens. There's
no reason it should ever let a too-expensive item through, so I'm not giving
it any slack.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
