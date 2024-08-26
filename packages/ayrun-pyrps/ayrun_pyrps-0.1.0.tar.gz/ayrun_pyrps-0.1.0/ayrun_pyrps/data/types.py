from typing import Literal, TypeAlias

GameChoice: TypeAlias = Literal["Rock", "Paper", "Scissors"]
GameResult: TypeAlias = Literal["User", "AI", "Tie"]
GameStat: TypeAlias = Literal["wins", "losses", "ties"]
