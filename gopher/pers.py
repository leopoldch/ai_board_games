import math
import random
from collections import defaultdict

class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_actions = self.state.get_legits()

    def add_child(self, child_state):
        child_node = Node(child_state, parent=self)
        self.children.append(child_node)
        self.untried_actions.remove(child_state.__played[-1])
        return child_node

    def update(self, result):
        self.visits += 1
        self.wins += result

    def fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self, exploration_weight=1.41):
        choices_weights = [
            (child.wins / child.visits) + exploration_weight * math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]

def mcts(game, iterations=1000):
    root = Node(game.copy())

    for _ in range(iterations):
        node = root
        game_state = game.copy()

        # Selection
        while node.fully_expanded() and node.children:
            node = node.best_child()
            game_state.move(node.state.__played[-1])

        # Expansion
        if node.untried_actions:
            move = random.choice(node.untried_actions)
            game_state.move(move)
            node = node.add_child(game_state.copy())

        # Simulation
        while not game_state.final():
            move = random.choice(game_state.get_legits())
            game_state.move(move)

        # Backpropagation
        result = game_state.score()
        while node:
            node.update(result)
            node = node.parent

    return root.best_child(0).state.__played[-1]