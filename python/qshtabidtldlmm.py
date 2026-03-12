from datetime import datetime, timedelta
from itertools import product
import random

# Pre-computed selector functions to avoid list creation in hot path
_CMP = (lambda a, b: a <= b, lambda a, b: a >= b)
_OPT = (min, max)

# qshtabidtldlmm: Quiescence Search
#                 History Table
#                 Alpha Beta pruning
#                 Iterative Deepening
#                 Time Limited
#                 Depth Limited
#                 MiniMax
class Searcher:
  def __init__(self):
    self.histTable = {}
    for to in product(range(1,9), range(1,9)):
      for fro in product(range(1,9), range(1,9)):
        if to != fro:
          self.histTable[(to,fro)] = 0
    self._node_count = 0

  # Iterative Deepening: searches at depth 1, then 2, etc. up to maxLimit.
  # Returns the best move from the deepest completed search, ensuring we
  # always have a valid move even if time runs out mid-search.
  def qshtabidtldlmm(self, board, maxLimit, qlimit, deadline):
    '''
    Calls abidtldlmm the appropriate amount of times
    Returns the best move
    '''
    self._node_count = 0
    alpha = float("-inf")
    beta  = float("inf")
    limit = 1

    bestMove = random.choice(board.getChildren())[0]
    while(limit <= maxLimit):
      possibleMove = self._dlmm(limit, qlimit, board, deadline, alpha, beta)
      if possibleMove is None:
        return bestMove
      bestMove = possibleMove
      limit+=1
    return bestMove

  # Root-level Maximizer with History Heuristic move ordering:
  # evaluates all moves from the current position using alpha-beta search,
  # sorts children by history table scores to try the most historically
  # successful moves first, improving pruning efficiency.
  def _dlmm(self, limit, qlimit, board, deadline, alpha, beta):
    '''
    This gets all the children of the passed in board
    Sorts them on there HT value
    This starts of the minimax functionality
    And calls the max() of those boards heuristic
    '''
    children = board.getChildren()
    children.sort(reverse=True, key=lambda x: self.histTable[(x[0][1],x[0][2])])
    best = None
    for child in children:
      self._node_count += 1
      if self._node_count & 127 == 0 and datetime.now() > deadline:
        return None
      child[1].h = self._dlminimax(limit-1, qlimit, child[1], 0, deadline, alpha, beta)
      if child[1].h is None:
        return None
      if best is None or child[1].h > best[1].h:
        best = child
      if child[1].h > alpha:
        alpha = child[1].h

    #neo, the one. get it!? hahahahaha. Aw, I'm sad now.
    neo = best[0]
    self.histTable[(neo[1],neo[2])] += 1
    return neo

  # Alpha-Beta Minimax with Quiescence Search extension:
  # Recursively evaluates positions, alternating between min and max players.
  # Uses alpha-beta pruning (first/second bounds) to cut off branches that
  # can't affect the outcome. When a capture causes a large heuristic swing
  # (detected by _quieSearch), extends the search depth to avoid the
  # horizon effect — where a shallow search stops right before a big exchange.
  # History table orders moves and records cutoff-causing moves.
  def _dlminimax(self, limit, qlimit, b, selector, deadline, first, second):
    '''
    Then calls its sell recursively until the depth and qlimit or time limit is reached
    It looks to see if a qsearch is needed, if it is it recurses that way
      otherwise it recurses with decresing the limit
    This calls either min or max on the children of the passed in board
    Then selected heuristic is then passed up to generate the best move
    '''
    parentHeur = b.h + b.endgameBonus()

    if limit <= 0:
      return parentHeur

    b.h = float("inf") if selector == 0 else float("-inf")

    children = b.getChildren()
    if not children:
      return b.h

    cmp_fn = _CMP[selector]
    opt_fn = _OPT[selector]

    children.sort(reverse=True, key=lambda x: self.histTable[(x[0][1],x[0][2])])
    best_h = None
    for child in children:
      self._node_count += 1
      if self._node_count & 127 == 0 and datetime.now() > deadline:
        return None
      if _quieSearch(child, qlimit, parentHeur) == True:
        child[1].h = self._dlminimax(limit, qlimit-1, child[1], selector^1, deadline, second, first)
      else:
        child[1].h = self._dlminimax(limit-1, qlimit, child[1], selector^1, deadline, second, first)
      if child[1].h is None:
        return None
      if best_h is None:
        best_h = child[1].h
      else:
        best_h = opt_fn(best_h, child[1].h)
      if cmp_fn(child[1].h, first):
        self.histTable[(child[0][1],child[0][2])] += 1
        return child[1].h
      second = opt_fn(second, child[1].h)

    return best_h

# Time Management: allocates a per-move time budget based on game phase.
# Early moves get fixed time, mid-game gets more aggressive allocation,
# and endgame conserves remaining time.
def timeHeur(ai):
  '''
  Gives each move a set amount of time, which is based on how many moves had been made
  '''
  for player in ai.players:
    if player.getId() == ai.playerID():
      timeLeft = player.getTime()

  numMoves = len(ai.moves)
  if numMoves < 10:
    delta = 15
  elif numMoves < 20:
    delta = timeLeft * 0.03
  elif numMoves < 30:
    delta = timeLeft * 0.10
  elif numMoves < 40:
    delta = timeLeft * 0.07
  else:
    delta = timeLeft * 0.01
  return datetime.now() + timedelta(seconds = delta)

# Quiescence Search trigger: detects tactical instability (a large heuristic
# jump, e.g. a piece capture) that would make a static evaluation unreliable.
# Returns True if the position should be searched deeper to resolve the tactic.
def _quieSearch(child, qlimit, parentHeur):
  '''
  Checks to see if there is a positive change of any piece worth more than a
    pawn being taken. If thats true, then qsearch should occur
  '''
  return (child[1].h - parentHeur) >= 3 and qlimit > 0
