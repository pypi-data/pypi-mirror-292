import time

from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel

from ayrun_pyrps.components.gameplay import json_io

console = Console()


def display_stats():
    with console.status("📝 Loading stats..."):
        wins: int = json_io.get("wins")
        losses: int = json_io.get("losses")
        ties: int = json_io.get("ties")
        matches_played: int = wins + losses + ties
        time.sleep(1)

        console.print(
            Padding(
                Panel.fit(
                    f":trophy: Wins: [green]{wins}[/green]\n:x: Losses: [red]{losses}[/red]\n:handshake: Ties: [yellow]{ties}[/yellow]\n:video_game: Matches Played: [cyan]{matches_played}[/cyan]\n\nPress any key to continue...",
                    title=":bar_chart: Your Stats",
                    padding=1,
                    border_style="magenta",
                ),
                1,
            )
        )

    input()


def reset_stats():
    with console.status("🗑️ Please wait..."):
        json_io.reset()
        time.sleep(1)
        console.print(
            Padding(
                Panel.fit(
                    "[bold green]Your game stats have been successfully reset![/bold green]\n\nPress any key to continue...",
                    title="Done!",
                    border_style="magenta",
                    padding=1,
                ),
                1,
            )
        )

    input()
