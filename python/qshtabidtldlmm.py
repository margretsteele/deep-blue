from datetime import datetime, timedelta
from itertools import product
import random

#lolglobal
histTable = dict()

#filling in ht
for to in product(range(1,9), range(1,9)):
  for fro in product(range(1,9), range(1,9)):
    if to != fro:
      histTable[(to,fro)] = 0

# qshtabidtldlmm: Quiescence Search
#                 History Table
#                 Alpha Beta pruning
#                 Iterative Deepening
#                 Time Limited
#                 Depth Limited
#                 MiniMax
def qshtabidtldlmm(board, maxLimit, qlimit, deadline):
  '''
  Calls abidtldlmm the appropriate amount of times
  Returns the best move
  '''
  global histTable
  alpha = float("-inf")
  beta  = float("inf")
  limit = 1

  bestMove = random.choice(board.getChildren())[0]
  while(limit <= maxLimit):
    possibleMove = dlmm(limit, qlimit, board, deadline, alpha, beta)
    if possibleMove is None:
      return bestMove
    bestMove = possibleMove
    limit+=1
  return bestMove

def dlmm(limit, qlimit, board, deadline, alpha, beta):
  '''
  This gets all the children of the passed in board
  Sorts them on there HT value
  This starts of the minimax functionality
  And calls the max() of those boards heuristic
  '''
  children = board.getChildren()
  children.sort(reverse=True, key=lambda x: histTable[(x[0][1],x[0][2])])
  best = None
  for child in children:
    if datetime.now() > deadline:
      return None
    child[1].h = dlminimax(limit-1, qlimit, child[1], 0, deadline, alpha, beta)
    if child[1].h is None:
      return None
    if best is None or child[1].h > best[1].h:
      best = child
    if child[1].h > alpha:
      alpha = child[1].h

  #neo, the one. get it!? hahahahaha. Aw, I'm sad now.
  neo = best[0]
  histTable[(neo[1],neo[2])] += 1
  return neo

def dlminimax(limit, qlimit, b, selector, deadline, first, second):
  '''
  Then calls its sell recursively until the depth and qlimit or time limit is reached
  It looks to see if a qsearch is needed, if it is it recurses that way
    otherwise it recurses with decresing the limit
  This calls either min or max on the children of the passed in board
  Then selected heuristic is then passed up to generate the best move
  '''
  parentHeur = b.heruisticGen(True)

  if limit <= 0:
    return parentHeur

  b.h = float("inf") if selector == 0 else float("-inf")

  children = b.getChildren()
  if not children:
    return b.h

  children.sort(reverse=True, key=lambda x: histTable[(x[0][1],x[0][2])])
  for child in children:
    if datetime.now() > deadline:
      return None
    if quieSearch(child, qlimit, parentHeur) == True:
      child[1].h = dlminimax(limit, qlimit-1, child[1], selector^1, deadline, second, first)
    else:
      child[1].h = dlminimax(limit-1, qlimit, child[1], selector^1, deadline, second, first)
    if child[1].h is None:
      return None
    if [lte,gte][selector](child[1].h, first):
      histTable[(child[0][1],child[0][2])] += 1
      return child[1].h
    second = [min,max][selector]([second, child[1].h])

  b.h = [min,max][selector]([child[1].h for child in children])
  return b.h

def timeHeur(ai):
  '''
  Gives each move a set amount of time, which is baddsed on how many moves had been made
  '''
  for player in ai.players:
    if player.getId() == ai.playerID():
      timeLeft = player.getTime()

  numMoves = len(ai.moves)
  if numMoves < 10:
    delta = 5
  elif numMoves < 20:
    delta = timeLeft * 0.03
  elif numMoves < 30:
    delta = timeLeft * 0.10
  elif numMoves < 40:
    delta = timeLeft * 0.07
  else:
    delta = timeLeft * 0.01
  return datetime.now() + timedelta(seconds = delta)

def quieSearch(child, qlimit, parentHeur):
  '''
  Checks to see if there is a positive change of any piece worth more than a
    pawn being taken. If thats true, then qsearch should occur
  '''
  return (child[1].heruisticGen(True) - parentHeur) >= 3 and qlimit > 0

#greater than and less than functions
def gte(a, b):
  return a >= b

def lte(a, b):
  return a <= b
