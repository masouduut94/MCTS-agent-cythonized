from mctsagent import mctsagent
from gamestate import gamestate
from tkinter import *
from tkinter import ttk
import numpy as np


class Gui:
    """
    This class is built to let the user have a better interaction with
    game.
    inputs =>
    root = Tk() => an object which inherits the traits of Tkinter class
    agent = an object which inherit the traits of mctsagent class.

    """

    def __init__(self, root, agent):
        self.root = root
        self.root.geometry('1366x690+0+0')
        self.agent = agent
        self.game = gamestate(8)
        self.time = 1
        self.agent.set_gamestate(self.game)
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
        self.frame_board = Frame(self.root)  # main frame for the play board
        self.canvas = Canvas(self.frame_board, bg=bg)
        self.scroll_y = ttk.Scrollbar(self.frame_board, orient=VERTICAL)
        self.scroll_x = ttk.Scrollbar(self.frame_board, orient=HORIZONTAL)

        # the notebook frame which holds the left panel frames

        self.notebook = ttk.Notebook(self.frame_board, width=350)
        self.panel_game = Frame(self.notebook, highlightbackground=self.colors['white'])
        self.panel_tournament = Frame(self.notebook, highlightbackground=self.colors['white'])
        self.developers = Frame(self.notebook, highlightbackground=self.colors['white'])
        self.contact = Frame(self.notebook, highlightbackground=self.colors['white'])

        # Introduction of items in left panel ---> Game

        self.game_size_value = IntVar()
        self.game_time_value = IntVar()
        self.game_turn_value = IntVar()
        self.turn = {1: 'white', 2: 'black'}
        self.game_size = Scale(self.panel_game)
        self.game_time = Scale(self.panel_game)
        self.game_turn = Scale(self.panel_game)
        self.generate = Button(self.panel_game)
        self.reset_board = Button(self.panel_game)

        # Introduction of items in left panel ---> Tournament

        self.tournament_size_val = IntVar()
        self.tournament_time_val = IntVar()
        self.tournament_num_val = IntVar()

        # -----------------------------------------------

        self.hex_board = []
        # Holds the IDs of hexagons in the main board for implementing the click and play functions
        self.game_size_value.set(8)
        self.game_time_value.set(1)
        self.size = self.game_size_value.get()
        self.time = self.game_time_value.get()
        self.tournament_size = Scale(self.panel_tournament)
        self.tournament_time = Scale(self.panel_tournament)
        self.board = self.game.board
        self.board = np.int_(self.board).tolist()
        self.array_to_hex(self.board)  # building the game board
        self.black_side()
        self.white_side()

        # Frame_header

        frame_header = Frame(self.root, bg=bg)
        frame_header.pack(fill=X)
        Label(frame_header, font=('Calibri', 40, 'bold'), fg='white',
              bg=bg, text='MB-Hex').pack(side=LEFT, padx=260, pady=10)

        # Frame_content

        self.frame_board.configure(width=1100, height=545, bg=bg)
        self.frame_board.pack(fill=X)
        self.notebook.add(self.panel_game, text='       Game       ')
        self.notebook.add(self.panel_tournament, text='    Tournament    ')
        self.notebook.add(self.developers, text='    Developers    ')
        self.notebook.add(self.contact, text='     Contact     ')
        self.notebook.pack(side=LEFT, fill=Y)
        self.canvas.configure(width=980, bg=bg, cursor='hand2')
        self.canvas.pack(side=LEFT, fill=Y)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.scroll_y.configure(command=self.canvas.yview)
        self.scroll_x.configure(command=self.canvas.xview)
        self.scroll_y.place(x=387, y=482)
        self.scroll_x.place(x=370, y=500)

        # Frame_left_panel

        """
        the left panel notebook ---->   Game

        """
        self.panel_game.configure(bg=bg)
        Label(self.panel_game, text=' Game ',
              font=('Calibri', 18, 'bold'),
              foreground='white', bg=bg, pady=5).pack(fill=X, side=TOP)
        Label(self.panel_game, text='Board size',
              font=('Calibri', 14, 'bold'),
              foreground='white', bg=bg, pady=30).pack(fill=X, side=TOP)  # label ---> Board size
        self.game_size.configure(from_=3, to=20, tickinterval=1, bg=bg, fg='white',
                                 orient=HORIZONTAL, variable=self.game_size_value)
        self.game_size.pack(side=TOP, fill=X)
        Label(self.panel_game, text='Time',
              font=('Calibri', 14, 'bold'),
              foreground='white', bg=bg, pady=30).pack(side=TOP, fill=X)  # label ---> Time
        self.game_time.configure(from_=1, to=20, tickinterval=1, bg=bg, fg='white',
                                 orient=HORIZONTAL, variable=self.game_time_value)
        self.game_time.pack(side=TOP, fill=X)
        Label(self.panel_game, text='Player',
              font=('Calibri', 14, 'bold'),
              foreground='white', bg=bg, pady=30).pack(side=TOP, fill=X)  # label ---> Turn
        self.game_turn.configure(from_=1, to=2, tickinterval=1, bg=bg, fg='white',
                                 orient=HORIZONTAL, variable=self.game_turn_value)
        self.game_turn.pack(side=TOP)
        Label(self.panel_game, text='   ',
              font=('Calibri', 14, 'bold'),
              foreground='white', bg=bg).pack(side=TOP, fill=X)
        self.reset_board.configure(text='Reset Board', pady=10,
                                   cursor='hand2', width=22,
                                   font=('Calibri', 12, 'bold'))
        self.reset_board.pack(side=LEFT)
        self.generate.configure(text='Generate', pady=10,
                                cursor='hand2', width=22,
                                font=('Calibri', 12, 'bold'))
        self.generate.pack(side=LEFT)
        """
        the left panel notebook ---->   tournament

        """
        self.panel_tournament.configure(bg=bg)
        Label(self.panel_tournament, text='Tournament',
              font=('Calibri', 18, 'bold'),
              foreground='white', bg=bg, pady=5).pack(side=TOP, fill=X)
        Label(self.panel_tournament, text='Board size',
              font=('Calibri', 14, 'bold'),
              foreground='white', bg=bg, pady=30).pack(side=TOP, fill=X)  # label ---> Board size
        self.tournament_size.configure(from_=3, to=20, tickinterval=1,
                                       bg=bg, fg='white', orient=HORIZONTAL,
                                       variable=self.game_size_value)
        self.tournament_size.pack(side=TOP, fill=X)
        Label(self.panel_tournament, text='Time',
              font=('Calibri', 14, 'bold'),
              foreground='white', bg=bg, pady=30).pack(side=TOP, fill=X)  # label ---> Time
        self.tournament_time.configure(from_=1, to=20, tickinterval=1,
                                       bg=bg, fg='white', orient=HORIZONTAL,
                                       variable=self.game_time_value)
        self.tournament_time.pack(side=TOP, fill=X)
        Label(self.panel_tournament, text='Game number',
              font=('Calibri', 14, 'bold'),
              foreground='white', bg=bg, pady=30).pack(side=TOP, fill=X)  # label ---> Game number
        self.tournament_number = Scale(self.panel_tournament, from_=0, to=100,
                                       tickinterval=10, bg=bg, fg='white', orient=HORIZONTAL,
                                       variable=self.tournament_num_val)
        self.tournament_number.pack(side=TOP, fill=X)
        Label(self.panel_tournament, text='  ',
              font=('Calibri', 14, 'bold'),
              foreground='white', bg=bg).pack(side=TOP, fill=X)
        Button(self.panel_tournament, text='   START   ', cursor='hand2',
               width=12, font=('Calibri', 12, 'bold'), pady=10).pack(side=TOP, fill=X)
        """
        the left panel notebook ---> Developers

        """
        self.developers.configure(bg=bg)
        Label(self.developers, text='Develped by:',
              font=('Calibri', 18, 'bold'), justify=LEFT,
              foreground='white', bg=bg, pady=20).pack(side=TOP, fill=X)
        Label(self.developers, text='Masoud Masoumi Moghadam\nNemat Rahmani\nMaster of science Students at',
              font=('Calibri', 15, 'bold'), wraplength=300, justify=LEFT,
              foreground='white', bg=bg, pady=10).pack(side=TOP, fill=X)
        Label(self.developers, text='Supervised by:',
              font=('Calibri', 18, 'bold'), wraplength=200, justify=LEFT,
              foreground='white', bg=bg, pady=20).pack(side=TOP, fill=X)
        Label(self.developers, text='Dr. Tahmouresnezhad',
              font=('Calibri', 15, 'bold'), wraplength=300, justify=LEFT,
              foreground='white', bg=bg, pady=10, padx=20).pack(side=TOP, fill=X)
        Label(self.developers, text=' ', bg=bg).pack(side=TOP, fill=X)
        Label(self.developers, text='Summer 2016',
              font=('Calibri', 18, 'bold'), wraplength=350, justify=LEFT,
              foreground='white', bg=bg, pady=40).pack(side=TOP, fill=X)
        """
        the left panel notebook ---> Contact

        """
        self.contact.configure(bg=bg)
        Label(self.contact, text='Masoud Masoumi Moghadam',
              font=('Calibri', 15, 'bold'), justify=LEFT,
              fg='white', bg=bg, pady=10).pack(side=TOP)
        Label(self.contact, text='masouduut94@gmail.com',
              font=('Calibri', 15, 'bold'), justify=LEFT,
              fg='white', bg=bg, pady=10).pack(side=TOP)
        Label(self.contact, text='Nemat Rahmani',
              font=('Calibri', 15, 'bold'), justify=LEFT,
              fg='white', bg=bg, pady=10).pack(side=TOP)
        Label(self.contact, text='nemat_rahmani@gmail.com',
              font=('Calibri', 15, 'bold'), justify=LEFT,
              fg='white', bg=bg, pady=10).pack(side=TOP)
        Label(self.contact, text='Dr.Tahmoresnezhad',
              font=('Calibri', 15, 'bold'), justify=LEFT,
              fg='white', bg=bg, pady=10).pack(side=TOP)
        Label(self.contact, text='j.tahmores@gmail.com',
              font=('Calibri', 15, 'bold'), justify=LEFT,
              fg='white', bg=bg, pady=10).pack(side=TOP)

        # Binding Actions

        """
        Binding triggers for the actions defined in the class.

        """
        self.canvas.bind('<1>', self.mouse_click)
        self.game_size.bind('<ButtonRelease>', self.set_size)
        self.tournament_size.bind('<ButtonRelease>', self.set_size)
        self.game_time.bind('<ButtonRelease>', self.set_time)
        self.tournament_time.bind('<ButtonRelease>', self.set_time)
        self.generate.bind('<ButtonRelease>', self.generate_move)
        self.reset_board.bind('<ButtonRelease>', self.reset)

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
                hx = self.hexagon(temp_array, 1)
            else:
                hx = self.hexagon(temp_array, 2)
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
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        idd = self.canvas.find_overlapping(x, y, x, y)
        idd = list(idd)
        if len(idd) is not 0:
            clicked_cell = idd[0]
            if any([clicked_cell in x for x in self.hex_board]):
                coordinated_cell = clicked_cell - self.hex_board[0][0]
                if coordinated_cell % self.size == 0:
                    row = int(coordinated_cell / self.size)
                else:
                    row = int(coordinated_cell / self.size)
                col = (coordinated_cell % self.size)
                print([row, col], 'id = ', coordinated_cell)
                turn = self.turn[self.game_turn_value.get()]
                print('play ', turn, ' ', str(chr(65 + row)) + str(col))
                if self.board[row][col] == 0:
                    self.board[row][col] = self.game_turn_value.get()
                    if self.game_turn_value.get() == 1:
                        self.game_turn_value.set(2)
                    else:
                        self.game_turn_value.set(1)
                self.canvas.delete('all')
                self.hex_board.clear()
                self.array_to_hex(self.board)
                self.black_side()
                self.white_side()
                y = row
                x = col
                if turn[0].lower() == 'w':
                    if self.game.turn() == gamestate.PLAYERS["white"]:
                        self.game.play((x, y))
                        self.agent.move((x, y))
                        return (str(self.game))
                    else:
                        self.game.place_white((x, y))
                        self.agent.set_gamestate(self.game)
                        return (str(self.game))
                elif turn[0].lower() == 'b':
                    if self.game.turn() == gamestate.PLAYERS["black"]:
                        self.game.play((x, y))
                        self.agent.move((x, y))
                        return (str(self.game))
                    else:
                        self.game.place_black((x, y))
                        self.agent.set_gamestate(self.game)
                        return (str(self.game))

    def set_size(self, event):
        """
        It changes the board size and reset the whole game.

        """
        self.canvas.delete('all')
        self.size = self.game_size_value.get()
        self.game = gamestate(self.size)
        self.agent.set_gamestate(self.game)
        self.board = self.game.board
        self.board = np.int_(self.board).tolist()
        self.hex_board.clear()
        self.array_to_hex(self.board)
        self.black_side()
        self.white_side()

    def set_time(self, event):
        """
        It changes the time for CPU player to think and generate a move.

        """
        self.time = self.game_time_value.get()
        print('The CPU time = ', self.time, ' seconds')

    def winner(self):
        """
        Return the winner of the current game (black or white), none if undecided.

        """
        if self.game.winner() == gamestate.PLAYERS["white"]:
            return "white"
        elif self.game.winner() == gamestate.PLAYERS["black"]:
            return "black"
        else:
            return "none"

    def generate_move(self, event):
        """
        By pushing the generate button, It produces an appropriate move
        by using monte carlo tree search algorithm for the player which
        turn is his or hers! .

        """
        if self.winner() == 'none':
            self.agent.search(self.time)
            move = self.agent.best_move()  # the move is tuple like (3, 1)
            if (move == gamestate.GAMEOVER):  # which denotes a cell in the array
                return (False, "The game is already over" +
                        '\n' + 'The winner is ----> ' + str(self.winner()))
            self.game.play(move)
            self.agent.move(move)
            row, col = move[0], move[1]  # Relating the 'move' tuple with index of self.board
            self.board[col][row] = self.game_turn_value.get()
            if self.game_turn_value.get() == 1:  # change the turn of players
                self.game_turn_value.set(2)
            else:
                self.game_turn_value.set(1)
            self.canvas.delete('all')  # Refreshing the canvas
            self.hex_board.clear()
            self.array_to_hex(self.board)
            self.black_side()
            self.white_side()
            return (True, chr(ord('a') + move[0]) + str(move[1] + 1))
        else:
            return (False, "The game is already over" +
                    '\n' + 'The winner is ----> ' + str(self.winner()))

    def reset(self, event):
        """
        By clicking on the Reset button game board would be cleared
        for a new game

        """
        self.game = gamestate(self.game.size)
        self.agent.set_gamestate(self.game)
        self.set_size(event)
        self.game_turn_value.set(1)
