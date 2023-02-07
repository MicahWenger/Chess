from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

# from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock

from kivy.graphics import Color, Rectangle

import math
import time

import RAND_AI
import MW_AI

# need to implement 'on pasant' for pawns

#static lists
ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
COLOR_LIST = dict({
   'LIGHT_GRAY':Color(0.8, 0.8, 0.8, 1),
   'DARK_GRAY': Color(0.2, 0.2, 0.2, 1),
   'GRAY':      Color(0.5, 0.5, 0.5, 1),
   'BLACK':     Color(  0,   0,   0, 1),
   'WHITE':     Color(  1,   1,   1, 1),
   'GREEN':     Color(  0,   1,   0, 1),
   'RED':       Color(  1,   0,   0, 1)
})
# white
PIECE_SETUP_W = dict({
    'PAWN': [(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1)],
    'ROOK': [(0,0),(7,0)],
    'KNIGHT': [(1,0),(6,0)],
    'BISHOP': [(2,0),(5,0)],
    'QUEEN': [(3,0)],
    'KING': [(4,0)]
})
#black
PIECE_SETUP_B = dict({
    'PAWN': [(0,6),(1,6),(2,6),(3,6),(4,6),(5,6),(6,6),(7,6)],
    'ROOK': [(0,7),(7,7)],
    'KNIGHT': [(1,7),(6,7)],
    'BISHOP': [(2,7),(5,7)],
    'QUEEN': [(3,7)],
    'KING': [(4,7)]
})
PIECE_VALUES = dict({   # taken from chess.com (except king)
    "PAWN": 1,
    "ROOK": 5,
    "KNIGHT": 3,
    "BISHOP": 3,
    "QUEEN": 9,
    "KING": 20,
})

PLAYER_TYPES = ['USER', 'RAND_AI', 'MW_AI']

class Player:
    def __init__(self, type, team):
        self.type = type
        self.team = team
        if self.type != 'USER':
            module = __import__(self.type)
            class_ = getattr(module, self.type)
            self.AI = class_(self.team)
    def setKing(self, k):
        self.king = k
    def getMove(self, board):
        if self.type != 'USER':
            return self.AI.getMove(board)

# PLAYERS = [Player('USER', 0), Player('RAND_AI', 1)]
PLAYERS = [Player('USER', 0), Player('MW_AI', 1)]

class Square:
    def __init__(self, loc, length, color):
        self.loc = loc
        self.pos = (loc[0] * length, loc[1]* length)
        self.size = (length, length)
        self.color = color
        self.highlighted = self.selected = False

    def draw(self, canvas):
        color = COLOR_LIST[self.color]
        alpha = 1
        if self.highlighted:
            # color = COLOR_LIST['RED']
            alpha = 0.2
        elif self.selected:
            # color = COLOR_LIST['GREEN']
            alpha = 0.7
        # canvas.add(COLOR_LIST[color])
        # canvas.add( Rectangle(pos=self.pos, size=self.size) )
        with canvas:
            Color(color.r, color.g, color.b, alpha)
            Rectangle(pos=self.pos, size=self.size)

    def __repr__(self):
        return "square at x=" + str(self.loc[0]) + ", y=" + str(self.loc[1]) + ", color: " + self.color

