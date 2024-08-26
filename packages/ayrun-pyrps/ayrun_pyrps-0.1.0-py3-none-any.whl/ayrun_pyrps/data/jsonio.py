import json
import os

from ayrun_pyrps.data.types import GameStat


class JsonIO:
    path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

    def __init__(self) -> None:
        self.data = self._load_json()

    def _load_json(self):
        """Private method to load JSON data from the file."""
        if os.path.exists(self.path):
            with open(self.path, "r") as file:
                try:
                    return json.load(file)

                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON Format.")

        else:
            return {}

    def get(self, key: GameStat) -> int:
        """Retrieve a value from the JSON data."""
        return self.data[key]

    def _save(self):
        """Private Method to save the current data to the JSON file."""
        with open(self.path, "w") as file:
            json.dump(self.data, file, indent=4)

    def reset(self):
        """Reset all the keys back to zero."""
        self.data = {"wins": 0, "losses": 0, "ties": 0}
        self._save()

    def update_wins(self):
        """Increment the value of `wins` key by 1."""
        self.data["wins"] += 1
        self._save()

    def update_losses(self):
        """Increment the value of `losses` key by 1."""
        self.data["losses"] += 1
        self._save()

    def update_ties(self):
        """Increment the value of `ties` key by 1."""
        self.data["ties"] += 1
        self._save()