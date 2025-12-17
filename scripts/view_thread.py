#!/usr/bin/env python3
"""
View full conversation thread with contact details.

Usage:
    python scripts/view_thread.py --chat-id CHAT_ID [--account-id ACCOUNT_ID]
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

from src.unipile_client import UniPileClient, UniPileError
from src.config import Config

console = Console()


def get_sender_name(client: UniPileClient, sender_id: str, account_id: str) -> str:
    """Try to get sender's full name from profile."""
    try:
        profile = client.get_user_profile(sender_id, account_id)
        first = profile.get("first_name", "")
        last = profile.get("last_name", "")
        if first or last:
            return f"{first} {last}".strip()
    except Exception:
        pass
    return "Unknown"


def main():
    parser = argparse.ArgumentParser(description="View full conversation thread")
    parser.add_argument(
        "--chat-id", "-c",
        required=True,
        help="Chat ID",
    )
    parser.add_argument(
        "--account-id", "-a",
        help="UniPile account ID (if not provided, uses first account)",
    )
    parser.add_argument(
        "--show-profile", "-p",
        action="store_true",
        help="Show contact profile details",
    )

    args = parser.parse_args()

    try:
        Config.validate()
        client = UniPileClient()

        # Get account ID if not provided
        if not args.account_id:
            accounts = client.list_accounts()
            if not accounts:
                console.print("[red]Error: No accounts connected[/red]")
                return
            args.account_id = accounts[0].id

        # Get chat info
        chat = client.get_chat(args.chat_id)
        messages, _ = client.list_messages(args.chat_id, limit=100)

        # Header
        console.print(Panel.fit(
            f"[bold cyan]{chat.name or 'Conversation'}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        ))

        console.print(f"[dim]Total messages: {len(messages)}[/dim]\n")

        # Cache of sender names
        sender_cache = {}

        # Display thread from oldest to newest
        for msg in messages:
            # Determine who's speaking
            if msg.is_sender:
                speaker = "[bold cyan]You[/bold cyan]"
            else:
                # Try to get sender name
                if msg.sender_id not in sender_cache:
                    name = get_sender_name(client, msg.sender_id, args.account_id)
                    sender_cache[msg.sender_id] = name
                else:
                    name = sender_cache[msg.sender_id]

                speaker = f"[bold yellow]{name}[/bold yellow]"

            # Format time
            time_str = ""
            if msg.timestamp:
                dt = msg.timestamp
                time_str = f"[dim]{dt.strftime('%Y-%m-%d %H:%M:%S')}[/dim] "

            # Message text
            text = msg.text or "[italic]No text[/italic]"

            # Display
            console.print(f"{time_str}{speaker}:")
            console.print(f"  {text}")
            console.print()

        # Show profile if requested
        if args.show_profile and messages:
            # Get first non-self sender
            for msg in messages:
                if not msg.is_sender:
                    try:
                        profile = client.get_user_profile(msg.sender_id, args.account_id)
                        console.print(Panel(
                            f"[cyan]{profile.get('first_name')} {profile.get('last_name')}[/cyan]\n"
                            f"[yellow]{profile.get('headline', 'N/A')}[/yellow]\n"
                            f"[dim]{profile.get('location', 'N/A')}[/dim]\n"
                            f"📊 {profile.get('connections_count', 0)} connections | "
                            f"{profile.get('follower_count', 0)} followers\n"
                            f"🔗 linkedin.com/in/{profile.get('public_identifier', 'profile')}",
                            title="Contact Profile",
                            border_style="cyan",
                        ))
                    except Exception:
                        pass
                    break

    except UniPileError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
