import numpy as np
from unionfind import unionfind

class gamestate:
    """
    Stores information representing the current state of a game of hex, namely
    the board and the current turn. Also provides functions for playing the game
    """
    # dictionary associating numbers with players for book keeping
    PLAYERS = {"none": 0, "white": 1, "black": 2}

    # move value of -1 indicates the game has ended so no move is possible
    GAMEOVER = -1

    # represent edges in the union find strucure for win detection
    EDGE1 = 1
    EDGE2 = 2

    neighbor_patterns = ((-1, 0), (0, -1), (-1, 1), (0, 1), (1, 0), (1, -1))

    def __init__(self, size):
        """
        Initialize the game board and give white first turn.
        Also create our union find structures for win checking.
        """
        self.size = size  # the number of cells in each row or column
        self.toplay = self.PLAYERS["white"]  # the turn of player in each state
        self.board = np.zeros((size, size))  # board representation
        self.board = np.int_(self.board)  
        self.white_groups = unionfind()  # White zones
        self.black_groups = unionfind()  # Black zones
        self.empty_cells = []
        for y in range(self.size):
            for x in range(self.size):
                self.empty_cells.append((x, y))


    def play(self, cell):
        """
        Play a stone of the current turns color in the passed cell.
        """
        if (self.toplay == self.PLAYERS["white"]):
            self.place_white(cell)
            self.toplay = self.PLAYERS["black"]
        elif (self.toplay == self.PLAYERS["black"]):
            self.place_black(cell)
            self.toplay = self.PLAYERS["white"]
        self.empty_cells.remove(cell)

    def place_white(self, cell):
        """
        Place a white stone regardless of whose turn it is.
        """
        if (self.board[cell] == self.PLAYERS["none"]):
            self.board[cell] = self.PLAYERS["white"]
        else:
            raise ValueError("Cell occupied")
        # if the placed cell touches a white edge connect it appropriately
        if (cell[0] == 0):
            self.white_groups.join(self.EDGE1, cell)
        if (cell[0] == self.size - 1):
            self.white_groups.join(self.EDGE2, cell)
        # join any groups connected by the new white stone
        for n in self.neighbors(cell):
            if (self.board[n] == self.PLAYERS["white"]):
                self.white_groups.join(n, cell)

    def place_black(self, cell):
        """
        Place a black stone regardless of whose turn it is.
        """
        if (self.board[cell] == self.PLAYERS["none"]):
            self.board[cell] = self.PLAYERS["black"]
        else:
            raise ValueError("Cell occupied")
        # if the placed cell touches a black edge connect it appropriately
        if (cell[1] == 0):
            self.black_groups.join(self.EDGE1, cell)
        if (cell[1] == self.size - 1):
            self.black_groups.join(self.EDGE2, cell)
        # join any groups connected by the new black stone
        for n in self.neighbors(cell):
            if (self.board[n] == self.PLAYERS["black"]):
                self.black_groups.join(n, cell)

    def turn(self):
        """
        Return the player with the next move.
        """
        return self.toplay

    def set_turn(self, player):
        """
        Set the player to take the next move.
        """
        if (player in self.PLAYERS.values() and player != self.PLAYERS["none"]):
            self.toplay = player
        else:
            raise ValueError('Invalid turn: ' + str(player))

    def winner(self):
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

    def neighbors(self, cell):
        """
        Return list of neighbors of the passed cell.
        """
        x = cell[0]
        y = cell[1]
        return [(n[0] + x, n[1] + y) for n in self.neighbor_patterns
                if (0 <= n[0] + x and n[0] + x < self.size and 0 <= n[1] + y and n[1] + y < self.size)]

    def moves(self):
        """
        Get a list of all moves possible on the current board.
        """
        return self.empty_cells

    def __str__(self):
        """
        Print an ascii representation of the game board.
        """
        white = 'W'
        black = 'B'
        empty = '.'
        ret = '\n'
        coord_size = len(str(self.size))
        offset = 1
        ret += ' ' * (offset + 2)
        for x in range(self.size):  # this line prints out the characters (A, B, C, D, ...)
            ret += chr(ord('A') + x) + ' ' * offset * 2  # sets A, B, C, D, ...
        ret += '\n'
        for y in range(self.size):
            ret += str(y + 1) + ' ' * (offset * 2 + coord_size - len(str(y + 1)))  # Adds spaces after numbers (1, 2, 3)
            for x in range(self.size):
                if (self.board[x, y] == self.PLAYERS["white"]):  # if stone in direction (x,y) is a white stone put W
                    ret += white
                elif (self.board[x, y] == self.PLAYERS["black"]):  # if stone in direction (x,y) is a black stone put B
                    ret += black
                else:
                    ret += empty  # if stone in direction (x,y) is neither white nor black put '.'
                ret += ' ' * offset * 2
            ret += white + "\n"
        ret += ' ' * (offset * 2 + 1) + (black + ' ' * offset * 2) * self.size
        return ret


