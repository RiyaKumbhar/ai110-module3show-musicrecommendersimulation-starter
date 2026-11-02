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

A simple **Strategy pattern**. A `RankingStrategy` object holds the weights for one ranking mode. `score_song()` and `recommend_songs()` take a strategy as an argument. Three modes exist: **Genre-First** (genre 2.0, mood 1.0, energy 1.5, the original recipe), **Mood-First** (genre 1.0, mood 2.5, energy 1.5) and **Energy-Focused** (genre 0.5, mood 0.5, energy 3.0). You switch with `python3 src/main.py --mode mood-first`, or compare all three with `--compare`.

**Prompt used:**

"Build two or more different ranking strategies (e.g., 'Genre-First,' 'Mood-First,' or 'Energy-Focused') so a user can switch between modes in main.py. Attach recommender.py and brainstorm a design pattern (like a simple 'Strategy' pattern) that keeps your code modular."

**How did AI help you brainstorm or implement it?**

The AI read `recommender.py` and laid out four options before writing any code:

1. **An `if mode == ...` flag inside `score_song`.** Quickest, but every new mode adds more branches to one function. Rejected.
2. **One class per strategy** with a `score()` method (the textbook Strategy pattern). Flexible, but our modes differ only in their numbers. Three near-identical classes would be boilerplate. Rejected for now.
3. **A dict of scoring functions.** Light, but the weights would be buried inside each function and hard to compare.
4. **A frozen dataclass of weights plus a registry dict.** This is what I picked. Modes become data, so a new mode is one new line in `STRATEGIES`. The scoring code stays in one place, and a reader can see all weights side by side.

The AI wrote the first version of the dataclass, the registry and the `--mode` / `--compare` flags. I made the final choice of option 4 and the weight values.

**How does the pattern appear in your final code?**

- `RankingStrategy` and `STRATEGIES` in `src/recommender.py`. `score_song(user_prefs, song, strategy)` and `recommend_songs(..., strategy)` use whatever strategy they are given. The default is `GENRE_FIRST`, so older calls still work.
- `show_ranking()`, `compare_modes()` and the `--mode` / `--compare` flags in `src/main.py`.

**What did you verify or fix manually?**

- **Branch workflow.** I built this on `experiment/mood-first`, so `main` stayed untouched until it worked. I merged it back once it did.
- **Old behavior unchanged.** The default mode (`genre-first`) prints exactly the same output as before the refactor, except for a new "Mode:" line. I diffed the two runs.
- **Hand-checked one score.** Mood-First, *Sunrise City* for High-Energy Pop: 1.0 (genre) + 2.5 (mood) + 1.38 (energy) = 4.88 / 5.00. The program printed 4.88.
- **Bad input.** `--mode bogus` gives a clear error that lists the valid modes. `pytest` still passes (2 passed).
- **A limit of this pattern.** These strategies differ only in numbers. If I wanted a mode that works differently, such as a hard filter that removes explicit songs, the dataclass would not be enough. That would need a class or a function per strategy.
