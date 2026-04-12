import readline # noqa: F401

from colorama import Fore, Style, init
init(autoreset=True)


# Dictionary Warna Global
class C:
    HEADER = Fore.MAGENTA + Style.BRIGHT
    MENU = Fore.CYAN + Style.BRIGHT
    INPUT = Fore.YELLOW + Style.BRIGHT
    SUCCESS = Fore.GREEN + Style.BRIGHT
    ERROR = Fore.RED + Style.BRIGHT
    RESET = Style.RESET_ALL

    BLUE = Fore.BLUE + Style.BRIGHT

class CC:
    START = "\001"
    END = "\002"

    BLUE = f"{START}{C.BLUE}{END}"
    CYAN = f"{START}{C.MENU}{END}"
    YELLOW = f"{START}{C.INPUT}{END}"
    RED = f"{START}{C.ERROR}{END}"
    RESET = f"{START}{C.RESET}{END}"
