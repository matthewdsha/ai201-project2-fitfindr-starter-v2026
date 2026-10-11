# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

A user types a plain-language query — "vintage graphic tee under $30" — along with their wardrobe. FitFindr searches thrift listings for a match, asks the model for an outfit pairing the item with pieces the user already owns, and writes a short social caption mentioning the item's price and platform. If nothing matches the query, it stops early and says what to change instead of forcing an outfit and caption onto nothing.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Finds listings matching a description, size, and max price.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None)
- **Returns:** A list of matching listing dicts (each with `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, `platform`), ranked by keyword overlap with `description` — zero-overlap items are dropped, best match first. Size match is whole-token and case-insensitive ("M" matches "S/M" but not "US 9" or "XL") — not a substring test.
- **When it has nothing:** Empty list (`[]`) — never `None`, never an exception.

### `suggest_outfit`

- **What it does:** Suggests an outfit pairing a new item with the user's wardrobe.
- **Inputs:** `new_item` (dict), `wardrobe` (dict with an `items` list)
- **Returns:** A non-empty string with outfit suggestions.
- **When it has nothing:** Empty wardrobe (`wardrobe['items'] == []`) → general styling advice instead, still a non-empty string — never raises, never `""`.

### `create_fit_card`

- **What it does:** Writes a short caption for the item and outfit, mentioning the item, its price, and its platform once each.
- **Inputs:** `outfit` (str), `new_item` (dict)
- **Returns:** A 2-4 sentence caption string.
- **When it has nothing:** Empty or whitespace-only `outfit` → a descriptive message saying no fit card could be made, instead of raising.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` — saying what the user could change, not just "no results" — and stop, without calling `suggest_outfit` or `create_fit_card`. Otherwise, take the first result as `session["selected_item"]` and go to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex — one pattern pulls `max_price` out of "under $N", another pulls `size` out of "size X"; whatever's left after removing both becomes `description`.

**What moves through the session:** `query` → `parsed` (description/size/max_price) → `search_results` → `selected_item` → `outfit_suggestion` → `fit_card`. `error` is set only if the branch stops early, in which case the later fields stay `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   **Outfit 1 (Casual Y2K):**
Pair the Y2K butterfly baby tee with your baggy straight-leg dark wash jeans, layered under the black cropped zip hoodie. Finish with chunky white sneakers and the black crossbody bag.

**Outfit 2 (Contrast Mix):**
Pair the baby tee tucked into your wide-leg khaki trousers, cinched with the brown leather belt, and top it with the vintage black denim jacket. Complete the look with your black combat boots.

  Fit card: Found this absolute gem of a butterfly tee while digging through the racks this weekend. Giving major 2000s mallrat energy, and honestly, I might keep it for myself if nobody snags it. Grab it on my depop for just $18 before I change my mind!

0 model calls this session, 2 served from cache
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
**Outfit 1: Casual Streetwear**
*   **Top:** White ribbed tank top
*   **Outerwear:** Oversized grey crewneck sweatshirt
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag

**Outfit 2: Edge & Contrast**
*   **Top:** Black cropped zip hoodie
*   **Outerwear:** Vintage black denim jacket
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Nothing beats the hunt for the ultimate vintage 501s, especially when they actually fit like a glove. Just threw these on with my go-to white sneakers and honestly, the medium wash wear-in is unreal. Snagged them for $38 and they're live on my depop now.

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked Claude to attack the five acceptance criteria
  in `criteria.md` — could someone check each one without asking me what I
  meant.
- *What came back:* It found that several "N of 5 tries" targets never said
  what varies between the five tries. For criterion 1, running the *same*
  query five times against a deterministic keyword search gives 5/5 or 0/5,
  never 4/5 — the 4/5 target only makes sense across five *different*
  matching queries. The fit-card criterion also bundled two separate checks
  (no-repeat openings, mentions price/platform) under one rate with neither
  defined precisely enough to code into a test.
- *What I changed:* Rewrote all five criteria to name exactly what varies
  across the five tries, and made "opening sentence" and "mentions
  price/platform" concrete enough to check (text up to the first `.`/`!`/`?`;
  a literal `$`+exact price substring and a case-insensitive platform match).

**Moment 2**

- *What I asked for:* After pasting the three tool tests into the README's
  Sample Run section, I asked Claude to confirm the output was good and
  already pasted in.
- *What came back:* It flagged itself that the `search_listings` output had
  been abbreviated with `...` for readability, which conflicts with the
  README's own instruction that only a full typed block of output earns
  credit — a picture or summary of the output does not.
- *What I changed:* Had it replace the abbreviated list with the complete,
  unabbreviated output before committing.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Item in session matches item passed on | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card: distinct opening, price and platform | 4 of 5 | PASS | FAIL | PASS | FAIL | PASS | MISSED (3/5) |
| 5. Nothing returned over max_price | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

How the tries were run: caching off, temperature 0.9. For criteria 1, 2, 3 and 5 the criterion asks for five *different* queries, so Try N is query N (all in `scenarios.py`). Criterion 3 is scored on the same five runs as criterion 1, with `suggest_outfit` wrapped to record the id it received. For criterion 4, Try N is fit card N for one item and one outfit (Y2K Baby Tee, same outfit text). Scoring is done by `score_criteria.py::main`; the full output is `results/scored_2026-10-11_1814_before.md`. Criterion 4 counts a price as present when a `$` amount equals the listing price numerically ("$18" for 18.0 counts; "18 bucks" does not).

**Real output from one try per criterion**, from `score_criteria.py` calling `agent.py::run_agent` and `tools.py::create_fit_card`:

Criterion 1, query `oversized flannel shirt` (`agent.py::run_agent`, fit_card):
```
error: None
fit_card: 'Scored this oversized red plaid for just $22 on thredUp and honestly, it’s about to become my whole personality. Total 90s grunge energy open over a ribbed tank, or layered under a cropped hoodie when it gets chilly. Can’t beat a good flannel find.'
```

Criterion 2, query `quantum spaceship helmet` (`agent.py::run_agent`, session["error"]; no filters set, so it must say "keywords"):
```
parsed: {'description': 'quantum spaceship helmet', 'size': None, 'max_price': None}
suggest_outfit called: False
error: No listings matched "quantum spaceship helmet". Try different keywords.
```

Criterion 3, query `vintage graphic tee under $30` (`agent.py::run_agent`, suggest_outfit wrapped):
```
selected_item id: lst_002; id passed to suggest_outfit: ['lst_002']
```

Criterion 4, try 4, a FAIL (`tools.py::create_fit_card`; the opening sentence is the same as try 2's, and the price is written "18 bucks" with no `$`):
```
Found this little butterfly tee and I'm obsessed with the print. It’s giving major early 2000s energy and looks so good with baggy denim or contrasted with some edgy black boots. Up on Depop now for 18 bucks if you need it!
```
Try 2, the other FAIL (same opening sentence as try 4, "Found this little butterfly tee and I'm obsessed with the print."):
```
Found this little butterfly tee and I'm obsessed with the print. Already picturing it with baggy denim and a zip hoodie. Snagged it for $18 over on depop before someone else could!
```

Criterion 5, query `vintage jacket under $30`, max_price 30 (`tools.py::search_listings`):
```
10 results, prices [18.0, 22.0, 24.0, 20.0, 30.0, 12.0, 26.0, 24.0, 16.0, 29.0]
over budget: []
```
Note: two of the five criterion-5 queries (`jeans under $25`, `sweatshirt under $15`) returned zero results. That is correct (the matching jeans cost $30 to $38 and the only matching sweatshirt costs $20), so the price filter is working, but those two passes mean "nothing over budget" rather than "checked several prices".

Also noticed: `vintage graphic tee under $30` selects the Y2K Baby Tee (lst_002), not the item titled "Graphic Tee — 2003 Tour Bootleg Style" (lst_006, size L). The keyword search ranks it first, which is what criterion 1's own "Why this target" predicted.

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools | 4 of 5 | **MET** (5/5) | All five queries ended with `session["error"]` None and a non-empty `fit_card`. |
| 2 | An impossible query stops before the second tool | 5 of 5 | **MET** (5/5) | `suggest_outfit` was never called in any of the five, and each message named every filter set (or said "keywords" when none was). |
| 3 | Item in session matches item passed on | 5 of 5 | **MET** (5/5) | The id recorded by the wrapped `suggest_outfit` equalled `session["selected_item"]["id"]` in all five runs. |
| 4 | Fit card: distinct opening, price and platform | 4 of 5 | **MISSED** (3/5) | Tries 1, 3, 5 passed. Tries 2 and 4 share the opening sentence "Found this little butterfly tee and I'm obsessed with the print." and so both fail; try 4 also has no `$` price. |
| 5 | Nothing returned over max_price | 5 of 5 | **MET** (5/5) | No result in any of the five runs cost more than its `max_price`. Two of the five returned no results at all (see below). |

**Diagnoses**

**Criterion 4 (the only miss): the model's output, steered by the prompt in `tools.py::create_fit_card`.** The tool ran every time and the loop and session were fine. Two separate things went wrong, both on the same step:

- *Repeated opening (tries 2 and 4).* All five calls get an identical prompt (same item, same outfit text), and temperature is 0.9, so wording varies but the opening doesn't vary enough. "Found this … butterfly tee" is the natural first sentence for a casual caption about one specific item, and nothing in the prompt asks for variety. The sampling randomness isn't the cause, since the cache was off and the five cards were all different overall. The prompt gives the model no reason to open differently.
- *Price not written as a dollar amount (try 4).* The prompt says "Mention the price and the platform once each" and shows `Price: $18.0`, but doesn't say to write it with a `$`. The model wrote "18 bucks", which is a fair reading of the prompt and a miss against the criterion.

Both fixes would live in the same place, the prompt, so this is one problem, not two. The other four criteria passed because they test code (a branch, a pass-through, a number comparison) rather than model wording. The model-dependent criterion is the one that missed.

**Pattern:** the misses are all model output, none are tool, branch or session bugs.

**On the criterion's wording (not revised):** criterion 4 says "a dollar sign followed by the listing's exact `price` value (e.g. $24.99)". My listing's price is stored as `18.0`, so the literal string "$18.0" never appeared in any card; I counted a numerically equal `$18` as a pass. A strict reading would fail all five tries on price. That doesn't change the verdict (MISSED either way) and I'm not changing the criterion, because I'm not lowering a target; I'm noting that the price format was ambiguous and I read it generously.

**Arguing the opposite verdict for each one** (my own cross-examination, trying to flip each call):

- *Criterion 1, MET → could it be MISSED?* The strongest case: "completes all three tools" is checked only as "no error and a non-empty string", so a run can pass while returning the wrong thing. It did: `vintage graphic tee under $30` selected the Y2K Baby Tee, not the item titled "Graphic Tee — 2003 Tour Bootleg Style". And I picked five queries I knew would match. That is a fair criticism of the criterion's strength, but the criterion as written is about completion, and all five completed. **Verdict stands: MET.** The target (4 of 5) was probably easy for these five queries; the keyword-match problem it was meant to leave room for didn't show up in my set.
- *Criterion 2, MET → MISSED?* Weak case. The checks (wrapper never called, message names every filter or "keywords") held for all five, including the size-only and price-only variants. **Verdict stands.**
- *Criterion 3, MET → MISSED?* There's no way to argue a failure, but there is an argument that the pass means little: the loop sets `selected_item` once and passes that same variable on, so almost nothing can make the ids differ. **Verdict stands: MET**, but this is the criterion I'd tighten. Next time I'd check the item the model's outfit text actually mentions, not just the id that was passed.
- *Criterion 4, MISSED → could it be MET?* The strongest case: tries 2 and 4 only "fail" because they match *each other*, so it could be read as one duplicate rather than two failures, which would give 4 of 5. But the criterion says a run passes only if its opening matches *no other* run's, so both fail. And try 4 independently fails on price. **Verdict stands: MISSED (3/5).**
- *Criterion 5, MET → MISSED?* Two of the five queries (`jeans under $25`, `sweatshirt under $15`) returned zero results, so those passes are empty, not confirmed. The criterion is "zero violations across all 5 runs", which holds, but only three runs actually exercised the filter. **Verdict stands: MET**, and the zero-result cases are still a real test that the filter excludes things (matching items exist at $30 and above).

**Targets:** I missed one criterion, so my targets weren't all too low. The one I'd tighten is criterion 3 (see above); criterion 1's target of 4 of 5 is generous for a set of queries I knew would match.

---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path** (`python app.py ask 'vintage graphic tee under $30, size M' --trace`)

```
[1] parse query
      in:  vintage graphic tee under $30, size M
      out: {'description': 'vintage graphic tee', 'size': 'M', 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': 'M', 'max_price': 30.0}
      out: 8 items: Y2K Baby Tee — Butterfly Print, Mesh Long-Sleeve Top — Black, 90s Silk Slip Dress — Floral, Midi Length … +5 more
[3] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print, 10 wardrobe items
      out: **Outfit 1 (Casual Y2K):** Pair the Y2K butterfly baby tee with your baggy straight-leg dark wash jeans, layer…
[4] create_fit_card
      in:  outfit text + Y2K Baby Tee — Butterfly Print
      out: Found this absolute gem of a butterfly tee while digging through the racks this weekend. Giving major 2000s ma…
```

**Empty search** (stops at step 2 — shorter, as it should be)

```
[1] parse query
      in:  purple tuxedo with sequins under $5, size XXS
      out: {'description': 'purple tuxedo with sequins', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'purple tuxedo with sequins', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping
```

**On the MCP move:** `search_listings` now runs on an MCP server (`mcp_server.py`) and `run_agent()` calls it with `mcp_client.call_tool`; step 2 of the trace is labelled "via MCP". Nothing behaved differently: the MCP result equals the direct call's (6 results for "graphic tee", max_price 30, and `[]` for a no-match query).

**Failure modes triggered**

| Failure | How I triggered it | What the agent said |
|---|---|---|
| Empty search | `python app.py ask 'purple tuxedo with sequins under $5, size XXS'` | "No listings matched "purple tuxedo with sequins" with the $5 price ceiling and the size filter (XXS). Try raising the price, loosening the size, or changing the keywords." Stopped without calling the model. |
| Empty wardrobe | `python app.py ask 'vintage graphic tee under $30' --empty-wardrobe` | No crash, but it was silent about why the advice was generic. Now prints: "Your wardrobe is empty, so these are general styling ideas. Add some pieces you own to get outfits built around them." followed by the advice and fit card. |
| Model unavailable | Ran with `GEMINI_API_KEY=bad` set in the environment (`.env` untouched) and a new query | **Before:** a bare `ModelUnavailable: The model rejected your API key…` line. **After (handler in `run_agent`):** "I found "Knit Cardigan — Chunky Brown" ($35 on depop), but the styling service isn't responding right now, so I couldn't write the outfit or fit card. Please try again in a few minutes. If it keeps happening, the app's access key may need renewing by whoever runs it." The technical error stays in the trace. |

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
