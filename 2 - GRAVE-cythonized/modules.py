from time import clock
import random
from math import sqrt, log, exp
from copy import deepcopy
from queue import Queue
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import numpy as np
import sys

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#############################                                                    ######################################
#############################                                                    ######################################
#############################                      GAMESTATE                     ######################################
#############################                                                    ######################################
#############################                                                    ######################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################





cdef class gamestate:
  """
  Stores information representing the current state of a game of hex, namely
  the board and the current turn. Also provides functions for playing the game
  """

  cdef public:
    dict PLAYERS
    int[6][2] neighbor_patterns
    int EDGE1
    int EDGE2
    int GAMEOVER
    int size
    int toplay
    list wb_played 
    unionfind white_groups, black_groups
    int[:, :] board
    list legal_moves


  def __cinit__(self, int size):
    """
    Initialize the game board and give white first turn.
    Also create our union find structures for win checking.
    """
    self.PLAYERS = {"none": 0, "white": 1, "black": 2}
    self.EDGE1, self.EDGE2 = 1, 2
    self.GAMEOVER = -1
    self.neighbor_patterns = [[-1, 0], [0, -1], [-1, 1], [0, 1], [1, 0], [1, -1]]
    self.size = size
    self.toplay = self.PLAYERS["white"]
    self.board = np.zeros((size, size), dtype=np.int32)
    self.wb_played = [0, 0]
    self.white_groups = unionfind()
    self.black_groups = unionfind()
    self.white_groups.set_ignored_elements([self.EDGE1, self.EDGE2])
    self.black_groups.set_ignored_elements([self.EDGE1, self.EDGE2])
    self.legal_moves = []
    cdef list moves = []
    cdef int x, y
    for y in range(self.size):
      for x in range(self.size):
        self.legal_moves.append((x, y))

  cpdef play(self, tuple cell):
    """
    Play a stone of the current turns color in the passed cell.
    """
    if (self.toplay == self.PLAYERS["white"]):
      self.place_white(cell)
      self.toplay = self.PLAYERS["black"]
    elif (self.toplay == self.PLAYERS["black"]):
      self.place_black(cell)
      self.toplay = self.PLAYERS["white"]
    self.legal_moves.remove(cell)

  
  cpdef place_white(self, tuple cell):
    """
    Place a white stone regardless of whose turn it is.
    """
    x,y = cell[0], cell[1]
    if (self.board[x, y] == 0):
      self.board[cell[0], cell[1]] = 1
      self.wb_played[0] += 1
    else:
      raise ValueError("Cell occupied")
    # if the placed cell touches a white edge connect it appropriately
    if (cell[0] == 0):
      self.white_groups.join(self.EDGE1, cell)
    if (cell[0] == self.size - 1):
      self.white_groups.join(self.EDGE2, cell)
    # join any groups connected by the new white stone
    cdef tuple n
    for n in self.neighbors(cell):
      if (self.board[n[0], n[1]] == 1):
        self.white_groups.join(n, cell)

  cpdef place_black(self, tuple cell):
    """
    Place a black stone regardless of whose turn it is.
    """
    x,y = cell[0], cell[1]
    if (self.board[x, y] == 0):
      self.board[cell[0], cell[1]] = 2
      self.wb_played[1] += 1
    else:
      raise ValueError("Cell occupied")
    # if the placed cell touches a black edge connect it appropriately
    if (cell[1] == 0):
      self.black_groups.join(self.EDGE1, cell)
    if (cell[1] == self.size - 1):
      self.black_groups.join(self.EDGE2, cell)
    # join any groups connected by the new black stone
    cdef tuple n
    for n in self.neighbors(cell):
      if (self.board[n[0], n[1]] == 2):
        self.black_groups.join(n, cell)


  cpdef bint would_win(self, tuple cell, int color):
    cdef bint connect1 = False, connect2 = False
    cdef tuple n

    if color == self.PLAYERS["black"]:
      if cell[1] == 0:
        connect1 = True
      elif cell[1] == self.size - 1:
        connect2 = True

      for n in self.neighbors(cell):
        if self.black_groups.connected(self.EDGE1, n):
          connect1 = True
        elif self.black_groups.connected(self.EDGE2, n):
          connect2 = True
    elif color == self.PLAYERS["white"]:
      if cell[0] == 0:
        connect1 = True
      elif cell[0] == self.size - 1:
        connect2 = True

      for n in self.neighbors(cell):
        if self.white_groups.connected(self.EDGE1, n):
          connect1 = True
        elif self.white_groups.connected(self.EDGE2, n):
          connect2 = True
      
    return connect1 and connect2


  cpdef int turn(self):
    """
    Return the player with the next move.
    """
    return self.toplay

  cpdef set_turn(self, int player):
    """
    Set the player to take the next move.
    """
    if (player in self.PLAYERS.values() and player != self.PLAYERS["none"]):
      self.toplay = player
    else:
      raise ValueError('Invalid turn: ' + str(player))

  cpdef int winner(self):
    """
    Return a number corresponding to the winning player,
    or none if the game is not over.
    """
    if (self.white_groups.connected(self.EDGE1, self.EDGE2)):
      return self.PLAYERS["white"]
    elif (self.black_groups.connected(self.EDGE1, self.EDGE2)):
      return self.PLAYERS["black"]
    else:
      return self.PLAYERS["none"]

  cpdef tuple neighbors(self, tuple cell):
    """
    Return list of neighbors of the passed cell.

    """
    cdef int x = cell[0]
    cdef int y = cell[1]
    cdef int i, N=6
    cdef list ans = []
    for i in range(N):
        if (x + self.neighbor_patterns[i][0] >= 0 and self.neighbor_patterns[i][0] + x < self.size \
        and self.neighbor_patterns[i][1] + y >= 0 and self.neighbor_patterns[i][1] + y < self.size):
            ans.append((x + self.neighbor_patterns[i][0], y + self.neighbor_patterns[i][1]))
    
    return tuple(ans)

  cpdef list moves(self):
    """
    Get a list of all moves possible on the current board.
    """
    return self.legal_moves
  
  cpdef list get_num_played(self):
    return self.wb_played

  cpdef dict get_white_groups(self):
    return self.white_groups.get_groups()

  cpdef dict get_black_groups(self):
    return self.black_groups.get_groups()

  cpdef __deepcopy__(self,memo_dictionary):
    res = gamestate(self.size)
    res.PLAYERS = self.PLAYERS
    res.EDGE1, res.EDGE2 = self.EDGE1, self.EDGE2
    res.GAMEOVER = self.GAMEOVER
    res.neighbor_patterns = self.neighbor_patterns
    res.size = int(self.size)
    res.toplay = int(self.toplay)
    res.board = np.array(self.board, dtype=np.int32)
    res.wb_played = self.wb_played.copy()
    res.white_groups = deepcopy(self.white_groups, memo_dictionary)
    res.black_groups = deepcopy(self.black_groups, memo_dictionary)
    res.legal_moves = list(self.legal_moves)
    return res



#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#############################                                                    ######################################
#############################                                                    ######################################
#############################                      UNIONFIND                     ######################################
#############################                                                    ######################################
#############################                                                    ######################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################





