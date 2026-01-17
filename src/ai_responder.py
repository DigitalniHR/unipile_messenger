"""
AI-powered comment response generator using Anthropic Claude.

This module handles the generation of professional LinkedIn comment responses
using Claude AI. It loads system prompts from external markdown files (following
the project's architecture preference for separated concerns) and generates
context-aware responses that match the user's professional tone.

WORKFLOW:
1. Initialize AIResponder with Anthropic API key from .env
2. System prompt loads from prompts/comment_response.md
3. Call generate_response() with post context and comment text
4. Claude generates a professional, value-adding reply
5. Return raw response text (no prefixes, no meta-commentary)

CONFIGURATION:
- ANTHROPIC_API_KEY: Required, from https://console.anthropic.com/
- ANTHROPIC_MODEL: Optional, defaults to claude-3-5-sonnet-20241022

ERROR HANDLING:
- Missing API key → ValueError with setup instructions
- API failures → Exception with error details
- File not found → Falls back to inline default prompt
"""
import anthropic
from pathlib import Path
from typing import Optional

from src.config import Config

# Load system prompt from file - keeps AI instructions separate from code
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
SYSTEM_PROMPT_FILE = PROMPTS_DIR / "comment_response.md"


class AIResponder:
    """Generate professional LinkedIn comment responses using Claude AI.

    This class encapsulates the AI response generation logic, handling:
    - Anthropic client initialization
    - System prompt loading from external file
    - Context-aware response generation
    - Error handling for API failures

    Usage:
        ai = AIResponder()
        response = ai.generate_response(
            post_text="My latest article on leadership...",
            post_author_name="Jane Doe",
            comment_text="Great insights on delegation!",
            commenter_name="John Smith"
        )
        print(response)  # Professional reply to John's comment
    """

    def __init__(self):
        """Initialize Anthropic client with credentials from .env.

        Raises:
            ValueError: If ANTHROPIC_API_KEY is not set in .env

        Side effects:
            - Loads system prompt from prompts/comment_response.md
            - Falls back to inline prompt if file missing
            - Stores Anthropic client and model name
        """
        if not Config.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY not set in .env. "
                "Get one from: https://console.anthropic.com/"
            )

        # Initialize Anthropic client - handles API communication
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        # Store model name for logging/debugging
        self.model = Config.ANTHROPIC_MODEL

        # Load system prompt from external markdown file
        # This keeps AI instructions separate from code (architectural preference)
        if SYSTEM_PROMPT_FILE.exists():
            self.system_prompt_template = SYSTEM_PROMPT_FILE.read_text()
        else:
            # Fallback inline prompt if file is missing (safety net)
            self.system_prompt_template = self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Default prompt if file doesn't exist."""
        return """You are a professional LinkedIn engagement assistant.

Generate thoughtful, professional responses that:
- Thank the commenter for their input
- Add value to the conversation
- Are concise (2-3 sentences max)
- Avoid generic phrases

Keep tone professional yet personable."""

    def generate_response(
        self,
        post_text: str,
        post_author_name: str,
        comment_text: str,
        commenter_name: str,
        conversation_thread: Optional[str] = None,
        max_tokens: int = 300,
    ) -> str:
        """Generate a professional AI response to a LinkedIn comment.

        This method orchestrates the full response generation workflow:
        1. Builds context-aware prompt with post + comment info
        2. Sends to Claude API with professional engagement guidelines
        3. Returns generated response ready to send

        IMPORTANT: Response is returned as raw text with no prefixes or
        meta-commentary. It's ready to post directly to LinkedIn.

        Args:
            post_text: The original LinkedIn post content (for context)
            post_author_name: Your name (will appear as responder)
            comment_text: The comment you're responding to
            commenter_name: Name of person who commented (for personalization)
            conversation_thread: Previous comments/replies with this person (optional, for better context)
            max_tokens: Maximum length of response (default: 300 chars)

        Returns:
            str: Generated response text, ready to post
                Example: "Thanks for pointing that out! Have you considered..."

        Raises:
            Exception: If Claude API fails (network, quota, etc.)

        Example:
            >>> ai = AIResponder()
            >>> response = ai.generate_response(
            ...     post_text="Why delegation is critical for leaders",
            ...     post_author_name="Jane Doe",
            ...     comment_text="Great point about trust!",
            ...     commenter_name="John Smith"
            ... )
            >>> print(response)
            "Absolutely - trust is the foundation. Have you found any specific..."
        """
        # Build context-aware prompt that Claude will respond to
        # Include full conversation thread if available for better context
        thread_section = ""
        if conversation_thread:
            thread_section = f"\nCONVERSATION THREAD WITH {commenter_name}:\n{conversation_thread}\n"

        user_prompt = f"""POST CONTENT:
{post_text}{thread_section}
CURRENT COMMENT FROM {commenter_name}:
{comment_text}

Generate a response from {post_author_name}:"""

        try:
            # Call Claude API with system prompt + context
            # System prompt comes from prompts/comment_response.md
            # (guidelines for professional, value-adding responses)
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=self.system_prompt_template,  # Professional engagement guidelines
                messages=[
                    {"role": "user", "content": user_prompt}  # Context + request
                ]
            )

            # Extract generated text from Claude's response
            # message.content is a list of content blocks, first is text
            response_text = message.content[0].text.strip()
            return response_text

        except anthropic.APIError as e:
            # Wrap API errors with context about what went wrong
            raise Exception(f"AI generation failed: {e}")
