from collections import deque
from functools import lru_cache
import numpy as np
from dodo.utils import (
    Cell,
    Player,
)

class MonteCarloNode:
    """Node for Monte Carlo Tree Search"""

    def __init__(self, available_actions: list[tuple[Cell, Cell]], player: Player, parent_node=None, parent_action=None):
        self.parent_node: MonteCarloNode = parent_node
        self.current_player: Player = player
        self.parent_action: tuple[Cell, Cell] = parent_action
        self.child_nodes: list[MonteCarloNode] = []
        self.visits: int = 0
        self.results: int = 0
        self.available_moves: set[tuple[Cell, Cell]] = set(available_actions)


    def get_results(self) -> int:
        """return results for the node"""
        return self.results

    def get_visits(self) -> int:
        """Get the number of times the node has been visited"""
        return self.visits

    def expand_node(self, game):
        """Add a new child node to the current node"""
        while self.available_moves:
            action: tuple[Cell, Cell] = self.available_moves.pop()
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

    @lru_cache(maxsize=None)
    def rollout(self, game) -> int:
        """Perform a simulation from the current node"""
        action_deque: deque = deque()
        while game.final():
            action: tuple[Cell, Cell] = game.strategy_random()
            if game.is_legit(action):
                action_deque.append(action)
                game.make_move(action)

        rollout_result: int = game.score()
        while action_deque:
            game.unmake_move(action_deque.pop())
        return rollout_result

    def backpropagation(self, result: int):
        '''backpropagate result with recursion'''
        self.visits += 1
        if self.current_player == 1:
            self.results += 1 if result == 1 else -1
        else:
            self.results += 1 if result == -1 else -1
        if self.parent_node:
            self.parent_node.backpropagation(result)

    def is_expanded(self) -> bool:
        """Check if node is fully expanded"""
        return len(self.available_moves) == 0

    def select_promising_child(self, exploration_param=np.sqrt(2)+1):
        """Promising child selection with UCT"""
        if not self.child_nodes:
            return None
        uct_scores = [
            (child.get_results() / child.get_visits()) + exploration_param * np.sqrt((np.log(self.get_visits()) / child.get_visits()))
            for child in self.child_nodes if child.get_visits() > 0
        ]
        if not uct_scores:
            return None
        return self.child_nodes[np.argmax(uct_scores)]

    def select_simulation_node(self, game):
        """Select a node to run a simulation from"""
        action_deque: deque[tuple[Cell, Cell]] = deque()
        current_node: MonteCarloNode = self
        while current_node.is_terminal(game):
            if not current_node.is_expanded():
                child = current_node.expand_node(game)
                if child:
                    return child, action_deque
            promising_child = current_node.select_promising_child()
            if promising_child is None:
                break
            current_node = promising_child
            action_deque.append(current_node.parent_action)
            game.make_move(current_node.parent_action)
        return current_node, action_deque

    def determine_optimal_action(self, game, num_simulations=100000):
        """Determine the optimal action by running simulations"""
        for _ in range(num_simulations):
            selected_node, action_deque = self.select_simulation_node(game)
            rollout_result = selected_node.rollout(game)
            while action_deque:
                game.unmake_move(action_deque.pop())
            selected_node.backpropagation(rollout_result)
        promising_child = self.select_promising_child()
        return promising_child.parent_action if promising_child else None


def mcts(game):
    """stratégie MCTS"""
    legits = game.get_legits()
    if not legits:
        raise ValueError("No valid actions available at the start of MCTS")
    root_node = MonteCarloNode(legits, game.get_player())
    optimal_action = root_node.determine_optimal_action(game)
    if optimal_action is None:
        raise ValueError("No valid actions found during MCTS")
    return optimal_action