cdef class unionfind:
  """
  Unionfind data structure specialized for finding hex connections.
  Implementation inspired by UAlberta CMPUT 275 2015 class notes.
  """
  cdef public:
    dict parent
    dict rank
    dict groups
    list ignored

  def __cinit__(self):
    """
    Initialize parent and rank as empty dictionarys, we will
    lazily add items as nessesary.
    """
    self.parent = {}
    self.rank = {}
    self.groups = {}
    self.ignored = []

  cpdef join(self, x, y):
    """
    Merge the groups of x and y if they were not already,
    return False if they were already merged, true otherwise
    """
    rep_x = self.find(x)
    rep_y = self.find(y)

    if rep_x == rep_y:
      return False
    if self.rank[rep_x] < self.rank[rep_y]:
      self.parent[rep_x] = rep_y
    
      self.groups[rep_y].extend(self.groups[rep_x])
      del self.groups[rep_x]
    elif self.rank[rep_x] >self.rank[rep_y]:
      self.parent[rep_y] = rep_x
    
      self.groups[rep_x].extend(self.groups[rep_y])
      del self.groups[rep_y]      
    else:
      self.parent[rep_x] = rep_y
      self.rank[rep_y] += 1
    
      self.groups[rep_y].extend(self.groups[rep_x])
      del self.groups[rep_x]  

    return True

  cpdef find(self, x):
    """
    Get the representative element associated with the set in
    which element x resides. Uses grandparent compression to compression
    the tree on each find operation so that future find operations are faster.
    """

    if x not in self.parent:
      self.parent[x] = x
      self.rank[x] = 0
      if x in self.ignored:
        self.groups[x] = []
      else:
        self.groups[x] = [x]
    px = self.parent[x]
    if x == px: return x
    gx = self.parent[px]
    if gx==px: return px

    self.parent[x] = gx

    return self.find(gx)

  cpdef connected(self, x, y):
    """
    Check if two elements are in the same group.
    """
    return self.find(x)==self.find(y)

  cpdef set_ignored_elements(self, list ignore):
    """
    Elements in ignored 
    """
    self.ignored = ignore

  cpdef dict get_groups(self):
    return self.groups

  cpdef __deepcopy__(self, memo_dictionary):
    res = unionfind()
    res.parent = deepcopy(self.parent, memo_dictionary)
    res.rank = deepcopy(self.rank, memo_dictionary)
    res.groups = deepcopy(self.groups, memo_dictionary)
    res.ignored = self.ignored[:]
    del self.ignored[:]
    return res




#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#############################                                                    ######################################
#############################                                                    ######################################
#############################           NODE FOR STORING INFORMATION             ######################################
#############################                                                    ######################################
#############################                                                    ######################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################






inf = float('inf')


cdef class node:
  """
  Node for the MCTS. Stores the move applied to reach this node from its parent,
  stats for the associated game position, children, parent and outcome

  """
  cdef public:
    tuple move
    int N
    float Q
    int N_RAVE
    float Q_RAVE
    list children
    node parent
    int ref

  def __cinit__(self, tuple move=None, node parent=None):
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
    self.children = []

  cpdef add_children(self, list moves):
    """
    Add a list of nodes to the children of this node.

    """
    cdef int i = 0
    cdef int N = len(moves)
    for i in range(N):
      self.children.append(node(moves[i], self))
    

  cpdef float value(self, float explore, int rave_const, int eval = 0):
    """
    Calculate the UCT value of this node relative to its parent, the parameter
    "explore" specifies how much the value should favor nodes that have
    yet to be thoroughly explored versus nodes that seem to have a high win
    rate.

    """
    # if the node is not visited, set the value as infinity.
    cdef dict eval_methods = {'uct':0, 'rave':1}
    cdef float EXPLORE, EXPLOIT, UCT
    cdef float AMAF = 0
    cdef float alpha = 0
    cdef int N_RAVE
    cdef float Q_RAVE
    cdef int REF = 50
    if (self.N == 0):
      return inf  # infinity (maximum value)
    else:
      EXPLOIT = self.Q / self.N
      EXPLORE = sqrt(2 * log(self.parent.N) / self.N)
      UCT = EXPLOIT + explore * EXPLORE
      if eval == eval_methods['uct']:
        return UCT

      elif eval == eval_methods['rave']:
        N_RAVE = self.N_RAVE
        Q_RAVE = self.Q_RAVE

        if self.N_RAVE < REF:
          nodeCopy = self
          while nodeCopy.parent is not None:
            nodeCopy = nodeCopy.parent
            if nodeCopy.N_RAVE >= REF:
              N_RAVE = nodeCopy.N_RAVE
              Q_RAVE = nodeCopy.Q_RAVE
              break
          alpha = max(0, (rave_const - self.N) / rave_const)
          AMAF = Q_RAVE / N_RAVE if N_RAVE is not 0 else 0
        return (1-alpha) * UCT + alpha * AMAF




#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#############################                                                    ######################################
#############################                                                    ######################################
#############################                  BASIC AGENTS                      ######################################
#############################                                                    ######################################
#############################                                                    ######################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################





##############################################################################
##############################################################################
################                                                  ############
################            BASIC MCTS AGENT USING UCT            ############
################                                                  ############
##############################################################################
##############################################################################



cdef class mctsagent:
  """
  Basic no frills implementation of an agent that performs MCTS for hex.

  """
  cdef public:
    float EXPLORATION
    int RAVE_CONSTANT
    int node_count
    int num_rollouts
    int time_budget
    float run_time
    tuple move
    node root
    gamestate rootstate


  def __init__(self, state=gamestate(8)):
    self.rootstate = deepcopy(state)
    self.root = node()
    self.EXPLORATION = 0.4
    self.RAVE_CONSTANT = 300
    self.run_time = 0
    self.node_count = 0
    self.num_rollouts = 0
  

  cpdef void search(self, int time_budget):
    """
    Search and update the search tree for a 
    specified amount of time in secounds.

    """

    cdef node node
    cdef gamestate state
    cdef unsigned int outcome, turn
    self.num_rollouts = 0
    self.run_time = clock()

    # do until we exceed our time budget
    while (clock() - self.run_time < time_budget):
      node, state = self.select_node()
      turn = state.turn()
      outcome, _ = self.roll_out(state)
      self.backup(node, turn, outcome)
      self.num_rollouts += 1

    self.run_time = clock() - self.run_time
    self.node_count = self.tree_size()


  cpdef tuple select_node(self):
    """
    Select a node in the tree to preform a single simulation from.

    """
    new_node = self.root
    state = deepcopy(self.rootstate)
    cdef int i
    cdef node n
    cdef int length
    #stop if we find reach a leaf node
    while(len(new_node.children) !=0 ):
      #descend to the maximum value node, break ties at random
      length = len(new_node.children)
      max_value = new_node.children[0].value(self.EXPLORATION, self.RAVE_CONSTANT, 0)
      for i in range(1,length):
        if new_node.children[i].value(self.EXPLORATION, self.RAVE_CONSTANT, 0) > max_value:
          max_value = new_node.children[i].value(self.EXPLORATION, self.RAVE_CONSTANT, 0)
      
      max_nodes = [n for n in new_node.children 
                   if n.value(self.EXPLORATION, self.RAVE_CONSTANT, 0) == max_value]
      new_node = random.choice(max_nodes)
      state.play(new_node.move)

      #if some child node has not been explored select it before expanding
      #other children
      if new_node.N == 0:
        return (new_node, state)

    #if we reach a leaf node generate its children and return one of them
    #if the node is terminal, just return the terminal node
    if(self.expand(new_node, state)):
      new_node = random.choice(new_node.children)
      state.play(new_node.move)
    return (new_node, state)

  cpdef bint expand(self, node parent, gamestate state):
    """
    Generate the children of the passed "parent" node based on the available
    moves in the passed gamestate and add them to the tree.

    """
    if (state.winner() != state.PLAYERS["none"]):
      # game is over at this node so nothing to expand
      return False

    parent.add_children(state.moves())
    return True


  cpdef tuple roll_out(self, gamestate state):
    """
    Simulate an entirely random game from the passed state and return the winning
    player.

    """
    cdef list moves
    moves = list(state.moves())  # Get a list of all possible moves in current state of the game

    while (state.winner() == state.PLAYERS["none"]):
      move = random.choice(moves)
      state.play(move)
      moves.remove(move)

    return state.winner(), []


  cpdef void backup(self, node node, int turn, int outcome, list pl_length=None):
    """
    Update the node statistics on the path from the passed node to root to reflect
    the outcome of a randomly simulated playout.

    """
    # Careful: The reward is calculated for player who just played
    # at the node and not the next player to play
    cdef int reward
    reward = -1 if outcome == turn else 1

    while node != None:
      node.N += 1
      node.Q += reward
      node = node.parent
      reward = -1 if reward == 1 else 1


  def best_move(self):
    """
    Return the best move according to the current tree.

    """
    if (self.rootstate.winner() != 0):
      return self.rootstate.GAMEOVER
    cdef int max_value
    cdef list max_nodes
    cdef node bestchild
    # choose the move of the most simulated node breaking ties randomly
    max_value = max(self.root.children, key = lambda n: n.N).N
    max_nodes = [n for n in self.root.children if n.N == max_value]
    bestchild = random.choice(max_nodes)
    return bestchild.move


  def move(self, move):
    """
    Make the passed move and update the tree approriately. It is 
    designed to let the player choose an action manually (which might
    not be the best action).

    """
    cdef int item
    cdef int N = len(self.root.children)
    for item in range(N):
      if move == self.root.children[item].move:
        child = self.root.children[item]
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


  cpdef tuple statistics(self):
    return(self.num_rollouts, self.node_count, self.run_time)


  cpdef int tree_size(self):
    """
    Count nodes in tree by BFS.
    """
    Q = Queue()
    cdef int count = 0
    Q.put(self.root)
    while not Q.empty():
      node = Q.get()
      count +=1
      for child in node.children:
        Q.put(child)
    return count


