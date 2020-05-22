OKWHITE = '\033[00m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
BOLD = '\033[1m'


def print_info(msg: str) -> None:
    print(OKBLUE + msg)


def print_success(msg: str, bold: bool = False) -> None:
    if bold:
        print(BOLD + OKGREEN + msg)
    else:
        print(OKGREEN + msg)


def print_warning(msg: str) -> None:
    print(WARNING + msg)


def print_fail(msg: str) -> None:
    print(FAIL + msg)


def prompt(msg: str) -> str:
    return input(OKBLUE + msg)
    