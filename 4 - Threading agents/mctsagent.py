from gamestate import gamestate
from time import clock
import random
from math import sqrt, log
from copy import copy, deepcopy
from sys import stderr
from queue import Queue


inf = float('inf')


class node:
  """
  Node for the MCTS. Stores the move applied to reach this node from its parent,
  stats for the associated game position, children, parent and outcome
  (outcome==none unless the position ends the game).
  """

  def __init__(self, move=None, parent=None):
    """
    Initialize a new node with optional move and parent and initially empty
    children list and rollout statistics and unspecified outcome.

    """
    self.move = move
    self.parent = parent
    self.N = 0  # times this position was visited
    self.Q = 0  # average reward (wins-losses) from this position
    self.Q_RAVE = 0 # times this move has been critical in a rollout
    self.N_RAVE = 0 # times this move has appeared in a rollout
    self.children = {}

  def add_children(self, children):
    """
    Add a list of nodes to the children of this node.

    """
    for child in children:
      self.children[child.move] = child

  def value(self, explore):
    """
    Calculate the UCT value of this node relative to its parent, the parameter
    "explore" specifies how much the value should favor nodes that have
    yet to be thoroughly explored versus nodes that seem to have a high win
    rate.
    Currently explore is set to one.

    """
    # if the node is not visited, set the value as infinity.
    if (self.N == 0):
      if (explore == 0):
        return 0
      else:
        return inf  # infinity (maximum value)
    else:
      return self.Q / self.N + explore * sqrt(2 * log(self.parent.N) / self.N)


class mctsagent:
  """
  Basic no frills implementation of an agent that preforms MCTS for hex.

  """
  EXPLORATION = 1

  def __init__(self, state=gamestate(8)):
    self.rootstate = deepcopy(state)
    self.root = node()
    self.run_time = 0
    self.node_count = 0
    self.num_rollouts = 0

  def search(self, time_budget):
    """
    Search and update the search tree for a 
    specified amount of time in secounds.

    """
    startTime = clock()
    num_rollouts = 0

    # do until we exceed our time budget
    while (num_rollouts < 5000):
      node, state = self.select_node()
      turn = state.turn()
      outcome = self.roll_out(state)
      self.backup(node, turn, outcome)
      num_rollouts += 1
    run_time = clock() - startTime
    node_count = self.tree_size()
    self.run_time = run_time
    self.node_count = node_count
    self.num_rollouts = num_rollouts
    print(self.run_time)

  def select_node(self):
    """
    Select a node in the tree to preform a single simulation from.

    """
    node = self.root
    state = deepcopy(self.rootstate)

    #stop if we find reach a leaf node
    while(len(node.children) != 0 ):
      # descend to the maximum value node, break ties at random
      max_node = max(node.children.values(), key = lambda n: n.value(self.EXPLORATION))
      max_value = max_node.value(self.EXPLORATION)
      max_nodes = [n for n in node.children.values()
                   if n.value(self.EXPLORATION) == max_value]
      node = random.choice(max_nodes)
      # LOCK NODE
      # VIRTUAL LOSS
      state.play(node.move)
      # UNLOCK NODE
      # if some child node has not been explored select it before expanding
      # other children
      if node.N == 0:
        return (node, state)

    #if we reach a leaf node generate its children and return one of them
    #if the node is terminal, just return the terminal node
    # LOCK NODE
    if(self.expand(node, state)):
      node = random.choice(list(node.children.values()))
      state.play(node.move)
    # UNLOCK NODE
    return (node, state)

  def expand(self, parent, state):
    """
    Generate the children of the passed "parent" node based on the available
    moves in the passed gamestate and add them to the tree.

    """
    children = []
    if (state.winner() != gamestate.PLAYERS["none"]):
      # game is over at this node so nothing to expand
      return False
    for move in state.moves():
      children.append(node(move, parent))

    parent.add_children(children)
    return True

  def roll_out(self, state):
    """
    Simulate an entirely random game from the passed state and return the winning
    player.

    """
    moves = state.moves()  # Get a list of all possible moves in current state of the game

    while (state.winner() == gamestate.PLAYERS["none"]):
      move = random.choice(moves)
      state.play(move)

    return state.winner()

  def backup(self, node, turn, outcome):
    """
    Update the node statistics on the path from the passed node to root to reflect
    the outcome of a randomly simulated playout.

    """
    # Careful: The reward is calculated for player who just played
    # at the node and not the next player to play
    reward = 0 if outcome == turn else 1

    while node != None:
      # LOCK NODE
      node.N += 1
      node.Q += reward
      # REMOVING VIRTUAL LOSS
      node = node.parent
      # UNLOCK NODE
      reward = 0 if reward == 1 else 1

  def best_move(self):
    """
    Return the best move according to the current tree.

    """
    if (self.rootstate.winner() != gamestate.PLAYERS["none"]):
      return gamestate.GAMEOVER

    # choose the move of the most simulated node breaking ties randomly
    max_value = max(self.root.children.values(), key = lambda n: n.N).N
    max_nodes = [n for n in self.root.children.values() if n.N == max_value]
    bestchild = random.choice(max_nodes)
    return bestchild.move

  def move(self, move):
    """
    Make the passed move and update the tree approriately. It is 
	  designed to let the player choose an action manually (which might
	  snot be the best action).

    """
    if move in self.root.children:
      child = self.root.children[move]
      child.parent = None
      self.root = child
      self.rootstate.play(child.move)
      return

    # if for whatever reason the move is not in the children of
    # the root just throw out the tree and start over
    self.rootstate.play(move)
    self.root = node()

  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all
    the information stored in the tree since none of it applies to the new
    state.

    """
    self.rootstate = deepcopy(state)
    self.root = node()

  def statistics(self):
    return(self.num_rollouts, self.node_count, self.run_time)

  def tree_size(self):
    """
    Count nodes in tree by BFS.
    """
    Q = Queue()
    count = 0
    Q.put(self.root)
    while not Q.empty():
      node = Q.get()
      count +=1
      for child in node.children.values():
        Q.put(child)
    return count
