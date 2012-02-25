#-*-python-*-
from BaseAI import BaseAI
from GameObject import *

import random
import board
from board import *

class AI(BaseAI):
  """The class implementing gameplay logic."""
  @staticmethod
  def username():
    return "Deep Blue"

  @staticmethod
  def password():
    return "password"

  def init(self):
    pass

  def end(self):
    pass

  def run(self):
    b = board(self, True)
    b.populate()
    validMoves = b.pruneMoves(b.getMoves())
    p = random.choice(validMoves)
    for move in validMoves:
      if move[0] == p[0]:
        print chr(move[0].getType()), ' File:', move[1][0], 'Rank:', move[1][1]
    print '======================='
    p[0].move(p[1][0], p[1][1], ord('Q'))
    return 1

  def __init__(self, conn):
      BaseAI.__init__(self, conn)