##############################################################################
##############################################################################
###########                                                      #############
###########          RAPID-ACTION-VALUE-ESTIMATION AGENT         #############
###########                                                      #############
##############################################################################
##############################################################################




cdef class rave_mctsagent(mctsagent):

  cdef public:
    list black_rave_pts
    list white_rave_pts
 
  def __init__(self, state=gamestate(8)):
    super().__init__(state)
    self.black_rave_pts = []
    self.white_rave_pts = []
  
  cpdef void search(self, int time_budget):
    """
    Search and update the search tree for a specified amount of time in secounds.
    """
    self.num_rollouts = 0
    self.run_time = clock()


    while(clock() - self.run_time < time_budget):
      node, state = self.select_node()
      turn = state.turn()
      outcome, _ = self.roll_out(state)
      self.backup(node, turn, outcome)
      self.num_rollouts += 1

    self.run_time = clock() - self.run_time
    self.node_count = self.tree_size()


  cpdef tuple select_node(self):
    """
    Select a node in the tree to preform a single simulation from.
    """
    new_node = self.root
    state = deepcopy(self.rootstate)
    cdef int i
    cdef node n
    cdef int length
    #stop if we find reach a leaf node
    while(len(new_node.children) !=0 ):
      #descend to the maximum value node, break ties at random
      length = len(new_node.children)
      max_value = new_node.children[0].value(self.EXPLORATION, self.RAVE_CONSTANT, 1)
      for i in range(1,length):
        if new_node.children[i].value(self.EXPLORATION, self.RAVE_CONSTANT, 1) > max_value:
          max_value = new_node.children[i].value(self.EXPLORATION, self.RAVE_CONSTANT, 1)
      
      max_nodes = [n for n in new_node.children 
                   if n.value(self.EXPLORATION, self.RAVE_CONSTANT, 1) == max_value]
      new_node = random.choice(max_nodes)
      state.play(new_node.move)

      #if some child node has not been explored select it before expanding
      #other children
      if new_node.N == 0:
        return (new_node, state)

    #if we reach a leaf node generate its children and return one of them
    #if the node is terminal, just return the terminal node
    if(self.expand(new_node, state)):
      new_node = random.choice(new_node.children)
      state.play(new_node.move)
    return (new_node, state)


  cpdef tuple roll_out(self, gamestate state):
    """
    Simulate a random game except that we play all known critical
    cells first, return the winning player and record critical cells at the end.

    """
    moves = state.moves().copy()
    while(state.winner() == state.PLAYERS["none"]):
      move = random.choice(moves)
      state.play(move)
      moves.remove(move)
  
    cdef int size = state.size

    for x in range(size):
      for y in range(size):
        if state.board[x, y] == 2:
          self.black_rave_pts.append((x, y))
        elif state.board[x, y] == 1:
          self.white_rave_pts.append((x, y))

    return state.winner(), []


  cpdef void backup(self, node node1, int turn, int outcome, list pl_length= None):
    """
    Update the node statistics on the path from the passed node to root to reflect
    the outcome of a randomly simulated playout.
    """
    # note that reward is calculated for player who just played
    # at the node and not the next player to play
    cdef int reward, i
    reward = -1 if outcome == turn else 1

    cdef int WL = len(self.white_rave_pts)
    cdef int BL = len(self.black_rave_pts)
    cdef node ch

    while node1!= None:
      if turn == 1: # gamestate.PLAYERS["white"]
        for i in range(WL):
          for ch in node1.children:
            if self.white_rave_pts[i] == ch.move:
              ch.Q += -reward
              ch.N += 1
      else:
        for i in range(BL):
          for ch in node1.children:
            if self.black_rave_pts[i] == ch.move:
              ch.Q += -reward
              ch.N += 1

      node1.N += 1
      node1.Q += reward
      if turn == 2:
        turn = 1 # gamestate.PLAYERS["white"]
      else:
        turn = 2 #gamestate.PLAYERS["black"]
      reward = -reward
      node1 = node1.parent
    self.black_rave_pts.clear()
    self.white_rave_pts.clear()


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
########################################                                         ######################################
########################################                                         ######################################
########################################              RAVE HEURISTICS            ######################################
########################################                                         ######################################
########################################                                         ######################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################




##############################################################################
##############################################################################
##############################################################################
##############################################################################
############                                               ###################
############               QUALITY-BASED RAVE              ###################
############                                               ###################
##############################################################################
##############################################################################
##############################################################################
##############################################################################



