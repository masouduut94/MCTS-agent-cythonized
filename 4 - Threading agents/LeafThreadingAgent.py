from mctsagent import *
from parallelization import LeafThread


class LeafThreadingAgent(mctsagent):
  """
  Basic no frills implementation of an agent that preforms MCTS for hex.

  """
  EXPLORATION = 1

  def __init__(self, state=gamestate(8), threads=3):
    super().__init__(state)
    self.threads = threads

  def search(self, time_budget):
    """
    Search and update the search tree for a 
    specified amount of time in secounds.

    """
    startTime = clock()
    num_rollouts = 0

    # do until we exceed our time budget
    while (clock() - startTime < time_budget):
      node, state = self.select_node()
      turn = state.turn()
      threads = []
      for i in range(self.threads):
        threads.append(LeafThread(state))
        threads[i].start()
      for t in threads:
        t.join()

      outcome = [t.get_results() for t in threads]
      self.backup(node, turn, outcome)
      num_rollouts += 1
    run_time = clock() - startTime
    node_count = self.tree_size()
    self.run_time = run_time
    self.node_count = node_count
    self.num_rollouts = num_rollouts

  def backup(self, node, turn, outcome):
    """
    Update the node statistics on the path from the passed node to root to reflect
    the outcome of a randomly simulated playout.

    """
    # Careful: The reward is calculated for player who just played
    # at the node and not the next player to play
    score = 0
    for res in outcome:
      if res == turn:
        score -=1
      else:
        score +=1
    num = len(outcome)
    reward = score

    while node != None:
      node.N += num
      node.Q += reward
      node = node.parent
      reward = -reward 

