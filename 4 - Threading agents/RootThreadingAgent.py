from mctsagent import *
from parallelization import RootThread

class RootThreadingAgent:
  """
  Implementation of root parallelization in MCTS.
  different agents use different cores to search
  and then according to moves available in current 
  state of all agents, the best move (the move 
  with the most number of playouts) is chosen.

  """
  
  def __init__(self, state=gamestate(8), processes=5):
    self.agents = []
    self.threads = processes
    self.workers = []
    self.results = []
    for i in range(self.threads):
      self.agents.append(mctsagent(state))

  def search(self, time_budget):
    """
    Search and update the search tree for a 
    specified amount of time in secounds.

    """
    for agent in self.agents:
      w = RootThread(agent, time_budget, mlp.Queue(), mlp.Queue())
      self.workers.append(w)

    for w in self.workers:
      w.start()

    self.results = [w.get_moves() for w in self.workers]
    self.agents = [w.get_result() for w in self.workers]

    for w in self.workers:
      w.join()

    del self.workers[:]

  def best_move(self):
    """
    Return the best move according to the current tree.

    """
    
    if (self.agents[0].rootstate.winner() != gamestate.PLAYERS["none"]):
      return gamestate.GAMEOVER

    res = {}
    moves = list(self.results[0].keys())
    for move in moves:
      for item in self.results:
        if move in list(res.keys()):
          res[move] += item[move]
        else:
          res[move] = item[move]

    largest_key = []
    largest_value = 0
    for key, value in res.items():
      if value > largest_value:
        largest_value = value
        largest_key = [key]
      elif value == largest_value:
        largest_key.append(key)
    bestchild = random.choice(largest_key)
    del self.results[:]
    return bestchild

  def move(self, move):
    """
    Make the passed move and update the tree approriately. It is 
    designed to let the player choose an action manually (which might
    not be the best action).

    """
    for agent in self.agents:
      agent.move(move)

  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all
    the information stored in the tree since none of it applies to the new
    state.

    """
    for agent in self.agents:
      agent.set_gamestate(state)