cdef class qb_rave_mctsagent(rave_mctsagent):

  cdef public:
    long[:, :] pl_list
    int move_played
    float a_const
    float k_const
 
  def __init__(self, state=gamestate(8)):
    super().__init__(state)
    self.pl_list = np.array([[0, 0]])
    self.move_played = 0
    self.a_const = 0.25
    self.k_const = 7

  cpdef void search(self, int time_budget):
    """
    Search and update the search tree for a specified amount of time in secounds.
    """
    self.num_rollouts = 0
    self.run_time = clock()

    while(self.num_rollouts < 650):
      node, state = self.select_node()
      turn = state.turn()
      outcome, pl_length = self.roll_out(state)
      self.backup(node, turn, outcome, pl_length=pl_length)
      self.num_rollouts += 1

    self.run_time = clock() - self.run_time
    self.node_count = self.tree_size()


  cpdef tuple select_node(self):
    """
    Select a node in the tree to preform a single simulation from.
    """
    new_node = self.root
    state = deepcopy(self.rootstate)
    cdef int i
    cdef node n
    cdef int length
    #stop if we find reach a leaf node
    while(len(new_node.children) != 0 ):
      #descend to the maximum value node, break ties at random
      length = len(new_node.children)
      max_value = new_node.children[0].value(self.EXPLORATION, self.RAVE_CONSTANT, 1)
      for i in range(1,length):
        if new_node.children[i].value(self.EXPLORATION, self.RAVE_CONSTANT, 1) > max_value:
          max_value = new_node.children[i].value(self.EXPLORATION, self.RAVE_CONSTANT, 1)
      
      max_nodes = [n for n in new_node.children 
                   if n.value(self.EXPLORATION, self.RAVE_CONSTANT, 1) == max_value]
      new_node = random.choice(max_nodes)
      state.play(new_node.move)

      #if some child node has not been explored select it before expanding
      #other children
      if new_node.N == 0:
        return (new_node, state)

    #if we reach a leaf node generate its children and return one of them
    #if the node is terminal, just return the terminal node
    if(self.expand(new_node, state)):
      new_node = random.choice(new_node.children)
      state.play(new_node.move)
    return (new_node, state)


  cpdef tuple roll_out(self, gamestate state):
    """
    Simulate a random game except that we play all known critical
    cells first, return the winning player and record critical cells at the end.

    """
    moves = state.moves().copy()
    while(state.winner() == state.PLAYERS["none"]):
      move = random.choice(moves)
      state.play(move)
      moves.remove(move)
    num_played = state.get_num_played()

    cdef int size = state.size
    cdef int i = 0, j = 0, x, y

    for x in range(size):
      for y in range(size):
        if state.board[x, y] == 2:
          self.black_rave_pts.append((x, y))
        elif state.board[x, y] == 1:
          self.white_rave_pts.append((x, y))

    return state.winner(), num_played


  def modify_reward(self, list pl_length):
    mean = np.mean(self.pl_list, axis=0)
    mean_offset = np.asarray([mean[0] - pl_length[0], mean[1] - pl_length[1]])
    deviation = np.std(self.pl_list, axis=0)
    landa = np.asarray(list(map(lambda x, y: x/y if y != 0 else 0, mean_offset, deviation)))
    bonus = -1 + (2 / (1 + np.exp(-self.k_const * landa)))
    a = {'white':bonus[0], 'black':bonus[1]}
    return a


  cpdef void backup(self, node node1, int turn, int outcome, list pl_length = None):
    """
    Update the node statistics on the path from the passed node to root to reflect
    the outcome of a randomly simulated playout.
    """
    # note that reward is calculated for player who just played
    # at the node and not the next player to play
    cdef int reward, i
    cdef float a_const = 0.25
    cdef float q_reward
    cdef dict bonus

    reward = -1 if outcome == turn else 1
    
    self.pl_list = np.concatenate((self.pl_list, [pl_length]), axis=0)
    bonus = self.modify_reward(pl_length)

    if self.num_rollouts == 0:
      self.pl_list = np.delete(self.pl_list, 0, 0)
    
    cdef int WL = len(self.white_rave_pts)
    cdef int BL = len(self.black_rave_pts)

    while node1 != None:
      if turn == 1: # gamestate.PLAYERS["white"]
        q_reward = reward + (reward * a_const * bonus['white'])
        node1.Q += q_reward
        for i in range(WL):
          for ch in node1.children:
            if self.white_rave_pts[i] == ch.move:
              ch.Q += -q_reward
              ch.N += 1
      else:
        q_reward = reward + (reward * a_const * bonus['black'])
        node1.Q += q_reward
        for i in range(BL):
          for ch in node1.children:
            if self.black_rave_pts[i] == ch.move:
              ch.Q += -q_reward
              ch.N += 1

      node1.N += 1
      if turn == 2:
        turn = 1 # gamestate.PLAYERS["white"]
      else:
        turn = 2 #gamestate.PLAYERS["black"]
      reward = -reward
      node1 = node1.parent
    self.black_rave_pts.clear()
    self.white_rave_pts.clear()


  def move(self, move):
    """
    Make the passed move and update the tree approriately. It is 
    designed to let the player choose an action manually (which might
    not be the best action).

    """
    self.pl_list = np.array([[0, 0]])
    cdef int item
    for item in range(len(self.root.children)):
      if move == self.root.children[item].move:
        child = self.root.children[item]
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
    self.pl_list = np.array([[0, 0]])



##############################################################################
##############################################################################
##############################################################################
##############################################################################
############                                             #####################
############               LAST-GOOD-REPLY               #####################
############                                             #####################
##############################################################################
##############################################################################
##############################################################################
##############################################################################



