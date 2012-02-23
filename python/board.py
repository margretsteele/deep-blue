#Author    : Margret Steele
#Class     : AI
#Assignment: Game 1 
#File      : board.py

class board(): 
  def __init__(self, ai):
    self.locations = dict()
    self.size      = 8
    self.ai        = ai
  
  def populate(self):
    for piece in self.ai.pieces:
      self.locations[(piece.getFile(), piece.getRank())] = piece

  #returns all the adjacent neighbors of the passed in state
  def getMoves(self):
    moves = []
    for loc in self.locations:
      current = self.locations[loc]
      if self.isPieceMine(current):
        if current.getType() == ord('P'): 
          moves += self.pawnMove(current.getFile(), current.getRank())
        if current.getType() == ord('R'): 
          moves += self.rookMove(current.getFile(), current.getRank())
        if current.getType() == ord('B'): 
          moves += self.bishopMove(current.getFile(), current.getRank())
        if current.getType() == ord('N'): 
          moves += self.knightMove(current.getFile(), current.getRank())
        if current.getType() == ord('Q'):
          moves += self.queenMove(current.getFile(), current.getRank())
        if current.getType() == ord('K'): 
          moves += self.kingMove(current.getFile(), current.getRank())
    return moves     

  def pawnMove(self, file, rank):
    '''
    Depending on what color I am:
    First add generic move forward once
    Second if havent moved add move forward twice
    Third add capture moves
    Look through those moves, only add valid moves
    '''
    (x, y)         = (file, rank)
    moves          = []
    validPositions = []
    piece          = self.locations[(file, rank)]

    if self.amIBlack() == False:
      if (x,y+1) not in self.locations:
        validPositions.append((piece, (x,y+1)))
      if self.locations[(x,y)].getHasMoved() == 0 and \
                       (x,y+2) not in self.locations and \
                       (x,y+1) not in self.locations:

        validPositions.append((piece, (x,y+2)))
      
      for position in [(x+1,y+1), (x-1,y+1)]:
        if position in self.locations:
          if self.isPieceMine(self.locations[position]) == False:
            validPositions.append((piece, position))
      
    else:
      if (x,y-1) not in self.locations:
        validPositions.append((piece, (x,y-1)))
      if self.locations[(x,y)].getHasMoved() == 0 and \
                       (x,y-2) not in self.locations and \
                       (x,y-1) not in self.locations:
        validPositions.append((piece, (x,y-2)))
      
      for position in [(x+1,y-1), (x-1,y-1)]:
        if position in self.locations:
          if self.isPieceMine(self.locations[position]) == False:
            validPositions.append((piece, position))
      

    for loc in validPositions:
      if self.isMoveOnBoard(loc[1][0], loc[1][1]):
        moves.append(loc)

    #return all valid moves
    return moves

  def rookMove(self, file, rank):
    return self.likeToMoveItMoveIt(file, rank, [(-1,0), (1,0), (0,1), (0,-1)])

  def bishopMove(self, file, rank):
    return self.likeToMoveItMoveIt(file, rank, [(-1,-1), (-1,1), (1,1), (1,-1)])

  def knightMove(self, file, rank):
    '''
    Look at all moves at the end of the swastika
    Only move if there is no one, except an enemy, in the way
    '''
    (x, y)         = (file, rank)
    moves          = []
    validPositions = []
    piece          = self.locations[(file, rank)]
    
    for position in [(x+1,y+2), (x-1,y+2), (x+1,y-2), (x-1,y-2), 
                     (x+2,y+1), (x+2,y-1), (x-2,y-1), (x-2,y+1)]:
      if position in self.locations:
          if self.isPieceMine(self.locations[position]) == False:
            validPositions.append((piece, position))
      else:
        validPositions.append((piece, position))
    for loc in validPositions:
      if self.isMoveOnBoard(loc[1][0], loc[1][1]):
        moves.append(loc)

    #return all valid moves
    return moves

  def kingMove(self, file, rank):
    '''
    Look at a move in any direction
    only move if there is no one, except and enemy, in the way 
    '''
    (x, y)         = (file, rank)
    moves          = []
    validPositions = []
    piece          = self.locations[(file, rank)]

    for position in [(x+1,y), (x-1,y), (x,y+1), (x,y-1), 
                     (x+1,y+1), (x-1,y-1), (x+1,y-1), (x-1,y+1)]:
      if position in self.locations:
          if self.isPieceMine(self.locations[position]) == False:
            validPositions.append((piece, position))
      else:
        validPositions.append((piece, position))

    for loc in validPositions:
      if self.isMoveOnBoard(loc[1][0], loc[1][1]):
        moves.append(loc)

    #return all valid moves
    return moves

  def queenMove(self, file, rank):
    return (self.rookMove(file, rank) + self.bishopMove(file, rank))

  def isPieceMine(self, piece):
    return(piece.getOwner() == self.ai.playerID())

  def isMoveOnBoard(self, file, rank):
    return(rank < self.size+1 and rank > 0 and file < self.size+1 and file > 0)
  
  def amIBlack(self):
    return(self.ai.playerID() == 1)

  def likeToMoveItMoveIt(self, file, rank, modifiers):
    moves = []
    piece = self.locations[(file, rank)]

    for (xmod, ymod) in modifiers:
      (x, y) = (file, rank)
      while True:
        x += xmod
        y += ymod 
        if not self.isMoveOnBoard(x,y):
          break 
        if (x,y) in self.locations:
          if self.isPieceMine(self.locations[(x,y)]) == False:
            moves.append((piece, (x,y)))
          break
        moves.append((piece, (x,y)))

    #return all valid moves
    return moves
  
  def castling(self, king):
    rooks = []
    moves = []
    (x,y) = (king.getFile(), king.getRank())
    for loc in self.locations:
      current = self.locations[loc]
      if self.isPieceMine(current):
        if current.getType() == ord('R'):
          rooks.append(current)
    for rook in rooks:
      if king.getRank() == rook.getRank():
        if king.getHasMoved() == 0 and rook.getHasMoved() == 0:
          if rook.getFile() == 8:
            if (x,y+1) not in self.locations and (x,y+2) not in self.locations:
              moves.append((x,y+2))
          elif rook.getFile() == 1:
            if (x,y-1) not in self.locations and (x,y-2) not in self.locations:
              moves.append((x,y-2))
    return moves

