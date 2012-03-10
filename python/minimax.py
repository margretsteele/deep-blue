def iddlmm(board, maxLimit):
  '''
  Calls dlmm the appropriate amount of times
  Returns the best move
  '''
  limit = 1
  while(limit <= maxLimit):
    bestMove = dlmm(limit, board)
    limit+=1
  return bestMove

def dlmm(limit, board):
  '''
  This gets all the children of the passed in board
  And calls the max() of those boards heuristic
  This starts of the minimax functionality
  '''
  children = board.getChildren()
  for child in children:
    child[1].h = dlminimax(limit-1, child[1], 0)
  return max(children, key = lambda x:x[1].h)[0]

def dlminimax(limit, b, selector):
  '''
  This calls its sell recursively until the limit is reached 
  This calls either min or max on the children of the passed in board
  Then selected heuristic is then passed up to generate the best move
  '''
  if limit == 0:
    return b.h
  children = [x[1] for x in b.getChildren()]
  if not children:
    return b.h
  for child in children:
    child.h = dlminimax(limit-1, child, selector^1)
  b.h = [min,max][selector]([child.h for child in children])
  return b.h  








  

