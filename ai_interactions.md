# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

### Challenge 1: Add advanced song features

**What task did you give the agent?**

Add 5 or more new song attributes to `data/songs.csv`, and update the scoring in `src/recommender.py` so the new attributes count. Keep the existing profiles working.

**Prompts used:**

"Introduce 5 or more complex attributes to your dataset that are not currently present in the baseline data, such as Song Popularity (0-100), Release Decade, or Detailed Mood Tags (e.g., 'nostalgic,' 'aggressive,' 'euphoric'). Update both `data/songs.csv` and the scoring logic in `src/recommender.py` so scoring accounts for the new attributes. In `ai_interactions.md`, document the agentic workflow: the example prompt(s) you used, a summary of the changes the AI generated, and your manual verification notes."

**What did the agent generate or change?**

- `data/songs.csv`: added six columns to all 42 songs: `popularity` (0-100), `release_decade`, `mood_tags` (three tags per song, separated by `|`), `language`, `explicit` and `instrumental`. The original ten columns were not touched.
- `src/recommender.py`:
  - `Song` has six new fields, all with defaults, so the existing tests still work.
  - `load_songs` converts the new columns: ints, bools and the tag list.
  - `score_song` has six new scoring rules (below). Each one only runs if the user profile asks for that feature.
  - New `max_score(user_prefs)` works out the best possible score for the features a profile asked for.
- `src/main.py`: five new profiles (`ADVANCED_PROFILES`) and the printed "/ max" now comes from `max_score`.

| New feature | How it scores | Max points |
|---|---|---|
| `tags` (list of wanted mood tags) | share of wanted tags the song has | 1.0 |
| `decade` | full points for the same decade, loses one third per decade apart | 0.5 |
| `popularity` (0-100) | closeness to the target | 0.5 |
| `language` | exact match | 0.5 |
| `instrumental` (True/False) | match | 0.5 |
| `explicit` (True/False) | match | 0.5 |

**What did you verify or fix manually?**

- **Old behavior unchanged.** I saved the output of the nine earlier profiles before the change and diffed it afterward. All songs, scores and rankings are identical. The only difference is the Empty Profile: it now prints `/ 0.00` instead of `/ 4.50`. That is correct under the new rule, since an empty profile asks for no features.
- **Data checks.** 42 rows, 16 columns, no blank cells. Popularity runs 30–90. Decades run 1960–2020. Every song has exactly 3 tags (48 distinct tags). The original ten columns match the old file exactly.
- **Hand-checked one score.** *Fuego Nights* for "Mainstream Latin Party" should be 2.0 (genre) + 1.0 (mood) + 1.5 (energy, exact) + 1.0 (both tags) + 0.5 (decade) + 0.5 (popularity, exact) + 0.5 (language) = 7.0. The program printed 7.00 / 7.00.
- **Tests.** `pytest` passes (2 passed).
- **Important caveat.** The new values (popularity, decade, tags, language, explicit, instrumental) were written by the AI. They are made up to be plausible. They are not real chart data and I did not look them up. The songs are fictional, so they could not be looked up anyway.
- **A weakness I found by reading the results.** The "Clean Gym Playlist (no explicit)" profile still ranks *Block Party* first, and it is explicit. Genre, mood and tag points (about 4.5) easily beat the 0.5 "clean" bonus. So `explicit` acts as a nudge, not a filter. If a user really wants no explicit songs, it should be a hard filter. I did not change this; it is listed under future work in the model card.
- **A smaller oddity.** In "Retro Jazz Purist", *Study Hall Static* is the #5 result only because it is instrumental and has a close energy. It is not jazz. The scorer rewards weak matches when the list runs out of real ones.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
