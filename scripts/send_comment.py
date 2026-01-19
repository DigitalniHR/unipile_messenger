#!/usr/bin/env python3
"""
Send a comment reply to a LinkedIn post.

This is an atomic script designed for AI orchestration - it performs ONE task:
send a pre-approved comment text to a specific LinkedIn post.

USAGE:
    python scripts/send_comment.py \
        --post-id "urn:li:activity:..." \
        --text "Your approved response text"

OUTPUT (JSON to stdout):
    {
        "success": true,
        "comment_id": "urn:li:comment:..."
    }

CONFIGURATION:
    Loads from .env:
    - UNIPILE_ACCOUNT_ID
    - UNIPILE_ACCESS_TOKEN
    - UNIPILE_DSN

EXIT CODES:
    0: Success
    1: Error (printed to stderr)
"""
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.unipile_client import UniPileClient, UniPileError
from src.config import Config


def main():
    parser = argparse.ArgumentParser(
        description="Send a comment reply to a LinkedIn post",
    )
    parser.add_argument(
        "--post-id",
        required=True,
        help="The post ID (social_id) to reply to",
    )
    parser.add_argument(
        "--text",
        required=True,
        help="The comment text to send",
    )
    args = parser.parse_args()

    try:
        # Initialize client (loads config from .env)
        client = UniPileClient()

        # Send comment
        comment_id = client.send_comment(
            post_id=args.post_id,
            account_id=Config.UNIPILE_ACCOUNT_ID,
            text=args.text,
        )

        # Output JSON
        result = {
            "success": True,
            "comment_id": comment_id,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)

    except UniPileError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
