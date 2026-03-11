#Author    : Margret Steele
#Class     : AI
#Assignment: Game 4
#File      : board.py

import random

PIECE_VAL = {'P':1, 'N':3, 'B':3, 'R':5, 'Q':9, 'K':200}

class board():
  '''
  locations : list of coordinates -> their piece
  ai        : reference to ai object, used to access player/piece info
  lookAtMe  : flag used to allow for generation of either player's moves
  h         : piece value heuristic
  moveGen   : dictionary used in optimizing move generation speed
  '''
  def __init__(self, ai, lookAtMe):
    self.locations  = dict()
    self.ai         = ai
    self.lookAtMe   = lookAtMe
    self.h          = 0
    self.moveHist   = []
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
    # Pre-compute the root board heuristic for incremental updates
    self.h = self._computeHeuristic()

  def _computeHeuristic(self):
    '''Full heuristic computation - only needed at root.'''
    heur = 0
    for loc in self.locations:
      current = self.locations[loc]
      if self.isPieceMine(current) == self.lookAtMe:
        heur += PIECE_VAL[chr(current.getType())]
      else:
        heur -= PIECE_VAL[chr(current.getType())]
    return heur

  def endgameBonus(self):
    '''
    When ahead in material, reward pushing opponent king to edges/corners
    and keeping our king close to theirs for mating patterns.
    '''
    myKing = None
    theirKing = None
    myMaterial = 0
    theirMaterial = 0

    for loc in self.locations:
      current = self.locations[loc]
      ptype = chr(current.getType())
      isMine = self.isPieceMine(current) == self.lookAtMe
      if ptype == 'K':
        if isMine:
          myKing = loc
        else:
          theirKing = loc
      elif isMine:
        myMaterial += PIECE_VAL[ptype]
      else:
        theirMaterial += PIECE_VAL[ptype]

    if myKing is None or theirKing is None:
      return 0

    advantage = myMaterial - theirMaterial
    if advantage < 3:
      return 0  # only apply in winning endgames

    # Reward opponent king being near edges/corners (center = bad for them)
    ef, er = theirKing
    centerDistFile = max(abs(ef - 4), abs(ef - 5))  # 0 at center, 3 at edge
    centerDistRank = max(abs(er - 4), abs(er - 5))
    edgeBonus = (centerDistFile + centerDistRank) * 0.3

    # Reward our king being close to their king (for delivering checkmate)
    kingDist = abs(myKing[0] - ef) + abs(myKing[1] - er)
    proximityBonus = (14 - kingDist) * 0.2  # closer = better

    return edgeBonus + proximityBonus

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
    Check if king has moved
    Get a list of all my rooks that haven't moved.
    Look at each rook.
        Is there nothing between the king and the rook?
        Yes. Awesome. Move the king.
    '''
    rooks = []
    moves = []

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
    Returns a list of all valid children boards with heuristic values.
    Combines move generation, legality checking (in-check pruning),
    and board creation into a single pass to avoid creating each board twice.
    '''
    moves    = self.getMoves()
    children = []
    for move in moves:
      if self.stalemateCheck(move):
        continue
      childBoard = self.createBoard(move)
      # Check if this move leaves our king in check
      # childBoard has flipped lookAtMe, so getMoves generates opponent moves
      opponentMoves = childBoard.getMoves()
      king = childBoard.getKingsLocation()
      if king is not None and any(m[1] == king for m in opponentMoves):
        continue
      children.append((move, childBoard))
    return children

  def heruisticGen(self, value):
    '''
    Piece value heuristic - only used for root board initialization.
    Child boards use incremental heuristic from createBoard.
    '''
    heur = self._computeHeuristic()
    if value == False:
      self.h = heur
    else:
      return heur

  def stalemateCheck(self, move):
    '''
    Makes sure that the latest move doesn't end in a 3 turn stalemate
    '''
    if len(self.moveHist) < 8:
      return False
    newMoveHist = [(move[1], move[2])] + self.moveHist
    return newMoveHist[0:4] == newMoveHist[4:8]

  def createBoard(self, move):
    '''
    Creates a new board state after applying a move.
    Computes heuristic incrementally from capture value.
    '''
    b = board(self.ai, not(self.lookAtMe))
    b.locations  = dict(self.locations)
    b.moveHist   = self.moveHist  # shared reference, never modified by children

    # Compute capture value before modifying the board
    captured_val = 0
    dest = move[1]
    src = move[2]
    if dest in b.locations:
      captured_val = PIECE_VAL.get(chr(b.locations[dest].getType()), 0)

    if src in b.locations:
      del b.locations[src]
    b.locations[dest] = move[0]

    # Incremental heuristic: captures change score
    # Heuristic is always from the AI's perspective
    # If it's our turn (lookAtMe=True), we captured their piece: +val
    # If it's their turn (lookAtMe=False), they captured our piece: -val
    sign = 1 if self.lookAtMe else -1
    b.h = self.h + sign * captured_val

    return b

  def getKingsLocation(self):
    '''
    Returns our king's location (from the perspective of the board's lookAtMe)
    '''
    for loc in self.locations:
      current = self.locations[loc]
      if current.getType() == ord('K'):
        if self.isPieceMine(current) == self.lookAtMe:
          return loc

  def isPieceMine(self, piece):
    '''
    Based on the lookAtMe flag, return true if the piece being looked at matches
    the player in scope
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
