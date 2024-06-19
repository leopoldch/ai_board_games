    
# A mettre dans dodo_game pour test
def heuristic_evaluation(self, action: Action) -> int:
        """Heuristic evaluation function for the game state."""
        # Evaluate the game state after making the move
        player = self.get_player()
        opponent = 3 - player
        #player_moves = len(self.get_legits())
        self.make_move(action)
        player_moves = len(self.get_legits())
        positions_importantes = [(0, 0), (-1, 0), (0, -1), (1, 0), (0, 1), (1, 1), (-1, -1),
                                 (-1, 1), (1, -1), (-2, 1), (1, -2), (2, -1), (-1, 2)]
        center = 0
        for cell, occupant in self.__grid.items():
            if occupant == player:
                if cell in positions_importantes:
                    center += 1
        race_turn = - self.race_turns_left(player)
        #print("center", center)
        #print("race_turn", race_turn)
        #print("player_moves", player_moves)




        self.set_player(opponent)
        #opponent_moves = len(self.get_legits())
        self.unmake_move(action)
        self.set_player(3 - opponent)
        if center != 0 and player_moves != 0:
            return -np.log(player_moves) + 5 * race_turn + 5 * np.log(center)
        return -player_moves + 5 * race_turn + center


#MCTS avec tri par l'heuristique

from functools import lru_cache
import numpy as np
from utils import (
    Cell,
    Player,
)

class MonteCarloNode:
    """Node for Monte Carlo Tree Search"""

    def __init__(self, available_actions: list[tuple[Cell, Cell]], player: Player, parent_node=None, parent_action=None):
        self.current_player: Player = player
        self.parent_node: MonteCarloNode = parent_node
        self.parent_action: tuple[Cell, Cell] = parent_action
        self.child_nodes: list[MonteCarloNode] = []
        self.visits: int = 0
        self.results: int = 0
        self.remaining_actions: set[tuple[Cell, Cell]] = set(available_actions)

    def get_results(self) -> int:
        """Return results for the node"""
        return self.results

    def get_visits(self) -> int:
        """Get the number of times the node has been visited"""
        return self.visits

    def add_child(self, game):
        """Add a new child node to the current node"""
        while self.remaining_actions:
            action: tuple[Cell, Cell] = self.remaining_actions.pop()
            if game.is_legit(action):
                game.make_move(action)
                next_actions: list[tuple[Cell, Cell]] = game.get_legits()
                new_child_node = MonteCarloNode(next_actions, 3 - self.current_player, parent_node=self, parent_action=action)
                game.unmake_move(action)
                self.child_nodes.append(new_child_node)
                return new_child_node
        return None

    def is_terminal(self, game) -> bool:
        """Check if the node represents a terminal state"""
        return game.final()

    def heuristic_evaluation(self, game, action) -> int:
        """Evaluate the game state using a heuristic"""
        #nbr_visits: int = self.visits
        return game.heuristic_evaluation(action)

    @lru_cache(maxsize=None)
    def rollout(self, game) -> int:
        """Perform a simulation from the current node using a heuristic"""
        move_stack: list = []
        while game.final():
            legal_actions = [action for action in game.get_legits() if game.is_legit(action)]
            if not legal_actions:
                break
            # Sort actions based on heuristic evaluation
            legal_actions.sort(key=lambda action: self.heuristic_evaluation(game, action), reverse=True)
            # Choose the best action according to the heuristic evaluation
            action = legal_actions[0]
            move_stack.append(action)
            game.make_move(action)

        simulation_result: int = game.score()
        while move_stack:
            game.unmake_move(move_stack.pop())
        return simulation_result



    def backpropagation(self, result: int):
        '''Backpropagate result with recursion'''
        self.visits += 1
        if self.current_player == 1:
            self.results += 1 if result == 1 else -1
        else:
            self.results += 1 if result == -1 else -1
        if self.parent_node:
            self.parent_node.backpropagation(result)

    def is_expanded(self) -> bool:
        """Check if node fully expanded"""
        return len(self.remaining_actions) == 0

    def select_best_child(self, exploration_param= np.sqrt(2)):
        """Best child selection with UCT"""
        if not self.child_nodes:
            return None
        uct_values = [
            (child.get_results() / child.get_visits()) + exploration_param * np.sqrt((np.log(self.get_visits()) / child.get_visits()))
            for child in self.child_nodes if child.get_visits() > 0
        ]
        if not uct_values:
            return None
        return self.child_nodes[np.argmax(uct_values)]

    def select_simulation_node(self, game):
        """Select a node to run a simulation from"""
        move_stack: list[tuple[Cell, Cell]] = []
        current_node: MonteCarloNode = self
        while current_node.is_terminal(game):
            if not current_node.is_expanded():
                child = current_node.add_child(game)
                if child:
                    return child, move_stack
            best_child = current_node.select_best_child()
            if best_child is None:
                break
            current_node = best_child
            move_stack.append(current_node.parent_action)
            game.make_move(current_node.parent_action)
        return current_node, move_stack

    def determine_best_action(self, game, num_simulations=100000):
        """Find the best action by running simulations"""
        for _ in range(num_simulations):
            selected_node, move_stack = self.select_simulation_node(game)
            simulation_result = selected_node.rollout(game)
            while move_stack:
                game.unmake_move(move_stack.pop())
            selected_node.backpropagation(simulation_result)
        best_child = self.select_best_child()
        return best_child.parent_action if best_child else None


def mcts(game):
    """Stratégie MCTS"""
    legits = game.get_legits()
    if not legits:
        raise ValueError("No valid actions available at the start of MCTS")
    root_node = MonteCarloNode(legits, game.get_player())
    best_action = root_node.determine_best_action(game)
    if best_action is None:
        raise ValueError("No valid actions found during MCTS")
    return best_action
