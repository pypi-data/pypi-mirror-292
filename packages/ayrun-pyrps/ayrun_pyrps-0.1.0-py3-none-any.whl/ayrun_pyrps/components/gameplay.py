import random
import time
from typing import Dict, Tuple

from InquirerPy import inquirer
from InquirerPy import get_style
from InquirerPy.base.control import Choice
from rich.console import Console
from rich.panel import Panel
from rich.padding import Padding

from ayrun_pyrps.data.jsonio import JsonIO
from ayrun_pyrps.data.types import GameChoice, GameResult

json_io = JsonIO()
console = Console()
game_style = get_style(
    {
        "question": "#FFFF00",  # yellow
        "answer": "#08e8de",  # bright cyan
        "answered_question": "#66ff00",  # bright green
        "pointer": "#08e8de",  # bright cyan
    }
)


def determine_winner(user_choice: GameChoice, ai_choice: GameChoice) -> GameResult:
    outcomes: Dict[Tuple[GameChoice, GameChoice], GameResult] = {
        ("Rock", "Rock"): "Tie",
        ("Rock", "Paper"): "AI",
        ("Rock", "Scissors"): "User",
        ("Paper", "Rock"): "User",
        ("Paper", "Paper"): "Tie",
        ("Paper", "Scissors"): "AI",
        ("Scissors", "Rock"): "AI",
        ("Scissors", "Paper"): "User",
        ("Scissors", "Scissors"): "Tie",
    }

    return outcomes[(user_choice, ai_choice)]


def gameplay():
    user_choice: GameChoice = inquirer.select(
        message="Rock, Paper or Scissors:",
        choices=[
            Choice("Rock", "🪨 Rock"),
            Choice("Paper", "📰 Paper"),
            Choice("Scissors", "✂️ Scissors"),
        ],
        default=None,
        raise_keyboard_interrupt=False,
        style=game_style,
    ).execute()

    ai_choice: GameChoice = random.choice(["Rock", "Paper", "Scissors"])

    result: GameResult = determine_winner(user_choice, ai_choice)

    match result:
        case "User":
            json_io.update_wins()
            content = "[bright_green]You Won![/bright_green]"

        case "AI":
            json_io.update_losses()
            content = "[bright_red]You Lost![/bright_red]"

        case "Tie":
            json_io.update_ties()
            content = "[yellow]It's a Tie![/yellow]"

    with console.status("🤖 AI is thinking..."):
        time.sleep(1)
        console.print(
            Padding(
                Panel.fit(
                    f"You chose: [magenta]{user_choice}[/magenta]\nAI chose: [magenta]{ai_choice}[/magenta]\nResult: {content}\n\nPress any key to continue...",
                    title="Result",
                    padding=1,
                    border_style="magenta",
                ),
                1,
            )
        )

    input()
