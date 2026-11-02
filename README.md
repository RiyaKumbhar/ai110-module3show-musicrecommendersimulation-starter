# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms like Spotify and YouTube combine two ideas. **Collaborative filtering** learns from the behavior of millions of users (plays, skips, likes, playlist adds) to find songs that people with similar taste enjoyed. **Content-based filtering** compares the attributes of the songs themselves (tempo, energy, mood, genre) to what a user already likes. In practice they blend both, and they rely heavily on implicit signals like skips and replays rather than only explicit likes. My simulation has no user history, so it is a purely **content-based** recommender. It compares each song's attributes to a stated taste profile, rewards categorical matches (genre, mood), and rewards *closeness* on energy rather than simply "higher" or "lower".

### Data flow

```
INPUT                     PROCESS (the loop)                          OUTPUT
user_prefs         load_songs("data/songs.csv") -> list of song dicts
 genre, mood,              |
 energy, k                 v                                      ranked list
      |            for song in songs:                             (top k, with
      +----------->   score_song(prefs, song) -> (score, reasons)   reasons)
                          |                                            ^
                          v                                            |
                   scored.append((song, score, reasons)) --> sort by score DESC, take [:k]
```

### Features used

**`Song` object** (from `data/songs.csv`)

- `id`, `title`, `artist` (identification only, not scored)
- `genre` (categorical, scored as match / no match)
- `mood` (categorical, scored as match / no match)
- `energy` (0-1, scored by closeness)
- `tempo_bpm`, `valence`, `danceability`, `acousticness` (loaded but **not scored** in the baseline; candidates for later experiments)

**`UserProfile` object**

- `favorite_genre`
- `favorite_mood`
- `target_energy`

**Example profile used for planning:** `genre = lofi`, `mood = chill`, `target_energy = 0.40`, `k = 3`.

### Algorithm Recipe

Each song is scored independently, then all songs are ranked.

```
score = 2.0 * genre_match                          # 1 if equal, else 0
      + 1.0 * mood_match                           # 1 if equal, else 0
      + 1.5 * (1 - |song.energy - target_energy|)  # continuous, 0 to 1.5
```

Maximum score: **4.5**.

| Component | Points | Reasoning |
|---|---|---|
| Genre match | +2.0 | Coarse, stable label. A lofi fan rarely wants metal regardless of mood, so it counts most. |
| Mood match | +1.0 | Useful but flexible and subjective. It boosts a song without gating it. |
| Energy closeness | up to +1.5 | The only continuous feature, so it separates songs inside the same genre or mood bucket. Capped below genre (2.0) so genre still dominates, but above mood (1.0) so a near-perfect energy fit beats a bare mood match. |

- **Scoring rule (one song):** `score_song(user_prefs, song)` returns `(score, reasons)`, where `reasons` lists what contributed (for example `"genre match"`, `"mood match"`, `"energy 0.05 from target"`). It has no I/O, so it can be tested with a single hand-made song.
- **Ranking rule (whole list):** score every song, sort from highest to lowest (stable sort, so ties keep CSV order), and return the top `k`.
- **Hand-calculated expectation for the example profile:**
  1. *Midnight Coding* (lofi, chill, 0.42): 2.0 + 1.0 + 1.47 = **4.47**
  2. *Library Rain* (lofi, chill, 0.35): 2.0 + 1.0 + 1.425 = **4.43**
  3. *Focus Flow* (lofi, focused, 0.40): 2.0 + 0.0 + 1.5 = **3.50**

### Planned experiments

1. **Baseline:** genre 2.0 / mood 1.0 / energy 1.5.
2. **Genre-light:** genre 1.0, to see whether results become more varied.
3. **Energy-heavy:** energy 3.0, to check whether energy swamps the labels.
4. **Conflicting profile:** `pop` + `sad` + energy 0.2, to see how the weights trade off.

### Expected biases and limitations

- **Genre over-prioritization.** A +2.0 genre bonus can outrank a song that matches mood and energy almost perfectly. For example, a `rock` fan asking for `chill` / low energy still gets *Storm Runner* (intense, 0.91) in the top three, while *Spacewalk Thoughts* (ambient, chill, 0.28) scores lower. The extra rock song *Porch Light Sessions* (rock, chill, 0.41) is a better fit and shows the weights can work as intended.
- **Small catalog amplifies it.** The catalog has 42 songs, but most genres still have only two (lofi has five, pop four, and rock, jazz and hip-hop three each). The genre bonus therefore fills the top one or two slots, and every later slot comes from mood and energy alone.
- **Exact-string mood matching.** `chill`, `relaxed`, `peaceful` and `focused` are close in meaning but get no partial credit, so good matches can be missed.
- **Unused features.** Valence, acousticness, danceability and tempo are ignored, so two songs with the same energy but very different feel (for example *Gym Hero* vs. *Fuego Nights*) can look identical to the scorer.
- **Single-point taste.** One genre, one mood and one energy target cannot represent users with varied taste, and there is no learning from behavior over time.
- **Popularity and cultural bias.** The catalog reflects what I chose to include, so genres and moods outside it can never be recommended.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

(.venv) (base) riyakumbhar@mac ai110-module3show-musicrecommendersimulation-starter % python3 src/main.py
Loaded songs: 42

============================================================
Top 5 for: genre=pop, mood=happy, energy=0.8
============================================================

1. Sunrise City - Neon Echo
   Score: 4.47 / 4.50
   Why:
     - genre match: pop (+2.0)
     - mood match: happy (+1.0)
     - energy 0.82 is 0.02 from target 0.80 (+1.47)

2. Candy Static - Neon Echo
   Score: 3.38 / 4.50
   Why:
     - genre match: pop (+2.0)
     - energy 0.88 is 0.08 from target 0.80 (+1.38)

3. Gym Hero - Max Pulse
   Score: 3.30 / 4.50
   Why:
     - genre match: pop (+2.0)
     - energy 0.93 is 0.13 from target 0.80 (+1.30)

4. Glass Hearts - Mira Lane
   Score: 2.87 / 4.50
   Why:
     - genre match: pop (+2.0)
     - energy 0.38 is 0.42 from target 0.80 (+0.87)

5. Verano Eterno - Luna Cortez
   Score: 2.47 / 4.50
   Why:
     - mood match: happy (+1.0)
     - energy 0.78 is 0.02 from target 0.80 (+1.47)

============================================================

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



