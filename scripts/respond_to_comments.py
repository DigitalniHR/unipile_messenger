#!/usr/bin/env python3
"""
Respond to unanswered LinkedIn post comments with AI-generated responses.

COMPLETE WORKFLOW:
1. Fetch N most recent LinkedIn posts
2. Download all comments from those posts (with pagination)
3. Build comment threading tree (parent_id relationships)
4. Filter out:
   - Your own comments
   - Comments you've already replied to
5. For each unanswered top-level comment:
   - Show comment in rich panel
   - Generate professional response using Claude AI
   - Open multi-line editor pre-filled with AI response
   - Allow editing (Ctrl+D to finish, Ctrl+C to skip)
   - Preview final response in panel
   - Wait for approval
   - Send comment reply to LinkedIn
   - Rate-limit: 1s sleep between sends
6. Display summary (sent/skipped counts)

KEY FEATURES:
- Inline editor: Edit AI responses before sending (Ctrl+D to finish, Ctrl+C to skip)
- Mandatory approval workflow: Every response requires "yes" before sending
- Conversation context: Uses full comment thread for better AI relevance
- Dry-run mode: Preview all responses without sending anything
- Comment threading: Only responds to top-level comments
- Rate limiting: 1 second sleep between API sends
- Error handling: Skips failed comments, continues with next

EXAMPLE USAGE:
    # Preview mode (safe to test)
    python scripts/respond_to_comments.py --posts 3 --dry-run

    # Interactive mode (approve each response)
    python scripts/respond_to_comments.py --posts 3

    # Process more posts
    python scripts/respond_to_comments.py --posts 10

CONFIGURATION REQUIRED:
    .env file must contain:
    - UNIPILE_ACCOUNT_ID: Your UniPile account ID
    - UNIPILE_ACCESS_TOKEN: UniPile API key
    - UNIPILE_DSN: UniPile server domain
    - ANTHROPIC_API_KEY: Claude API key (from https://console.anthropic.com/)

OUTPUT EXAMPLE:
    Account: Matěj Matolín
    AI Model: claude-3-5-sonnet-20241022

    Fetching 3 most recent posts...
    ✓ Found 3 post(s)

    Processing post: 733266186479...
      Total comments: 12, Unanswered: 2

    ┌─ Unanswered Comments (2) ──────────┐
    │ # │ Post          │ Commenter │ Comment   │
    ├───┼───────────────┼───────────┼───────────┤
    │ 1 │ Latest article│ John Doe  │ Great... │
    │ 2 │ Latest article│ Jane Smith│ Thanks... │
    └───┴───────────────┴───────────┴───────────┘

    ─── Comment 1/2 ───
    [Shows comment in yellow panel]
    Generating response...
    [Shows AI-generated response in green panel]

    Send this response?
    Type 'yes' or 'send' to confirm: yes
    ✓ Sent! (Comment ID: abc123...)

    Summary:
      Sent: 2
      Skipped: 0
"""
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import questionary

from src.unipile_client import UniPileClient, UniPileError
from src.config import Config
from src.models import Post, Comment, PostAuthor, CommentAuthor
from src.ai_responder import AIResponder

console = Console()


def parse_post(data: Dict, account_id: str) -> Post:
    """Convert raw API response dict into typed Post model.

    Handles:
    - Missing fields (uses sensible defaults)
    - Author nested object parsing
    - Engagement stats (reaction_counter, comment_counter, etc.)
    - Both 'id' and 'social_id' (uses social_id for LinkedIn actions)

    Args:
        data: Raw dict from UniPile API /users/{id}/posts endpoint
        account_id: The account this post belongs to

    Returns:
        Post: Pydantic model with typed fields
    """
    author_data = data.get("author", {})
    author = None
    if author_data:
        author = PostAuthor(
            id=author_data.get("id"),
            name=author_data.get("name"),
            headline=author_data.get("headline"),
            profile_url=author_data.get("profile_picture_url"),  # API uses profile_picture_url
        )

    return Post(
        id=data.get("id", ""),
        social_id=data.get("social_id", data.get("id", "")),  # Use social_id for API calls
        account_id=account_id,
        author=author,
        text=data.get("text", ""),
        timestamp=data.get("parsed_datetime"),  # API returns parsed_datetime
        like_count=data.get("reaction_counter", 0),  # API uses reaction_counter
        comment_count=data.get("comment_counter", 0),  # API uses comment_counter
        share_count=data.get("repost_counter", 0),  # API uses repost_counter
        view_count=data.get("impressions_counter", 0),  # API uses impressions_counter
        post_url=data.get("share_url"),  # API uses share_url
        is_shared=data.get("is_repost", False),  # API uses is_repost
    )


