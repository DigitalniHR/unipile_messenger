#!/usr/bin/env python3
"""
UniPile Messenger - Main interactive application.
LinkedIn messaging via UniPile API with Rich terminal UI.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
import questionary
from questionary import Style

from src.unipile_client import UniPileClient, UniPileError
from src.config import Config

console = Console()

# Custom style for questionary
custom_style = Style([
    ("qmark", "fg:cyan bold"),
    ("question", "bold"),
    ("answer", "fg:cyan"),
    ("pointer", "fg:cyan bold"),
    ("highlighted", "fg:cyan bold"),
    ("selected", "fg:cyan"),
])


def show_header():
    """Display application header."""
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]UniPile Messenger[/bold cyan]\n"
        "[dim]LinkedIn Messaging via UniPile API[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))
    console.print()


def show_error(message: str):
    """Display error message."""
    console.print(f"\n[bold red]Error:[/bold red] {message}\n")


def show_success(message: str):
    """Display success message."""
    console.print(f"\n[bold green]Success:[/bold green] {message}\n")


def pause():
    """Wait for user to press Enter."""
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def list_accounts_menu(client: UniPileClient):
    """Display connected accounts."""
    show_header()
    console.print("[bold]Connected Accounts[/bold]\n")

    try:
        accounts = client.list_accounts()

        if not accounts:
            console.print("[yellow]No accounts connected.[/yellow]")
            console.print("[dim]Connect an account at dashboard.unipile.com[/dim]")
        else:
            table = Table(box=box.ROUNDED, show_header=True)
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Provider", style="green")
            table.add_column("Name/Email")
            table.add_column("Status")

            for acc in accounts:
                status_color = "green" if acc.status == "OK" else "yellow"
                table.add_row(
                    acc.id,
                    acc.provider,
                    acc.name or acc.identifier or "-",
                    f"[{status_color}]{acc.status}[/{status_color}]",
                )

            console.print(table)

    except UniPileError as e:
        show_error(str(e))

    pause()


def select_account(client: UniPileClient) -> str | None:
    """Let user select an account."""
    try:
        accounts = client.list_accounts()
        if not accounts:
            show_error("No accounts connected.")
            return None

        choices = [
            f"{acc.id} ({acc.provider} - {acc.name or acc.identifier or 'Unknown'})"
            for acc in accounts
        ]

        selected = questionary.select(
            "Select account:",
            choices=choices,
            style=custom_style,
        ).ask()

        if selected:
            return selected.split(" ")[0]  # Extract ID
        return None

    except UniPileError as e:
        show_error(str(e))
        return None


def view_conversations_menu(client: UniPileClient):
    """Display conversations for selected account."""
    show_header()
    console.print("[bold]Conversations[/bold]\n")

    account_id = select_account(client)
    if not account_id:
        return

    try:
        chats, _ = client.list_chats(account_id, limit=20)

        if not chats:
            console.print("[yellow]No conversations found.[/yellow]")
        else:
            table = Table(box=box.ROUNDED, show_header=True)
            table.add_column("#", style="dim", width=3)
            table.add_column("Chat ID", style="cyan", no_wrap=True, max_width=20)
            table.add_column("Participants", max_width=30)
            table.add_column("Last Message", max_width=40)
            table.add_column("Unread", justify="center", width=6)

            for i, chat in enumerate(chats, 1):
                participants = ", ".join(
                    [a.name or "Unknown" for a in chat.attendees[:2]]
                )
                if len(chat.attendees) > 2:
                    participants += f" +{len(chat.attendees) - 2}"

                last_msg = chat.last_message_text or "-"
                if len(last_msg) > 37:
                    last_msg = last_msg[:37] + "..."

                unread = f"[red]{chat.unread_count}[/red]" if chat.unread_count else "-"

                table.add_row(
                    str(i),
                    chat.id[:18] + "..." if len(chat.id) > 20 else chat.id,
                    participants,
                    last_msg,
                    unread,
                )

            console.print(table)

    except UniPileError as e:
        show_error(str(e))

    pause()


def view_messages_menu(client: UniPileClient):
    """View messages in a specific chat."""
    show_header()
    console.print("[bold]View Messages[/bold]\n")

    # Get chat ID from user
    chat_id = questionary.text(
        "Enter Chat ID:",
        style=custom_style,
    ).ask()

    if not chat_id:
        return

    try:
        messages, _ = client.list_messages(chat_id, limit=20)

        if not messages:
            console.print("[yellow]No messages in this chat.[/yellow]")
        else:
            console.print(f"\n[bold]Messages (latest {len(messages)}):[/bold]\n")

            for msg in reversed(messages):  # Show oldest first
                sender = msg.sender_name or "Unknown"
                direction = "[bold cyan]You[/bold cyan]" if msg.is_sender else f"[bold]{sender}[/bold]"
                text = msg.text or "[attachment]"

                timestamp = ""
                if msg.timestamp:
                    timestamp = f"[dim]{msg.timestamp}[/dim] "

                console.print(f"{timestamp}{direction}: {text}")
                console.print()

    except UniPileError as e:
        show_error(str(e))

    pause()


def send_message_menu(client: UniPileClient):
    """Send a message to a chat."""
    show_header()
    console.print("[bold]Send Message[/bold]\n")

    # Get chat ID
    chat_id = questionary.text(
        "Enter Chat ID:",
        style=custom_style,
    ).ask()

    if not chat_id:
        return

    # Get message text
    message = questionary.text(
        "Enter message:",
        style=custom_style,
        multiline=False,
    ).ask()

    if not message:
        console.print("[yellow]Message cancelled.[/yellow]")
        pause()
        return

    # Confirm
    confirm = questionary.confirm(
        f"Send this message?\n\"{message[:50]}{'...' if len(message) > 50 else ''}\"",
        style=custom_style,
        default=False,
    ).ask()

    if not confirm:
        console.print("[yellow]Message cancelled.[/yellow]")
        pause()
        return

    try:
        result = client.send_message(chat_id, message)
        show_success(f"Message sent! ID: {result.id}")

    except UniPileError as e:
        show_error(str(e))

    pause()


def main_menu():
    """Main application loop."""
    try:
        Config.validate()
        client = UniPileClient()
    except ValueError as e:
        show_header()
        show_error(str(e))
        console.print("[dim]Edit .env file and try again.[/dim]")
        return

    while True:
        show_header()

        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "List Connected Accounts",
                "View Conversations",
                "View Messages",
                "Send Message",
                questionary.Separator(),
                "Exit",
            ],
            style=custom_style,
        ).ask()

        if choice is None or choice == "Exit":
            console.print("\n[cyan]Goodbye![/cyan]\n")
            break

        if choice == "List Connected Accounts":
            list_accounts_menu(client)
        elif choice == "View Conversations":
            view_conversations_menu(client)
        elif choice == "View Messages":
            view_messages_menu(client)
        elif choice == "Send Message":
            send_message_menu(client)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[cyan]Goodbye![/cyan]\n")
