import readline  # noqa: F401

from colorama import Fore, Style, init

init(autoreset=True)


# Global colors
class C:
    HEADER = Fore.MAGENTA + Style.BRIGHT
    MENU = Fore.CYAN + Style.BRIGHT
    INPUT = Fore.YELLOW + Style.BRIGHT
    SUCCESS = Fore.GREEN + Style.BRIGHT
    ERROR = Fore.RED + Style.BRIGHT
    RESET = Style.RESET_ALL

    BLUE = Fore.BLUE + Style.BRIGHT


# Global clean color
class CC:
    START = "\001"
    END = "\002"

    MAGENTA = f"{START}{C.HEADER}{END}"
    GREEN = f"{START}{C.SUCCESS}{END}"
    BLUE = f"{START}{C.BLUE}{END}"
    CYAN = f"{START}{C.MENU}{END}"
    YELLOW = f"{START}{C.INPUT}{END}"
    RED = f"{START}{C.ERROR}{END}"
    RESET = f"{START}{C.RESET}{END}"
