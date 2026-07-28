"""Utility to import existing LinkedIn posts for style analysis.

Supports three input formats:
  - CSV file (columns: date, text, likes, comments, hashtags)
  - Directory of individual .txt files
  - JSON file (array of objects with "text", "date", "engagement" fields)

Usage:
    python -m app.utils.linkedin_scraper data/sample_posts/
    python -m app.utils.linkedin_scraper posts.csv
    python -m app.utils.linkedin_scraper posts.json
"""

from __future__ import annotations

import asyncio
import csv
import json
import sys
from pathlib import Path

from app.ai.style_analyzer import StyleAnalyzer
from app.db.models import StyleProfile


def load_from_csv(path: Path) -> list[str]:
    """Load post texts from a CSV file.

    Expected columns: date, text, likes, comments, hashtags.
    The 'text' column is required; all others are optional.
    """
    posts: list[str] = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file {path} appears to be empty or has no header row.")
        lower_fields = [f.lower().strip() for f in reader.fieldnames]
        if "text" not in lower_fields:
            raise ValueError(
                f"CSV file {path} is missing the required 'text' column. "
                f"Found columns: {reader.fieldnames}"
            )
        text_key = reader.fieldnames[lower_fields.index("text")]
        for row in reader:
            text = (row.get(text_key) or "").strip()
            if text:
                posts.append(text)
    return posts


def load_from_txt_directory(path: Path) -> list[str]:
    """Load post texts from .txt files in a directory.

    Files are read in sorted order so the result is deterministic.
    """
    posts: list[str] = []
    txt_files = sorted(path.glob("*.txt"))
    if not txt_files:
        raise ValueError(f"No .txt files found in directory {path}.")
    for txt_file in txt_files:
        text = txt_file.read_text(encoding="utf-8").strip()
        if text:
            posts.append(text)
    return posts


def load_from_json(path: Path) -> list[str]:
    """Load post texts from a JSON file.

    Expected format: array of objects, each with at least a "text" field.
    Optional fields: "date", "engagement".
    """
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"JSON file {path} must contain a top-level array.")
    posts: list[str] = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            raise ValueError(f"Entry {i} in {path} is not a JSON object.")
        text = (entry.get("text") or "").strip()
        if text:
            posts.append(text)
    return posts


def detect_format(source_path: str) -> str:
    """Auto-detect whether *source_path* points to a CSV, JSON file, or txt directory.

    Returns one of ``"csv"``, ``"json"``, or ``"txt_directory"``.
    """
    path = Path(source_path)
    if path.is_dir():
        return "txt_directory"
    if not path.is_file():
        raise FileNotFoundError(f"Path does not exist: {source_path}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".json":
        return "json"
    raise ValueError(
        f"Cannot auto-detect format for '{path.name}'. "
        "Expected a .csv file, a .json file, or a directory of .txt files."
    )


def load_posts(source_path: str) -> list[str]:
    """Load posts from *source_path*, auto-detecting the format."""
    fmt = detect_format(source_path)
    path = Path(source_path)
    if fmt == "csv":
        return load_from_csv(path)
    if fmt == "json":
        return load_from_json(path)
    return load_from_txt_directory(path)


async def import_and_analyze(source_path: str) -> StyleProfile:
    """Import posts from *source_path* and run style analysis.

    1. Auto-detects the input format (csv / json / txt directory).
    2. Loads all post texts.
    3. Passes them to ``StyleAnalyzer.analyze_posts()``.
    4. Returns the resulting :class:`StyleProfile`.
    """
    posts = load_posts(source_path)
    if not posts:
        raise ValueError(f"No post texts found at {source_path}.")
    analyzer = StyleAnalyzer()
    return await analyzer.analyze_posts(posts)


def main() -> None:
    """CLI entry-point for standalone execution."""
    if len(sys.argv) < 2:
        print("Usage: python -m app.utils.linkedin_scraper <source_path>")
        print()
        print("  source_path  Path to a .csv, .json file or a directory of .txt files.")
        sys.exit(1)

    source_path = sys.argv[1]

    try:
        posts = load_posts(source_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error loading posts: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(posts)} post(s) from {source_path}.")
    for i, post in enumerate(posts, 1):
        preview = post[:80].replace("\n", " ")
        if len(post) > 80:
            preview += "..."
        print(f"  [{i}] {preview}")

    print()
    print("Running style analysis via Anthropic API...")
    try:
        profile = asyncio.run(import_and_analyze(source_path))
    except Exception as exc:
        print(f"Analysis failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print()
    print("=== Style Profile ===")
    print(f"  Name:        {profile.name}")
    print(f"  Summary:     {profile.summary}")
    print(f"  Tone:        {profile.tone}")
    print(f"  Avg length:  {profile.avg_length}")
    print(f"  Emoji usage: {profile.emoji_usage}")
    if profile.hook_patterns:
        print(f"  Hooks:       {profile.hook_patterns}")
    if profile.cta_patterns:
        print(f"  CTAs:        {profile.cta_patterns}")
    if profile.hashtag_strategy:
        print(f"  Hashtags:    {profile.hashtag_strategy}")


if __name__ == "__main__":
    main()
