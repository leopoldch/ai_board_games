import math
import random
from typing import List, Optional

class Node:
    def __init__(self, game, parent: Optional['Node'] = None, action: Optional['Action'] = None) -> None:
        self.game = game
        self.parent: Node = parent
        self.action: Action = action
        self.children: List['Node'] = []
        self.visits: int = 0
        self.wins: float = 0.0

    def add_child(self, child: 'Node') -> None:
        self.children.append(child)

    def update(self, result: float):
        self.visits += 1
        self.wins += result

    def ucb1(self) -> float:
        coeff_value: float = 3
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + coeff_value * (math.sqrt(2 * math.log(self.parent.visits) / self.visits))

class MCTS:
    def __init__(self, root_game) -> None:
        self.root = Node(root_game)
        self.simulation_results = {}

    def selection(self, node: Node) -> Node:
        while node.children:
            node = max(node.children, key=lambda child: child.ucb1())
        return node

    def expansion(self, node: Node) -> None:
        game = node.game
        legal_moves = game.get_legits()
        for move in legal_moves:
            tmp = game.save_state()
            game.move(move)
            game.set_player(3 - game.get_player())
            child = Node(game, parent=node, action=move)
            node.add_child(child)
            game.restore_state(tmp)

    def negamax(self, game, depth: int, alpha: float, beta: float, player: int) -> float:
        if depth == 0 or game.final():
            return self.evaluate_negamax(game, player)

        max_eval = float("-inf")
        legal_moves = game.get_legits()
        original_grid = game.save_state()

        for move in legal_moves:
            game.move(move)
            game.set_player(3 - game.get_player())
            eval = -self.negamax(game, depth - 1, -beta, -alpha, 3 - player)
            game.restore_state(original_grid)
            game.set_player(player)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if alpha >= beta:
                break

        return max_eval

    def evaluate_negamax(self, game, player: int) -> float:
        """Fonction d'évaluation pour le Négamax."""
        return game.score() if game.get_player() == player else -game.score()

    def simulation(self, game) -> float:
        state = game.save_state()
        state_key = self.get_state_key(state)

        if state_key in self.simulation_results:
            return self.simulation_results[state_key]

        depth = 4  
        result = self.negamax(game, depth=depth, alpha=-float('inf'), beta=float('inf'), player=game.get_player())
        game.restore_state(state)

        self.simulation_results[state_key] = result
        return result

    def backpropagation(self, node: Node, result: float) -> None:
        while node:
            node.update(result)
            node = node.parent

    def search(self, iterations: int) -> 'Action':
        for _ in range(iterations):
            node = self.selection(self.root)
            if node.game.final():
                self.expansion(node)
            else:
                if not node.children:
                    self.expansion(node)
                result = self.simulation(node.game)
                self.backpropagation(node, result)

        if self.root.children:
            best_child = max(self.root.children, key=lambda child: child.wins / child.visits if child.visits != 0 else float('-inf'))
            return best_child.action
        else:
            raise ValueError("No children found after MCTS iterations. The game might be already won/lost or no legal moves are available.")

    def get_state_key(self, state) -> str:
        """Generate a unique key for the game state."""
        return str(state)  

def mcts(game) -> 'Action':
    mcts_search = MCTS(game)
    return mcts_search.search(1000)
