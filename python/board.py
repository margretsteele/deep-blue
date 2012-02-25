#Author    : Margret Steele
#Class     : AI
#Assignment: Game 1 
#File      : board.py

class board(): 
  ''' 
  locations: list of coordinates -> their piece
  size     : dimensions of board
  ai       : reference to ai object, used to access player/piece info 
  lookAtMe : flag used to allow for generation of either player's moves 
  '''
  def __init__(self, ai, lookAtMe):
    self.locations = dict()
    self.size      = 8
    self.ai        = ai
    self.lookAtMe  = lookAtMe
  
  #populates board representation
  def populate(self):
    for piece in self.ai.pieces:
      self.locations[(piece.getFile(), piece.getRank())] = piece

  #returns all the valid moves of each piece
  def getMoves(self):
    moves = []
    for loc in self.locations:
      current = self.locations[loc]
      if self.isPieceMine(current):
        if current.getType() == ord('P'): 
          moves += self.pawnMove(current.getFile(),current.getRank())
        if current.getType() == ord('R'): 
          moves += self.rookMove(current.getFile(),current.getRank())
        if current.getType() == ord('B'): 
          moves += self.bishopMove(current.getFile(),current.getRank())
        if current.getType() == ord('N'): 
          moves += self.knightMove(current.getFile(),current.getRank())
        if current.getType() == ord('Q'):
          moves += self.queenMove(current.getFile(),current.getRank())
        if current.getType() == ord('K'): 
          moves += self.kingMove(current.getFile(),current.getRank())
    return moves     

  def pawnMove(self, file, rank):
    '''
    Depending on what color I am:
    First add generic move forward once
    Second if havent moved add move forward twice
    Third add capture moves
    Look through those moves, only add valid moves
    '''
    (x,y)         = (file, rank)
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
      
    moves += self.enPassant(piece)

    for loc in validPositions:
      if self.isMoveOnBoard(loc[1][0], loc[1][1]):
        moves.append(loc)

    #return all valid moves
    return moves

  def knightMove(self, file, rank):
    '''
    Look at all moves at the end of the L formation
    Move if there is an enemy on the end spot
    Or if there is nothing on the end spot
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
    Look at a single move in any direction
    Move if there is an enemy on the end spot
    Or if there is nothing on the end spot
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
    
    moves += self.castling(piece)

    for loc in validPositions:
      if self.isMoveOnBoard(loc[1][0], loc[1][1]):
        moves.append(loc)

    #return all valid moves
    return moves

  #see comment on likeToMoveItMoveIt
  def rookMove(self, file, rank):
    return self.likeToMoveItMoveIt(file, rank, [(-1,0), (1,0), (0,1), (0,-1)])

  #see comment on likeToMoveItMoveIt
  def bishopMove(self, file, rank):
    return self.likeToMoveItMoveIt(file, rank, [(-1,-1), (-1,1), (1,1), (1,-1)])

  #see comment on likeToMoveItMoveIt
  def queenMove(self, file, rank):
    return(self.rookMove(file,rank) + self.bishopMove(file,rank))

  def likeToMoveItMoveIt(self, file, rank, modifiers):
    '''
    Based on the modifiers, move to every x,y combination specified
      -Rook  : in every cardinal direction
      -Bishop: in every diagonal direction
      -Queen : Bishop + Rook moves
     Include every move in the valid direction until something is hit as an option
     Move if there is an enemy on the end spot
     Or if there is nothing on the end spot
     '''
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

  def isPieceMine(self, piece):
    '''
    Based on the lookAtMe flag, return true if the piece being looked at matches
    the player in scope 
    (if looking at enemys pieces, my pieces should return false)
    '''
    if self.lookAtMe == True:
      return(piece.getOwner() == self.ai.playerID())
    else:
      return(piece.getOwner() != self.ai.playerID())

  #make sure board is in bounds
  def isMoveOnBoard(self, file, rank):
    return(rank < self.size+1 and rank > 0 and file < self.size+1 and file > 0)
  
  def amIBlack(self):
    '''
    Based on the lookAtMe flag, return true if the player in scope is Black 
    '''
    if self.lookAtMe == True:
      return(self.ai.playerID() == 1)
    else:
      return(self.ai.playerID() == 0)

  def castling(self, king):
    '''
    First: pull out the king (x,y)
    Get a list of all the rooks.
    Look at each rook.
      For that rook, do the king and the rook have the same rank?
        Yes. Have they both not moved?
        Yes. Is there nothing between the king and the rook?
        Yes. Awesome. Move the king. Since only one move can be moved each turn 
             and the rook will be handled accordingly (Say the devs)
    '''
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
            if (x+1,y) not in self.locations and (x+2,y) not in self.locations:
              moves.append((king, (x+2,y)))
          elif rook.getFile() == 1:
            if (x-1,y) not in self.locations and (x-2,y) not in self.locations:
              moves.append((king, (x-2,y)))
    #return valid move
    return moves
  
  def enPassant(self, pawn):
    '''
    First: pull out my pawn (x,y)
    Get a list of all the enemy pawns.
    Then look at my opponents last move:
      (lx,ly) the spot they ended on
      (px,py) the spot they started on

    Look at each enemypawn.
      For that pawn, did it start and end at the same location as the last move
      Yes. Did it's rank change by 2?
      Yes. Is my pawn along side the end location, offset by one?
      Yes. Awesome. Move to one below the enemy pawn and take it.
    '''
    pawns   = []
    moves   = []
    (x,y)   = (pawn.getFile(),pawn.getRank())
    
    if len(self.ai.moves) == 0:
      return moves

    (lx,ly) = (self.ai.moves[0].getToFile(),self.ai.moves[0].getToRank())
    (px,py) = (self.ai.moves[0].getFromFile(),self.ai.moves[0].getFromRank())
    for loc in self.locations:
      current = self.locations[loc]
      if self.isPieceMine(current) == False:
        if current.getType() == ord('P'):
          pawns.append(current)
    for enemypawn in pawns:
      if enemypawn.getFile() == lx and enemypawn.getRank() == ly:
        if abs(ly - py) == 2:
          if (lx == x+1 or lx == x-1) and (ly == y):
            moves.append((pawn, (lx, ly-1)))
    return moves
 
  def shallowMove(self, movingPiece, file, rank):
    '''
    Since I cannot move a piece instance without actually calling the move 
    function, I wanted a way to look at the board state after a move.  
    This adds the updated move to the board representation and removes the 
    original location of the piece
    '''
    for loc in self.locations:
      if self.locations[loc] == movingPiece:
         del self.locations[loc] 
         self.locations[(file, rank)] = movingPiece
 
  def pruneMoves(self, moves):
    '''
    After all the moves for each piece are generated, I prune it.
    I look at each move and see if it will end in check, if it does I delete it
    If the board is in check currently, I see if a move gets me out, 
    if it doesn't I delete it.
    '''
    for move in moves:
      if self.willMoveEndInCheck(moves[0][0], moves[1][0], moves[1][1]):
        del(move)
    for move in moves:
      if self.currentlyInCheck():
        pass
    return moves
 
  def willMoveEndInCheck(self, movingPiece, file, rank):
    '''
    I generate a list of all the pieces after this move
    From that I pull out the king.
    I create a new board, with the move added
    Then I return True if any pieces end on my king
    Returns False otherwise
    '''
    newBoard = dict()
    moves = []
    for piece in self.ai.pieces:
      if piece is not movingPiece:
        newBoard[(piece.getFile(), piece.getRank())] = piece
    newBoard[(file, rank)] = movingPiece
    for loc in newBoard:
      king = newBoard[loc]
      if self.isPieceMine(king):
        if king.getType() == ord('K'):
          break 
    b = board(self.ai, False)
    b.populate()
    b.shallowMove(movingPiece, file, rank)
    moves = b.getMoves()
    for move in moves:
      if move[1][0] == king.getFile() and move[1][1] == king.getRank():
        return True
    return False

  def currentlyInCheck(self):
    '''
    I look at a list of all the pieces currently from that I pull out the king.
    I create a new board, and look at possible opponent moves
    Then I return True if any pieces end on my king
    Returns False otherwise
    '''  
    for loc in self.locations:
      king = self.locations[loc]
      if self.isPieceMine(king):
        if king.getType() == ord('K'):
          break    
    b = board(self.ai, False)
    b.populate()
    moves = b.getMoves()
    for move in moves:
      if move[1][0] == king.getFile() and move[1][1] == king.getRank():
        return True
    return False

