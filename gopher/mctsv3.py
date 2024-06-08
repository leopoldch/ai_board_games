import random
import math
from collections import defaultdict

class MCTSNode:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0

    def is_fully_expanded(self):
        return len(self.children) == len(self.state.get_legits())

    def best_child(self, c_param=1.4):
        choices_weights = [
            (child.wins / child.visits) + c_param * math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]

    def most_visited_child(self):
        visits = [child.visits for child in self.children]
        return self.children[visits.index(max(visits))]

def mcts(root, n_iter=1000):
    root_node = MCTSNode(root)
    for _ in range(n_iter):
        node = tree_policy(root_node)
        reward = default_policy(node.state)
        backup(node, reward)
    if not root_node.children:
        print('eheh')
        return random.choice(root_node.state.get_legits())  # Return a random legal move if no children exist
    print('ahah')
    return root_node.best_child(c_param=0)

def tree_policy(node):
    while not node.state.final():
        if not node.is_fully_expanded():
            return expand(node)
        else:
            node = node.best_child()
    return node

def expand(node):
    tried_children = [child.state.get_grid() for child in node.children]
    for move in node.state.get_legits():
        new_state = node.state.copy()
        new_state.move(move)
        if new_state.get_grid() not in tried_children:
            child_node = MCTSNode(new_state, parent=node)
            node.children.append(child_node)
            return child_node
    raise Exception("Should not reach here")

def default_policy(state):
    current_state = state.copy()
    while not current_state.final():
        move = random.choice(current_state.get_legits())
        current_state.move(move)
    return current_state.score()

def backup(node, reward):
    while node is not None:
        node.visits += 1
        node.wins += reward
        node = node.parent

def mcts_strategy(game):
    root = MCTSNode(game)
    best_child = mcts(root, n_iter=1000)
    return best_child.state.get_legits()[0] if best_child.children else random.choice(game.get_legits())