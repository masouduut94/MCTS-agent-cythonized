from mctsagent import *

class rave1_node(node):
  def __init__(self, move = None, parent = None):
    """
    Initialize a new node with optional move and parent and initially empty
    children list and rollout statistics and unspecified outcome.

    """
    self.move = move
    self.parent = parent
    self.N = 0 #times this position was visited
    self.Q = 0 #average reward (wins-losses) from this position
    self.Q_RAVE = 0 # times this move has been critical in a rollout
    self.N_RAVE = 0 # times this move has appeared in a rollout
    self.children = {}

  def add_children(self, children):
    for child in children:
      self.children[child.move] = child

  def value(self, explore, rave_const):
    """
    Calculate the UCT value of this node relative to its parent, the parameter
    "explore" specifies how much the value should favor nodes that have
    yet to be thoroughly explored versus nodes that seem to have a high win
    rate. 
    Currently explore is set to zero when choosing the best move to play so
    that the move with the highest winrate is always chosen. When searching
    explore is set to EXPLORATION specified above.

    """
    # unless explore is set to zero, maximally favor unexplored nodes
    if(self.N == 0):
      if(explore == 0):
          return 0
      else:
        return inf
    else:
      # rave valuation:
      alpha = max(0,(rave_const - self.N)/rave_const)
      UCT = self.Q / self.N + explore * sqrt(2 * log(self.parent.N) / self.N)
      AMAF = self.Q_RAVE / self.N_RAVE if self.N_RAVE is not 0 else 0
      return (1-alpha) * UCT + alpha * AMAF

class rave_mctsagent(mctsagent):
  RAVE_CONSTANT = 10

  def special_case(self, last_move):
    return None

  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all
    the information stored in the tree since none of it applies to the new 
    state.
    """
    self.rootstate = deepcopy(state)
    self.root = rave1_node()


  def move(self, move):
    """
    Make the passed move and update the tree approriately.

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
    self.root = rave1_node()


  def best_move(self):
    """
    Return the best move according to the current tree.

    """
    if(self.rootstate.winner() != gamestate.PLAYERS["none"]):
      return gamestate.GAMEOVER

    # choose the move of the most simulated node breaking ties randomly
    max_value = max(self.root.children.values(), key = lambda n: n.N).N
    max_nodes = [n for n in self.root.children.values() if n.N == max_value]
    bestchild = random.choice(max_nodes)
    return bestchild.move


  def search(self, time_budget):
    """
    Search and update the search tree for a specified amount of time in secounds.
    """
    startTime = clock()
    num_rollouts = 0

    # do until we exceed our time budget
    while(num_rollouts < 1000):
      node, state = self.select_node()
      turn = state.turn()
      outcome, black_rave_pts, white_rave_pts = self.roll_out(state)
      self.backup(node, turn, outcome, black_rave_pts, white_rave_pts)
      num_rollouts += 1
    run_time = clock() - startTime
    node_count = self.tree_size()
    self.run_time = run_time
    self.node_count = node_count
    self.num_rollouts = num_rollouts

  def select_node(self):
    """
    Select a node in the tree to preform a single simulation from.
    """
    node = self.root
    state = deepcopy(self.rootstate)

    # stop if we reach a leaf node
    while(len(node.children)!= 0):
      max_value = max(node.children.values(), key = lambda n: n.value(self.EXPLORATION, self.RAVE_CONSTANT)).value(self.EXPLORATION, self.RAVE_CONSTANT)
      # descend to the maximum value node, break ties at random
      max_nodes = [n for n in node.children.values() if n.value(self.EXPLORATION, self.RAVE_CONSTANT) == max_value]
      node = random.choice(max_nodes)
      state.play(node.move)

      #if some child node has not been explored select it before expanding
      #other children
      if node.N == 0:
        return (node, state)

    #if we reach a leaf node generate its children and return one of them
    #if the node is terminal, just return the terminal node
    if(self.expand(node, state)):
      node = random.choice(list(node.children.values()))
      state.play(node.move)
    return (node, state)


  def expand(self, parent, state):
    """
    Generate the children of the passed "parent" node based on the available
    moves in the passed gamestate and add them to the tree.
    """
    children = []
    if(state.winner() != gamestate.PLAYERS["none"]):
      #game is over at this node so nothing to expand
      return False


    for move in state.moves():
      children.append(rave1_node(move, parent))

    parent.add_children(children)
    return True


  def roll_out(self, state):
    """
    Simulate a random game except that we play all known critical
    cells first, return the winning player and record critical cells at the end.

    """
    moves = state.moves()
    while(state.winner() == gamestate.PLAYERS["none"]):
      move = random.choice(moves)
      state.play(move)

    black_rave_pts = []
    white_rave_pts = []

    for x in range(state.size):
      for y in range(state.size):
        if state.board[(x,y)] == gamestate.PLAYERS["black"]:
          black_rave_pts.append((x,y))
        elif state.board[(x,y)] == gamestate.PLAYERS["white"]:
          white_rave_pts.append((x,y))

    return state.winner(), black_rave_pts, white_rave_pts


  def backup(self, node, turn, outcome, black_rave_pts, white_rave_pts):
    """
    Update the node statistics on the path from the passed node to root to reflect
    the outcome of a randomly simulated playout.
    """
    # note that reward is calculated for player who just played
    # at the node and not the next player to play
    reward = -1 if outcome == turn else 1

    while node!=None:
      if turn == gamestate.PLAYERS["white"]:
        for point in white_rave_pts:
          if point in node.children:
            node.children[point].Q_RAVE += -reward
            node.children[point].N_RAVE += 1
      else:
        for point in black_rave_pts:
          if point in node.children:
            node.children[point].Q_RAVE += -reward
            node.children[point].N_RAVE += 1

      node.N += 1
      node.Q += reward
      if turn == gamestate.PLAYERS["black"]:
        turn = gamestate.PLAYERS["white"]
      else:
        turn = gamestate.PLAYERS["black"]
      reward = -reward
      node = node.parent


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
