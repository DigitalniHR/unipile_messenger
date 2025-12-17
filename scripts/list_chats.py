#!/usr/bin/env python3
"""
List chats/conversations for an account.

Usage:
    python scripts/list_chats.py --account-id ACCOUNT_ID [--limit 20]
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich import box

from src.unipile_client import UniPileClient, UniPileError

console = Console()


def main():
    parser = argparse.ArgumentParser(description="List UniPile chats")
    parser.add_argument(
        "--account-id", "-a",
        required=True,
        help="UniPile account ID",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=20,
        help="Max chats to show (default: 20)",
    )

    args = parser.parse_args()

    try:
        client = UniPileClient()
        chats, cursor = client.list_chats(args.account_id, limit=args.limit)

        if not chats:
            console.print("[yellow]No conversations found.[/yellow]")
            return

        table = Table(
            title=f"Conversations (Account: {args.account_id[:15]}...)",
            box=box.ROUNDED,
            show_header=True,
        )
        table.add_column("#", style="dim", width=3)
        table.add_column("Chat ID", style="cyan", no_wrap=True)
        table.add_column("Name/Subject", max_width=35)
        table.add_column("Provider", style="green")
        table.add_column("Unread", justify="center")

        for i, chat in enumerate(chats, 1):
            # Use chat name or show attendee count
            name = chat.name or f"{len(chat.attendees)} participant(s)"
            if len(name) > 32:
                name = name[:32] + "..."

            unread = f"[red]{chat.unread_count}[/red]" if chat.unread_count else "-"

            table.add_row(
                str(i),
                chat.id,
                name,
                chat.provider,
                unread,
            )

        console.print(table)
        console.print(f"\n[dim]Showing {len(chats)} conversation(s)[/dim]")

        if cursor:
            console.print(f"[dim]More results available (cursor: {cursor[:20]}...)[/dim]")

    except UniPileError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
