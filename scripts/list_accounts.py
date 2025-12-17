#!/usr/bin/env python3
"""
List connected UniPile accounts.

Usage:
    python scripts/list_accounts.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich import box

from src.unipile_client import UniPileClient, UniPileError

console = Console()


def main():
    try:
        client = UniPileClient()
        accounts = client.list_accounts()

        if not accounts:
            console.print("[yellow]No accounts connected.[/yellow]")
            return

        table = Table(
            title="Connected Accounts",
            box=box.ROUNDED,
            show_header=True,
        )
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
        console.print(f"\n[dim]Total: {len(accounts)} account(s)[/dim]")

    except UniPileError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
