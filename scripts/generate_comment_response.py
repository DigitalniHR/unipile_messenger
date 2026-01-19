#!/usr/bin/env python3
"""
Generate AI response for a LinkedIn comment.

This is an atomic script designed for AI orchestration - it performs ONE task:
generate a personalized response to a LinkedIn comment using Claude AI.

USAGE:
    python scripts/generate_comment_response.py \
        --post-text "Your post content..." \
        --post-author "Matěj Matolín" \
        --comment-text "Great insights!" \
        --commenter-name "John Doe" \
        --conversation-thread "John: Previous comment..."

OUTPUT (plain text to stdout):
    Thanks John! Glad you found it useful...

CONFIGURATION:
    Loads from .env:
    - ANTHROPIC_API_KEY

EXIT CODES:
    0: Success
    1: Error (printed to stderr)
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_responder import AIResponder


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI response for a LinkedIn comment",
    )
    parser.add_argument(
        "--post-text",
        required=True,
        help="The text of your original post",
    )
    parser.add_argument(
        "--post-author",
        required=True,
        help="Your name (post author)",
    )
    parser.add_argument(
        "--comment-text",
        required=True,
        help="The comment text to respond to",
    )
    parser.add_argument(
        "--commenter-name",
        required=True,
        help="Name of the person who commented",
    )
    parser.add_argument(
        "--conversation-thread",
        default=None,
        help="Previous comments from this commenter (optional)",
    )
    args = parser.parse_args()

    try:
        # Initialize AI responder
        ai = AIResponder()

        # Generate response
        response = ai.generate_response(
            post_text=args.post_text,
            post_author_name=args.post_author,
            comment_text=args.comment_text,
            commenter_name=args.commenter_name,
            conversation_thread=args.conversation_thread,
        )

        # Output plain text (no JSON, no formatting)
        print(response)
        sys.exit(0)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
