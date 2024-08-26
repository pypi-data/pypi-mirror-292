"""
Module for interactive command line menu. Simply accepts a list of str-able objects
and allows user to select using arrow keys.
"""
import sys
if sys.platform != "win32":
    raise NotImplementedError("This module is only available on Windows.")
from typing import Any
import msvcrt
import ctypes

stdout = -11
enable_ansi_codes = 7
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(stdout), enable_ansi_codes)

ANSI_MOVE_CURSOR = "\x1b[{up}F\r\x1b[{right}C"
ANSI_HIGHLIGHT   = "\x1b[30;47m"
ANSI_YELLOW      = "\x1b[93m"
ANSI_BLUE        = "\x1b[94m"
ANSI_RESET       = "\x1b[0m"
SPECIAL_KEY = 224
UP_ARROW    = 72
DOWN_ARROW  = 80
ENTER_KEY   = 13
CTL_C       = 3
BACKSPACE   = 8
SPACEBAR    = 32

class Menu:
    def __init__(self, options: list, label: str, window_size: int=10) -> None:
        assert options
        assert label
        assert 1 < window_size
        if len(options) < window_size:
            window_size = len(options)

        self.options_original = options
        self.options_current = options
        self.indices = []
        self.search_string = ""
        self.label = label
        self.selected_index = 0
        self.window_top = 0
        self.window_original_size = window_size
        self.window_current_size = window_size
        self.help_string = "Enter: Select, Ctl+C: Cancel"

    def show(self):
        print(f"{ANSI_BLUE}{self.label}>{ANSI_RESET}")
        self.printMenu()
        while True:
            something_changed = False
            char = self.getChar()
            if char == SPECIAL_KEY:
                char = self.getChar()
                if 1 < len(self.options_current):
                    # Update selected index
                    if char == UP_ARROW:
                        self.selected_index = (self.selected_index - 1) % len(self.options_current)
                        something_changed = True
                    elif char == DOWN_ARROW:
                        self.selected_index = (self.selected_index + 1) % len(self.options_current)
                        something_changed = True
                
                    # Update window
                    if something_changed:
                        bottom = self.window_top + self.window_current_size
                        if self.selected_index < self.window_top:
                            self.window_top = self.selected_index
                        elif bottom <= self.selected_index:
                            self.window_top = self.selected_index - self.window_current_size + 1
            elif self.isAscii(char) or (char == SPACEBAR and 0 < len(self.search_string)):
                # TODO: search string
                pass
            elif char == BACKSPACE and 0 < len(self.search_string):
                # TODO: search string
                pass
            elif char == ENTER_KEY:
                if self.options_current:
                    self.printSelected()
                    return self.options_original[self.selected_index]
            elif char == CTL_C:
                self.clearMenu(clear_label=True)
                print("cancelled")
                return None

            if something_changed:
                self.clearMenu()
                self.printMenu()

    def getChar(self):
        return ord(msvcrt.getch())

    def isAscii(self, char):
        return (33 <= char and char <= 126)
    
    def clearMenu(self, clear_label=False):
        if clear_label:
            print("\x1b[0G\x1b[J", end="", flush=True)
        else:
            print("\x1b[J")

    def printMenu(self):
        bottom = self.window_top + self.window_current_size
        for i in range(self.window_top, bottom):
            if i == self.selected_index:
                print(f"{ANSI_HIGHLIGHT}{self.options_current[i]}{ANSI_RESET}")
            else:
                print(self.options_current[i])
        print(f"{ANSI_YELLOW}{self.help_string}{ANSI_RESET}\n{ANSI_MOVE_CURSOR.format(up=self.window_current_size + 2, right=len(self.label) + len(self.search_string) + 1)}", end="", flush=True)

    def printSelected(self):
        self.clearMenu(clear_label=True)
        print(f"{self.label}> {self.options_current[self.selected_index]}")

def makeSelection(options: list[Any], label: str, window_size: int=None) -> Any:
    """
    Entry point for menu selection.

    Parameters
    ----------
    options
        List of str-able objects.
    label
        Label to describe the items being selected.
    window_size
        Max number of items to show at once.

    Returns
    -------
    Selected value.
    """
    if window_size:
       return Menu(options, label, window_size).show()
    else:
       return Menu(options, label).show()

if __name__ == "__main__":
    makeSelection(["interactive", "cli", "menu"], "make_selection")