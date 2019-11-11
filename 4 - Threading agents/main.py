from TreeThreadingAgent import TreeThreadingAgent		
from tkinter import *
from tkinter import ttk
from gui import Gui


def main():
    root = Tk()
    agent = TreeThreadingAgent()
    interface = Gui(root, agent)
    root.mainloop()

if __name__ == "__main__":
    main()
