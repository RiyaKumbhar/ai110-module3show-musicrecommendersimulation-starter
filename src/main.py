"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, max_score, recommend_songs


PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.95},
}


# Edge cases meant to trick the scorer or expose unexpected behavior
ADVERSARIAL_PROFILES = {
    "Conflicting: High-Energy Sad": {"genre": "pop", "mood": "sad", "energy": 0.9},
    "Conflicting: Peaceful Metal": {"genre": "metal", "mood": "peaceful", "energy": 0.1},
    "Unknown Genre and Mood": {"genre": "k-pop", "mood": "hyperpop", "energy": 0.5},
    "Case Mismatch": {"genre": "Pop", "mood": "Happy", "energy": 0.8},
    "Out-of-Range Energy": {"genre": "lofi", "mood": "chill", "energy": 2.0},
    "Empty Profile": {},
}


# Profiles that use the advanced song features (tags, decade, popularity, ...)
ADVANCED_PROFILES = {
    "Nostalgic Folk (tags + decade)": {
        "genre": "folk", "mood": "nostalgic", "energy": 0.35,
        "tags": ["nostalgic", "tender", "rustic"], "decade": 2000,
    },
    "Mainstream Latin Party": {
        "genre": "latin", "mood": "energetic", "energy": 0.85,
        "tags": ["party", "euphoric"], "decade": 2020, "popularity": 90, "language": "es",
    },
    "Instrumental Study Session": {
        "genre": "lofi", "mood": "focused", "energy": 0.4,
        "tags": ["study", "cozy"], "popularity": 40, "instrumental": True,
    },
    "Retro Jazz Purist": {
        "genre": "jazz", "mood": "romantic", "energy": 0.45,
        "tags": ["smooth", "warm"], "decade": 1960, "instrumental": True,
    },
    "Clean Gym Playlist (no explicit)": {
        "genre": "hip-hop", "mood": "energetic", "energy": 0.9,
        "tags": ["pumped", "party"], "popularity": 80, "explicit": False,
    },
}


def main() -> None:
    songs = load_songs("data/songs.csv")

    width = 60
    for name, user_prefs in {**PROFILES, **ADVERSARIAL_PROFILES, **ADVANCED_PROFILES}.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print()
        print("=" * width)
        print(f"{name}: {user_prefs}")
        print("=" * width)

        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"\n{rank}. {song['title']} - {song['artist']}")
            print(f"   Score: {score:.2f} / {max_score(user_prefs):.2f}")
            print("   Why:")
            for reason in explanation.split("; "):
                print(f"     - {reason}")

    print("\n" + "=" * width)


if __name__ == "__main__":
    main()
