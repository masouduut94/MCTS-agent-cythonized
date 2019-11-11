import threading
import multiprocessing as mlp
from mctsagent import *


class RootThread(mlp.Process):
  """
  Implementation of Root parallelization in MCTS agent

  """
  def __init__(self, agent, time, q1, q2):
    mlp.Process.__init__(self)
    self.agent = agent
    self.agent_q = q1
    self.moves_q = q2
    self.time = time

  def run(self):
    self.agent.search(self.time)
    moves = {}
    for child in self.agent.root.children.values():
      moves[child.move] = child.N
    self.agent_q.put(self.agent)
    self.moves_q.put(moves)

  def get_result(self):
    return self.agent_q.get()

  def get_moves(self):
    return self.moves_q.get()


class LeafThread(threading.Thread):
  """
  This class uses parallel threads for parallelizing playout phase 

  """
  def __init__(self, state):
    self.state = deepcopy(state)
    self.moves = state.moves()
    threading.Thread.__init__(self)

  def run(self):

    while (self.state.winner() == 0):
      move = random.choice(self.moves)
      self.state.play(move)
      self.moves.remove(move)

  def get_results(self):
    return self.state.winner()


class Threadnode:
  
  def __init__(self, move=None, parent=None):
    """
    The same node module in mctsagent which is designed 
    specifically for Tree_threading in MCTS. A lock is added
    to the module parameters.

    """
    self.lock = threading.Lock()
    self.lock.acquire()
    self.move = move
    self.parent = parent
    self.N = 0  # times this position was visited
    self.Q = 0  # average reward (wins-losses) from this position
    self.Q_RAVE = 0  # times this move has been critical in a rollout
    self.N_RAVE = 0  # times this move has appeared in a rollout
    self.children = {}
    self.lock.release()

  def acquire_lock(self):
    self.lock.acquire()

  def release_lock(self):
    self.lock.release()

  def add_children(self, children):
    """
    Add a list of nodes to the children of this node.

    """
    self.lock.acquire()
    for child in children:
      self.children[child.move] = child
    self.lock.release()

  def value(self, explore):
    # if the node is not visited, set the value as infinity.
    if (self.N == 0):
      if (explore == 0):
        return 0
      else:
        return inf  # infinity (maximum value)
    else:
      return self.Q / self.N + explore * sqrt(2 * log(self.parent.N) / self.N)


class SearchThread(threading.Thread):

  def __init__(self, root, state, budget):
    self.rootstate = deepcopy(state)
    self.root = root
    self.EXPLORATION = 0.2
    self.num_rollouts = 0
    self.budget = budget
    threading.Thread.__init__(self)

  def run(self):
    """
    # 1st PHASE
    SELECTION 

    """

    startTime = clock()

    while (self.num_rollouts <= self.budget):

      node = self.root
      state = deepcopy(self.rootstate)

      unvisited_node = False
      while(len(node.children) != 0 ):

        max_node = max(node.children.values(), key = lambda n: n.value(self.EXPLORATION))
        max_value = max_node.value(self.EXPLORATION)
        max_nodes = [n for n in node.children.values()
                   if n.value(self.EXPLORATION) == max_value]
        node = random.choice(max_nodes)
        #node.acquire_lock()
        node.Q -= 1  # virtual loss
        state.play(node.move)
        #node.release_lock()

        if node.N == 0:
          unvisited_node = True
          break

      # 2nd PHASE
      # EXPANSION
      children = []
      if not unvisited_node:
        expanded = False
        if (state.winner() == gamestate.PLAYERS["none"]):
          for move in state.moves():
            children.append(Threadnode(move, node))
          #node.acquire_lock()
          node.add_children(children)
          #node.release_lock()
          node = random.choice(list(node.children.values()))
          node.Q -= 1 # virtual loss
          state.play(node.move)

      turn = state.turn()

      # 3rd PHASE
      # ROLLOUT

      moves = state.moves()
      while (state.winner() == gamestate.PLAYERS["none"]):
        move = random.choice(moves)
        state.play(move)

      outcome = state.winner()

      # 4th PHASE
      # BACKPROPAGATION

      reward = 0 if outcome == turn else 1

      while node != None:
        #node.acquire_lock()
        node.N += 1
        node.Q += reward
        node.Q += 1 # virtual loss removal
        #node.release_lock()
        node = node.parent
        reward = 0 if reward == 1 else 1

      self.num_rollouts += 1
    #print('finished %a rollouts in %a seconds' % (self.num_rollouts, clock() - startTime))
