import curses

# This implelents the curses interface. Curses doesn't provide key-up
# events, so you have to explicitly stop by pressing space.
class CursesInterface:
    __slots__ = ["win", "y"]

    keys    = {
        27:                 "quit",
        ord(" "):           "stop",
        ord("w"):           "forward",
        ord("s"):           "backward",
        ord("a"):           "left",
        ord("d"):           "right",
        curses.KEY_UP:      "faster",
        curses.KEY_DOWN:    "slower",
        curses.KEY_RIGHT:   "turn-faster",
        curses.KEY_LEFT:    "turn-slower",
    }

    def __init__ (self):
        self.y  = 0

    def setup (self):
        self.win    = curses.initscr()
        curses.savetty()
        curses.noecho()
        curses.cbreak()
        self.win.keypad(1)

    def quit (self):
        curses.resetty()
        curses.endwin()

    def get_actions (self):
        k   = self.win.getch();
        if k in self.keys:
            return [self.keys[k]]
        else:
            return []

    def puts (self, msg):
        self.win.addstr(0, self.y, msg)
        self.y = self.y + 1

    def update (self):
        self.win.refresh()
        self.y  = 0

