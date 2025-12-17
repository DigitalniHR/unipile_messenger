#!/usr/bin/env python3
"""
Send a reply with suggested message.

Usage:
    python scripts/send_reply.py --chat-id CHAT_ID [--message "Your custom message"]
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
import questionary

from src.unipile_client import UniPileClient, UniPileError

console = Console()


def get_suggested_reply(chat_name: str) -> str:
    """Generate a suggested reply based on context."""
    if "svátky" in chat_name.lower() or "vánoce" in chat_name.lower():
        return "Také Ti přeju hezké svátky a krásný nový rok! Děkuji za příjemnou konverzaci. Těšíme se na další spolupráci."

    return "Děkuji za zprávu. Těším se na další komunikaci."


def main():
    parser = argparse.ArgumentParser(description="Send a reply message")
    parser.add_argument(
        "--chat-id", "-c",
        required=True,
        help="Chat ID",
    )
    parser.add_argument(
        "--message", "-m",
        help="Custom message (if not provided, shows suggestion)",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt",
    )

    args = parser.parse_args()

    try:
        client = UniPileClient()

        # Get chat info for context
        chat = client.get_chat(args.chat_id)

        # Prepare message
        if args.message:
            message = args.message
        else:
            message = get_suggested_reply(chat.name or "")

        # Show message for review
        console.print(Panel(
            f"[bold]{message}[/bold]",
            title=f"💬 Reply to: {chat.name or 'Chat'}",
            border_style="cyan",
            padding=(1, 2),
        ))

        # Confirm
        if not args.yes:
            console.print()
            confirm = questionary.confirm(
                "Send this message?",
                default=True,
                auto_enter=False,
            ).ask()

            if not confirm:
                console.print("[yellow]Cancelled.[/yellow]")
                return

        # Send
        result = client.send_message(args.chat_id, message)
        console.print(f"\n[bold green]✓ Message sent![/bold green]")
        console.print(f"[dim]Message ID: {result.id}[/dim]")

    except UniPileError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
