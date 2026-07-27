def format_post_preview(content: str, max_length: int = 200) -> str:
    if len(content) <= max_length:
        return content
    return content[:max_length].rsplit(" ", 1)[0] + "..."


def count_hashtags(content: str) -> int:
    return content.count("#")


def extract_hashtags(content: str) -> list[str]:
    words = content.split()
    return [w for w in words if w.startswith("#")]


def validate_post_length(content: str) -> dict:
    length = len(content)
    return {
        "length": length,
        "optimal": 1200 <= length <= 1800,
        "too_short": length < 800,
        "too_long": length > 3000,
        "recommendation": (
            "Perfekte Laenge!" if 1200 <= length <= 1800
            else "Etwas kurz - mehr Details?" if length < 800
            else "Etwas lang - kuerzen?" if length > 3000
            else "OK, aber 1200-1800 Zeichen waere optimal."
        ),
    }