cdef class lgr(rave_mctsagent):
  
  cdef public:
    dict black_reply
    dict white_reply

  def __init__(self, state=gamestate(8)):
    super().__init__(state)
    self.black_reply = {}
    self.white_reply = {}

  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all
    the information stored in the tree since none of it applies to the new 
    state.
    """
    super().set_gamestate(state)
    self.white_reply = {}
    self.black_reply = {}

  cpdef tuple roll_out(self, gamestate state):
    """
    Simulate a random game except that we play all known critical
    cells first, return the winning player and record critical cells at the end.
    
    """
    cdef list moves = list(state.moves())
    cdef int first = state.turn()
    if first == self.rootstate.PLAYERS["black"]:
      current_reply = self.black_reply
      other_reply = self.white_reply
    else:
      current_reply = self.white_reply
      other_reply = self.black_reply
    cdef list black_moves = []
    cdef list white_moves = []
    cdef tuple last_move = None
    cdef tuple move
    while(state.winner() == self.rootstate.PLAYERS["none"]):
      if last_move in current_reply:
        move = current_reply[last_move]
        if move not in moves or random.random() > 0.5:
          move = random.choice(moves)
      else:
        move = random.choice(moves)
      if state.turn() == self.rootstate.PLAYERS["black"]:
        black_moves.append(move)
      else:
        white_moves.append(move)
      current_reply, other_reply = other_reply, current_reply
      state.play(move)
      moves.remove(move)
      last_move = move


    cdef int size = state.size 
    cdef int i = 0, j = 0, x, y

    for x in range(size):
      for y in range(size):
        if state.board[x, y] == 2:
          self.black_rave_pts.append((x, y))
        elif state.board[x, y] == 1:
          self.white_rave_pts.append((x, y))


    cdef int skip = 0, offset = 0, k = 0

    if state.winner() == self.rootstate.PLAYERS["black"]:
      if first == self.rootstate.PLAYERS["black"]:
        offset = 1
      if state.turn() == self.rootstate.PLAYERS["black"]:
        skip = 1
      for k in range(len(white_moves) - skip):
        self.black_reply[white_moves[k]] = black_moves[k + offset]
    else:
      if first == self.rootstate.PLAYERS["white"]:
        offset = 1
      if state.turn() == self.rootstate.PLAYERS["white"]:
        skip = 1
      for k in range(len(black_moves) - skip):
        self.white_reply[black_moves[k]] = white_moves[k + offset]

    return state.winner(), []


##############################################################################
##############################################################################
##############################################################################
##############################################################################
#############                                            #####################
#############            DECISIVE-MOVE AGENT             #####################
#############                                            #####################
##############################################################################
##############################################################################
##############################################################################
##############################################################################





cdef class decisive_move(rave_mctsagent):

  cpdef tuple roll_out(self, gamestate state):
    """
    Simulate a random game except that we play all known critical cells
    first, return the winning player and record critical cells at the end.
    """
    cdef list moves = list(state.moves())
    cdef list good_moves = moves.copy()
    cdef list good_opponent_moves = moves.copy()
    cdef int to_play = state.turn()
    cdef bint done

    
    while(state.winner() == self.rootstate.PLAYERS["none"]):
      done = False
      while len(good_moves) > 0 and not done:
        move = random.choice(good_moves)
        good_moves.remove(move)
        if state.would_win(move, to_play):
          state.play(move)
          moves.remove(move)
          if move in good_opponent_moves:
            good_opponent_moves.remove(move)
          done = True
      
      if not done:
        move = random.choice(moves)
        state.play(move)
        moves.remove(move)
        if move in good_opponent_moves:
          good_opponent_moves.remove(move)
          
      good_moves, good_opponent_moves = good_opponent_moves, good_moves
    
    cdef int size = state.size 
    cdef int i = 0, j = 0, x, y

    for x in range(size):
      for y in range(size):
        if state.board[x, y] == 2:
          self.black_rave_pts.append((x, y))
        elif state.board[x, y] == 1:
          self.white_rave_pts.append((x, y))

    return state.winner(), []


##############################################################################
##############################################################################
##############################################################################
##############################################################################
############                                             #####################
############                   POOLRAVE                  #####################
############                                             #####################
##############################################################################
##############################################################################
##############################################################################
##############################################################################





cdef class poolrave_mctsagent(rave_mctsagent):

  cdef public:
    dict black_rave
    dict white_rave

  def __init__(self, state=gamestate(8)):
    super().__init__(state)
    self.black_rave = {}
    self.white_rave = {} 
  
  def set_gamestate(self, state):
 
    self.rootstate = deepcopy(state)
    self.root = node()
    self.black_rave = {}
    self.white_rave = {}
    self.white_rave_pts.clear()
    self.black_rave_pts.clear()


  def roll_out(self, gamestate state):

    cdef list black_rave_moves
    cdef list white_rave_moves
    cdef list black_pool = []
    cdef list white_pool = []
    cdef int i = 0, x, y
    cdef int num_pool = 0
    cdef int size = state.size
    cdef tuple move

    black_rave_moves = sorted(self.black_rave.keys(),
                              key=lambda cell: self.black_rave[cell])
    white_rave_moves = sorted(self.white_rave.keys(),
                              key=lambda cell: self.white_rave[cell])

    # sorting dict items by using each item value ordering.
    


    while len(black_pool) < 10 and i < len(black_rave_moves):
      if black_rave_moves[i] in moves:
        black_pool.append(black_rave_moves[i])
      i += 1
    i = 0
    while len(white_pool) < 10 and i < len(white_rave_moves):
      if white_rave_moves[i] in moves:
        white_pool.append(white_rave_moves[i])
      i += 1

    while(state.winner() == self.rootstate.PLAYERS['none']):
      move = None
      if len(black_pool) > 0 and state.turn() == self.rootstate.PLAYERS["black"]:
        move = random.choice(black_pool)
        num_pool += 1
      elif len(white_pool) > 0:
        move = random.choice(white_pool)
        num_pool += 1
      if random.random() > 0.5 or not move or move not in moves:
        move = random.choice(moves)
        num_pool -= 1

      state.play(move)
      moves.remove(move)


    for x in range(size):
      for y in range(size):
        if state.board[x,y] == 2:
          self.black_rave_pts.append((x, y))
          j+=1
          if state.winner() == 2:
            if (x, y) in self.black_rave:
              self.black_rave[(x, y)] += 1
            else:
              self.black_rave[(x, y)] = 1
          else:
            if (x, y) in self.black_rave:
              self.black_rave[(x, y)] -= 1
            else:
              self.black_rave[(x, y)] = -1
        elif state.board[x,y] == 1:
          self.white_rave_pts.append((x, y))
          k+=1
          if state.winner() == 1:
            if (x, y) in self.white_rave:
              self.white_rave[(x, y)] += 1
            else:
              self.white_rave[(x, y)] = 1
          else:
            if (x, y) in self.white_rave:
              self.white_rave[(x, y)] -= 1
            else:
              self.white_rave[(x, y)] = -1

    return state.winner(), []



#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#############################                                                    ######################################
#############################                                                    ######################################
#############################             GRAPHICAL USER INTERFACE               ######################################
#############################                                                    ######################################
#############################                                                    ######################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


class Gui:
  """
  This class is built to let the user have a better interaction with
  game.
  inputs =>
  root = Tk() => an object which inherits the traits of Tkinter class
  agent = an object which inherit the traits of mctsagent class.

  """

  


  def __init__(self, root, agent_name='UCT'):
    self.root = root
    self.root.geometry('1366x690+0+0')
    self.game = deepcopy(gamestate(8))
    self.agent_name = agent_name
    self.agent_type = {
              1:"UCT",
              2:"RAVE",
              3:"QBR-RAVE",
              4:"LGR",
              5:"DECISIVE_MOVE",
              6:"POOLRAVE"
                      }
    self.AGENTS = {  
              "UCT": mctsagent,
              "RAVE": rave_mctsagent,
              "QBR-RAVE": qb_rave_mctsagent,
              "LGR":lgr,
              "DECISIVE_MOVE":decisive_move,
              "POOLRAVE": poolrave_mctsagent
                  }
    try:
      self.agent = self.AGENTS[agent_name](self.game)
    except KeyError:
      print("Unknown agent defaulting to basic")
      self.agent_name = "uct"
      self.agent = self.AGENTS[agent_name](self.game)
    self.time = 1
    self.root.configure(bg='#363636')
    self.colors = {'white': '#ffffff',
                   'milk': '#e9e5e5',
                   'red': '#9c0101',
                   'orange': '#ee7600',
                   'yellow': '#f4da03',
                   'green': '#00ee76',
                   'cyan': '#02adfd',
                   'blue': '#0261fd',
                   'purple': '#9c02fd',
                   'gray1': '#958989',
                   'gray2': '#1c1c1c',
                   'black': '#000000'}
    global bg
    bg = self.colors['gray2']
    self.last_move = None
    self.frame_board = Frame(self.root)  # main frame for the play board
    self.canvas = Canvas(self.frame_board, bg=bg)
    self.scroll_y = ttk.Scrollbar(self.frame_board, orient=VERTICAL)
    self.scroll_x = ttk.Scrollbar(self.frame_board, orient=HORIZONTAL)

    # the notebook frame which holds the left panel frames

    self.notebook = ttk.Notebook(self.frame_board, width=450)
    self.panel_game = Frame(self.notebook, highlightbackground=self.colors['white'])
    self.developers = Frame(self.notebook, highlightbackground=self.colors['white'])

    # Registering variables for: 

    self.game_size_value = IntVar()  # size of the board
    self.game_time_value = IntVar()  # time of CPU player
    self.game_turn_value = IntVar()  # defines whose turn is it

    self.switch_agent_value = IntVar()  # defines which agent to play against
    self.switch_agent_value.set(1)

    self.game_turn_value.set(1)
    self.turn = {1: 'white', 2: 'black'}

    self.game_size = Scale(self.panel_game)
    self.game_time = Scale(self.panel_game)
    self.game_turn = Scale(self.panel_game)
    self.generate = Button(self.panel_game)
    self.reset_board = Button(self.panel_game)

    self.switch_agent = Scale(self.panel_game)
    self.agent_show = Label(self.panel_game, font=('Calibri', 14, 'bold'), fg='white',justify=LEFT,
                            bg=bg, text='Agent Policy: ' + self.agent_name + '\n')

    self.hex_board = []
    # Holds the IDs of hexagons in the main board for implementing the click and play functions
    self.game_size_value.set(8)
    self.game_time_value.set(1)
    self.size = self.game_size_value.get()
    self.time = self.game_time_value.get()
    self.board = np.array(self.game.board, dtype=np.int32).tolist()
    self.array_to_hex(self.board)  # building the game board
    self.black_side()
    self.white_side()

    # Frame_content

    self.frame_board.configure(bg=bg, width=1366, height=760)
    self.frame_board.pack(fill=BOTH)
    self.notebook.add(self.panel_game, text='       Game       ')
    self.notebook.add(self.developers, text='    Developers    ')
    self.notebook.pack(side=LEFT, fill=Y)
    self.canvas.configure(width=980, bg=bg, cursor='hand2')
    self.canvas.pack(side=LEFT, fill=Y)
    self.canvas.configure(yscrollcommand=self.scroll_y.set)
    self.scroll_y.configure(command=self.canvas.yview)
    self.scroll_x.configure(command=self.canvas.xview)
    self.scroll_y.place(x=487, y=470)
    self.scroll_x.place(x=470, y=500)

    # Frame_left_panel

    """
    the left panel notebook ---->   Game

    """
    self.panel_game.configure(bg=bg)
    Label(self.panel_game, text='Board size',
          font=('Calibri', 14, 'bold'),
          foreground='white', bg=bg, pady=10).pack(fill=X, side=TOP)  # label ---> Board size
    self.game_size.configure(from_=3, to=20, tickinterval=1, bg=bg, fg='white',
                             orient=HORIZONTAL, variable=self.game_size_value)
    self.game_size.pack(side=TOP, fill=X)
    Label(self.panel_game, text='Time',
          font=('Calibri', 14, 'bold'),
          foreground='white', bg=bg, pady=10).pack(side=TOP, fill=X)  # label ---> Time
    self.game_time.configure(from_=1, to=20, tickinterval=1, bg=bg, fg='white',
                             orient=HORIZONTAL, variable=self.game_time_value)
    self.game_time.pack(side=TOP, fill=X)
    Label(self.panel_game, text='Player',
          font=('Calibri', 14, 'bold'),
          foreground='white', bg=bg, pady=10).pack(side=TOP, fill=X)  # label ---> Turn
    self.game_turn.configure(from_=1, to=2, tickinterval=1, bg=bg, fg='white',
                             orient=HORIZONTAL, variable=self.game_turn_value)
    self.game_turn.pack(side=TOP)
    Label(self.panel_game, text='   ',
          font=('Calibri', 14, 'bold'),
          foreground='white', bg=bg).pack(side=TOP, fill=X)

    ################################### AGENT CONTROLS #############################

    self.agent_show.pack(fill=X, side=TOP)
    agents_num = len(self.AGENTS)
    self.switch_agent.configure(from_=1, to=agents_num, tickinterval=1, bg=bg, fg='white',
                             orient=HORIZONTAL, variable=self.switch_agent_value,)
    self.switch_agent.pack(side=TOP, fill=X)

    ################################### MOVE LABELS ################################
    self.move_label = Label(self.panel_game, font=('Calibri', 15, 'bold'),height=5, fg='white',justify=LEFT,
          bg=bg, text='To play : Click on a cell \nMCTS Agent play : Click on Generate')
    self.move_label.pack(side=TOP, fill=X)

    self.reset_board.configure(text='Reset Board', pady=10,
                               cursor='hand2', width=22,
                               font=('Calibri', 12, 'bold'))
    self.reset_board.pack(side=LEFT)
    self.generate.configure(text='Generate', pady=10,
                            cursor='hand2', width=22,
                            font=('Calibri', 12, 'bold'))
    self.generate.pack(side=LEFT)
    

    """
    the left panel notebook ---> Developers

    """
    self.developers.configure(bg=bg)
    Label(self.developers,
          text= 'ULTRA-HEX',
          font=('Calibri', 18, 'bold'),
          foreground='white', bg=bg, pady=5).pack(side=TOP, fill=X)
    Label(self.developers,
          text='DEVELOPED BY:\n'
          + 'Masoud Masoumi Moghadam\n\n'
          + 'SUPERVISED BY:\n'
          + 'Dr.Pourmahmoud Aghababa\n\n'
          + 'THANKS FOR THE SUPPORTS:\n'
          + 'Dr.Tahmouresnezhad\n'
          + 'Nemat Rahmani\n',
          font=('Calibri', 16, 'bold'), justify=LEFT,
          foreground='white', bg=bg, pady=10).pack(side=TOP, fill=X)
    Label(self.developers, text='Summer 2016',
          font=('Calibri', 17, 'bold'), wraplength=350, justify=LEFT,
          foreground='white', bg=bg, pady=30).pack(side=TOP, fill=X)

    # Binding Actions

    """
    Binding triggers for the actions defined in the class.

    """
    self.canvas.bind('<1>', self.mouse_click)
    self.game_size.bind('<ButtonRelease>', self.set_size)
    self.game_time.bind('<ButtonRelease>', self.set_time)
    self.generate.bind('<ButtonRelease>', self.generate_move)
    self.reset_board.bind('<ButtonRelease>', self.reset)
    self.switch_agent.bind('<ButtonRelease>', self.set_agent)


  def pts(self):
    """
    Returns the points which the first hexagon has to be created based on.

    """
    return [[85, 50], [105, 65], [105, 90], [85, 105], [65, 90], [65, 65]]


  def hexagon(self, points, color):
    """
    Creates a hexagon by getting a list of points and their assigned colors
    according to the game board
    """
    if color is 0:
      hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                      points[3], points[4], points[5],
                                      fill=self.colors['gray1'], outline='black', width=2, activefill='cyan')
    elif color is 1:
      hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                      points[3], points[4], points[5],
                                      fill=self.colors['yellow'], outline='black', width=2, activefill='cyan')
    elif color is 2:
      hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                      points[3], points[4], points[5],
                                      fill=self.colors['red'], outline='black', width=2, activefill='cyan')
    elif color is 3:
      hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                      points[3], points[4], points[5],
                                      fill=self.colors['black'], outline='black', width=2)
    else:
      hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                      points[3], points[4], points[5],
                                      fill=self.colors['white'], outline='black', width=2)
    return hx


  def genrow(self, points, colors):
    """
    By getting a list of points as the starting point of each row and a list of
    colors as the dedicated color for each item in row, it generates a row of
    hexagons by calling hexagon functions multiple times.
    """
    x_offset = 40
    row = []
    temp_array = []
    for i in range(len(colors)):
      for point in points:
          temp_points_x = point[0] + x_offset * i
          temp_points_y = point[1]
          temp_array.append([temp_points_x, temp_points_y])
      if colors[i] is 0:
          hx = self.hexagon(temp_array, 0)
      elif colors[i] is 1:
          hx = self.hexagon(temp_array, 4)
      else:
          hx = self.hexagon(temp_array, 3)
      row.append(hx)
      temp_array = []
    return row


  def array_to_hex(self, array):
    """
    Simply gets the gameboard and generates the hexagons by their dedicated colors.
    """
    initial_offset = 20
    y_offset = 40
    temp = []
    for i in range(len(array)):
      points = self.pts()
      for point in points:
          point[0] += initial_offset * i
          point[1] += y_offset * i
          temp.append([point[0], point[1]])
      row = self.genrow(temp, self.board[i])
      temp.clear()
      self.hex_board.append(row)


  def white_side(self):
    """
    Generates the white zones in the left and right of the board.

    """
    init_points = self.pts()
    for pt in init_points:
      pt[0] -= 40
    for pt in init_points:
      pt[0] -= 20
      pt[1] -= 40
    label_x, label_y = 0, 0
    init_offset = 20
    y_offset = 40
    temp_list = []
    for i in range(len(self.board)):
      for pt in range(len(init_points)):
          init_points[pt][0] += init_offset
          init_points[pt][1] += y_offset
          label_x += init_points[pt][0]
          label_y += init_points[pt][1]
      label_x /= 6
      label_y /= 6
      self.hexagon(init_points, 4)
      self.canvas.create_text(label_x, label_y, fill=self.colors['black'], font="Times 20 bold",
                              text=chr(ord('A') + i))
      label_x, label_y = 0, 0
      for j in init_points:
          temp_list.append([j[0] + (len(self.board) + 1) * 40, j[1]])
      self.hexagon(temp_list, 4)
      temp_list.clear()


  def black_side(self):
    """
    Generates the black zones in the top and bottom of the board.

    """
    init_points = self.pts()
    label_x, label_y = 0, 0
    temp_list = []
    for pt in init_points:
      pt[0] -= 60
      pt[1] -= 40
    for t in range(len(init_points)):
      init_points[t][0] += 40
      label_x += init_points[t][0]
      label_y += init_points[t][1]
    label_x /= 6
    label_y /= 6
    for i in range(len(self.board)):
      self.hexagon(init_points, 3)
      self.canvas.create_text(label_x, label_y, fill=self.colors['white'], font="Times 20 bold", text=i + 1)
      label_x, label_y = 0, 0
      for pt in init_points:
          temp_list.append([pt[0] + (len(self.board) + 1) * 20, pt[1] + (len(self.board) + 1) * 40])
      self.hexagon(temp_list, 3)
      temp_list.clear()
      for j in range(len(init_points)):
          init_points[j][0] += 40
          label_x += init_points[j][0]
          label_y += init_points[j][1]
      label_x /= 6
      label_y /= 6


  def mouse_click(self, event):
    """
    Whenever any of the hexagons in the board is clicked, depending
    on the player turns, it changes the color of hexagon to the player
    assigned color.

    """
    if self.winner() == 'none':
      x = self.canvas.canvasx(event.x)
      y = self.canvas.canvasy(event.y)
      idd = self.canvas.find_overlapping(x, y, x, y)
      idd = list(idd)
      if len(idd) is not 0:
        clicked_cell = idd[0]
        if any([clicked_cell in x for x in self.hex_board]):
          coordinated_cell = clicked_cell - self.hex_board[0][0]
          row = int(coordinated_cell / self.size)
          col = (coordinated_cell % self.size)
          turn = self.turn[self.game_turn_value.get()]
          cell = str(chr(65 + row)) + str(col+1)
          self.move_label.configure(text=str(turn)+' played '+cell,justify=LEFT, height=5)
          if self.board[row][col] == 0:
            self.board[row][col] = self.game_turn_value.get()
            if self.game_turn_value.get() == 1:
              self.game_turn_value.set(2)
            else:
              self.game_turn_value.set(1)
          self.refresh()
          y = row
          x = col
          if turn[0].lower() == 'w':
            self.last_move = (x, y)
            if self.game.turn() == self.game.PLAYERS["white"]:
              self.game.play((x, y))
              self.agent.move((x, y))
              if self.winner() != 'none':
                messagebox.showinfo(" GAME OVER", " Wow, You won! \n Winner is %s" % self.winner())
              return
            else:
              self.game.place_white((x, y))
              self.agent.set_gamestate(self.game)
              if self.winner() != 'none':
                messagebox.showinfo(" GAME OVER", " Wow, You won! \n Winner is %s" % self.winner())
              return
          elif turn[0].lower() == 'b':
            self.last_move = (x, y)
            if self.game.turn() == self.game.PLAYERS["black"]:
              self.game.play((x, y))
              self.agent.move((x, y))
              if self.winner() != 'none':
                messagebox.showinfo(" GAME OVER", " Wow, You won! \n Winner is %s" % self.winner())
              return
            else:
              self.game.place_black((x, y))
              self.agent.set_gamestate(self.game)
              if self.winner() != 'none':
                messagebox.showinfo(" GAME OVER", " Wow, You won! \n Winner is %s" % self.winner())
              return
    else:
      messagebox.showinfo(" GAME OVER ", " The game is already over! Winner is %s" % self.winner())


  def set_size(self, event):
    """
    It changes the board size and reset the whole game.

    """
    self.canvas.delete('all')
    self.size = self.game_size_value.get()
    g = gamestate(self.size)
    self.game = deepcopy(g)
    self.agent.set_gamestate(self.game)
    self.board = np.int_(self.game.board, dtype=np.int32).tolist()
    self.last_move = None
    self.move_label.config(text='To play : Click on a cell \nMCTS Agent play : Click on Generate',justify='left', height=5)
    self.refresh()


  def set_time(self, event):
    """
    It changes the time for CPU player to think and generate a move.

    """
    self.time = self.game_time_value.get()
    print('The CPU time = ', self.time, ' seconds')


  def set_agent(self, event):
    """
    It changes the time for CPU player to think and generate a move.

    """
    agent_num = self.switch_agent_value.get()
    self.agent_name = self.agent_type[agent_num]
    self.agent = self.AGENTS[self.agent_name](self.game)
    self.agent_show.config( font=('Calibri', 14, 'bold'),justify=LEFT,
        text= 'Agent Policy: ' + self.agent_name + '\n' )


  def winner(self):
    """
    Return the winner of the current game (black or white), none if undecided.

    """
    if self.game.winner() == self.game.PLAYERS["white"]:
      return "white"
    elif self.game.winner() == self.game.PLAYERS["black"]:
      return "black"
    else:
      return "none"


  def generate_move(self, event):
    """
    By pushing the generate button, It produces an appropriate move
    by using monte carlo tree search algorithm for the player which
    turn is his/hers! .

    """
    if self.winner() == 'none':
      # move = self.agent.special_case(self.last_move)
      move = None
      self.agent.search(self.time)
      num_rollouts, node_count, run_time = self.agent.statistics()[0], self.agent.statistics()[1], self.agent.statistics()[2]
      if move is None:
        move = self.agent.best_move()  # the move is tuple like (3, 1)
      self.game.play(move)
      self.agent.move(move)
      row, col = move[0], move[1]  # Relating the 'move' tuple with index of self.board
      self.board[col][row] = self.game_turn_value.get()
      if self.game_turn_value.get() == 1:  # change the turn of players
        self.game_turn_value.set(2)
      else:
        self.game_turn_value.set(1)
      self.refresh()
      player = self.turn[self.game_turn_value.get()]
      cell = chr(ord('A') + move[1]) + str(move[0] + 1)
      self.move_label.config( font=('Calibri', 15, 'bold'),justify='left',
        text= str(num_rollouts) + ' Game Simulations '+'\n'\
        + 'In ' + str(run_time) + ' seconds ' + '\n'\
        + 'Node Count : ' + str(node_count) + '\n'\
        + player + ' played at ' + cell, height=5 )
      
      if self.winner() != 'none':
        messagebox.showinfo(" GAME OVER", " Oops!\n You lost! \n Winner is %s" % self.winner())
    else:
      messagebox.showinfo(" GAME OVER", " The game is already over! Winner is %s" % self.winner())


  def refresh(self):
    """
    Delete the whole world and recreate it again

    """
    self.canvas.delete('all')
    self.hex_board.clear()
    self.array_to_hex(self.board)
    self.black_side()
    self.white_side()  


  def reset(self, event):
    """
    By clicking on the Reset button game board would be cleared
    for a new game

    """

    self.game = gamestate(self.game.size)
    self.agent.set_gamestate(self.game)
    self.set_size(event)
    self.last_move = None
    self.game_turn_value.set(1)
    self.move_label.config(text='To play : Click on a cell \nMCTS Agent play : Click on Generate',justify='left', height=5)


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#############################                                                    ######################################
#############################                                                    ######################################
#############################             GAME-TEXT-PROTOCOL INTERFACE           ######################################
#############################                                                    ######################################
#############################                                                    ######################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


class gtpinterface:
  """
  Interface for using game-text-protocol to control the program
  designed for controling the  tournaments effeciently.

  """

  def __init__(self, agent):
    """
    Initilize the list of available commands, binding appropriate names to the
    funcitons defined in this file.
    """
    self.game = deepcopy(gamestate(8))
    self.agent = agent
    self.agent.set_gamestate(self.game)
    self.move_time = 1
    self.last_move = None

  def gtp_boardsize(self, args):
    """
    Set the size of the game board (will also clear the board).

    """
    if (len(args) < 1):
      return (False, "Not enough arguments")
    try:
      size = int(args[0])
    except ValueError:
      return (False, "Argument is not a valid size")
    if size < 1:
      return (False, "Argument is not a valid size")

    self.game = gamestate(size)
    self.agent.set_gamestate(self.game)
    self.last_move = None
    return (True, "")

  def gtp_clear(self, args):
    """
    Clear the game board.

    """
    self.game = gamestate(self.game.size)
    self.agent.set_gamestate(self.game)
    self.last_move = None
    return (True, "")

  def gtp_play(self, args):
    """
    Play a stone of a given colour in a given cell.
    1st arg = colour (white/w or black/b)
    2nd arg = cell (i.e. g5)

    Note: play order is not enforced but out of order turns will cause the
    search tree to be reset

    """
    if (len(args) < 2):
      return (False, "Not enough arguments")
    try:
      x = ord(args[1][0].lower()) - ord('a')
      y = int(args[1][1:]) - 1

      if (x < 0 or y < 0 or x >= self.game.size or y >= self.game.size):
        return (False, "Cell out of bounds")

      if args[0][0].lower() == 'w':
        self.last_move = (x, y)
        if self.game.turn() == self.game.PLAYERS["white"]:
          self.game.play((x, y))
          self.agent.move((x, y))
        else:
          self.game.place_white((x, y))
          self.agent.set_gamestate(self.game)

      elif args[0][0].lower() == 'b':
        self.last_move = (x, y)
        if self.game.turn() == self.game.PLAYERS["black"]:
          self.game.play((x, y))
          self.agent.move((x, y))
        else:
          self.game.place_black((x, y))
          self.agent.set_gamestate(self.game)
      else:
        return (False, "Player not recognized")

    except ValueError:
      return (False, "Malformed arguments")

  def gtp_genmove(self, args):
    """
    Allow the agent to play a stone of the given colour (white/w or black/b)

    Note: play order is not enforced but out of order turns will cause the
    agents search tree to be reset

    """
    # if user specifies a player generate the appropriate move
    # otherwise just go with the current turn
    if self.gtp_winner([])[1] == 'none':
      if (len(args) > 0):
        if args[0][0].lower() == 'w':
          if self.game.turn() != self.game.PLAYERS['white']:
            self.game.set_turn(1)
            self.agent.set_gamestate(self.game)

        elif args[0][0].lower() == 'b':
          if self.game.turn() != self.game.PLAYERS['black']:
            self.game.set_turn(2)
            self.agent.set_gamestate(self.game)
        else:
          return (False, "Player not recognized")

      self.agent.search(self.move_time)
      move = self.agent.best_move()

      if (move == self.game.GAMEOVER):
        return (False, "The game is already over" +
                '\n' + 'The winner is ----> ' + str(self.gtp_winner([])[1]), 0)
      self.game.play(move)
      self.agent.move(move)
      return (True, chr(ord('a') + move[0]) + str(move[1] + 1), self.agent.statistics()[0])
    else:
      return(False, "The game is already over" +
            '\n' + 'The winner is ----> ' + str(self.gtp_winner([])[1]), 0)

  def gtp_time(self, args):
    """
    Change the time per move allocated to the search agent (in units of secounds)

    """
    if (len(args) < 1):
      return (False, "Not enough arguments")
    try:
      time = int(args[0])
    except ValueError:
      return (False, "Argument is not a valid time limit")
    if time < 1:
      return (False, "Argument is not a valid time limit")
    self.move_time = time
    return (True, "")

  def gtp_winner(self, args):
    """
    Return the winner of the current game (black or white), none if undecided.

    """
    if (self.game.winner() == self.game.PLAYERS["white"]):
      return (True, "white")
    elif (self.game.winner() == self.game.PLAYERS["black"]):
      return (True, "black")
    else:
      return (True, "none")


def tournament(interface1, interface2, game_number=100, movetime=10, size=8):
  """
  Run some number of games between two agents, alternating who has first move
  each time. Return the winrate for the first of the two agents. Print games
  played along the way.
  
  """
  begin = clock()
  p1_score = 0    # score for player 1
  p2_score = 0    # score for player 2
  interface1.gtp_time([movetime])
  interface2.gtp_time([movetime])
  interface1.gtp_boardsize([size])
  interface2.gtp_boardsize([size])

  agent1_rollouts = []
  agent2_rollouts = []
  print('Tournament Started ...')
  print("%a games will be running between agents ..." % (game_number))
  for i in range(game_number):
    interface1.gtp_clear([])
    interface2.gtp_clear([])
    turn = interface1.game.turn()
    c1 = 'w' if turn == 1 else 'b' # white turn for player 1
    c2 = 'b' if turn == 1 else 'w' # black turn for player 2

    if i % 2 == 0:
      while (interface1.gtp_winner([])[1] == "none"):
        move = interface1.gtp_genmove([c1])
        agent1_rollouts.append(move[2])

        if move[0]:
          interface2.gtp_play([c1, move[1]])

        move = interface2.gtp_genmove([c2])
        agent2_rollouts.append(move[2])

        if move[0]:
          interface1.gtp_play([c2, move[1]])

      if (interface1.gtp_winner([])[1][0] == c1):
        p1_score += 1
        print("GAME OVER, WINNER : PLAYER 1 (" + c1 + ")\n")
        print("Games played =  [ %i   /  %g ]"  %  (i+1, game_number))
        print("Wins   |  Player 1 =  [%a]  |  Player 2 = [%s]  " % (p1_score, p2_score))
      else:
        p2_score += 1
        print("GAME OVER, WINNER : PLAYER 2 (" + c2 + ")\n")
        print("Games played =  [ %i   /  %g ] "  %  (i+1, game_number) )
        print("Wins   |  Player 1 =  [%a] |  Player 2 = [%s]  " % (p1_score, p2_score))

    else:
      while (interface1.gtp_winner([])[1] == "none"):
        move = interface2.gtp_genmove([c1])
        agent2_rollouts.append(move[2])
        if move[0]:
          interface1.gtp_play([c1, move[1]])

        move = interface1.gtp_genmove([c2])
        agent1_rollouts.append(move[2])

        if move[0]:
          interface2.gtp_play([c2, move[1]])

      if (interface1.gtp_winner([])[1][0] == c2):
        p1_score += 1
        print("GAME OVER, WINNER : PLAYER 1 (" + c2 + ")\n")
        print("Games played =  [ %i   /  %g ] "  %  (i+1, game_number) )
        print("Wins   |  Player 1 =  [%a]  |  Player 2 = [%s]  " % (p1_score, p2_score))
      else:
        p2_score += 1
        print("GAME OVER, WINNER : PLAYER 2 (" + c1 + ")\n")
        print("Games played =  [ %i   /  %g ] "  %  (i+1, game_number) )
        print("Wins   |  Player 1 =  [%a] |  Player 2 = [%s]  " % (p1_score, p2_score))
    sys.stdout.flush()  # flush buffer so intermediate results can be viewed
  agent1_rollouts = list(filter(lambda a: a != 0, agent1_rollouts))
  agent2_rollouts = list(filter(lambda a: a != 0, agent2_rollouts))

  p1 = (p1_score / game_number) * 100
  p2 = (p2_score / game_number) * 100
  rollouts_info = [round(sum(agent1_rollouts)/ len(agent1_rollouts)),
                   round(sum(agent2_rollouts)/ len(agent2_rollouts))]

  print('\n\n\n')
  print('player 1 wins = ', p1, ' %')
  print('player 2 wins = ', p2, ' %')

  print("Average Simulations for agent1 = [ %a ] "  %  round(sum(agent1_rollouts)/ len(agent1_rollouts)))
  print("Average Simulations for agent2 = [ %a ] "  %  round(sum(agent2_rollouts)/ len(agent2_rollouts)))

  print('Finished in %i seconds' % (clock() - begin))
  return p1_score, p2_score, rollouts_info, clock() - begin


