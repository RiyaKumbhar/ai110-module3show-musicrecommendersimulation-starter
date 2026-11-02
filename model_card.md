# 🎧 Model Card: VibeFinder 1.0

## 1. Model Name

**VibeFinder 1.0**

A small, rule-based music recommender. It matches your vibe to songs.

---

## 2. Goal / Intended Use

**Goal.** VibeFinder suggests the top 5 songs from a small catalog. You tell it your favorite genre, the mood you want, and how energetic you want the music to feel. It scores every song and shows the best ones.

**What it assumes about you.**

- You can name one genre and one mood.
- You want one energy level, not a range.
- Your taste stays the same from song to song.

**Intended use.**

- Classroom exploration.
- Learning how scoring rules turn data into recommendations.
- Seeing how simple choices (like weights) change results.

**Not intended for.**

- Real music apps or real users.
- Judging anyone's taste.
- Replacing a real recommender. It has no listening history, no lyrics and no artist info.
- Catalogs far bigger than 42 songs. The rules were not tested at that scale.

---

## 3. How the Model Works

Think of a judge at a talent show. You tell the judge your genre, mood and energy. The judge listens to every song and gives points. You get the songs with the most points.

**What the judge looks at (original weights)**

- **Genre:** a match gives **2 points**. It is the biggest prize.
- **Mood:** a match gives **1 point**.
- **Energy:** a perfect match gives **1.5 points**. The further the song is from your level, the fewer points it gets.

The best possible score is 4.5.

**Turning points into a list**

The judge scores every song. Then it sorts them from highest to lowest and shows the top 5. Each song comes with reasons, like "genre match: lofi (+2.0)". You can see why it was picked.

**A quick example**

You ask for lofi, chill, energy 0.40. *Midnight Coding* is chill lofi with energy 0.42. It gets 2 for genre, 1 for mood and 1.47 for energy. The total is 4.47. It ranks first.

**What it ignores**

Tempo, valence (how upbeat), danceability and acousticness are in the data. They are not scored. The model also knows nothing about lyrics or artists.

**Weights in the code right now**

I ran one experiment with genre = 1.0 and energy = 3.0. The code in `recommender.py` is still set to those test values. Everything in this card uses the original weights unless it says otherwise.

---

## 4. Data Used

- **Size:** 42 songs. The starter had 20. I added 22.
- **Columns:** title, artist, genre, mood, energy, tempo, valence, danceability, acousticness.
- **Advanced columns (added later):** popularity (0–100), release decade, three mood tags per song, language, explicit and instrumental. These values are made up and plausible, not real data.
- **Used in scoring:** genre, mood and energy always. The advanced columns only count when a user profile asks for them (mood tags, decade, popularity, language, instrumental, explicit).
- **Genres:** 17 (like lofi, pop, rock, jazz, metal, blues and folk).
- **Moods:** 16 (like happy, chill, intense, sad and peaceful).
- **Songs per genre:** between 2 and 5. Lofi has 5. Pop has 4. Many genres have only 2.
- **Energy range:** from 0.18 to 0.97. Few songs sit between 0.6 and 0.8.

**Limits**

- The catalog is tiny.
- Each song has exactly one genre and one mood label.
- It has no lyrics, no language and no listening history.
- Western genres dominate. Many styles of music are missing.

---

## 5. Strengths

- **Clear taste, clear answers.** Chill Lofi and Deep Intense Rock got very different lists. This is what I wanted.
- **Easy to explain.** Every score has reasons attached. I can trace any result by hand.
- **Good when everything lines up.** The Lofi profile gave a perfect 4.50 to *Library Rain*. The top 5 all felt right.
- **Energy works.** Songs closest to the energy target score higher. Low-energy and high-energy users get different songs.
- **Mood changes the answer.** Switching pop from "happy" to "sad" put a sad pop ballad first.

---

## 6. Observed Behavior / Biases

**Main weakness: genre is a filter bubble.**

- A genre match is worth 2 points. That is more than energy can ever add.
- So the user's genre fills the top of the list, even when the songs fit badly.
- Example: for High-Energy Pop (energy 0.9), the slow ballad *Glass Hearts* (0.38) ranked 4th. It beat *Verano Eterno* (happy, 0.78). It only won because it is tagged pop.
- Small genres make it worse. Metal has two songs. A metal fan always sees both.
- The problem is genre rigidity, not pop dominance. Pop is only 4 of 42 songs.

**Other problems I found**

- Typos and caps break matching. `Pop` is not `pop`. The user then loses all genre points.
- Unknown genres (like `k-pop`) get an energy-only list. The system does not say so.
- Energy above 1.0 gives negative points and scrambles the order.
- An empty profile scores every song 0. It returns the first five rows of the file.
- Mixed tastes break it. "High-energy but sad" gets a slow ballad.

**Ranking modes.** The program has three modes: Genre-First, Mood-First and Energy-Focused (see the README). Mood-First fixes the Gym Hero problem for Happy Pop. But every mode has a blind spot, so the bubble just moves. Mood-First lets mood override energy, and Energy-Focused ignores genre.

**Does the weight shift fix it?**

Partly. I halved genre and doubled energy. Mixed profiles got more sensible. But rock fans lost their rock songs. No single weight setting works for everyone.

---

## 7. Evaluation Process

**Profiles I tested (9).**

- Three normal listeners: **High-Energy Pop**, **Chill Lofi**, **Deep Intense Rock**.
- Six tricky ones: **High-Energy Sad**, **Peaceful Metal**, **Unknown Genre and Mood** (k-pop), **Case Mismatch** (`Pop`, `Happy`), **Out-of-Range Energy** (2.0), **Empty Profile**.

