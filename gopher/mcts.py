import math
import random
from gopher import Gopher_Game
from utils import *

class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = state.get_legits().copy()

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, exploration_weight=1.4):
        choices_weights = [
            (child.wins / child.visits) + exploration_weight * math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]

class MCTS:
    def __init__(self, iterations=1000):
        self.iterations = iterations

    def search(self, initial_state):
        root = Node(initial_state)

        for _ in range(self.iterations):
            node = root
            state = initial_state.copy()

            # Selection
            while node.is_fully_expanded() and node.children:
                node = node.best_child()
                state.move(node.state.__played[-1])

            # Expansion
            if node.untried_moves:
                move = node.untried_moves.pop()
                state.move(move)
                new_node = Node(state.copy(), node)
                node.children.append(new_node)
                node = new_node

            # Simulation
            while not state.final():
                move = random.choice(state.get_legits())
                state.move(move)

            # Backpropagation
            result = state.score()
            while node is not None:
                node.visits += 1
                if state.get_player() == result:
                    node.wins += 1
                node = node.parent

        return max(root.children, key=lambda c: c.visits).state.__played[-1]

