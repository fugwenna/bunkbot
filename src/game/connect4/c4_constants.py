from typing import List

EMPTY_PIECE: str = ":white_circle: "
PLAYER1_PIECE: str = ":green_circle: "
PLAYER2_PIECE: str = ":red_circle: "
WIN_PIECE: str = ":blue_circle: "
#EMPTY_PIECE: str = "`⚪` "
#PLAYER1_PIECE: str = "`🟢` "
#PLAYER2_PIECE: str = "`🔴` "
#WIN_PIECE: str = "`🔵` "
BOARD_HEIGHT: int = 6
BOARD_WIDTH: int = 7
BOARD_TEMPLATE: str = """ Type a **number** to drop a piece in that column

{5}
{4}
{3}
{2}
{1}
{0}
 --- ---  ---  ---  ---   ---  ---
  1     2     3    4     5     6    7
"""