class GameScreen(Screen):

    def __init__(self, config, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.chessConfig = config
        self.pieces = []
        for r in range(self.chessConfig.rows):
            col = []
            [col.append(0) for c in range(self.chessConfig.cols)]
            self.pieces.append(col)
        self.createGrid()
        #Window.bind(mouse_pos = self.on_mouse_pos)
        self.selectedPiece = self.turn = 0

        # draw squares/ pieces
        # PLAYERS = self.players = [Player('USER', 0), Player('RAND_AI', 1)]
        self.players = PLAYERS

        self.createPieces()
        printBoard(self.pieces) # init board
        self.draw()

        self.event = Clock.schedule_interval(self.nextMove, 0.1)
        # run game
    def nextMove(self, a):
        print(40 * "-")
        print('player '+ str(self.turn) +"'s ("+ self.players[self.turn].type + ") turn")
        if not self.checkWin():
            if self.players[self.turn].type == 'USER':
                Clock.unschedule(self.event)
                return
            # send copy of board so that an AI wont modify the game board
            oldPos, newPos = self.players[self.turn].getMove(self.copyBoard())

            if self.pieces[newPos[0]][newPos[1]] is Piece:
                self.pieces[newPos[0],newPos[1]].die();
            self.pieces[oldPos[0]][oldPos[1]].move(newPos[0], newPos[1])
            self.pieces[newPos[0]][newPos[1]] = self.pieces[oldPos[0]][oldPos[1]]
            self.pieces[oldPos[0]][oldPos[1]] = 0
            self.turn = 1 - self.turn
        else: # game over
            print("~~~~~~ Game Over ~~~~~~~")
            if self.players[self.turn].king.inCheck(self.pieces):
                winner = 1 - self.turn
                print("------ Player "+str(winner)+" ("+self.players[winner].type+") wins! -------")
            else:
                print("------ Stalemate -------")
            Clock.unschedule(self.event)
        self.draw()

    def draw(self):
        # draw squares
        self.canvas.clear()
        with self.canvas:
            color = COLOR_LIST['GRAY']
            screenSize = (self.chessConfig.dimX, self.chessConfig.dimY)
            Color(color.r, color.g, color.b)
            Rectangle(pos=(0,0), size=screenSize)
        [[sq.draw(self.canvas) for sq in row] for row in self.arr]
        # draw pieces
        for r in range(len(self.pieces)):
            for c in range(len(self.pieces[r])):
                if type(self.pieces[r][c]) in (Piece, King):
                    self.pieces[r][c].draw(self.canvas)

    def setHighlightedSquares(self, piece):
        for m in piece.getValidMoves(self.pieces):
            self.arr[m[0]][m[1]].highlighted = True

    def unHighlightAllSquares(self):
        for row in self.arr:
            for square in row:
                square.highlighted = False

    def on_touch_down(self, event):
        pos = event.pos
        coords = getLocFromCoords(int(self.chessConfig.dimX / self.chessConfig.rows), pos)
        # print("click! " + str(coords))
        self.unHighlightAllSquares()
        if self.turn == 0:
            if self.selectedPiece:
                self.arr[self.selectedPiece.x][self.selectedPiece.y].selected = False
                # if coords in self.selectedPiece.getValidMoves(self.copyBoard()):
                if coords in self.selectedPiece.getValidMoves(self.pieces):
                    self.movePiece(coords)
                    self.turn = 1 - self.turn
                    self.event()
                else:
                    #color and select new peice
                    piece = self.pieces[coords[0]][coords[1]]
                    if type(piece) in (Piece, King) and piece.team == self.turn: # set selected piece
                        self.selectedPiece = piece
                        self.arr[coords[0]][coords[1]].selected = True
                        # highlight squares with a valid move
                        self.setHighlightedSquares(piece)
                    else:
                        print("not a valid move")
                        #self.selectedPiece = 0
            else:
                piece = self.pieces[coords[0]][coords[1]]
                if type(piece) in (Piece, King) and piece.team == self.turn: # set selected piece
                    # print("selecting " + str(piece))
                    self.selectedPiece = piece
                    self.arr[coords[0]][coords[1]].selected = True
                    # highlight squares with a valie move
                    for move in piece.getValidMoves(self.pieces):
                        self.arr[move[0]][move[1]].highlighted = True
                    # self.setHighlightedSquares(piece)
        self.draw()
    def createGrid(self):
        squareLength = int(self.chessConfig.dimX / self.chessConfig.rows)
        self.arr = [ [ Square((r,c), squareLength, list(COLOR_LIST.keys())[(r+c+1) % 2])
            for c in range(self.chessConfig.cols) ]
            for r in range(self.chessConfig.rows) ]

    def createPieces(self):
        squareLength = int(self.chessConfig.dimX / self.chessConfig.rows)
        for k in list(PIECE_SETUP_W.keys()):
            for p in PIECE_SETUP_W[k]:
                if k == "KING":
                    self.pieces[p[0]][p[1]] = King(0, p[0], p[1], squareLength)
                    print(self.pieces[p[0]][p[1]])
                    self.players[0].setKing(self.pieces[p[0]][p[1]])
                else:
                    self.pieces[p[0]][p[1]] = Piece(k, 0, p[0], p[1], squareLength)
        for k in list(PIECE_SETUP_B.keys()):
            for p in PIECE_SETUP_B[k]:
                if k == "KING":
                    self.pieces[p[0]][p[1]] = King(1, p[0], p[1], squareLength)
                    self.players[1].setKing(self.pieces[p[0]][p[1]])
                else:
                    self.pieces[p[0]][p[1]] = Piece(k, 1, p[0], p[1], squareLength)

    def movePiece(self, coords):
        self.pieces[coords[0]][coords[1]] = self.selectedPiece
        self.pieces[self.selectedPiece.x][self.selectedPiece.y] = 0
        self.selectedPiece.move(coords[0],coords[1])
        self.selectedPiece = 0

    def checkWin(self):
        for row in self.pieces:
            for p in row:
                if type(p) in (Piece, King) and p.team == self.turn:
                    # print("found an allied piece")
                    if len(p.getValidMoves(self.pieces)) > 0:
                        return False
        return True

    def copyBoard(self):
        board = self.pieces
        newBoard = []
        for r in range(len(board[0])):
            col = []
            for c in range(len(board[r])):
                piece = board[r][c]
                if type(piece) is King:
                    col.append(King(piece.team, piece.x, piece.y, piece.length))
                elif type(piece) is Piece:
                    col.append(Piece(piece.type, piece.team, piece.x, piece.y, piece.length))
                else:
                    col.append(0)
            newBoard.append(col)
        return newBoard

# conversion functions
def getLocFromCoords(squareLength, coords):
    return (math.floor(coords[0] / squareLength), math.floor(coords[1] / squareLength))
def getCoordsFromLoc(squareLength, coords):
    return (coords[0] * squareLength, coords[1] * squareLength)



class Piece:
    def __init__(self, type, team, x, y, length):
        self.type = type
        self.team = team
        self.x = x
        self.y = y
        self.length = length
        self.path = 'images/' + ('black' if self.team == 1 else 'white')+'/'+ self.type.lower()+'.png'
        loc = getCoordsFromLoc(self.length,(self.x,self.y))
        self.rect = Rectangle(source=self.path, pos=loc, size=(self.length,self.length))
        self.movedTwoSpaces = False

    def move(self, newX, newY):
        if self.type == "PAWN":
            if newY in (0,7):
                self.queen()
            if abs(self.y - newY) == 2:
                self.movedTwoSpaces = True
        self.x = newX
        self.y = newY
        loc = getCoordsFromLoc(self.length,(self.x,self.y))
        self.rect.pos = loc


    def queen(self): # change pawn to queen
        self.type = 'QUEEN'
        path = 'images/' + ('black' if self.team == 1 else 'white')+'/'+ self.type.lower()+'.png'
        loc = getCoordsFromLoc(self.length,(self.x,self.y))
        self.rect = Rectangle(source=path, pos=loc, size=(self.length,self.length))

    def draw(self, canvas):
        c = COLOR_LIST['WHITE']
        with canvas:
            Color(c.r, c.g, c.b, c.a)
            Rectangle(source=self.path, pos=self.rect.pos, size=(self.length,self.length))

    def getValidMoves(self, board, deep=True):
    # def getValidMoves(self, board, onlyValid=True, deep=True):
        moves = []
        if self.type == 'PAWN':
            facingDir = (1-self.team)*2 - 1
            #print('pawn y '+str(self.y))
            newY = self.y + facingDir
            if newY in range(len(board)) and type(board[self.x][newY]) not in (Piece, King):
            # if self.y+facingDir >= 0 and self.y+facingDir < len(board) and type(board[self.x][self.y+facingDir]) is not Piece:
                moves.append((self.x, newY))
                # moving 2 spaces at start
                if self.y+(2*facingDir) >= 0 and self.y+(2*facingDir) < len(board) and type(board[self.x][self.y+(2*facingDir)]) not in (Piece, King):
                    if self.team == 0:
                        if self.y == 1:
                            moves.append((self.x, self.y + (2*facingDir)))
                    elif self.y == 6:
                            moves.append((self.x, self.y + (2*facingDir)))
            # diagonal jumping
            if newY in range(len(board)):
            # if self.y+facingDir >= 0 and self.y+facingDir < len(board):
                if self.x < len(board) - 1:
                    p = board[self.x + 1][newY]
                    # if type(p) in (Piece, King) and p.team != self.team or not onlyValid:
                    if type(p) in (Piece, King) and p.team != self.team:
                        moves.append((self.x + 1, newY))
                if self.x > 0:
                    p = board[self.x - 1][newY]
                    # if type(p) in (Piece, King) and p.team != self.team or not onlyValid:
                    if type(p) in (Piece, King) and p.team != self.team:
                        moves.append((self.x - 1, newY))
        elif self.type == "ROOK" or self.type == "QUEEN":
            #move horiz right
            for x in range(self.x+1,len(board)):
                if type(board[x][self.y]) in (Piece, King):
                    # if board[x][self.y].team != self.team or not onlyValid:
                    if board[x][self.y].team != self.team:
                        moves.append((x,self.y))
                    break
                else:
                    moves.append((x,self.y))
            #move horiz left
            for x in range(self.x-1,-1,-1):
                if type(board[x][self.y]) in (Piece, King):
                    # if board[x][self.y].team != self.team or not onlyValid:
                    if board[x][self.y].team != self.team:
                        moves.append((x,self.y))
                    break
                else:
                    moves.append((x,self.y))

            #move vert up
            for y in range(self.y+1,len(board)):
                if type(board[self.x][y]) in (Piece, King):
                    # if board[self.x][y].team != self.team or not onlyValid:
                    if board[self.x][y].team != self.team:
                        moves.append((self.x,y))
                    break
                else:
                    moves.append((self.x,y))
            #move vert down
            for y in range(self.y-1,-1,-1):
                if type(board[self.x][y]) in (Piece, King):
                    # if board[self.x][y].team != self.team or not onlyValid:
                    if board[self.x][y].team != self.team:
                        moves.append((self.x,y))
                    break
                else:
                    moves.append((self.x,y))
        elif self.type == "KNIGHT":
            for r in range(len(board)):
                for c in range(len(board[r])):
                    if abs(r - self.x) == 2 and abs(c - self.y) == 1 or abs(r - self.x) == 1 and abs(c - self.y) == 2:
                        if type(board[r][c]) in (Piece, King):
                            if board[r][c].team != self.team:
                            # if board[r][c].team != self.team or not onlyValid:
                                moves.append((r,c))
                        else:
                            moves.append((r,c))
        if self.type == "BISHOP" or self.type == "QUEEN":
            # up right
            for i in range(1,len(board)-self.x):
                if self.y+i >= len(board): break
                if type(board[self.x+i][self.y+i]) in (Piece, King):
                    if board[self.x+i][self.y+i].team != self.team:
                    # if board[self.x+i][self.y+i].team != self.team or not onlyValid:
                        moves.append((self.x+i,self.y+i))
                    break
                else:
                    moves.append((self.x+i,self.y+i))
            # up left
            for i in range(1,self.x+1):
                if self.y+i >= len(board): break
                if type(board[self.x-i][self.y+i]) in (Piece, King):
                    if board[self.x-i][self.y+i].team != self.team:
                    # if board[self.x-i][self.y+i].team != self.team or not onlyValid:
                        moves.append((self.x-i,self.y+i))
                    break
                else:
                    moves.append((self.x-i,self.y+i))
            # down right
            for i in range(1,len(board)-self.x):
                if self.y-i < 0: break
                if type(board[self.x+i][self.y-i]) in (Piece, King):
                    if board[self.x+i][self.y-i].team != self.team:
                    # if board[self.x+i][self.y-i].team != self.team or not onlyValid:
                        moves.append((self.x+i,self.y-i))
                    break
                else:
                    moves.append((self.x+i,self.y-i))
            # down left
            for i in range(1,self.x+1):
                if self.y-i < 0:
                    break
                # if not onlyValid:
                #     if type(board[self.x-i][self.y-i]) is Piece:
                #         moves.append((self.x-i,self.y-i))
                #         break
                #     else:
                #         moves.append((self.x-i,self.y-i))
                # else:
                if type(board[self.x-i][self.y-i]) in (Piece, King):
                    if board[self.x-i][self.y-i].team != self.team:
                        moves.append((self.x-i,self.y-i))
                    break
                else:
                    moves.append((self.x-i,self.y-i))

        if deep:
            m = 0
            while m < len(moves):
                simBoard = self.simulateMove(moves[m], board)
                # printBoard(simBoard)
                simKing = None
                for r in simBoard:
                    for c in r:
                        if type(c) is King and c.team == self.team:
                            simKing = c
                            break
                    if simKing is not None:
                        break
                if simKing is None:
                    printBoard(simBoard)
                if simKing.inCheck(simBoard):
                    moves.remove(moves[m])
                else:
                    m += 1
        return moves

    def canBeJumped(self, board):
        enemyPieces = []
        for row in board:
            for piece in row:
                if type(piece) in (Piece, King) and piece.team != self.team:
                    enemyPieces.append(piece)

        # print(str(len(enemyPieces))+" enemy pieces")
        for p in enemyPieces:
            if (self.x, self.y) in p.getValidMoves(board, deep=False):
                # special case where pawn cant jump a piece directly in front of it
                if p.type == "PAWN":
                    if self.x != p.x:
                        return True # print("check")
                else:
                    # print("check")
                    return True
        print(str(self.team)+" can not be jumped")
        return False
    #returns new board where move has been made
    def simulateMove(self, move, board):
        cpy = self.duplicateBoard(board)
        cpy[move[0]][move[1]] = cpy[self.x][self.y]
        cpy[self.x][self.y].move(move[0],move[1])
        cpy[self.x][self.y] = 0
        return cpy

    def duplicateBoard(self, board):
        newBoard = []
        for r in range(len(board[0])):
            col = []
            for c in range(len(board[r])):
                piece = board[r][c]
                if type(piece) is King:
                    col.append(King(piece.team, piece.x, piece.y, piece.length))
                elif type(piece) is Piece:
                    col.append(Piece(piece.type, piece.team, piece.x, piece.y, piece.length))
                else:
                    col.append(0)
            newBoard.append(col)
        return newBoard

    def getValue(self):
        return PIECE_VALUES[self.type]

    def die(self):
        # self.x = -1
        # self.y = -1
        print(self.type+' has died')
        self.move(-1, -1)

    def __repr__(self):
        return self.type + " "+ str(self.team)
    def __str__(self):
        return self.type

class King(Piece):
    def __init__(self, team, x, y, length):
        Piece.__init__(self, "KING", team, x, y, length)

    def getValidMoves(self, board, deep=True):
        moves = []
        # get enemy pieces
        enemyPieces = []
        for row in board:
            for piece in row:
                if type(piece) in (Piece, King) and piece.team != self.team:
                    enemyPieces.append(piece)

        for r in range(len(board)):
            for c in range(len(board[r])):
                if abs(r - self.x) <= 1 and abs(c - self.y) <= 1 and not (self.x == r and self.y == c):
                    if type(board[r][c]) in (Piece, King):
                        if board[r][c].team != self.team:
                            moves.append((r,c))
                    else:
                        moves.append((r,c))

        if deep:
            m = 0
            while m < len(moves):
                simBoard = self.simulateMove(moves[m], board)
                printBoard(simBoard)
                simKing = 0
                for r in simBoard:
                    for c in r:
                        if type(c) is King and c.team == self.team:
                            simKing = c
                            break
                    if simKing != 0:
                        break
                if simKing.inCheck(simBoard):
                    moves.remove(moves[m])
                else:
                    m += 1

        return moves

    def inCheck(self, board):
        enemyPieces = []
        for row in board:
            for piece in row:
                if type(piece) in (Piece, King) and piece.team != self.team:
                    enemyPieces.append(piece)

        # print(str(len(enemyPieces))+" enemy pieces")
        for p in enemyPieces:
            if (self.x, self.y) in p.getValidMoves(board, deep=False):
                # special case where pawn cant jump a piece directly in front of it
                if p.type == "PAWN":
                    if self.x != p.x:
                        return True # print("check")
                else:
                    # print("check")
                    return True
        print(str(self.team)+" not in check")
        return False

def printBoard(board):
    print(" " + (63 * "_"))
    for r in range(len(board)):
        if type(board[0][7-r]) is Piece and board[0][7-r].type in ("KNIGHT", "BISHOP"):
            print("|", end="")
        else:
            print("|", end=" ")
        for c in range(len(board)):
            if type(board[c][7-r]) is King:
                print("_", end="")
            print(str(board[c][7-r]).replace("0","  ."), end="\t")
        print("|")
    print(" " + (63 * "-"))

class ChessConfig:
    def __init__(self, rows, cols, dimX, dimY):
        self.rows = rows
        self.cols = cols
        self.dimX = dimX
        self.dimY = dimY
