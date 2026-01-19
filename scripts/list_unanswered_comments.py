#!/usr/bin/env python3
"""
Fetch unanswered LinkedIn post comments and return as JSON.

This is an atomic script designed for AI orchestration - it performs ONE task:
fetch and filter unanswered comments from recent posts, then output structured JSON.

USAGE:
    python scripts/list_unanswered_comments.py --posts 3

OUTPUT (JSON to stdout):
    {
        "total_posts": 3,
        "total_comments": 15,
        "unanswered_count": 7,
        "comments": [
            {
                "comment_id": "urn:...",
                "post_id": "urn:...",
                "post_text": "Your post content...",
                "post_snippet": "Your post cont...",
                "commenter_name": "John Doe",
                "commenter_id": "urn:...",
                "comment_text": "Great post!",
                "conversation_thread": "John: Previous comment..."
            }
        ]
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
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.unipile_client import UniPileClient, UniPileError
from src.config import Config
from src.models import Post, Comment, PostAuthor, CommentAuthor


def parse_post(data: Dict, account_id: str) -> Post:
    """Convert raw API response dict into typed Post model."""
    author_data = data.get("author", {})
    author = None
    if author_data:
        author = PostAuthor(
            id=author_data.get("id"),
            name=author_data.get("name"),
            headline=author_data.get("headline"),
            profile_url=author_data.get("profile_picture_url"),
        )

    return Post(
        id=data.get("id", ""),
        social_id=data.get("social_id", data.get("id", "")),
        account_id=account_id,
        author=author,
        text=data.get("text", ""),
        timestamp=data.get("parsed_datetime"),
        like_count=data.get("reaction_counter", 0),
        comment_count=data.get("comment_counter", 0),
        share_count=data.get("repost_counter", 0),
        view_count=data.get("impressions_counter", 0),
        post_url=data.get("share_url"),
        is_shared=data.get("is_repost", False),
    )


def parse_comment(data: Dict, post_id: str, your_user_id: str) -> Comment:
    """Convert raw API response dict into typed Comment model."""
    author_data = data.get("author_details", {})
    author_name = data.get("author")

    author = None
    if author_data or author_name:
        author = CommentAuthor(
            id=author_data.get("id") if isinstance(author_data, dict) else None,
            name=author_name,
            headline=author_data.get("headline") if isinstance(author_data, dict) else None,
            profile_url=author_data.get("profile_url") if isinstance(author_data, dict) else None,
        )

    is_from_you = (
        author_data.get("id") == your_user_id
        if isinstance(author_data, dict) else False
    )

    return Comment(
        id=data.get("id", ""),
        post_id=post_id,
        social_id=data.get("social_id"),
        author=author,
        text=data.get("text", ""),
        timestamp=data.get("date"),
        parent_comment_id=data.get("parent_comment_id"),
        like_count=data.get("reaction_counter", 0),
        reply_count=data.get("reply_counter", 0),
        is_from_account=is_from_you,
    )


def get_commenter_thread(
    comments: List[Comment],
    commenter_id: Optional[str],
    current_comment_id: str,
) -> Optional[str]:
    """Build conversation thread with a specific commenter."""
    if not commenter_id:
        return None

    # Filter comments from the same author, excluding current comment
    commenter_comments = [
        c for c in comments
        if c.author
        and c.author.id == commenter_id
        and c.id != current_comment_id
    ]

    if not commenter_comments:
        return None

    # Sort by timestamp (oldest first)
    valid_comments = [c for c in commenter_comments if c.timestamp]
    valid_comments.sort(key=lambda c: c.timestamp or "")

    # Format as conversation thread
    thread_lines = []
    for comment in valid_comments:
        if comment.text:
            author_name = comment.author.name if comment.author else "User"
            thread_lines.append(f"{author_name}: {comment.text}")

    if not thread_lines:
        return None

    return "\n".join(thread_lines)


def get_unanswered_comments(
    comments: List[Comment],
    your_user_id: str,
) -> List[Comment]:
    """Filter comments to find those you haven't responded to yet."""
    # Build comment tree
    replies_by_parent = {}
    for comment in comments:
        parent_id = comment.parent_comment_id
        if parent_id not in replies_by_parent:
            replies_by_parent[parent_id] = []
        replies_by_parent[parent_id].append(comment)

    # Get top-level comments only
    top_level = [c for c in comments if c.parent_comment_id is None]

    # Filter for unanswered
    unanswered = []
    for comment in top_level:
        if comment.is_from_account:
            continue

        replies = replies_by_parent.get(comment.id, [])
        has_your_reply = any(r.is_from_account for r in replies)

        if not has_your_reply:
            unanswered.append(comment)

    return unanswered


def main():
    parser = argparse.ArgumentParser(
        description="Fetch unanswered LinkedIn post comments (JSON output)",
    )
    parser.add_argument(
        "--posts", "-p",
        type=int,
        default=3,
        help="Number of recent posts to process (default: 3)",
    )
    args = parser.parse_args()

    try:
        # Initialize client (loads config from .env)
        client = UniPileClient()

        # Get account info (for user ID)
        accounts = client.list_accounts()
        account = next(
            (acc for acc in accounts if acc.id == Config.UNIPILE_ACCOUNT_ID),
            None
        )
        if not account:
            print(json.dumps({"error": "Account not found"}), file=sys.stderr)
            sys.exit(1)

        # Use provider_id for LinkedIn posts API
        your_user_id = account.provider_id or account.identifier
        if not your_user_id:
            print(json.dumps({"error": "User ID not found in account"}), file=sys.stderr)
            sys.exit(1)

        # Fetch recent posts
        posts_data, _ = client.list_user_posts(
            identifier=your_user_id,
            account_id=Config.UNIPILE_ACCOUNT_ID,
            limit=args.posts,
        )

        posts = [parse_post(p, Config.UNIPILE_ACCOUNT_ID) for p in posts_data]

        # Collect all unanswered comments
        all_unanswered = []
        total_comments = 0

        for post in posts:
            # Fetch all comments for this post
            all_comments_data = []
            cursor = None
            while True:
                comments_data, cursor = client.list_post_comments(
                    post_id=post.social_id,
                    account_id=Config.UNIPILE_ACCOUNT_ID,
                    limit=100,
                    cursor=cursor,
                )
                all_comments_data.extend(comments_data)
                if not cursor:
                    break

            # Parse comments
            comments = [
                parse_comment(c, post.social_id, your_user_id)
                for c in all_comments_data
            ]
            total_comments += len(comments)

            # Filter unanswered
            unanswered = get_unanswered_comments(comments, your_user_id)

            # Build output for each unanswered comment
            for comment in unanswered:
                # Get conversation thread
                thread = None
                if comment.author and comment.author.id:
                    thread = get_commenter_thread(comments, comment.author.id, comment.id)

                # Create snippet (first 50 chars)
                post_snippet = (post.text[:50] + "...") if len(post.text) > 50 else post.text

                all_unanswered.append({
                    "comment_id": comment.id,
                    "post_id": post.social_id,
                    "post_text": post.text,
                    "post_snippet": post_snippet,
                    "post_author_name": post.author.name if post.author else "Unknown",
                    "commenter_name": comment.author.name if comment.author else "Unknown",
                    "commenter_id": comment.author.id if comment.author else None,
                    "comment_text": comment.text,
                    "conversation_thread": thread,
                })

        # Output JSON
        result = {
            "total_posts": len(posts),
            "total_comments": total_comments,
            "unanswered_count": len(all_unanswered),
            "comments": all_unanswered,
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
