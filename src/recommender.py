import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Advanced features (defaults keep older Song(...) calls working)
    popularity: int = 50
    release_decade: int = 2020
    mood_tags: Tuple[str, ...] = ()
    language: str = "en"
    explicit: bool = False
    instrumental: bool = False

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv into a list of dicts, converting numeric columns to int/float.

    Advanced columns: popularity and release_decade become ints, explicit and
    instrumental become bools, and mood_tags ("a|b|c") becomes a list of tags.
    """
    int_fields = ("id", "popularity", "release_decade")
    float_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")
    bool_fields = ("explicit", "instrumental")

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            for field in bool_fields:
                row[field] = row[field] == "1"
            row["mood_tags"] = [t for t in row["mood_tags"].split("|") if t]
            songs.append(row)

    print(f"Loaded songs: {len(songs)}")
    return songs

# Algorithm Recipe weights (max score = 2.0 + 1.0 + 1.5 = 4.5)
# Weight-shift experiment (genre 1.0, energy 3.0) is documented in the README.
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.5
MAX_SCORE = GENRE_WEIGHT + MOOD_WEIGHT + ENERGY_WEIGHT  # 4.5 (core features only)

# Advanced feature weights. Each only counts when the user profile asks for it.
TAGS_WEIGHT = 1.0        # share of the user's wanted mood_tags the song has
DECADE_WEIGHT = 0.5      # same decade = full, loses a third per decade apart
POPULARITY_WEIGHT = 0.5  # closeness to target popularity (0-100)
LANGUAGE_WEIGHT = 0.5    # language code match
INSTRUMENTAL_WEIGHT = 0.5  # instrumental / vocal match
EXPLICIT_WEIGHT = 0.5    # explicit / clean match

# Profile key -> weight, used to work out the best possible score for a profile
_FEATURE_WEIGHTS = {
    "genre": GENRE_WEIGHT,
    "mood": MOOD_WEIGHT,
    "energy": ENERGY_WEIGHT,
    "tags": TAGS_WEIGHT,
    "decade": DECADE_WEIGHT,
    "popularity": POPULARITY_WEIGHT,
    "language": LANGUAGE_WEIGHT,
    "instrumental": INSTRUMENTAL_WEIGHT,
    "explicit": EXPLICIT_WEIGHT,
}

def max_score(user_prefs: Dict) -> float:
    """Best score a song could earn for this profile (only requested features count)."""
    return sum(w for key, w in _FEATURE_WEIGHTS.items() if key in user_prefs)

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Return a song's score and the reasons behind it.

    Core: genre, mood, energy closeness (max 4.5). Advanced, only if the profile
    asks: mood tags, decade, popularity, language, instrumental, explicit.
    """
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs.get("genre"):
        score += GENRE_WEIGHT
        reasons.append(f"genre match: {song['genre']} (+{GENRE_WEIGHT:.1f})")

    if song["mood"] == user_prefs.get("mood"):
        score += MOOD_WEIGHT
        reasons.append(f"mood match: {song['mood']} (+{MOOD_WEIGHT:.1f})")

    if "energy" in user_prefs:
        gap = abs(song["energy"] - user_prefs["energy"])
        points = ENERGY_WEIGHT * (1 - gap)
        score += points
        reasons.append(
            f"energy {song['energy']:.2f} is {gap:.2f} from target "
            f"{user_prefs['energy']:.2f} (+{points:.2f})"
        )

    wanted_tags = user_prefs.get("tags")
    if wanted_tags:
        hits = [t for t in wanted_tags if t in song.get("mood_tags", [])]
        points = TAGS_WEIGHT * len(hits) / len(wanted_tags)
        score += points
        if hits:
            reasons.append(f"mood tags match: {', '.join(hits)} (+{points:.2f})")

    if "decade" in user_prefs:
        decades_apart = abs(song["release_decade"] - user_prefs["decade"]) / 10
        points = DECADE_WEIGHT * max(0.0, 1 - decades_apart / 3)
        score += points
        if points > 0:
            reasons.append(f"{song['release_decade']}s release, target {user_prefs['decade']}s (+{points:.2f})")

    if "popularity" in user_prefs:
        gap = abs(song["popularity"] - user_prefs["popularity"])
        points = POPULARITY_WEIGHT * (1 - gap / 100)
        score += points
        reasons.append(
            f"popularity {song['popularity']} is {gap} from target "
            f"{user_prefs['popularity']} (+{points:.2f})"
        )

    if "language" in user_prefs and song["language"] == user_prefs["language"]:
        score += LANGUAGE_WEIGHT
        reasons.append(f"language match: {song['language']} (+{LANGUAGE_WEIGHT:.1f})")

    if "instrumental" in user_prefs and song["instrumental"] == user_prefs["instrumental"]:
        score += INSTRUMENTAL_WEIGHT
        kind = "instrumental" if song["instrumental"] else "has vocals"
        reasons.append(f"{kind} as requested (+{INSTRUMENTAL_WEIGHT:.1f})")

    if "explicit" in user_prefs and song["explicit"] == user_prefs["explicit"]:
        score += EXPLICIT_WEIGHT
        kind = "explicit" if song["explicit"] else "clean"
        reasons.append(f"{kind} as requested (+{EXPLICIT_WEIGHT:.1f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top k as (song, score, explanation), best first."""
    scored = (
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    )
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