**What I checked.** Does the top song feel right for this person? Can I explain every score? Full output is in the README.

### What surprised me: why "Gym Hero" keeps showing up for Happy Pop

Gym Hero is a loud workout song. It is not happy. Yet it ranks 3rd for "Happy Pop".

Here is why:

- Gym Hero is pop, so it gets 2 points.
- Its energy is very close, so it gets 1.46 points.
- It misses only the mood point, because it is "intense", not "happy".
- Total: 3.46.

*Verano Eterno* is happy, but it is not pop. It scores only 2.32.

So the system cares about "pop" more than "happy". A pop song that feels wrong beats a happy song that feels right. This is not a math bug. It is a weight choice I made.

### Comparing the profiles

**Happy Pop vs Chill Lofi.**
Pop gets loud, bright songs (energy 0.8–0.9). Lofi gets quiet, slow songs (0.35–0.42). This makes sense. Only the genre and energy target differ. The lists flipped to match. Lofi also scores a perfect 4.50. The catalog has five lofi songs, and one is chill at exactly the right energy.

**Happy Pop vs Deep Intense Rock.**
Both want loud songs. The difference is the genre label. Pop gets pop songs. Rock gets *Storm Runner* and *Highway Static*. The rock list gets weak at the bottom. *Porch Light Sessions* is quiet and chill, but ranks 3rd. It is the third rock song, so the label gives it 2 free points. Rock has only three songs. After that the list fills with intense songs from other genres.

**Chill Lofi vs Deep Intense Rock.**
They are opposites, and so are the results. Nothing overlaps. This is the cleanest sign that the energy rule works. 0.35 and 0.95 are far apart.

**Happy Pop vs High-Energy Sad.**
Same genre, same energy. Only the mood changed. The sad user gets *Glass Hearts* first. It is a slow sad pop ballad. It is the only song that is both pop and sad (+3). The mood word does change the answer, as it should. But it beats the energy request. The user asked for loud and got quiet.

**Deep Intense Rock vs Peaceful Metal.**
Both use a heavy genre. Peaceful Metal also wants calm. The system ranks calm songs first. Then two metal songs at energy 0.95 show up in the top four. They are there only because they say "metal". The points add up, but a human would be confused. No one asks for quiet and wants screaming metal.

**Chill Lofi vs Out-of-Range Energy.**
Both want chill lofi. The second sets energy to 2.0, which is impossible. The order flips. *Midnight Coding* (0.42) beats *Library Rain* (0.35). 0.42 is "closer" to 2.0. The energy points even go negative. Bad input gives a meaningless answer. The system should reject it.

**Unknown Genre, Case Mismatch and Empty Profile vs everything else.**
These three get no genre or mood match. The recommender stops understanding taste. It just picks the closest energy. `Pop` with a capital P looks the same to a human. The computer sees a different word. The Empty Profile scores 0 for every song. It returns the first five rows of the file. None of these are real recommendations.

### Experiment: change the weights

I halved genre and doubled energy. Then I compared the top 5s (details in the README). The Sad and Peaceful Metal profiles got more sensible. Deep Intense Rock lost its rock songs. The bad results come from the weights. No setting makes every listener happy.

---

## 8. Ideas for Improvement

1. **Clean and check the input.** Lowercase genre and mood. Keep energy between 0 and 1. Warn the user when a genre is unknown.
2. **Use more features.** Add tempo, valence and acousticness. Add a "likes acoustic" choice. Then "happy pop" can mean upbeat, not just a pop label.
3. **Make "explicit" a real filter.** Today `explicit: False` is only a +0.5 nudge. An explicit song can still rank first for a user who wants clean music. A hard filter would fix that.
4. **Make results more varied and fair.** Reduce genre weight, or let a song from a related genre earn partial points. Cap how many songs from one genre can appear. Add more songs, so small genres do not run out.

---

## 9. Personal Reflection

**Biggest learning moment.**
It was seeing *Gym Hero* rank 3rd for "Happy Pop". The code was correct. The weights were the problem. I had picked "genre = 2 points" without thinking about what it would do. A weight is really an opinion. Changing it changed who got good results. I also learned that trick profiles teach more than normal ones. The normal profiles all looked fine. The trick profiles showed every weak spot.

**How AI tools helped, and when I double-checked them.**
The AI helped me move fast. It wrote the scoring code, the test profiles and the first draft of the write-ups. It also ran the profiles and compared the before and after lists. But I had to check its work several times:

- A suggested example said "60% of the dataset is pop". I counted. Pop is only 4 of 42 songs. The real issue was genre rigidity, not pop dominance.
- One draft sentence said *Gym Hero* showed up in the Rock results. It did not. I checked the saved output and fixed it.
- After I changed the weights, the "4.50" max score was still hardcoded in `main.py`. The printed scores would have been wrong. I checked that scores stayed between 0 and the new max.
- I left the test weights in the code while the model card described the original ones. I had to notice that the code and the write-up no longer matched.

The rule I will keep: let the AI draft, then check every number against the real data and output.

**What surprised me.**
Three simple rules felt like a real recommender. The reasons ("genre match +2.0") made the list feel smart. The top result often felt right. Then I saw the same simple rules fail in odd ways: a quiet ballad for a "high-energy" user, and metal for a "peaceful" user. A recommendation feels trustworthy before it is. A clear explanation can hide a weak rule.

**What I would try next.**

- Clean and check the input: lowercase text, energy limited to 0–1, and a warning for unknown genres.
- Score more features: tempo, valence and acousticness.
- Let related genres earn partial points, so "indie pop" can count a little for a pop fan.
- Add variety, so one genre cannot fill the whole top 5.
- Test with more songs and a few real people. I would ask them whether the top 5 feels right.
