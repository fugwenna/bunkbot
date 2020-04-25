from typing import List

HANGMAN_TEMPLATE: List[str] = ["o", "|", "/", "\\", "/", "\\", "", ""]
GALLOWS: str = """
                     Game Type: {9}
+________+           Last Guess By: {8}
|     |              Guesses: {7}
|     {0}          
|    {2}{1}{3}
|    {4} {5}
|
=============

{6}
"""