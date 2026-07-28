"""Tests for app.ai.post_generator."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ai.post_generator import GeneratedPost, PostGenerator
from app.ai.prompts import CLUSTER_DETECTION_PROMPT, POST_GENERATION_PROMPT
from app.db.models import StyleProfile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_CLUSTERS = [
    "Stellenschaltung & Kanal-Strategie",
    "KI im Recruiting",
    "Skills-based Hiring",
    "Founder Einblicke",
]


def _make_api_response(text: str) -> MagicMock:
    """Build a mock Anthropic API response with the given text content."""
    content_block = MagicMock()
    content_block.text = text
    response = MagicMock()
    response.content = [content_block]
    return response


def _make_style_profile(**overrides) -> StyleProfile:
    """Build a minimal StyleProfile for testing."""
    defaults = dict(
        id=1,
        name="default",
        summary="Professionell, direkt, praxisnah.",
        tone="direkt",
        avg_length=1500,
        emoji_usage="minimal",
        hook_patterns=["Frage stellen"],
        cta_patterns=["Was meint ihr?"],
        hashtag_strategy={"avg_count": 3, "placement": "end"},
        sample_posts=["Post 1", "Post 2", "Post 3"],
    )
    defaults.update(overrides)
    return StyleProfile(**defaults)


# ---------------------------------------------------------------------------
# detect_cluster
# ---------------------------------------------------------------------------

class TestDetectCluster:
    @pytest.mark.asyncio
    @patch("app.ai.post_generator.StyleAnalyzer")
    @patch("app.ai.post_generator.anthropic.AsyncAnthropic")
    async def test_returns_valid_cluster(self, mock_anthropic_cls, mock_sa_cls):
        cluster_text = "KI im Recruiting"
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = _make_api_response(cluster_text)
        mock_anthropic_cls.return_value = mock_client

        generator = PostGenerator()
        generator.client = mock_client

        result = await generator.detect_cluster("Wie KI den Recruiting-Prozess veraendert")
        assert result == cluster_text
        assert result in VALID_CLUSTERS

    @pytest.mark.asyncio
    @patch("app.ai.post_generator.StyleAnalyzer")
    @patch("app.ai.post_generator.anthropic.AsyncAnthropic")
    async def test_strips_whitespace(self, mock_anthropic_cls, mock_sa_cls):
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = _make_api_response(
            "  Founder Einblicke  \n"
        )
        mock_anthropic_cls.return_value = mock_client

        generator = PostGenerator()
        generator.client = mock_client

        result = await generator.detect_cluster("Mein Weg als Gruender")
        assert result == "Founder Einblicke"

    @pytest.mark.asyncio
    @patch("app.ai.post_generator.StyleAnalyzer")
    @patch("app.ai.post_generator.anthropic.AsyncAnthropic")
    async def test_prompt_contains_idea(self, mock_anthropic_cls, mock_sa_cls):
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = _make_api_response("KI im Recruiting")
        mock_anthropic_cls.return_value = mock_client

        generator = PostGenerator()
        generator.client = mock_client

        idea = "Automatisierung im Bewerbungsprozess"
        await generator.detect_cluster(idea)

        call_args = mock_client.messages.create.call_args
        prompt_sent = call_args.kwargs["messages"][0]["content"]
        assert idea in prompt_sent

    @pytest.mark.asyncio
    @patch("app.ai.post_generator.StyleAnalyzer")
    @patch("app.ai.post_generator.anthropic.AsyncAnthropic")
    async def test_uses_cluster_detection_prompt(self, mock_anthropic_cls, mock_sa_cls):
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = _make_api_response("Skills-based Hiring")
        mock_anthropic_cls.return_value = mock_client

        generator = PostGenerator()
        generator.client = mock_client

        idea = "Warum Skills wichtiger als Abschluesse sind"
        await generator.detect_cluster(idea)

        call_args = mock_client.messages.create.call_args
        prompt_sent = call_args.kwargs["messages"][0]["content"]
        expected = CLUSTER_DETECTION_PROMPT.format(idea=idea)
        assert prompt_sent == expected


# ---------------------------------------------------------------------------
# generate
# ---------------------------------------------------------------------------

class TestGenerate:
    @pytest.mark.asyncio
    @patch("app.ai.post_generator.StyleAnalyzer")
    @patch("app.ai.post_generator.anthropic.AsyncAnthropic")
    async def test_returns_generated_post(self, mock_anthropic_cls, mock_sa_cls):
        post_text = "Starker Hook!\n\nDer Inhalt des Posts.\n\n#HR #Recruiting"
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = _make_api_response(post_text)
        mock_anthropic_cls.return_value = mock_client

        mock_analyzer = AsyncMock()
        mock_analyzer.get_profile.return_value = _make_style_profile()
        mock_sa_cls.return_value = mock_analyzer

        generator = PostGenerator()
        generator.client = mock_client
        generator.style_analyzer = mock_analyzer

        result = await generator.generate("KI im Recruiting", cluster="KI im Recruiting")

        assert isinstance(result, GeneratedPost)
        assert result.content == post_text
        assert result.cluster == "KI im Recruiting"
        assert result.char_count == len(post_text)

    @pytest.mark.asyncio
    @patch("app.ai.post_generator.StyleAnalyzer")
    @patch("app.ai.post_generator.anthropic.AsyncAnthropic")
    async def test_content_is_not_empty(self, mock_anthropic_cls, mock_sa_cls):
        post_text = "Ein LinkedIn Post ueber Recruiting."
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = _make_api_response(post_text)
        mock_anthropic_cls.return_value = mock_client

        mock_analyzer = AsyncMock()
        mock_analyzer.get_profile.return_value = _make_style_profile()
        mock_sa_cls.return_value = mock_analyzer

        generator = PostGenerator()
        generator.client = mock_client
        generator.style_analyzer = mock_analyzer

        result = await generator.generate("Recruiting Trends", cluster="KI im Recruiting")
        assert len(result.content) > 0

    @pytest.mark.asyncio
    @patch("app.ai.post_generator.StyleAnalyzer")
    @patch("app.ai.post_generator.anthropic.AsyncAnthropic")
    async def test_auto_detects_cluster_when_not_given(self, mock_anthropic_cls, mock_sa_cls):
        mock_client = AsyncMock()
        # First call: cluster detection; second call: generation
        mock_client.messages.create.side_effect = [
            _make_api_response("Founder Einblicke"),
            _make_api_response("Mein Weg als Gruender war steinig..."),
        ]
        mock_anthropic_cls.return_value = mock_client

        mock_analyzer = AsyncMock()
        mock_analyzer.get_profile.return_value = _make_style_profile()
        mock_sa_cls.return_value = mock_analyzer

        generator = PostGenerator()
        generator.client = mock_client
        generator.style_analyzer = mock_analyzer

        result = await generator.generate("Mein Weg als Gruender")
        assert result.cluster == "Founder Einblicke"
        assert mock_client.messages.create.call_count == 2

    @pytest.mark.asyncio
    @patch("app.ai.post_generator.StyleAnalyzer")
    @patch("app.ai.post_generator.anthropic.AsyncAnthropic")
    async def test_uses_default_style_when_no_profile(self, mock_anthropic_cls, mock_sa_cls):
        post_text = "Post ohne Profil."
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = _make_api_response(post_text)
        mock_anthropic_cls.return_value = mock_client

        mock_analyzer = AsyncMock()
        mock_analyzer.get_profile.return_value = None  # No profile
        mock_sa_cls.return_value = mock_analyzer

        generator = PostGenerator()
        generator.client = mock_client
        generator.style_analyzer = mock_analyzer

        result = await generator.generate("Test Idee", cluster="KI im Recruiting")

        call_args = mock_client.messages.create.call_args
        prompt_sent = call_args.kwargs["messages"][0]["content"]
        assert "Professionell, direkt, praxisnah" in prompt_sent
        assert "Keine Beispiele verfuegbar." in prompt_sent

    @pytest.mark.asyncio
    @patch("app.ai.post_generator.StyleAnalyzer")
    @patch("app.ai.post_generator.anthropic.AsyncAnthropic")
    async def test_char_count_matches_content(self, mock_anthropic_cls, mock_sa_cls):
        post_text = "x" * 1500
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = _make_api_response(post_text)
        mock_anthropic_cls.return_value = mock_client

        mock_analyzer = AsyncMock()
        mock_analyzer.get_profile.return_value = _make_style_profile()
        mock_sa_cls.return_value = mock_analyzer

        generator = PostGenerator()
        generator.client = mock_client
        generator.style_analyzer = mock_analyzer

        result = await generator.generate("Test", cluster="KI im Recruiting")
        assert result.char_count == 1500


# ---------------------------------------------------------------------------
# Prompt formatting
# ---------------------------------------------------------------------------

class TestPromptFormatting:
    @pytest.mark.asyncio
    @patch("app.ai.post_generator.StyleAnalyzer")
    @patch("app.ai.post_generator.anthropic.AsyncAnthropic")
    async def test_generation_prompt_includes_all_fields(
        self, mock_anthropic_cls, mock_sa_cls
    ):
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = _make_api_response("Generated post")
        mock_anthropic_cls.return_value = mock_client

        profile = _make_style_profile()
        mock_analyzer = AsyncMock()
        mock_analyzer.get_profile.return_value = profile
        mock_sa_cls.return_value = mock_analyzer

        generator = PostGenerator()
        generator.client = mock_client
        generator.style_analyzer = mock_analyzer

        idea = "Warum Active Sourcing die Zukunft ist"
        cluster = "Stellenschaltung & Kanal-Strategie"
        await generator.generate(idea, cluster=cluster)

        call_args = mock_client.messages.create.call_args
        prompt_sent = call_args.kwargs["messages"][0]["content"]

        assert profile.summary in prompt_sent
        assert cluster in prompt_sent
        assert idea in prompt_sent
        # Sample posts should be included
        assert "Post 1" in prompt_sent

    @pytest.mark.asyncio
    @patch("app.ai.post_generator.StyleAnalyzer")
    @patch("app.ai.post_generator.anthropic.AsyncAnthropic")
    async def test_cluster_prompt_lists_all_clusters(
        self, mock_anthropic_cls, mock_sa_cls
    ):
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = _make_api_response("KI im Recruiting")
        mock_anthropic_cls.return_value = mock_client

        generator = PostGenerator()
        generator.client = mock_client

        await generator.detect_cluster("Test idea")

        call_args = mock_client.messages.create.call_args
        prompt_sent = call_args.kwargs["messages"][0]["content"]
        for cluster_name in VALID_CLUSTERS:
            assert cluster_name in prompt_sent

    @pytest.mark.asyncio
    @patch("app.ai.post_generator.StyleAnalyzer")
    @patch("app.ai.post_generator.anthropic.AsyncAnthropic")
    async def test_generation_uses_correct_model(self, mock_anthropic_cls, mock_sa_cls):
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = _make_api_response("Post content")
        mock_anthropic_cls.return_value = mock_client

        mock_analyzer = AsyncMock()
        mock_analyzer.get_profile.return_value = _make_style_profile()
        mock_sa_cls.return_value = mock_analyzer

        generator = PostGenerator()
        generator.client = mock_client
        generator.style_analyzer = mock_analyzer

        await generator.generate("Idee", cluster="KI im Recruiting")

        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["model"] == "claude-sonnet-5"

    @pytest.mark.asyncio
    @patch("app.ai.post_generator.StyleAnalyzer")
    @patch("app.ai.post_generator.anthropic.AsyncAnthropic")
    async def test_cluster_detection_uses_haiku(self, mock_anthropic_cls, mock_sa_cls):
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = _make_api_response("KI im Recruiting")
        mock_anthropic_cls.return_value = mock_client

        generator = PostGenerator()
        generator.client = mock_client

        await generator.detect_cluster("Test")

        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["model"] == "claude-haiku-4-5-20251001"


# ---------------------------------------------------------------------------
# GeneratedPost dataclass
# ---------------------------------------------------------------------------

class TestGeneratedPostDataclass:
    def test_creation(self):
        post = GeneratedPost(content="Hello", cluster="KI im Recruiting", char_count=5)
        assert post.content == "Hello"
        assert post.cluster == "KI im Recruiting"
        assert post.char_count == 5

    def test_fields(self):
        post = GeneratedPost(content="", cluster="", char_count=0)
        assert hasattr(post, "content")
        assert hasattr(post, "cluster")
        assert hasattr(post, "char_count")
