from modules import tournament, rave_mctsagent, gtpinterface
from itertools import combinations

game_number = 100
move_time = 1
boardsize = 8
tournament_number = 2

def main():

  interface1 = gtpinterface(rave_mctsagent())
  interface2 = gtpinterface(rave_mctsagent())

  address = 'results/BestRaveConst.txt'

  f = open(address, 'a')
  f.write('Defining Best RAVE Constant \n')
  print('Tournament between RAVE , RAVE \n')
  f.close()

  lst = [500, 1000, 1500, 2000, 2500, 3000]
  lst = list(combinations(lst, 2))

  for item in lst:

    interface1.agent.RAVE_CONSTANT = item[0]
    interface2.agent.RAVE_CONSTANT = item[1]

    print('agent1 RAVE_CONST = ', interface1.agent.RAVE_CONST)
    print('agent2 RAVE_CONST = ', interface2.agent.RAVE_CONST)

    for t in range(tournament_number):
      result = tournament(interface1, interface2, game_number, move_time, boardsize)
      with open(address, 'a') as file:

        file.write('\nAGENT1.RAVE_CONST = [ %a ]\nAGENT2.RAVE_CONST = [ %a ] \n'% tuple(item))
        file.write('Tournament %a \n' % str(t+1))

        file.write('player 1 wins = %a games \n' % result[0])
        file.write('player 2 wins = %a games \n' % result[1])
        file.write('player 1 = %a percent \n' % str((result[0] / game_number)*100))
        file.write('player 2 = %a percent \n' % str((result[1] / game_number)*100))

        file.write("Simulations avg: \nAgent1 [ %a ] Agent2 = [ %a ] \n"  %  tuple(result[2]))
        file.write("Total Time : [  %a  ] seconds\n\n" % int(result[3]))
        
        for i in range(10):
          file.write("********")
        file.write('\n\n')
        file.close()

if __name__ == "__main__":
  main()