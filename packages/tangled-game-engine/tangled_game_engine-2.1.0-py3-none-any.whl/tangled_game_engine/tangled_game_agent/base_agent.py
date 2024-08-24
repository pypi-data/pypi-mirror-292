"""
Base class for game agents.
Create a subclass of this class to implement a game agent.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple
from ..tangled_game.game import Game

class GameAgentBase(ABC):
    """
    Base class for game agents.
    Create a subclass of this class to implement a game agent.
    """

    player_id: str

    def __init__(self, player_id: str):
        """
        Initializes the game agent with the player id.
        This id must either match an id of the player in a game, or the game must allow all players.
        
        Args:
            player_id (str): The player id for this agent.
        """
        self.player_id = player_id

    def id(self) -> str:
        return self.player_id

    @abstractmethod
    def make_move(self, game: Game) -> Tuple[int, int, int]:
        """
        Have the agent make a move in the game. This method should be implemented by a subclass.
        This will be called each time it is the agent's turn to make a move.
        The move must be a valid move for the game and the agent.

        Args:
            game (Game): The game object to make a move in. Use this to get valid moves and the current state of the game.

        Returns:
            Tuple[int, int, int]: A tuple of the move type (see Game.MoveType), move index (vertex or edge), and move state (see Vertex.State and Edge.State).
        """
        pass


__all__ = ["GameAgentBase"]