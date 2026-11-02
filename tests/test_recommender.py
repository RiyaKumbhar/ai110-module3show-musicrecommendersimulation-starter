from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- Diversity penalty and table output ---

from src.recommender import load_songs, recommend_songs
from src.report import format_table


def _songs_same_artist():
    base = dict(tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5,
                popularity=50, release_decade=2020, mood_tags=[], language="en",
                explicit=False, instrumental=False)
    return [
        dict(id=1, title="A1", artist="Same", genre="lofi", mood="chill", energy=0.40, **base),
        dict(id=2, title="A2", artist="Same", genre="lofi", mood="chill", energy=0.41, **base),
        dict(id=3, title="B1", artist="Other", genre="jazz", mood="chill", energy=0.45, **base),
    ]


def test_diversity_penalty_demotes_repeat_artist():
    prefs = {"genre": "lofi", "mood": "chill", "energy": 0.4}
    songs = _songs_same_artist()

    plain = [s["title"] for s, _, _ in recommend_songs(prefs, songs, k=3)]
    diverse = recommend_songs(prefs, songs, k=3, artist_penalty=3.0)

    assert plain == ["A1", "A2", "B1"]
    assert [s["title"] for s, _, _ in diverse] == ["A1", "B1", "A2"]
    assert "diversity penalty" in diverse[2][2]


def test_diversity_off_by_default_and_first_pick_unchanged():
    prefs = {"genre": "lofi", "mood": "chill", "energy": 0.4}
    songs = _songs_same_artist()

    plain = recommend_songs(prefs, songs, k=3)
    diverse = recommend_songs(prefs, songs, k=3, artist_penalty=1.0, genre_penalty=0.5)

    assert plain[0][0]["title"] == diverse[0][0]["title"]
    assert plain[0][1] == diverse[0][1]
    assert all("diversity" not in why for _, _, why in plain)


def test_table_shows_every_reason():
    prefs = {"genre": "lofi", "mood": "chill", "energy": 0.4}
    recs = recommend_songs(prefs, _songs_same_artist(), k=2)
    table = format_table(recs, 4.5)

    assert "genre match: lofi" in table
    assert "mood match: chill" in table
    assert "energy 0.40" in table
    assert len({len(line) for line in table.splitlines()}) == 1  # rectangular
