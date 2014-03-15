#-------------------------------------------------------------------------------
# Name:        minesweeper
# Purpose:     a very simple minsweeper game implemented with python + Tkinter
# Author:      Arthur
# Created:     19/02/2014

# Note: the code relies on Numpy and Scipy (signal.convolve, specifically) to
#       save efforts in computing mine counts. The dependency can be removed by
#       replacing matrix convolution with explicit loops and enumerations, though.

# TODO: [x] open empty, [x] timer  [3] structure the directory
# 
# Learned: 1) how to bind events for control arrays. 2) how to set timers
#-------------------------------------------------------------------------------
from Tkinter import *
import tkMessageBox
import numpy as np
import scipy.signal
import time
import threading

class Minesweeper():
    def __init__(self, master):
        # parameters
        self.width = 9
        self.mine_num = 10
        self.size = self.width * self.width

        # import images
        self.tile_plain = PhotoImage(file = "images/tile_plain.gif")
        self.tile_clicked = PhotoImage(file = "images/tile_clicked.gif")
        self.tile_mine = PhotoImage(file = "images/tile_mine.gif")
        self.tile_flag = PhotoImage(file = "images/tile_flag.gif")
        self.tile_wrong = PhotoImage(file = "images/tile_wrong.gif")
        self.tile_explode = PhotoImage(file = "images/tile_explode.gif")
        self.tile_no = []
        for x in range(1, 8):
            self.tile_no.append(PhotoImage(file = "images/tile_"+str(x)+".gif"))

        # create main panel
        self.parent = master
        self.parent.title("Minesweeper")
        self.frame = Frame(self.parent)
        self.frame.pack()

        # create buttons
        self.buttons = []
        for i in range(self.size):
            btn = MineButton(self.frame)
            btn.id = i
            btn.r = i / self.width
            btn.c = i % self.width
            btn.bind("<Button-1>", lambda event, idx=i : self.lclick(idx))
            btn.bind("<Button-3>", lambda event, idx=i : self.rclick(idx))
            btn.grid(row = btn.r, column = btn.c)
            self.buttons.append(btn)

        # create info labels, timers
        self.flag_label = Label(self.frame)
        self.open_label = Label(self.frame)
        self.time_label = Label(self.frame)
        self.flag_label.grid(row = 10, column = 0, columnspan = 3)
        self.open_label.grid(row = 10, column = 3, columnspan = 3)
        self.time_label.grid(row = 10, column = 6, columnspan = 4)

        # generate mine fields
        self.init_game()
        #self.cheat()

    def cheat(self):
        for idx, btn in enumerate(self.buttons[:-1]):
            if btn.mine == 0:
                time.sleep(0.02)
                self.lclick(idx)

    def init_game(self):
        # generate mines at random
        idx = np.arange(self.size)
        np.random.shuffle(idx)
        mines = np.zeros(self.size)
        mines[idx[:self.mine_num]] = 1
        mines = np.reshape(mines, (self.width, self.width))

        # compute mine counts
        template = np.ones((3, 3))
        num = scipy.signal.convolve(mines, template, mode = 'same')

        # set mine fields
        for btn in self.buttons:
            btn.config(image = self.tile_plain)
            btn.mine = mines[btn.r, btn.c]
            btn.num = int(num[btn.r, btn.c])
            btn.clicked = False
            btn.marked = False
        self.open_counter = 0
        self.flag_counter = self.mine_num
        self.sec = 0
        self.flag_label.config(text = "Mines: %2d" %(self.flag_counter))
        self.open_label.config(text = "Open: %2d" %(self.open_counter))
        self.update_secs()

    def update_secs(self):
        self.time_label.config(text = "Sec: %3d" %(self.sec))
        self.sec += 1
        self.parent.after(1000, self.update_secs)

    def open_zeros(self, btn):
        dx = [0, 1, 1, 1, 0, -1, -1, -1]
        dy = [-1, -1, 0, 1, 1, 1, 0, -1]
        for i in range(8):
            newr = btn.r + dy[i]
            newc = btn.c + dx[i]
            if 0 <= newr and newr < self.width \
                and 0 <= newc and newc <self.width:
                self.lclick(newr * self.width + newc)

    def lclick(self, idx):
        btn = self.buttons[idx]
        if btn.marked or btn.clicked: return
        btn.clicked = True
        if btn.mine == 0:
            if btn.num == 0:
                btn.config(image = self.tile_clicked)
                self.open_zeros(btn)
            else:
                btn.config(image = self.tile_no[btn.num - 1])
            self.open_counter += 1
            self.open_label.config(text = "Open: %2d" %(self.open_counter))
            if self.open_counter == self.size - self.mine_num:
                self.show_all_mines(True)
                self.gameover("You Win")
        else:
            self.show_all_mines(flags = False)
            btn.config(image = self.tile_explode)
            self.gameover("You Lose!")

    def rclick(self, idx):
        btn = self.buttons[idx]
        if btn.clicked: return
        if btn.marked:
            btn.config(image = self.tile_plain)
            self.flag_counter += 1
            btn.marked = False
        elif self.flag_counter > 0:
            btn.config(image = self.tile_flag)
            self.flag_counter -= 1
            btn.marked = True
        self.flag_label.config(text = "Mines: %2d" %(self.flag_counter))

    def show_all_mines(self, flags):
        for btn in self.buttons:
            if flags:  # winning, show all mine flags
                if btn.mine == 1:
                    btn.config(image= self.tile_flag)
            else:  # losing, show remaining mines and mark wrong flags
                if btn.marked and not btn.mine == 1:
                    btn.config(image = self.tile_wrong)
                if btn.mine == 1 and not btn.marked:
                    btn.config(image = self.tile_mine)

    def gameover(self, message):
        if tkMessageBox.askyesno("Game Over!", message + "\nStart again?"):
            self.init_game()
        else:
            self.frame.quit()
            self.parent.destroy()


class MineButton(Button, object):
    def __init__(self, master, **kwargs):
        Button.__init__(self, master, **kwargs)

##class TimerClass(threading.Thread):
##    def __init__

if __name__ == '__main__':
    global root
    root = Tk()
    game = Minesweeper(root)
    root.mainloop()
