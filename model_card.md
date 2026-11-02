# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Think of the recommender as a judge at a talent show. You tell the judge three things about your taste: the genre you like, the mood you want, and how energetic you want the music to feel. The judge then listens to every song in the catalog, awards points, and hands you the songs with the most points.

**What the judge looks at**

- **Genre:** does the song's genre match the one you asked for? If yes, it gets **2 points**. This is the biggest prize because genre is a broad, stable preference: someone who likes lofi rarely wants metal, whatever their mood.
- **Mood:** does the song's mood match the one you asked for? If yes, it gets **1 point**. Mood matters, but moods overlap ("chill" and "relaxed" are close), so it counts for less than genre.
- **Energy:** how close is the song's energy to the level you want? This is not a yes-or-no question. A perfect match earns the full **1.5 points**, and the further away the song is, the fewer points it gets. A very calm song earns almost nothing for someone who wants a high-energy workout track.

A song can earn at most 4.5 points (2 + 1 + 1.5).

**Turning points into recommendations**

The judge scores every song one at a time, then lines them up from highest to lowest score and shows the top few (five by default). Each song also comes with a short list of reasons, such as "genre match: lofi (+2.0)", so you can see exactly why it was picked instead of just trusting a number.

**A worked example**

Say you ask for lofi, chill, and an energy of 0.40. *Midnight Coding* is a chill lofi song with an energy of 0.42. It gets 2 points for genre, 1 point for mood, and almost the full energy score (1.47) because 0.42 is so close to 0.40. Its total is 4.47, which puts it at the top.

**What the judge does not look at**

The song's tempo, how upbeat or sad it sounds (valence), how danceable it is, and how acoustic it is are all in the data but are not scored yet. The judge also knows nothing about lyrics, artists, or what you have listened to before. It only compares your stated taste to each song's labels.

**Changes from the starter logic**

The starter had no scoring rules, so I wrote the point system above, with genre worth the most and energy scored by closeness rather than "higher is better". I also made the program explain each score, and I grew the song list from 20 to 42 songs so that most genres have more than one song to choose from.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
