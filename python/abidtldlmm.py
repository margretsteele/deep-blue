from datetime import datetime, timedelta


def abiddlmm(board, maxLimit, deadline):
  '''
  Calls dlmm the appropriate amount of times
  Returns the best move
  '''
  alpha = float("-inf")
  beta  = float("inf")
  limit = 1
  while(limit <= maxLimit):
    possibleMove = dlmm(limit, board, deadline, alpha, beta)
    if possibleMove is None:
      return bestMove
    bestMove = possibleMove
    limit+=1
  return bestMove

def dlmm(limit, board, deadline, alpha, beta):
  '''
  This gets all the children of the passed in board
  And calls the max() of those boards heuristic
  This starts of the minimax functionality
  '''
  children = board.getChildren()
  for child in children:
    if datetime.now() > deadline:
      return None
    child[1].h = dlminimax(limit-1, child[1], 0, deadline, alpha, beta)
  return max(children, key = lambda x:x[1].h)[0]

def dlminimax(limit, b, selector, deadline, alpha, beta):
  '''
  This calls its sell recursively until the limit is reached 
  This calls either min or max on the children of the passed in board
  Then selected heuristic is then passed up to generate the best move
  '''
  b.h = float("inf") if selector == 0 else float("-inf")
  if limit == 0:
    return b.h
  children = [x[1] for x in b.getChildren()]
  if not children:
    return b.h
  for child in children:
    if datetime.now() > deadline:
      return None
    child.h = dlminimax(limit-1, child, selector^1, deadline, alpha, beta)
    if selector == 0:
      if child.h <= alpha:
        print "fail high"
        return child.h
      beta = min([beta, child.h])
    else:
      if child.h >= beta:
        print "fail low"
        return child.h
      alpha = max([alpha, child.h])

  b.h = [min,max][selector]([child.h for child in children])
  return b.h  

def timeHeur(ai):
  return datetime.now() + timedelta(seconds = 30)




  

