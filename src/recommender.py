import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import asdict, dataclass

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

    Uses the same scoring rules as recommend_songs(). likes_acoustic is kept on
    UserProfile but is not scored (acousticness is not part of the scoring rules).
    """
    def __init__(self, songs: List[Song], strategy: "RankingStrategy" = None):
        self.songs = songs
        self.strategy = strategy or GENRE_FIRST

    @staticmethod
    def _prefs(user: UserProfile) -> Dict:
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the k best-scoring songs for this user, best first."""
        prefs = self._prefs(user)
        ranked = sorted(
            self.songs,
            key=lambda song: score_song(prefs, asdict(song), self.strategy)[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Plain-language reasons for a song's score, e.g. 'genre match: pop (+2.0); ...'."""
        _, reasons = score_song(self._prefs(user), asdict(song), self.strategy)
        return "; ".join(reasons) or "no genre, mood or energy preferences matched"

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

@dataclass(frozen=True)
class RankingStrategy:
    """
    One way of ranking songs, expressed as a set of weights (Strategy pattern).

    score_song() and recommend_songs() take a strategy as an argument, so a new
    ranking mode is just a new RankingStrategy entry in STRATEGIES. The scoring
    code never changes. The advanced weights only count when the user profile
    asks for that feature.
    """
    name: str
    genre: float
    mood: float
    energy: float
    tags: float = 1.0          # share of the user's wanted mood_tags the song has
    decade: float = 0.5        # same decade = full, loses a third per decade apart
    popularity: float = 0.5    # closeness to target popularity (0-100)
    language: float = 0.5      # language code match
    instrumental: float = 0.5  # instrumental / vocal match
    explicit: float = 0.5      # explicit / clean match

    def weights(self) -> Dict[str, float]:
        """Profile key -> weight, used to work out the best possible score."""
        return {
            "genre": self.genre,
            "mood": self.mood,
            "energy": self.energy,
            "tags": self.tags,
            "decade": self.decade,
            "popularity": self.popularity,
            "language": self.language,
            "instrumental": self.instrumental,
            "explicit": self.explicit,
        }

# Ranking modes. Core max score is genre + mood + energy.
GENRE_FIRST = RankingStrategy("Genre-First", genre=2.0, mood=1.0, energy=1.5)       # 4.5 (original recipe)
MOOD_FIRST = RankingStrategy("Mood-First", genre=1.0, mood=2.5, energy=1.5)         # 5.0
ENERGY_FOCUSED = RankingStrategy("Energy-Focused", genre=0.5, mood=0.5, energy=3.0)  # 4.0

STRATEGIES: Dict[str, RankingStrategy] = {
    "genre-first": GENRE_FIRST,
    "mood-first": MOOD_FIRST,
    "energy-focused": ENERGY_FOCUSED,
}

def max_score(user_prefs: Dict, strategy: RankingStrategy = GENRE_FIRST) -> float:
    """Best score a song could earn for this profile (only requested features count)."""
    return sum(w for key, w in strategy.weights().items() if key in user_prefs)

def score_song(
    user_prefs: Dict, song: Dict, strategy: RankingStrategy = GENRE_FIRST
) -> Tuple[float, List[str]]:
    """Return a song's score and the reasons behind it, using the given strategy's weights.

    Core: genre, mood, energy closeness. Advanced, only if the profile asks:
    mood tags, decade, popularity, language, instrumental, explicit.
    """
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs.get("genre"):
        score += strategy.genre
        reasons.append(f"genre match: {song['genre']} (+{strategy.genre:.1f})")

    if song["mood"] == user_prefs.get("mood"):
        score += strategy.mood
        reasons.append(f"mood match: {song['mood']} (+{strategy.mood:.1f})")

    if "energy" in user_prefs:
        gap = abs(song["energy"] - user_prefs["energy"])
        points = strategy.energy * (1 - gap)
        score += points
        reasons.append(
            f"energy {song['energy']:.2f} is {gap:.2f} from target "
            f"{user_prefs['energy']:.2f} (+{points:.2f})"
        )

    wanted_tags = user_prefs.get("tags")
    if wanted_tags:
        hits = [t for t in wanted_tags if t in song.get("mood_tags", [])]
        points = strategy.tags * len(hits) / len(wanted_tags)
        score += points
        if hits:
            reasons.append(f"mood tags match: {', '.join(hits)} (+{points:.2f})")

    if "decade" in user_prefs:
        decades_apart = abs(song["release_decade"] - user_prefs["decade"]) / 10
        points = strategy.decade * max(0.0, 1 - decades_apart / 3)
        score += points
        if points > 0:
            reasons.append(f"{song['release_decade']}s release, target {user_prefs['decade']}s (+{points:.2f})")

    if "popularity" in user_prefs:
        gap = abs(song["popularity"] - user_prefs["popularity"])
        points = strategy.popularity * (1 - gap / 100)
        score += points
        reasons.append(
            f"popularity {song['popularity']} is {gap} from target "
            f"{user_prefs['popularity']} (+{points:.2f})"
        )

    if "language" in user_prefs and song["language"] == user_prefs["language"]:
        score += strategy.language
        reasons.append(f"language match: {song['language']} (+{strategy.language:.1f})")

    if "instrumental" in user_prefs and song["instrumental"] == user_prefs["instrumental"]:
        score += strategy.instrumental
        kind = "instrumental" if song["instrumental"] else "has vocals"
        reasons.append(f"{kind} as requested (+{strategy.instrumental:.1f})")

    if "explicit" in user_prefs and song["explicit"] == user_prefs["explicit"]:
        score += strategy.explicit
        kind = "explicit" if song["explicit"] else "clean"
        reasons.append(f"{kind} as requested (+{strategy.explicit:.1f})")

    return score, reasons

# Default diversity penalties (points taken off per song already picked by the same artist / genre)
ARTIST_PENALTY = 1.0
GENRE_PENALTY = 0.5

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    strategy: RankingStrategy = GENRE_FIRST,
    artist_penalty: float = 0.0,
    genre_penalty: float = 0.0,
) -> List[Tuple[Dict, float, str]]:
    """Score every song with the strategy and return the top k as (song, score, explanation), best first.

    Diversity penalty (off by default): when artist_penalty or genre_penalty is above 0,
    songs are picked one at a time. Before each pick, a song loses artist_penalty points
    for every song by the same artist already picked, and genre_penalty points for every
    song of the same genre already picked. The score returned includes the penalty.
    """
    scored = [(song, *score_song(user_prefs, song, strategy)) for song in songs]

    if artist_penalty <= 0 and genre_penalty <= 0:
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)[:k]
        return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked]

    picked: List[Tuple[Dict, float, str]] = []
    remaining = scored
    while remaining and len(picked) < k:
        best = None
        for song, score, reasons in remaining:
            same_artist = sum(1 for p, _, _ in picked if p["artist"] == song["artist"])
            same_genre = sum(1 for p, _, _ in picked if p["genre"] == song["genre"])
            penalty = artist_penalty * same_artist + genre_penalty * same_genre
            if best is None or score - penalty > best[1]:
                best = (song, score - penalty, reasons, same_artist, same_genre)
        song, adjusted, reasons, same_artist, same_genre = best
        notes = list(reasons)
        if same_artist and artist_penalty > 0:
            notes.append(
                f"diversity penalty: {song['artist']} already in list (-{artist_penalty * same_artist:.2f})"
            )
        if same_genre and genre_penalty > 0:
            notes.append(
                f"diversity penalty: {song['genre']} already in list (-{genre_penalty * same_genre:.2f})"
            )
        picked.append((song, adjusted, "; ".join(notes)))
        remaining = [r for r in remaining if r[0] is not song]
    return picked