def parse_comment(data: Dict, post_id: str, your_user_id: str) -> Comment:
    """Convert raw API response dict into typed Comment model.

    Handles:
    - Author nested object parsing (author_details field)
    - Determines if comment is from your account (is_from_account flag)
    - Comment threading via parent_comment_id (None = top-level)
    - Missing fields with sensible defaults

    Args:
        data: Raw dict from UniPile API /posts/{id}/comments endpoint
        post_id: The post_id this comment belongs to (social_id format)
        your_user_id: Your account's user ID (to detect own comments)

    Returns:
        Comment: Pydantic model with typed fields
    """
    # API returns author_details object with author info
    author_data = data.get("author_details", {})
    author_name = data.get("author")  # Author name is in separate field

    author = None
    if author_data or author_name:
        author = CommentAuthor(
            id=author_data.get("id") if isinstance(author_data, dict) else None,
            name=author_name,
            headline=author_data.get("headline") if isinstance(author_data, dict) else None,
            profile_url=author_data.get("profile_url") if isinstance(author_data, dict) else None,
        )

    # Detect if this comment is from your account (used for filtering)
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
        timestamp=data.get("date"),  # API returns 'date' field
        parent_comment_id=data.get("parent_comment_id"),  # None = top-level, else reply
        like_count=data.get("reaction_counter", 0),  # API uses reaction_counter
        reply_count=data.get("reply_counter", 0),  # API uses reply_counter
        is_from_account=is_from_you,  # Flag for filtering your own comments
    )


def get_commenter_thread(
    comments: List[Comment],
    commenter_id: Optional[str],
    current_comment_id: str,
) -> Optional[str]:
    """Build conversation thread with a specific commenter.

    Collects all comments from the same commenter (except the current one being responded to)
    and formats them chronologically as a conversation context.

    This helps the AI generate more personalized and contextual responses by understanding
    the previous conversation history with this specific person on this post.

    Args:
        comments: All Comment objects from the post
        commenter_id: The author ID of the commenter we're responding to
        current_comment_id: The ID of the current comment (to exclude from thread)

    Returns:
        Optional[str]: Formatted thread string (e.g., "User: comment text\nUser: reply text")
                      or None if no previous comments from this commenter

    Example:
        >>> comments = [
        ...     Comment(id="1", author=CommentAuthor(id="user1", name="John"), text="First comment"),
        ...     Comment(id="2", author=CommentAuthor(id="user1", name="John"), text="Follow-up comment"),
        ...     Comment(id="3", author=CommentAuthor(id="user2", name="Jane"), text="Different person"),
        ... ]
        >>> thread = get_commenter_thread(comments, "user1", "2")
        >>> print(thread)
        'John: First comment'
    """
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

    # Sort by timestamp (oldest first) for chronological order
    # Filter out None timestamps, sort the rest
    valid_comments = [c for c in commenter_comments if c.timestamp]
    valid_comments.sort(key=lambda c: c.timestamp or "")

    # Format as conversation thread
    thread_lines = []
    for comment in valid_comments:
        if comment.text:
            # Format: "Name: comment text"
            author_name = comment.author.name if comment.author else "User"
            thread_lines.append(f"{author_name}: {comment.text}")

    if not thread_lines:
        return None

    return "\n".join(thread_lines)


def get_unanswered_comments(
    comments: List[Comment],
    your_user_id: str,
) -> List[Comment]:
    """Filter comments to find those you haven't responded to yet.

    ALGORITHM:
    1. Build a comment tree: map parent_comment_id → [child comments]
    2. Get all top-level comments (parent_comment_id is None)
    3. For each top-level comment:
       a. Skip if is_from_account (it's your comment)
       b. Check if any reply to this comment is from your account
       c. If no reply from you, add to unanswered list

    IMPORTANT:
    - Only processes top-level comments (not replies to replies)
    - A comment is "answered" if you (your account) replied to it
    - Your own comments are always skipped (no need to respond to yourself)

    Args:
        comments: All Comment objects from the post (all levels)
        your_user_id: Your account's user ID (from account info)

    Returns:
        List[Comment]: Filtered list of top-level comments needing responses

    Example:
        >>> all_comments = [
        ...     Comment(id="1", parent_id=None, is_from_account=False),  # Top-level
        ...     Comment(id="2", parent_id="1", is_from_account=True),    # Your reply
        ...     Comment(id="3", parent_id=None, is_from_account=False),  # Top-level
        ...     Comment(id="4", parent_id="3", is_from_account=False),   # Someone's reply
        ... ]
        >>> unanswered = get_unanswered_comments(all_comments, "user123")
        >>> len(unanswered)
        1  # Only comment #3 (you replied to #1 but not to #3)
    """
    # Step 1: Build comment tree - map parent_id to list of replies
    # This helps us quickly find all replies to a specific comment
    replies_by_parent = {}
    for comment in comments:
        parent_id = comment.parent_comment_id
        if parent_id not in replies_by_parent:
            replies_by_parent[parent_id] = []
        replies_by_parent[parent_id].append(comment)

    # Step 2: Get top-level comments only (parent_id is None)
    # We only want to respond to main comments, not nested replies
    top_level = [c for c in comments if c.parent_comment_id is None]

    # Step 3: Filter for unanswered comments
    unanswered = []
    for comment in top_level:
        # Skip your own comments (no need to respond to yourself)
        if comment.is_from_account:
            continue

        # Check if you've already replied to this comment
        # Get all replies to this comment
        replies = replies_by_parent.get(comment.id, [])
        # Check if any reply is from your account
        has_your_reply = any(r.is_from_account for r in replies)

        # Only add to unanswered if you haven't replied yet
        if not has_your_reply:
            unanswered.append(comment)

    return unanswered


