from modules import tournament, mctsagent, gtpinterface, qb_rave_mctsagent, rave_mctsagent

game_number = 200
move_time = 1
boardsize = 11
tournament_number = 3

def main():

  interface1 = gtpinterface(rave_mctsagent())
  interface2 = gtpinterface(qb_rave_mctsagent())

  address = 'results/QB_RAVE_VS_RAVE.txt'

  f = open(address, 'a')
  f.write('QB_RAVE VS RAVE \n')
  print('QB_RAVE VS RAVE \n')
  f.close()
  for t in range(tournament_number):
    result = tournament(interface1, interface2, game_number, move_time, boardsize)
    with open(address, 'a') as file:
      file.write('Tournament %a \n' % str(t+1))
      file.write('player 1 wins = %a games \n' % result[0])
      file.write('player 2 wins = %a games \n' % result[1])
      file.write('player 1 = %a percent \n' % str((result[0] / game_number)*100))
      file.write('player 2 = %a percent \n' % str((result[1] / game_number)*100))
      file.write("Simulations avg: \nAgent1 [ %a ] Agent2 = [ %a ] \n"  %  tuple(result[2]))
      file.write("Total Time : [  %a  ] seconds\n\n" % int(result[3]))
      
      for i in range(10):
        file.write("*****")
      file.write('\n\n')
      file.close()

if __name__ == "__main__":
  main()