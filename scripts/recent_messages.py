#!/usr/bin/env python3
"""
View recent messages from all conversations.

Usage:
    python scripts/recent_messages.py --days 3 [--account-id ACCOUNT_ID]
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich import box

from src.unipile_client import UniPileClient, UniPileError

console = Console()


def parse_timestamp(ts) -> datetime | None:
    """Parse ISO timestamp to datetime."""
    if not ts:
        return None
    try:
        # Handle ISO format with Z suffix
        if isinstance(ts, str):
            ts = ts.replace('Z', '+00:00')
            return datetime.fromisoformat(ts)
        return ts
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="View recent messages")
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=3,
        help="Number of past days to show (default: 3)",
    )
    parser.add_argument(
        "--account-id", "-a",
        help="UniPile account ID (if not provided, uses first account)",
    )

    args = parser.parse_args()

    try:
        client = UniPileClient()

        # Get account ID if not provided
        if not args.account_id:
            accounts = client.list_accounts()
            if not accounts:
                console.print("[red]Error: No accounts connected[/red]")
                return
            args.account_id = accounts[0].id
            console.print(f"[dim]Using account: {accounts[0].name}[/dim]\n")

        # Calculate cutoff time
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
        console.print(f"[dim]Loading messages from last {args.days} day(s)...[/dim]\n")

        # Get all chats
        all_messages = []
        chats, cursor = client.list_chats(args.account_id, limit=50)

        while chats:
            for chat in chats:
                try:
                    # Get messages from this chat
                    messages, _ = client.list_messages(chat.id, limit=100)

                    for msg in messages:
                        msg_time = parse_timestamp(msg.timestamp)
                        if msg_time and msg_time > cutoff:
                            all_messages.append({
                                "time": msg_time,
                                "chat": chat.name or f"{len(chat.attendees)} participant(s)",
                                "sender": "You" if msg.is_sender else msg.sender_name or "Unknown",
                                "text": (msg.text or "")[:60],
                                "chat_id": chat.id,
                            })
                except Exception:
                    continue

            # Get next batch of chats
            if cursor:
                chats, cursor = client.list_chats(args.account_id, limit=50, cursor=cursor)
            else:
                break

        if not all_messages:
            console.print(f"[yellow]No messages from last {args.days} day(s)[/yellow]")
            return

        # Sort by time (newest first)
        all_messages.sort(key=lambda x: x["time"], reverse=True)

        # Display
        table = Table(
            title=f"Recent Messages (last {args.days} day(s))",
            box=box.ROUNDED,
            show_header=True,
        )
        table.add_column("Time", style="dim", no_wrap=True)
        table.add_column("Chat", max_width=30)
        table.add_column("From", style="cyan")
        table.add_column("Message", max_width=50)

        for msg in all_messages:
            time_str = msg["time"].strftime("%Y-%m-%d %H:%M")
            text = msg["text"]
            if len(msg["text"]) > 47:
                text = msg["text"][:47] + "..."

            table.add_row(
                time_str,
                msg["chat"],
                msg["sender"],
                text,
            )

        console.print(table)
        console.print(f"\n[dim]Total: {len(all_messages)} message(s)[/dim]")

    except UniPileError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
