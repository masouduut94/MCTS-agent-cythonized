import sys
from mctsagent import mctsagent
from gamestate import gamestate


class gtpinterface:
    """
    Interface for using go-text-protocol to control the program
    Each implemented GTP command returns a string response for the user, along with
    a boolean indicating success or failure in executing the command.
    The interface contains an agent which decides which moves to make on request
    along with a gamestate which holds the current state of the game.
    
    """

    def __init__(self, agent):
        """
        Initilize the list of available commands, binding appropriate names to the
        funcitons defined in this file.
        """
        commands = {}
        commands["list_commands"] = self.gtp_list
        commands["size"] = self.gtp_boardsize
        commands["reset"] = self.gtp_clear
        commands["play"] = self.gtp_play
        commands["genmove"] = self.gtp_genmove
        commands["set_time"] = self.gtp_time
        commands["winner"] = self.gtp_winner
        self.commands = commands
        self.game = gamestate(11)
        self.agent = agent
        self.agent.set_gamestate(self.game)
        self.move_time = 10

    def send_command(self, command):
        """
        Parse the given command into a function name and arguments, execute it
        then return the response.

        """
        parsed_command = command.split()
        # first word specifies function to call, the rest are args
        name = parsed_command[0]
        args = parsed_command[1:]
        if (name in self.commands):
            return self.commands[name](args)
        else:
            return (False, "Unrecognized command")

    def register_command(self, name, command):
        """
        Add a new command to the commands list under name which
        calls the function command, will also overwrite old commands.

        """
        self.commands[name] = command

    def gtp_list(self, args):
        """
        Return a list of all known command names.

        """
        ret = ''
        for command in self.commands:
            ret += '\n' + command
        return (True, ret)

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
        return (True, "")

    def gtp_clear(self, args):
        """
        Clear the game board.

        """
        self.game = gamestate(self.game.size)
        self.agent.set_gamestate(self.game)
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
                if self.game.turn() == gamestate.PLAYERS["white"]:
                    self.game.play((x, y))
                    self.agent.move((x, y))
                else:
                    self.game.place_white((x, y))
                    self.agent.set_gamestate(self.game)

            elif args[0][0].lower() == 'b':
                if self.game.turn() == gamestate.PLAYERS["black"]:
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
        if self.send_command('winner')[1] == 'none':
            if (len(args) > 0):
                if args[0][0].lower() == 'w':
                    if self.game.turn() != gamestate.PLAYERS["white"]:
                        self.game.set_turn(gamestate.PLAYERS["white"])
                        self.agent.set_gamestate(self.game)

                elif args[0][0].lower() == 'b':
                    if self.game.turn() != gamestate.PLAYERS["black"]:
                        self.game.set_turn(gamestate.PLAYERS["black"])
                        self.agent.set_gamestate(self.game)
                else:
                    return (False, "Player not recognized")

            self.agent.search(self.move_time)
            move = self.agent.best_move()
            if (move == gamestate.GAMEOVER):
                return (False, "The game is already over" +
                        '\n' + 'The winner is ----> ' + str(self.send_command('winner')[1]))
            self.game.play(move)
            self.agent.move(move)
            return (True, chr(ord('a') + move[0]) + str(move[1] + 1))
        else:
            return(False, "The game is already over" +
                   '\n' + 'The winner is ----> ' + str(self.send_command('winner')[1]))

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
        if (self.game.winner() == gamestate.PLAYERS["white"]):
            return (True, "white")
        elif (self.game.winner() == gamestate.PLAYERS["black"]):
            return (True, "black")
        else:
            return (True, "none")

