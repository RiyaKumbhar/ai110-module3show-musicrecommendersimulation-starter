"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import argparse

from recommender import (
    ARTIST_PENALTY, GENRE_PENALTY, STRATEGIES, load_songs, max_score, recommend_songs,
)
from report import format_table


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


ALL_PROFILES = {**PROFILES, **ADVERSARIAL_PROFILES, **ADVANCED_PROFILES}


def show_ranking(songs, mode: str, diverse: bool = False, table: bool = False, width: int = 60) -> None:
    """Print the top 5 with reasons for every profile, ranked by one strategy."""
    strategy = STRATEGIES[mode]
    print(f"Mode: {strategy.name}")
    if diverse:
        print(f"Diversity penalty: artist -{ARTIST_PENALTY}, genre -{GENRE_PENALTY} per repeat")

    for name, user_prefs in ALL_PROFILES.items():
        recommendations = recommend_songs(
            user_prefs, songs, k=5, strategy=strategy, **_penalties(diverse)
        )

        print()
        print("=" * width)
        print(f"{name}: {user_prefs}")
        print("=" * width)

        if table:
            print(format_table(recommendations, max_score(user_prefs, strategy)))
            continue

        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"\n{rank}. {song['title']} - {song['artist']}")
            print(f"   Score: {score:.2f} / {max_score(user_prefs, strategy):.2f}")
            print("   Why:")
            for reason in explanation.split("; "):
                print(f"     - {reason}")

    print("\n" + "=" * width)


def _penalties(diverse: bool) -> dict:
    return {"artist_penalty": ARTIST_PENALTY, "genre_penalty": GENRE_PENALTY} if diverse else {}


def compare_modes(songs, diverse: bool = False, width: int = 60) -> None:
    """Print each profile's top 5 song titles under every mode, to see what a mode changes."""
    for name, user_prefs in ALL_PROFILES.items():
        print()
        print("=" * width)
        print(name)
        print("=" * width)
        for mode, strategy in STRATEGIES.items():
            titles = [s["title"] for s, _, _ in recommend_songs(user_prefs, songs, k=5, strategy=strategy, **_penalties(diverse))]
            print(f"{strategy.name:>15}: " + " | ".join(titles))
    print("\n" + "=" * width)


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument(
        "--mode", choices=sorted(STRATEGIES), default="genre-first",
        help="ranking strategy to use (default: genre-first)",
    )
    parser.add_argument(
        "--compare", action="store_true",
        help="show every profile's top 5 under all modes, side by side",
    )
    parser.add_argument(
        "--diverse", action="store_true",
        help="penalize songs whose artist or genre is already in the top results",
    )
    parser.add_argument(
        "--format", choices=("detailed", "table"), default="detailed",
        help="detailed lists (default) or one ASCII table per profile",
    )
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    if args.compare:
        compare_modes(songs, args.diverse)
    else:
        show_ranking(songs, args.mode, args.diverse, args.format == "table")


if __name__ == "__main__":
    main()
