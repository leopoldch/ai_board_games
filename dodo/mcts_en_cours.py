from collections import deque
from functools import lru_cache
import numpy as np
from utils import (
    Cell,
    Player,
)

class MonteCarloNode:
    """Node for Monte Carlo Tree Search"""

    def __init__(self, available_actions: list[tuple[Cell, Cell]], player: Player, parent_node=None, action_from_parent=None):
        self.parent_node: MonteCarloNode = parent_node
        self.current_player: Player = player
        self.action_from_parent: tuple[Cell, Cell] = action_from_parent
        self.child_nodes: list[MonteCarloNode] = []
        self.visits: int = 0
        self.results: int = 0
        self.remaining_actions: set[tuple[Cell, Cell]] = set(available_actions)


    def get_results(self) -> int:
        """return results for the node"""
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
                new_child_node = MonteCarloNode(next_actions, 3 - self.current_player, parent_node=self, action_from_parent=action)
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
        actions_stack: deque = deque()
        while game.final():
            action: tuple[Cell, Cell] = game.strategy_random()
            if game.is_legit(action):
                actions_stack.append(action)
                game.make_move(action)

        simulation_result: int = game.score()
        while actions_stack:
            game.unmake_move(actions_stack.pop())
        return simulation_result

    def backpropagation(self, result: int):
        '''backpropagate result with recursion'''
        self.visits += 1
        if self.current_player == 1:
            self.results += 1 if result == 1 else -1
        else:
            self.results += 1 if result == -1 else -1
        if self.parent_node:
            self.parent_node.backpropagation(result)

    def fully_expanded(self) -> bool:
        """Check if node fully expanded"""
        return len(self.remaining_actions) == 0

    def select_best_child(self, exploration_param=sqrt(2)):
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

    def tree_policy(self, game):
        """Select a node to run a simulation from"""
        actions_stack: deque[tuple[Cell, Cell]] = deque()
        current_node: MonteCarloNode = self
        while current_node.is_terminal(game):
            if not current_node.fully_expanded():
                child = current_node.add_child(game)
                if child:
                    return child, actions_stack
            best_child = current_node.select_best_child()
            if best_child is None:
                break
            current_node = best_child
            actions_stack.append(current_node.action_from_parent)
            game.make_move(current_node.action_from_parent)
        return current_node, actions_stack

    def find_best_action(self, game, num_simulations=100000):
        """Find the best action by running simulations"""
        for _ in range(num_simulations):
            selected_node, actions_stack = self.tree_policy(game)
            simulation_result = selected_node.rollout(game)
            while actions_stack:
                game.unmake_move(actions_stack.pop())
            selected_node.backpropagation(simulation_result)
        best_child = self.select_best_child()
        return best_child.action_from_parent if best_child else None


def mcts(game):
    """stratégie MCTS"""
    legits = game.get_legits()
    if not legits:
        raise ValueError("No valid actions available at the start of MCTS")
    root_node = MonteCarloNode(legits, game.get_player())
    best_action = root_node.find_best_action(game)
    if best_action is None:
        raise ValueError("No valid actions found during MCTS")
    return best_action
