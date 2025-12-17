#!/usr/bin/env python3
"""
Send a message directly to a LinkedIn user (creates chat if needed).

This is the recommended way to send messages - you don't need to find existing chat.

Usage:
    python scripts/send_to_user.py --user-id USER_ID --message "Hello!"
    python scripts/send_to_user.py -u USER_ID -m "Hi" --yes
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

from src.unipile_client import UniPileClient, UniPileError

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="Send message to LinkedIn user (creates chat if needed)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/send_to_user.py --user-id ACoAABRD1jk... --message "Hello!"
  python scripts/send_to_user.py -u ACoAABRD1jk... -m "Hi" --yes
        """
    )
    parser.add_argument("--user-id", "-u", required=True, help="Recipient's provider user ID")
    parser.add_argument("--message", "-m", required=True, help="Message text to send")
    parser.add_argument("--account-id", "-a", help="Account ID (uses first account if not provided)")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")

    args = parser.parse_args()

    try:
        client = UniPileClient()

        # Get account ID
        if not args.account_id:
            accounts = client.list_accounts()
            if not accounts:
                console.print("[red]Error: No accounts connected[/red]")
                return
            args.account_id = accounts[0].id
            console.print(f"Using account: {accounts[0].name}\n")

        # Show message draft
        console.print(Panel(
            args.message,
            title=f"[cyan]Message Draft[/cyan]",
            border_style="cyan"
        ))

        # Confirmation
        if not args.yes:
            console.print("\n[yellow]⚠️  Send this message?[/yellow]")
            response = input("Type 'yes' or 'send' to confirm: ").strip().lower()
            if response not in ["yes", "send", "ok", "ano", "pošli"]:
                console.print("[red]❌ Message not sent[/red]")
                return

        # Send message
        console.print("\n[dim]Sending...[/dim]")
        chat_id, message_id = client.send_to_user(
            account_id=args.account_id,
            user_id=args.user_id,
            text=args.message
        )

        console.print(f"[green]✓ Message sent![/green]")
        console.print(f"[dim]Chat ID: {chat_id}[/dim]")
        console.print(f"[dim]Message ID: {message_id}[/dim]")

    except UniPileError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
