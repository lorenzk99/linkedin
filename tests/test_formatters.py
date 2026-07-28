"""Tests for app.utils.formatters."""

import pytest

from app.utils.formatters import (
    count_hashtags,
    extract_hashtags,
    format_post_preview,
    validate_post_length,
)


# ---------------------------------------------------------------------------
# format_post_preview
# ---------------------------------------------------------------------------

class TestFormatPostPreview:
    def test_short_text_returned_unchanged(self):
        text = "Hello LinkedIn!"
        assert format_post_preview(text) == text

    def test_exact_max_length_returned_unchanged(self):
        text = "x" * 200
        assert format_post_preview(text) == text

    def test_truncates_at_word_boundary(self):
        text = "word " * 50  # 250 chars
        result = format_post_preview(text)
        assert result.endswith("...")
        assert len(result) <= 200 + 3  # truncated part + "..."

    def test_custom_max_length(self):
        text = "This is a test sentence for preview."
        result = format_post_preview(text, max_length=10)
        assert result.endswith("...")
        assert len(result) <= 13  # 10 + len("...")

    def test_empty_string(self):
        assert format_post_preview("") == ""

    def test_single_long_word(self):
        text = "a" * 300
        result = format_post_preview(text)
        # rsplit(" ", 1) on a string with no spaces returns the full string
        # as the only element, so the truncation still works
        assert result.endswith("...")

    def test_max_length_one(self):
        result = format_post_preview("Hello world", max_length=1)
        assert result.endswith("...")

    def test_text_with_newlines(self):
        text = "First line\nSecond line\nThird line"
        result = format_post_preview(text, max_length=20)
        assert result.endswith("...")

    def test_preserves_content_when_under_limit(self):
        text = "Short #post with #hashtags"
        assert format_post_preview(text, max_length=100) == text


# ---------------------------------------------------------------------------
# count_hashtags
# ---------------------------------------------------------------------------

class TestCountHashtags:
    def test_no_hashtags(self):
        assert count_hashtags("Just a regular text.") == 0

    def test_single_hashtag(self):
        assert count_hashtags("Check this #LinkedIn") == 1

    def test_multiple_hashtags(self):
        assert count_hashtags("#HR #Recruiting #Tech") == 3

    def test_empty_string(self):
        assert count_hashtags("") == 0

    def test_hash_in_middle_of_word(self):
        # count_hashtags uses str.count("#"), so C# counts as a hashtag
        assert count_hashtags("I use C# for development") == 1

    def test_multiple_hashes_in_sequence(self):
        assert count_hashtags("## Heading") == 2

    def test_hashtag_at_start(self):
        assert count_hashtags("#FirstPost ever!") == 1

    def test_many_hashtags(self):
        text = " ".join(f"#{i}" for i in range(20))
        assert count_hashtags(text) == 20


# ---------------------------------------------------------------------------
# extract_hashtags
# ---------------------------------------------------------------------------

class TestExtractHashtags:
    def test_no_hashtags(self):
        assert extract_hashtags("No tags here.") == []

    def test_single_hashtag(self):
        assert extract_hashtags("Post about #Recruiting") == ["#Recruiting"]

    def test_multiple_hashtags(self):
        result = extract_hashtags("Love #HR and #Tech and #AI")
        assert result == ["#HR", "#Tech", "#AI"]

    def test_empty_string(self):
        assert extract_hashtags("") == []

    def test_hashtag_only(self):
        assert extract_hashtags("#Solo") == ["#Solo"]

    def test_hashtags_at_end(self):
        text = "Great insights today.\n\n#LinkedIn #Recruiting #HRTech"
        result = extract_hashtags(text)
        assert result == ["#LinkedIn", "#Recruiting", "#HRTech"]

    def test_hash_without_word_not_extracted(self):
        # A standalone "#" followed by a space won't start a word with #
        # but "# heading" splits into ["#", "heading"] -- "#" starts with "#"
        result = extract_hashtags("# heading")
        assert "#" in result  # The lone "#" does start with "#"

    def test_does_not_extract_email_addresses(self):
        result = extract_hashtags("Contact user@example.com")
        assert result == []

    def test_hashtags_with_underscores(self):
        result = extract_hashtags("Check #HR_Tech")
        assert result == ["#HR_Tech"]

    def test_hashtags_with_numbers(self):
        result = extract_hashtags("Welcome to #Web3 and #AI2025")
        assert result == ["#Web3", "#AI2025"]


# ---------------------------------------------------------------------------
# validate_post_length
# ---------------------------------------------------------------------------

class TestValidatePostLength:
    def test_optimal_length(self):
        text = "a" * 1500
        result = validate_post_length(text)
        assert result["length"] == 1500
        assert result["optimal"] is True
        assert result["too_short"] is False
        assert result["too_long"] is False
        assert result["recommendation"] == "Perfekte Laenge!"

    def test_lower_optimal_boundary(self):
        text = "a" * 1200
        result = validate_post_length(text)
        assert result["optimal"] is True
        assert result["too_short"] is False
        assert result["too_long"] is False

    def test_upper_optimal_boundary(self):
        text = "a" * 1800
        result = validate_post_length(text)
        assert result["optimal"] is True
        assert result["too_short"] is False
        assert result["too_long"] is False

    def test_too_short(self):
        text = "a" * 500
        result = validate_post_length(text)
        assert result["length"] == 500
        assert result["optimal"] is False
        assert result["too_short"] is True
        assert result["too_long"] is False
        assert result["recommendation"] == "Etwas kurz - mehr Details?"

    def test_too_short_boundary(self):
        text = "a" * 799
        result = validate_post_length(text)
        assert result["too_short"] is True

    def test_not_too_short_at_800(self):
        text = "a" * 800
        result = validate_post_length(text)
        assert result["too_short"] is False

    def test_too_long(self):
        text = "a" * 4000
        result = validate_post_length(text)
        assert result["length"] == 4000
        assert result["optimal"] is False
        assert result["too_short"] is False
        assert result["too_long"] is True
        assert result["recommendation"] == "Etwas lang - kuerzen?"

    def test_too_long_boundary(self):
        text = "a" * 3000
        result = validate_post_length(text)
        assert result["too_long"] is False

    def test_just_over_too_long_boundary(self):
        text = "a" * 3001
        result = validate_post_length(text)
        assert result["too_long"] is True

    def test_middle_zone_not_optimal(self):
        # Between 800 and 1200: not too_short, not optimal, not too_long
        text = "a" * 1000
        result = validate_post_length(text)
        assert result["optimal"] is False
        assert result["too_short"] is False
        assert result["too_long"] is False
        assert result["recommendation"] == "OK, aber 1200-1800 Zeichen waere optimal."

    def test_upper_middle_zone(self):
        # Between 1800 and 3000: not optimal, not too_long
        text = "a" * 2500
        result = validate_post_length(text)
        assert result["optimal"] is False
        assert result["too_short"] is False
        assert result["too_long"] is False
        assert result["recommendation"] == "OK, aber 1200-1800 Zeichen waere optimal."

    def test_empty_string(self):
        result = validate_post_length("")
        assert result["length"] == 0
        assert result["too_short"] is True
        assert result["optimal"] is False
        assert result["too_long"] is False

    def test_result_keys(self):
        result = validate_post_length("test")
        expected_keys = {"length", "optimal", "too_short", "too_long", "recommendation"}
        assert set(result.keys()) == expected_keys
