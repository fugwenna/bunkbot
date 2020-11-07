from os import walk
from os.path import join, splitext, sep
from typing import List

def get_cogs() -> list:
    """
    Dynamically load cogs depending on the
    formatting of the file name. 

    List of loaded cogs that are formatted with the
    appropriate _cog.py file extension will be the only
    things loaded.

    Returns
    --------
    List of file paths to cogs
    """
    cogs: List[str] = []

    for path, dirs, files in walk(join("src")):
        for f in files:
            file_path: str = join(path, f)
            cog_split: list = file_path.split("_")
            if len(cog_split) > 1 and cog_split[1] == "cog.py":
                sep_split: list = file_path.split(sep)
                sep_split[len(sep_split) - 1] = splitext(sep_split[len(sep_split) - 1])[0]
                cogs.append(".".join(sep_split))

    return cogs
