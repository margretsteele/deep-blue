#-*-python-*-
from BaseAI import BaseAI
from GameObject import *

import random
from minimax import abiddlmm, timeHeur
from board import board

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
    deadline = timeHeur(self)
    p = abiddlmm(b, 7, deadline)
    p[0].move(p[1][0], p[1][1], ord('Q'))
    return 1

  def __init__(self, conn):
      BaseAI.__init__(self, conn)
