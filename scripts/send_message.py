#!/usr/bin/env python3
"""
Send a message to a chat.

Usage:
    python scripts/send_message.py --chat-id CHAT_ID --message "Hello!"
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console

from src.unipile_client import UniPileClient, UniPileError

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Send message via UniPile")
    parser.add_argument(
        "--chat-id", "-c",
        required=True,
        help="Chat ID to send message to",
    )
    parser.add_argument(
        "--message", "-m",
        required=True,
        help="Message text to send",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt",
    )

    args = parser.parse_args()

    # Confirm unless --yes flag
    if not args.yes:
        console.print(f"\n[bold]Chat ID:[/bold] {args.chat_id}")
        console.print(f"[bold]Message:[/bold] {args.message}")
        console.print()

        confirm = input("Send this message? (y/N): ")
        if confirm.lower() != "y":
            console.print("[yellow]Cancelled.[/yellow]")
            return

    try:
        client = UniPileClient()
        result = client.send_message(args.chat_id, args.message)

        console.print(f"\n[bold green]Message sent![/bold green]")
        console.print(f"[dim]Message ID: {result.id}[/dim]")

    except UniPileError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
