import sys

sys.path.append("../")
from tournament import tournament
from mctsagent import mctsagent
from gamestate import gamestate
from gtpinterface import gtpinterface

game_number = 6
move_time = 1
boardsize = 5
opening_moves = ['a1']

def main():
    """
    Run a tournament between two agents and print the resulting winrate
    for the first agent.
    """
    interface1 = gtpinterface(mctsagent())
    interface2 = gtpinterface(mctsagent())
    print(str(tournament(interface1, interface2, game_number, move_time, boardsize, opening_moves)))


if __name__ == "__main__":
    main()
