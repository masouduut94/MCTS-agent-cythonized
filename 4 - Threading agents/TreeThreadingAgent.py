from parallelization import *


class TreeThreadingAgent:
  """
  Implementation of Tree Threading approach in MCTS.
  Different threads start running 4 steps of monte
  carlo tree search concurrently. virtual loss and
  lock is considered to boost its performance.

  """
  def __init__(self, state=gamestate(8), threads=5):
    self.rootstate = deepcopy(state)
    self.root = Threadnode()
    self.run_time = 0
    self.node_count = 0
    self.num_rollouts = 0
    self.threads = threads - 1

  def search(self, time_budget):
    threads = []
    for i in range(self.threads):
      threads.append(SearchThread(self.root, self.rootstate, time_budget))

    for t in threads:
      t.start()

    for t in threads:
      t.join()

    del threads[:]

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
	not be the best action).

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
    self.root = Threadnode()

  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all
    the information stored in the tree since none of it applies to the new
    state.

    """
    self.rootstate = deepcopy(state)
    self.root = Threadnode()

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
  
