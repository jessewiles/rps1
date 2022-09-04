import os
import random

from datetime import datetime, timezone
from getpass import getpass
from typing import Optional, Tuple, Type


class Player:
    """Data class for game players"""

    def __init__(self, name: str):
        self._name = name
        self.score = 0
        self.choice = None
        self.is_cpu = name is None

    @property
    def name(self) -> str:
        if self.is_cpu:
            return "CPU"
        elif self._name == "CPU":
            return "CPU (real player)"
        else:
            return self._name


class GameData:
    """Data class for the game details"""

    def __init__(self, player1: str, player2: Optional[str]):
        self.player1 = Player(player1)
        self.player2 = Player(player2)

    @property
    def score_tuple(self) -> Tuple[str]:
        """Convenience property for use in string formatting"""
        return (
            self.player1.name,
            self.player1.score,
            self.player2.name,
            self.player2.score,
        )


class BaseState:
    """Game state base class"""

    def __init__(self, game_data: Optional[GameData] = None):
        self.game_data = game_data

    def advance(self) -> Optional[Type["BaseState"]]:
        raise NotImplementedError()


class ViewOldGameState(BaseState):
    """Game state related to viewing old scores"""

    no_scores_message = """
No old game scores were found.
"""
    game_score_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "scores.txt"
    )

    def advance(self) -> Optional[Type[BaseState]]:
        if os.path.exists(self.game_score_file):
            with open(self.game_score_file, "r") as reader:
                print(reader.read())
        else:
            print(self.no_scores_message)
        return StartState()


class QuitGameState(BaseState):
    """Game state related to quitting the game"""

    message = "Bye."

    def advance(self) -> Optional[Type[BaseState]]:
        print(self.message)
        return None


class SaveGameState(BaseState):
    """Game state related to saving the game"""

    game_score_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "scores.txt"
    )
    message = """
Would you like to save this game? (y\\n)
>>> """
    dt_stamp = datetime.now(timezone.utc).astimezone().isoformat()

    def advance(self) -> Optional[Type[BaseState]]:
        save_game = input(self.message)
        while save_game.lower() not in (
            "y",
            "n",
        ):
            print(f"Invalid response: {save_game}")
            save_game = input(self.message)
        if save_game == "y":
            with open(self.game_score_file, "a") as writer:
                writer.write(
                    """
------ %s ------
"""
                    % self.dt_stamp
                )
                writer.write(
                    """
SCORE:
    %s: %s
    %s: %s
"""
                    % self.game_data.score_tuple
                )
        return QuitGameState(self.game_data)


class PlayGameState(BaseState):
    """Game state related to playing the game, or gathering user input."""

    message1 = """
%s, enter one of the following:
1) rock
2) paper
3) scissors
>>> """

    def __init__(self, game_data):
        self.game_data = game_data

    def _get_valid_choice(self, player) -> None:
        if player.is_cpu:
            player.choice = str(random.randint(1, 3))
        else:
            player.choice = getpass(self.message1 % player.name)
            while player.choice not in (
                "1",
                "2",
                "3",
            ):
                print(f"Invalid choice: {player.choice}")
                player.choice = getpass(self.message1 % player.name)

    def advance(self) -> Optional[Type[BaseState]]:
        self._get_valid_choice(self.game_data.player1)
        self._get_valid_choice(self.game_data.player2)
        return CalculateResult(self.game_data)


class NewGameState(BaseState):
    """
    Game state related to settting up a new game. Advaning from this state results in a
    new GateData object.
    """

    player1 = None
    player2 = None
    message1 = """\
Enter a name for player 1: """
    message2 = """\
Enter a name for player 2 or press Enter to play against the computer: """

    def advance(self) -> Optional[Type[BaseState]]:
        while self.player1 is None:
            self.player1 = input(self.message1)

        self.player2 = input(self.message2) or None

        return PlayGameState(GameData(self.player1, self.player2))


class CalculateResult(BaseState):
    """Game state related to calculating the result of gathering user input."""

    next_state = {
        "1": NewGameState,
        "2": PlayGameState,
        "3": SaveGameState,
    }

    choice_map = {
        "1": "rock",
        "2": "paper",
        "3": "scissors",
    }
    message1 = """
Both players selected: %s. Try again.
"""
    message2 = """
SCORE:
    %s: %s
    %s: %s
"""
    message3 = """
What would you like to do now?
1) Start a new game.
2) Play this game again.
3) Quit.
>>> """

    def __init__(self, game_data):
        self.game_data = game_data

        self.p1_name = self.game_data.player1.name
        self.p1_choice = self.game_data.player1.choice

        self.p2_name = self.game_data.player2.name
        self.p2_choice = self.game_data.player2.choice

    def advance(self) -> Optional[Type[BaseState]]:
        if self.game_data.player1.choice == self.game_data.player2.choice:
            print(self.message1 % self.choice_map[self.game_data.player1.choice])
            return PlayGameState(self.game_data)

        results_key = f"{self.p1_choice}:{self.p2_choice}"
        if results_key == "1:2":
            self.game_data.player2.score += 1
            print(f"paper beats rock. {self.p2_name} wins!")
        elif results_key == "1:3":
            self.game_data.player1.score += 1
            print(f"rock beats scissors. {self.p1_name} wins!")
        elif results_key == "2:1":
            self.game_data.player1.score += 1
            print(f"paper beats rock. {self.p1_name} wins!")
        elif results_key == "2:3":
            self.game_data.player2.score += 1
            print(f"scissors beats paper. {self.p2_name} wins!")
        elif results_key == "3:1":
            self.game_data.player2.score += 1
            print(f"rock beats scissors. {self.p2_name} wins!")
        elif results_key == "3:2":
            self.game_data.player1.score += 1
            print(f"scissors beats paper. {self.p1_name} wins!")

        print(
            self.message2
            % (
                self.p1_name,
                self.game_data.player1.score,
                self.p2_name,
                self.game_data.player2.score,
            )
        )
        next_thing = input(self.message3)
        while next_thing not in (
            "1",
            "2",
            "3",
        ):
            print("Invalid choice: {next_thing}")
            next_thing = input(self.message3)

        return self.next_state[next_thing](self.game_data)


class StartState(BaseState):
    """Game state related to game initialization."""

    next_state = {
        "1": NewGameState,
        "2": ViewOldGameState,
        "3": QuitGameState,
    }
    message = """
Welcome to Rock, Paper, Scissors! What would you like to do?
1) Start a new game.
2) View old games.
3) Quit.

>>> """
    answer = None

    def advance(self) -> Optional[Type[BaseState]]:
        while self.answer not in (
            "1",
            "2",
            "3",
        ):
            self.answer = input(self.message)
        return self.next_state[self.answer]()


def main():
    """
    The main game loop. A starting state instance is created. Then game state is reassigned via
    each instance's `advance` method until a `None` is returned.
    """
    game = StartState()
    while game:
        game = game.advance()


if __name__ == "__main__":
    main()
