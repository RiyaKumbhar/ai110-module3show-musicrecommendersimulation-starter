"""Plain-text table output for recommendations (standard library only)."""

import textwrap
from typing import Dict, List, Tuple

HEADERS = ("#", "Title", "Artist", "Genre", "Score", "Why (reasons)")
REASON_WIDTH = 52


def _wrap(text: str, width: int) -> List[str]:
    return textwrap.wrap(text, width) or [""]


def format_table(recommendations: List[Tuple[Dict, float, str]], max_score: float) -> str:
    """Return the top recommendations as an ASCII table, with every reason on its own line."""
    rows: List[List[List[str]]] = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reasons = [r for r in explanation.split("; ") if r] or ["(no preferences given)"]
        why: List[str] = []
        for reason in reasons:
            wrapped = textwrap.wrap(reason, REASON_WIDTH - 2) or [""]
            why.append("- " + wrapped[0])
            why.extend("  " + line for line in wrapped[1:])
        rows.append([
            [str(rank)],
            _wrap(song["title"], 22),
            _wrap(song["artist"], 16),
            _wrap(song["genre"], 10),
            [f"{score:.2f}/{max_score:.2f}"],
            why,
        ])

    widths = [
        max(len(HEADERS[i]), *(len(line) for row in rows for line in row[i]))
        for i in range(len(HEADERS))
    ]
    divider = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def line(cells: List[str]) -> str:
        return "| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths)) + " |"

    out = [divider, line(list(HEADERS)), divider]
    for row in rows:
        height = max(len(cell) for cell in row)
        for n in range(height):
            out.append(line([cell[n] if n < len(cell) else "" for cell in row]))
        out.append(divider)
    return "\n".join(out)
