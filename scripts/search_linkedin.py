#!/usr/bin/env python3
"""
Search for people on LinkedIn and get their user IDs.

Usage:
    python scripts/search_linkedin.py "John Doe" [--account-id ACCOUNT_ID]
    python scripts/search_linkedin.py "Product Manager Prague" --limit 20
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
    parser = argparse.ArgumentParser(
        description="Search for people on LinkedIn",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search by name
  python scripts/search_linkedin.py "Jakub Krakovsky"

  # Search by name and company
  python scripts/search_linkedin.py "Product Manager LMC"

  # Get more results
  python scripts/search_linkedin.py "John Doe" --limit 20
        """
    )
    parser.add_argument(
        "keywords",
        help="Search keywords (person's name, title, company)",
    )
    parser.add_argument(
        "--account-id", "-a",
        help="UniPile account ID (if not provided, uses first account)",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=10,
        help="Max results to show (default: 10)",
    )
    parser.add_argument(
        "--api",
        choices=["classic", "sales_navigator", "recruiter"],
        default="classic",
        help="LinkedIn interface to use (default: classic)",
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

        # Perform search
        console.print(f"[dim]Searching for: {args.keywords}...[/dim]\n")
        results, cursor = client.search_linkedin(
            account_id=args.account_id,
            keywords=args.keywords,
            api=args.api,
            limit=args.limit,
        )

        if not results:
            console.print(f"[yellow]No results found for '{args.keywords}'[/yellow]")
            return

        # Display results
        table = Table(
            title=f"LinkedIn Search: {args.keywords}",
            box=box.ROUNDED,
            show_header=True,
        )
        table.add_column("#", style="dim", width=3)
        table.add_column("Name", style="cyan", max_width=30)
        table.add_column("Headline", max_width=40)
        table.add_column("Location", max_width=20)
        table.add_column("User ID", style="green", no_wrap=True)

        for i, person in enumerate(results, 1):
            # Extract person data
            name = f"{person.get('first_name', '')} {person.get('last_name', '')}".strip()
            if not name:
                name = person.get("name", "Unknown")

            headline = person.get("headline", "-")
            if len(headline) > 37:
                headline = headline[:37] + "..."

            location = person.get("location", "-")
            if len(location) > 17:
                location = location[:17] + "..."

            # Get user ID (provider_id)
            user_id = person.get("id", person.get("member_urn", "-"))

            table.add_row(
                str(i),
                name,
                headline,
                location,
                user_id,
            )

        console.print(table)
        console.print(f"\n[dim]Total: {len(results)} result(s)[/dim]")

        if cursor:
            console.print(f"[dim]More results available (use cursor for pagination)[/dim]")

        # Show usage hint
        console.print("\n[cyan]💡 Tip:[/cyan] Use the User ID to send messages:")
        if results:
            first_id = results[0].get("id", results[0].get("member_urn"))
            console.print(f"[dim]   python scripts/send_message.py --chat-id CHAT_ID --message \"Hello\"[/dim]")
            console.print(f"[dim]   (Start chat with User ID: {first_id})[/dim]")

    except UniPileError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
