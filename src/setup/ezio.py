from ..core.constants import BOLD, OKGREEN, OKBLUE, WARNING, ERROR


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
    print(ERROR + msg)


def prompt(msg: str) -> str:
    return input(OKBLUE + msg)
    