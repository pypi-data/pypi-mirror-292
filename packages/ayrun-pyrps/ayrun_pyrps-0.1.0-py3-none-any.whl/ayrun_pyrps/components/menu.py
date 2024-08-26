from typing import Literal

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy import get_style
from rich.console import Console

from ayrun_pyrps.components.gameplay import gameplay
from ayrun_pyrps.components.stats import display_stats, reset_stats

console = Console()
menu_style = get_style(
    {
        "question": "#FFFF00",  # yellow
        "answer": "#08e8de",  # bright cyan
        "answered_question": "#66ff00",  # bright green
        "pointer": "#08e8de",  # bright cyan
    }
)


def menu() -> None:
    console.clear()
    menu_prompt: Literal[1, 2, 3, 4] = inquirer.select(
        message="Select an option:",
        choices=[
            Choice(1, "Play"),
            Choice(2, "View Stats"),
            Choice(3, "Reset Stats"),
            Choice(4, "Exit"),
        ],
        default=None,
        raise_keyboard_interrupt=False,
        style=menu_style,
    ).execute()

    match menu_prompt:
        case 1:
            gameplay()

        case 2:
            display_stats()

        case 3:
            reset_stats()

        case 4:
            quit()
