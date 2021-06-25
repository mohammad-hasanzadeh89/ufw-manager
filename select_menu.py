import sys
import tty
import termios


class Menu:
    """Interactive select menu.
    Attributes:
        opts (list of str): Options for the user to choose from.
    """
    opts = []

    def __init__(self, options, message=None):
        """Interactive select menu.
        Args:
            options (list of str): Options for the user to choose from.
            message (str, optional): Message to be displayed before showing options
        """
        self.opts = options
        if not message == None:
            print(message)

    def _getch(self):
        # Read single keypress from user
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(sys.stdin.fileno())
            ch = ""
            for _ in range(3):  # Reading maximum 3 bytes
                ch += sys.stdin.read(1)
                if not ch.startswith('\x1b'):
                    # Exit if no escape sequence (used by arrow keys)
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def _get_input(self):
        # Convert keycode input into commands
        while(1):
            k = self._getch()
            if k != "":
                break
        keycodes = {'\x1b[A': "prev", '\x1b[B': "next",
                    '\x1b[C': "next", '\x1b[D': "prev", "\n": "select"}
        if k in keycodes.keys():
            return keycodes[k]
        return None

    def __call__(self):
        """Creates an interactive select menu for the user. The user's choice is selected with up/down/left/right arrow keys and confirmed with the enter/return key.
        Returns:
            Option (from list) selected by user.
        """
        selected = 0
        while True:
            # Infinite loop broken by return
            print("\r", end="")
            for ind, opt in enumerate(self.opts):
                if ind == selected:
                    print("\033[0;30;47m{}\033[0m".format(opt), end=" | ")
                else:
                    print(opt, end=" | ")
            # Forcing options to show (would be delayed until after keypress in Python 3)
            sys.stdout.flush()

            key_pressed = None
            while key_pressed == None:
                # Looping until valid key pressed
                key_pressed = self._get_input()
                if (key_pressed == "next") and selected < (len(self.opts) - 1):
                    selected += 1
                elif (key_pressed == "prev") and selected > 0:
                    selected -= 1
                elif key_pressed == "select":
                    print("")
                    return self.opts[selected]


# while True:
#     user_select = Menu(
#         ['dynamic', 'static'],
#         "Please enter one of these keys type")
#     result = user_select()
#     print(result)
#     break
