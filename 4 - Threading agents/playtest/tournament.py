from gtpinterface import gtpinterface
from gamestate import gamestate
from copy import deepcopy
import sys


def print_game(game):
    for move in game:
        print(move, end=' ')
    print()


def setup(interface1, interface2, opening_moves):
    c = 'w'
    for move in opening_moves:
        interface1.send_command("play " + c + " " + move)
        interface2.send_command("play " + c + " " + move)
        c = ('w' if c == 'b' else 'b')


def tournament(interface1, interface2, game_number=100, movetime=10, size=8, opening_moves=[]):
    """
    Run some number of games between two agents, alternating who has first move
    each time. Return the winrate for the first of the two agents. Print games
    played along the way.
    """
    interface1.send_command("set_time " + str(movetime))
    interface2.send_command("set_time " + str(movetime))
    interface1.send_command("size " + str(size))
    interface2.send_command("size " + str(size))

    win_count = 0
    for i in range(game_number):
        interface1.send_command("reset")
        interface2.send_command("reset")
        setup(interface1, interface2, opening_moves)
        turn = interface1.game.turn()
        c1 = 'w' if turn == gamestate.PLAYERS["white"] else 'b'
        c2 = 'b' if turn == gamestate.PLAYERS["white"] else 'w'
        game = []

        if i % 2 == 0:
            while (interface1.send_command("winner")[1] == "none"):
                move = interface1.send_command("genmove " + c1)
                if move[0]:
                    interface2.send_command("play " + c1 + " " + move[1])
                    game.append(move[1])
                move = interface2.send_command("genmove " + c2)
                if move[0]:
                    interface1.send_command("play " + c2 + " " + move[1])
                    game.append(move[1])

            print_game(game)
            if (interface1.send_command("winner")[1][0] == c1):
                print("Game complete, winner: agent1(" + c1 + ")\n")
                win_count += 1
            else:
                print("Game complete, winner: agent2(" + c2 + ")\n")

        else:
            while (interface1.send_command("winner")[1] == "none"):
                move = interface2.send_command("genmove " + c1)
                if move[0]:
                    interface1.send_command("play " + c1 + " " + move[1])
                    game.append(move[1])
                move = interface1.send_command("genmove " + c2)
                if move[0]:
                    interface2.send_command("play " + c2 + " " + move[1])
                    game.append(move[1])

            print_game(game)
            if (interface1.send_command("winner")[1][0] == c2):
                print("Game complete, winner: agent1(" + c2 + ")\n")
                win_count += 1
            else:
                print("Game complete, winner: agent2(" + c1 + ")\n")
        sys.stdout.flush()  # flush buffer so intermediate results can be viewed

    return win_count / game_number
