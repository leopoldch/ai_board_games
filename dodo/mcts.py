from collections import defaultdict, deque
import numpy as np
from dodo.utils import (
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
        self.visits_count: int = 0
        self.results: defaultdict[int] = defaultdict(int)
        self.wins_count: int = 0
        self.loses_count: int = 0
        self.remaining_actions: list[tuple[Cell, Cell]] = available_actions.copy()

    def get_q_value(self) -> int:
        """Calculate Q-value (wins - loses) for the node"""
        return self.wins_count - self.loses_count

    def get_visits(self) -> int:
        """Get the number of times the node has been visited"""
        return self.visits_count

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

    def simulate(self, game) -> int:
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

    def update_with_result(self, result: int):
        """Backpropagate the simulation result up the tree"""
        self.visits_count += 1
        if self.current_player == 2:  
            if result == -1:
                self.wins_count += 1
            else:
                self.loses_count += 1
        else:
            if result == 1:
                self.wins_count += 1
            else:
                self.loses_count += 1
        if self.parent_node:
            self.parent_node.update_with_result(result)

    def fully_expanded(self) -> bool:
        """Check if all possible actions have been expanded"""
        return len(self.remaining_actions) == 0

    def select_best_child(self, exploration_param=np.sqrt(2)):
        """Select the best child node based on the UCT value"""
        if not self.child_nodes:
            return None
        uct_values = [
            (child.get_q_value() / child.get_visits()) + exploration_param * np.sqrt((np.log(self.get_visits()) / child.get_visits()))
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
            simulation_result = selected_node.simulate(game)
            while actions_stack:
                game.unmake_move(actions_stack.pop())
            selected_node.update_with_result(simulation_result)
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
