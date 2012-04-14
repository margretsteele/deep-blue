#Author    : Margret Steele
#Class     : AI
#Assignment: Game 2 
#File      : board.py

from copy import deepcopy

class board(): 
  ''' 
  locations : list of coordinates -> their piece
  ai        : reference to ai object, used to access player/piece info 
  lookAtMe  : flag used to allow for generation of either player's moves 
  h         : piece value heuristic
  threatened: list of all threatened pieces
  moveGen   : dictionary used in optimizing move generation speed 
  '''
  def __init__(self, ai, lookAtMe):
    self.locations  = dict()
    self.ai         = ai
    self.lookAtMe   = lookAtMe
    self.h          = 0
    self.moveHist   = []
    self.threatened = []
    self.moveGen    = { 'P' : self.pawnMove,
                        'R' : self.rookMove,
                        'B' : self.bishopMove,
                        'N' : self.knightMove,
                        'Q' : self.queenMove,
                        'K' : self.kingMove   }
  
  #populates board representation
  def populate(self):
    for piece in self.ai.pieces:
      self.locations[(piece.getFile(), piece.getRank())] = piece
    for move in self.ai.moves:
      self.moveHist.append(((move.getToFile(),move.getToRank()), 
                            (move.getFromFile(),move.getFromRank())))

  #returns all the valid moves of each piece
  def getMoves(self):
    moves = []
    for loc in self.locations:
      current = self.locations[loc]
      if self.isPieceMine(current):
        if self.moveGen[chr(current.getType())]:
          moves += self.moveGen[chr(current.getType())](*loc)
    return moves

  def pawnMove(self, file, rank):
    '''
    Depending on what color I am:
    First add generic move forward once
    Second if havent moved add move forward twice
    Third add capture moves
    Look through those moves, only add valid moves
    '''
    (x,y)          = (file,rank)
    moves          = []
    validPositions = []
    piece          = self.locations[(file, rank)]

    if self.amIBlack() == False: 
      if (x,y+1) not in self.locations:
        validPositions.append((piece, (x,y+1), (x,y)))
      if self.locations[(x,y)].getHasMoved() == 0 and \
                       (x,y+2) not in self.locations and \
                       (x,y+1) not in self.locations:
        validPositions.append((piece, (x,y+2), (x,y)))
      
      for position in [(x+1,y+1), (x-1,y+1)]:
        if position in self.locations:
          if self.isPieceMine(self.locations[position]) == False:
            validPositions.append((piece, position, (x,y)))
      
    else:
      if (x,y-1) not in self.locations:
        validPositions.append((piece, (x,y-1), (x,y)))
      if self.locations[(x,y)].getHasMoved() == 0 and \
                       (x,y-2) not in self.locations and \
                       (x,y-1) not in self.locations:
        validPositions.append((piece, (x,y-2), (x,y)))
      
      for position in [(x+1,y-1), (x-1,y-1)]:
        if position in self.locations:
          if self.isPieceMine(self.locations[position]) == False:
            validPositions.append((piece, position, (x,y)))
      
    validPositions += self.enPassant(piece, x, y)

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
          validPositions.append((piece, position, (x,y)))
      else:
        validPositions.append((piece, position, (x,y)))
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
            validPositions.append((piece, position, (x,y)))
      else:
        validPositions.append((piece, position, (x,y)))
    
    validPositions += self.castling(piece, x, y)

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
     Include every move in the valid direction until something is hit as move
     Move if there is an enemy on the end spot
     Or if there is nothing on the end spot
     '''
    moves = []
    piece = self.locations[(file, rank)]

    for (xmod, ymod) in modifiers:
      (x,y) = (file, rank)
      while True:
        x += xmod
        y += ymod 
        if not self.isMoveOnBoard(x,y):
          break 
        if (x,y) in self.locations:
          if self.isPieceMine(self.locations[(x,y)]) == False:
            moves.append((piece, (x,y), (file,rank)))
          break
        moves.append((piece, (x,y), (file,rank)))

    #return all valid moves
    return moves

  def castling(self, king, x, y):
    '''
    First: return no moves if I am in check

      def hasMoved <- only used here so it's only here. Deal with it.
      This checks if the passed in king or rook has moved from original position

    Check if king has moved
    Get a list of all my rooks that haven't moved.
    Look at each rook.
        Is there nothing between the king and the rook?
        Yes. Awesome. Move the king. Since only one move can be moved each turn 
             and the rook will be handled accordingly (Say the devs)
    '''
    rooks = []
    moves = []
   
    if (x,y) in self.threatened: 
      return moves

    def hasMoved(piece):
      blackStart = { 'R':[(1,8),(8,8)],
                     'K':[(5,8)] }
      whiteStart = { 'R':[(1,1),(8,1)],
                     'K':[(5,1)] }
      if self.amIBlack():
        return not piece[1] in blackStart[chr(piece[0].getType())]
      else:
        return not piece[1] in whiteStart[chr(piece[0].getType())]

    if hasMoved((king, (x,y))):
      return moves

    for loc in self.locations:
      current = self.locations[loc]
      if current.getType() == ord('R'):
        if self.isPieceMine(current):
          if not hasMoved((current, loc)):
            rooks.append((current, loc))

    for rook in rooks:
      if rook[1][0] == 1:
        if (x-1,y) not in self.locations and \
           (x-2,y) not in self.locations and (x-3,y) not in self.locations:
          moves.append((king, (x-2,y), (x,y)))

      elif rook[1][0] == 8:
        if (x+1,y) not in self.locations and (x+2,y) not in self.locations:
          moves.append((king, (x+2,y), (x,y)))

    #return valid move
    return moves
  
  def enPassant(self, pawn, file, rank):
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
    (x,y)   = (file, rank)
    
    if not self.ai.moves:
      return moves
    (lx,ly) = (self.moveHist[0][0])
    (px,py) = (self.moveHist[0][1])
    for loc in self.locations:
      current = self.locations[loc]
      if current.getType() == ord('P'):
        if self.isPieceMine(current) == False:
          pawns.append((current, loc))
    for enemypawn in pawns:
      if enemypawn[1][0] == lx and enemypawn[1][1] == ly:
        if ly - py == 2:
          if (lx == x+1 or lx == x-1) and (ly == y):
            moves.append((pawn, (lx, ly-1), (x,y)))
        elif ly - py == -2:
          if (lx == x+1 or lx == x-1) and (ly == y):
            moves.append((pawn, (lx, ly+1), (x,y)))
    return moves
  
  def getChildren(self):
    '''
    Returns a list of all the children boards with hueristic values for each
    '''
    moves    = self.pruneMoves(self.getMoves())
    children = []
    for move in moves:
      copyBoard = self.createBoard(move)
      copyBoard.heruisticGen(False)
      children.append((move, copyBoard))
    return children

  def heruisticGen(self, value):
    '''
    Piece value heuristic
    Using pre-defined values for each piece, the value of a board is 
      determined by the amount of pieces*their value
    Points are detucted for opponents pieces
    Points are added for my pieces
    '''
    heur = 0
    pieceVal = {'P':1, 'N':3, 'B':3, 'R':5, 'Q':9, 'K':200}
    for loc in self.locations:
      current = self.locations[loc]
      if self.isPieceMine(current) == self.lookAtMe:
        heur += pieceVal[chr(current.getType())]
      else:
        heur -= pieceVal[chr(current.getType())]
    if value == False:
      self.h = heur
    else:
      return heur 

  def pruneMoves(self, moves):
    '''
    After all the moves for each piece are generated, I prune it.
    I look at each move and see if it will end in check, if it does I delete it
    '''
    moves = [x for x in moves if not self.stalemateCheck(x)]
    return [x for x in moves if not self.inCheck(x)]
 
  def inCheck(self, move):
    '''
    I generate a list of all the pieces after this move
    From that I pull out the king.
    I create a new board, with the move added
    Then I return True if any pieces end on my king
    Returns False otherwise
    '''
    b = self.genThreatenedBits(move)
    king = b.getKingsLocation()
    return any([x[1] == king for x in self.threatened]) 
    
  def getKingsLocation(self):
    '''
    Returns my kings location 
    '''
    for loc in self.locations:
      current = self.locations[loc]
      if current.getType() == ord('K'):
        if self.isPieceMine(current) == self.lookAtMe:
          return loc

  def stalemateCheck(self, move):
    '''
    Makes sure that the latest move doesn't end in a 3 turn stalemate
    It adds the potential move to a copy of the move history
    It then compares the first 4 moves with the last 4 moves
    This verifies the same board state has not be repeated 3 times
    ***    Borrowed a bit of this from the server code. 
    '''
    if len(self.moveHist) < 8:
      return False
    newMoveHist = [(move[1], move[2])] + self.moveHist
    return newMoveHist[0:4] == newMoveHist[4:8]

  def createBoard(self, move):
    '''
    In order to make the board state immutable
    This replaces the need for the shallowMove function
    It generates a new board with the proper dictionary representation
    '''
    b = board(self.ai, not(self.lookAtMe))
    b.locations  = deepcopy(self.locations)
    b.moveHist   = deepcopy(self.moveHist)
    b.threatened = deepcopy(self.threatened)
    if move[2] in b.locations:
      del b.locations[move[2]]
      b.locations[move[1]] = move[0] 
    return b

  def genThreatenedBits(self, move):
    '''
    This looks at my opponents moves, and returns those that can capture 
      any of my pieces
    '''
    b     = self.createBoard(move)
    moves = b.getMoves()      
    for move in moves:
      if move[1] in b.locations:
        if self.isPieceMine(b.locations[move[1]]):
          self.threatened.append(move)
    return b

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
    return(rank < 9 and rank > 0 and file < 9 and file > 0)
  
  def amIBlack(self):
    '''
    Based on the lookAtMe flag, return true if the player in scope is Black 
    '''
    if self.lookAtMe == True:
      return(self.ai.playerID() == 1)
    else:
      return(self.ai.playerID() == 0)