def main():
    parser = argparse.ArgumentParser(
        description="Respond to LinkedIn post comments with AI-generated responses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/respond_to_comments.py --posts 3
  python scripts/respond_to_comments.py --posts 5 --dry-run
  python scripts/respond_to_comments.py --posts 10
        """
    )
    parser.add_argument(
        "--posts", "-p",
        type=int,
        default=3,
        help="Number of recent posts to process (default: 3)",
    )
    parser.add_argument(
        "--account-id", "-a",
        default=Config.UNIPILE_ACCOUNT_ID,
        help="UniPile account ID (default: from .env)",
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Preview responses without sending",
    )

    args = parser.parse_args()

    try:
        # Initialize clients
        client = UniPileClient()

        # Get account info
        account = client.get_account(args.account_id)
        # Use provider_id (LinkedIn user ID) for posts/comments endpoints
        your_user_id = account.provider_id or account.identifier or args.account_id
        console.print(f"[dim]Account: {account.name}[/dim]\n")

        # Initialize AI responder
        try:
            ai = AIResponder()
            console.print(f"[dim]AI Model: {ai.model}[/dim]\n")
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            return


        # Step 1: Fetch recent posts
        console.print(f"[cyan]Fetching {args.posts} most recent posts...[/cyan]")
        posts_data, _ = client.list_user_posts(
            identifier=your_user_id,
            account_id=args.account_id,
            limit=args.posts,
        )

        if not posts_data:
            console.print("[yellow]No posts found.[/yellow]")
            return

        posts = [parse_post(p, args.account_id) for p in posts_data]
        console.print(f"[green]✓ Found {len(posts)} post(s)[/green]\n")

        # Step 2: Fetch comments for each post
        all_unanswered = []

        for post in posts:
            console.print(f"[dim]Processing post: {post.social_id[:20]}...[/dim]")

            # Get all comments (with pagination)
            all_comments = []
            comments_data, cursor = client.list_post_comments(
                post_id=post.social_id,
                account_id=args.account_id,
                limit=100,
            )

            while comments_data:
                for c_data in comments_data:
                    comment = parse_comment(c_data, post.social_id, your_user_id)
                    all_comments.append(comment)

                # Get next page if exists
                if cursor:
                    time.sleep(0.5)  # Rate limit protection
                    comments_data, cursor = client.list_post_comments(
                        post_id=post.social_id,
                        account_id=args.account_id,
                        limit=100,
                        cursor=cursor,
                    )
                else:
                    break

            # Find unanswered comments
            unanswered = get_unanswered_comments(all_comments, your_user_id)

            console.print(
                f"[dim]  Total comments: {len(all_comments)}, "
                f"Unanswered: {len(unanswered)}[/dim]"
            )

            # Store with post context and all comments for thread building
            for comment in unanswered:
                all_unanswered.append({
                    "post": post,
                    "comment": comment,
                    "all_comments": all_comments,  # Keep all comments for conversation thread
                })

        console.print()

        if not all_unanswered:
            console.print("[green]All comments are answered! Nothing to do.[/green]")
            return

        # Step 3: Show summary table
        table = Table(
            title=f"Unanswered Comments ({len(all_unanswered)})",
            box=box.ROUNDED,
        )
        table.add_column("#", style="dim", width=3)
        table.add_column("Post", max_width=30)
        table.add_column("Commenter", style="cyan")
        table.add_column("Comment", max_width=40)

        for i, item in enumerate(all_unanswered, 1):
            post = item["post"]
            comment = item["comment"]

            post_preview = (post.text or "")[:27] + "..." if post.text else "[No text]"
            comment_preview = (comment.text or "")[:37] + "..." if comment.text else "[No text]"
            commenter = comment.author.name if comment.author else "Unknown"

            table.add_row(
                str(i),
                post_preview,
                commenter,
                comment_preview,
            )

        console.print(table)
        console.print()

        # Step 4: Generate and send responses
        sent_count = 0
        skipped_count = 0

        for i, item in enumerate(all_unanswered, 1):
            post = item["post"]
            comment = item["comment"]
            all_comments = item["all_comments"]

            console.print(f"\n[cyan]─── Comment {i}/{len(all_unanswered)} ───[/cyan]")

            # Show comment context
            console.print(Panel(
                f"[yellow]{comment.author.name if comment.author else 'Unknown'}:[/yellow]\n"
                f"{comment.text or '[No text]'}",
                title="Comment",
                border_style="yellow",
            ))

            # Generate AI response with conversation context
            console.print("[dim]Generating response...[/dim]")
            try:
                # Build conversation thread with this commenter (for better personalization)
                conversation_thread = get_commenter_thread(
                    comments=all_comments,
                    commenter_id=comment.author.id if comment.author else None,
                    current_comment_id=comment.id,
                )

                response_text = ai.generate_response(
                    post_text=post.text or "",
                    post_author_name=account.name or "You",
                    comment_text=comment.text or "",
                    commenter_name=comment.author.name if comment.author else "User",
                    conversation_thread=conversation_thread,  # Include previous comments for context
                )
            except Exception as e:
                console.print(f"[red]Failed to generate response: {e}[/red]")
                skipped_count += 1
                continue

            # Show proposed response
            console.print(Panel(
                response_text,
                title="[green]Proposed Response[/green]",
                border_style="green",
            ))

            # Allow editing the response before sending
            console.print("\n[cyan]Edit response (press Ctrl+D when done, or Ctrl+C to skip):[/cyan]")
            try:
                # Try interactive questionary editor
                try:
                    edited_response = questionary.text(
                        "",
                        default=response_text,
                        multiline=True,
                    ).ask()
                except Exception:
                    # Fallback for non-interactive environments
                    # (OSError, KeyError, ValueError, EOFError, etc.)
                    console.print("[yellow]Note: Interactive editor unavailable[/yellow]")
                    try:
                        console.print("Current response:")
                        console.print(Panel(response_text, border_style="dim"))
                        console.print("Press Enter to keep, or type new response (empty to skip):")
                        edited_response = input("> ").strip() or response_text
                    except EOFError:
                        # No input available, use original response
                        edited_response = response_text

                # User pressed Ctrl+C or closed editor
                if edited_response is None:
                    console.print("[dim]Skipped[/dim]")
                    skipped_count += 1
                    continue

                # Trim whitespace
                edited_response = edited_response.strip()

                # Show the final edited version if it changed
                if edited_response != response_text:
                    console.print("\n[green bold]Edited Response:[/green bold]")
                    console.print(Panel(
                        edited_response,
                        border_style="green",
                        box=box.ROUNDED,
                    ))

                # Get final approval
                console.print("\n[yellow]Send this response?[/yellow]")
                try:
                    approval = input("Type 'yes' or 'send' to confirm (or 'skip'): ").strip().lower()
                except EOFError:
                    # No input available, assume skip
                    console.print("[dim]Skipped[/dim]")
                    skipped_count += 1
                    continue

                if approval not in ["yes", "send", "ok"]:
                    console.print("[dim]Skipped[/dim]")
                    skipped_count += 1
                    continue

                # Use edited response for sending
                response_text = edited_response

            except KeyboardInterrupt:
                console.print("\n[dim]Skipped[/dim]")
                skipped_count += 1
                continue

            # Dry run mode (after editing/approval, don't actually send)
            if args.dry_run:
                console.print("[dim]Dry run: not sending[/dim]")
                continue

            # Send comment
            try:
                console.print("[dim]Sending...[/dim]")
                comment_id = client.send_comment(
                    post_id=post.social_id,
                    account_id=args.account_id,
                    text=response_text,
                    parent_comment_id=comment.id,
                )
                console.print(f"[green]✓ Sent![/green] (Comment ID: {comment_id[:20]}...)")
                sent_count += 1

                # Rate limiting
                time.sleep(1)

            except UniPileError as e:
                console.print(f"[red]Failed to send: {e}[/red]")
                skipped_count += 1

        # Summary
        console.print(f"\n[bold green]Summary:[/bold green]")
        console.print(f"  Sent: {sent_count}")
        console.print(f"  Skipped: {skipped_count}")

    except UniPileError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
