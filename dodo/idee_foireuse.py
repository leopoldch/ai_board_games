import copy
import math
import random
import time
import numpy as np
from typing import Union


from dodo import create_board, init_board, legit_moves, move, final, score, evaluate,evaluation, print_board

Environment = dict
Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]  # case de départ -> case d'arrivée
Action = Union[ActionGopher, ActionDodo]
Player = int  # 1 ou 2
State = list[tuple[Cell, Player]]  # État du jeu pour la boucle de jeu
Score = int
Time = int
Grid = dict[Cell:Player]

# Cache for possible actions
possible_actions_cache = {}

# Tree node class definition
class TreeNode:
    def __init__(self, state, player, parent=None):
        self.state = state
        self.parent = parent
        self.visits = 0
        self.score = 0
        self.children = {}
        self.player = player
        self.possibles_actions = self.get_possible_actions(state, player)

    def get_possible_actions(self, state, player):
        state_hash = hash(tuple(state))
        if (state_hash, player) in possible_actions_cache:
            return possible_actions_cache[(state_hash, player)]
        else:
            actions = legit_moves(state, player)
            possible_actions_cache[(state_hash, player)] = actions
            return actions

    def is_expanded(self):
        return len(self.possibles_actions) == 0

    def expand(self):
        if len(self.possibles_actions) == 0:
            self.possibles_actions = legit_moves(self.state,self.player)
            #print("coup legit depuis expand",legit_moves(self.state,self.player))
            #print("liste coup possible depuis expand",self.possibles_actions)
        action = self.possibles_actions.pop()
        possible_state = move(self.state, action, self.player)
        child = TreeNode(possible_state, 3 - self.player, self)
        self.children[action] = child
        return child

    def best_child(self, exploration_param=1.4):
        best_score = -float('inf')
        best_children = []
        self.expand()
        for action, child in self.children.items():
            if child.visits == 0:
                #print_board(child.state)
                child.possibles_actions = legit_moves(child.state,child.player)
                #child.expand()
                return child # handle unvisited child nodes

            else:
                score = (child.score / child.visits) + exploration_param * np.sqrt(np.log(self.visits) / child.visits)
            if score > best_score:
                best_score = score
                best_children = [child]
            elif score == best_score:
                best_children.append(child)
        if best_children:
            return random.choice(best_children)
        return self


    def backpropagation(self, score):
        self.visits += 1
        self.score += score
        if self.parent:
            self.parent.backpropagation(-score)

    def rollout(self, current_player):
        return evaluation(self.state, current_player)

    def select(self):
        current_node = self
        #print(current_node,type(current_node))
        #print(current_node.score)
        #print(current_node.visits)
        #print(current_node.state)
        current_node.possibles_actions = current_node.get_possible_actions(current_node.state, current_node.player)
        while not final(current_node.state):
            if current_node.is_expanded():
                #print("hummm")
                if current_node.visits == 0:
                    if len(current_node.possibles_actions) == 0:
                        current_node.possibles_actions = current_node.get_possible_actions(current_node.state, current_node.player)
                        #print("none type is really none", type(current_node))
                        #print("liste coup possible",current_node.possibles_actions)
                        # current_node.expand()
                    current_node.expand() #ptet a enlever
                    #return current_node.expand()
                    return current_node
                current_node = current_node.best_child()
                #print("type from select",type(current_node))
                #print("current_node from select",current_node.state)
                current_node.possibles_actions = current_node.get_possible_actions(current_node.state, current_node.player)
            else:
                return current_node.expand()
        return current_node

# MCTS class definition
class MCTS:
    def __init__(self, root):
        self.root = root

    def search(self, iterations):
        for _ in range(iterations):
            node = self.root.select()
            rollout_score = node.rollout(node.player)
            node.backpropagation(rollout_score)

        return self.root.best_child(0)  # only best, no exploration

def mcts(state, iterations, player):
    root = TreeNode(state, player)
    mcts = MCTS(root)
    best_child_node = mcts.search(iterations)
    for action, child in root.children.items():
        if child == best_child_node:
            return action

from concurrent.futures import ThreadPoolExecutor

# Memoization cache
memo = {}


def minimax_alpha_beta(state: State, depth: int, alpha: float, beta: float, maximizing_player: bool, player: Player) -> float:
    # Convert the state to a tuple to make it hashable for memoization
    state_tuple = tuple(state)

    if (state_tuple, depth, maximizing_player) in memo:
        return memo[(state_tuple, depth, maximizing_player)]

    if depth == 0 or final(state):
        return evaluation(state, player)

    if maximizing_player:
        max_eval = -float('inf')
        for action in legit_moves(state, player):
            new_state = move(state, action, player)
            eval = minimax_alpha_beta(new_state, depth - 1, alpha, beta, False, player)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        memo[(state_tuple, depth, maximizing_player)] = max_eval
        return max_eval
    else:
        min_eval = float('inf')
        opponent = 3 - player
        for action in legit_moves(state, opponent):
            new_state = move(state, action, opponent)
            eval = minimax_alpha_beta(new_state, depth - 1, alpha, beta, True, player)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        memo[(state_tuple, depth, maximizing_player)] = min_eval
        return min_eval


def best_move(state: State, player: Player, depth: int) -> Action:
    best_val = -float('inf')
    best_action = None
    alpha = -float('inf')
    beta = float('inf')

    moves = legit_moves(state, player)

    with ThreadPoolExecutor() as executor:
        futures = []
        for action in moves:
            new_state = move(state, action, player)
            futures.append(executor.submit(minimax_alpha_beta, new_state, depth - 1, alpha, beta, False, player))

        for i, future in enumerate(futures):
            move_val = future.result()
            if move_val > best_val:
                best_val = move_val
                best_action = moves[i]
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break

    return best_action


def strategy(env: Environment, state: State, player: Player, time_left: Time) -> tuple[Environment, Action]:
    depth = 2  # Depth can be adjusted based on available time and complexity
    best_action = best_move(state, player, depth)
    return (env, best_action)

def test(iterations: int, size: int):
    tps1 = time.time()
    stats1 = 0
    stats2 = 0
    for _ in range(iterations):
        current_player = 1
        board = create_board(size)
        state = init_board(board)
        while not final(state):
            if current_player == 2:
                play = mcts(state, 30, current_player)
                #print("action:",play)
            else:
                play = random_strat(state, current_player)
                #play = strategy({}, state, current_player, 0)[1]
            state = move(state, play, current_player)
            current_player = 3 - current_player

        if score(state, 1) == 1:
            stats1 += 1
        elif score(state, 2) == 1:
            stats2 += 1

    print(f"Execution time for {iterations} iterations: {time.time() - tps1:.4f} seconds")
    print(f"Games won by player 1: {(stats1/iterations)*100:.2f}%")
    print(f"Games won by player 2: {(stats2/iterations)*100:.2f}%")

def random_strat(state, current_player):
    actions = legit_moves(state, current_player)
    return random.choice(actions)



test(10, 8)