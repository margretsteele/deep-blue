#-*-python-*-
from BaseAI import BaseAI
from GameObject import *

import random
from qshtabidtldlmm import Searcher, timeHeur
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
    self.searcher = Searcher()

  def end(self):
    pass

  def run(self):
    b = board(self, True)
    b.populate()
    deadline = timeHeur(self)
    p = self.searcher.qshtabidtldlmm(b, 4, 3, deadline)
    p[0].move(p[1][0], p[1][1], ord('Q'))
    return 1

  def __init__(self, conn):
      BaseAI.__init__(self, conn)
