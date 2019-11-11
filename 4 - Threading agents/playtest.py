from tournament import tournament
from TreeThreadingAgent import *
from rave_mctsagent import *
from gamestate import gamestate
from gtpinterface import gtpinterface
from itertools import combinations

def subsets_of_2(iterable):
  res=list(combinations(iterable,2))
  return res

game_number = 200
num_rollouts = 1000
boardsize = 9
opening_moves = []


def main():
  """
  Run a tournament between two agents and print the resulting winrate
  for the first agent.
  """
  interface1 = gtpinterface(TreeThreadingAgent(threads=5))
  interface2 = gtpinterface(rave_mctsagent())
  
  arguments = [10, 500, 1000, 7000]
  # lst = subsets_of_2(arguments)
  address = 'results/result.txt'
  with open(address, 'a') as f:
    f.write('TESTING THREADING_MCTSAGENT\n')
    f.close()
  i = 0
  while i != len(arguments):
    interface2.RAVE_CONSTANT = arguments[i]
    result = tournament(interface1, interface2, game_number, num_rollouts, boardsize, opening_moves)
    with open(address, 'a') as file:
      file.write('Result of tournament %a \n' % i)
      file.write('For agent with RAVE_CONSTANT %a\n'% interface2.RAVE_CONSTANT)
      file.write('player 1 wins = %a games \n' % result[0])
      file.write('player 2 wins = %a games \n' % result[1])
      file.write("Total time : %a \n\n\n" % result[2])
      file.close()
    i+=1

def shutdown():
  import os
  os.system("shutdown /s /t 90")

if __name__ == "__main__":
  main()
  #shutdown()
