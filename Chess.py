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


#static lists
ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
COLOR_LIST = dict({
   'LIGHT_GRAY': Color(0.8, 0.8, 0.8, 1, mode='rgba'),
   'DARK_GRAY': Color(0.2, 0.2, 0.2, 1, mode='rgba'),
   'GRAY': Color(0.5, 0.5, 0.5, 1, mode='rgba'),
   'BLACK': Color(0, 0, 0, 1, mode='rgba'),
   'WHITE': Color(1, 1, 1, 1, mode='rgba'),
   'GREEN': Color(0, 1, 0, 1, mode='rgba'),
   'RED': Color(1, 0, 0, 1, mode='rgba')
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
PIECE_VALUES = dict({
    "PAWN": 1,
    "ROOK": 6,
    "KNIGHT": 4,
    "BISHOP": 4,
    "QUEEN": 8,
    "KING": 10,
})

PLAYER_TYPES = ['USER', 'RAND_AI', 'MW_AI']


class Square:
    def __init__(self, loc, length, color):
        self.loc = loc
        self.pos = (loc[0] * length, loc[1]* length)
        self.size = (length, length)
        self.color = color

    def draw(self, canvas, tempColor=None):
        canvas.add(COLOR_LIST[tempColor if tempColor else self.color])
        canvas.add( Rectangle(pos=self.pos, size=self.size) )

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
        self.createPieces()
        self.draw()

        self.event = Clock.schedule_interval(self.nextMove, 0.1)
        # run game
    def nextMove(self, a):
        if not self.checkWin():
            print('player '+ self.players[self.turn].type + '\'s turn')
            if self.players[self.turn].type == 'USER':
                Clock.unschedule(self.event)
                return
            oldPos, newPos = self.players[self.turn].getMove(self.copyBoard())
            #print('move aquired')
            if self.pieces[newPos[0]][newPos[1]] is Piece:
                self.pieces[newPos[0],newPos[1]].die();
            self.pieces[oldPos[0]][oldPos[1]].move(newPos[0], newPos[1])
            self.pieces[newPos[0]][newPos[1]] = self.pieces[oldPos[0]][oldPos[1]]
            self.pieces[oldPos[0]][oldPos[1]] = 0
            self.turn = 1 - self.turn
        else:
            print("game over")
            Clock.unschedule(self.event)
        self.draw()

    def draw(self):
        print("drawing")
        self.canvas.clear()
        [[sq.draw(self.canvas) for sq in r] for r in self.arr]

        for r in range(len(self.pieces)):
            for c in range(len(self.pieces[r])):
                if type(self.pieces[r][c]) is Piece:
                    self.pieces[r][c].draw(self.canvas)

    def highlightValidMoves(self, piece):
        moves = piece.getValidMoves(self.pieces)
        for m in moves:
            self.arr[m[0]][m[1]].draw(self.canvas, 'RED')


    def on_touch_down(self, event):
        pos = event.pos
        coords = getLocFromCoords(int(self.chessConfig.dimX / self.chessConfig.rows), pos)
        # print("click! " + str(coords))

        if self.turn == 0:
            if self.selectedPiece:
                if coords in self.selectedPiece.getValidMoves(self.copyBoard()):
                    self.movePiece(coords)
                    self.turn = 1 - self.turn
                    self.event()
                else:
                    # de-color old selected piece
                    self.draw()
                    #color and select new peice
                    piece = self.pieces[coords[0]][coords[1]]
                    if type(piece) is Piece and piece.team == self.turn: # set selected piece
                        self.selectedPiece = piece
                        self.arr[coords[0]][coords[1]].draw(self.canvas, 'GRAY')
                        self.pieces[coords[0]][coords[1]].draw(self.canvas)
                        self.highlightValidMoves(piece)
                    else:
                        print("not a valid move")
                        #self.selectedPiece = 0
            else:
                piece = self.pieces[coords[0]][coords[1]]
                if type(piece) is Piece and piece.team == self.turn: # set selected piece
                    self.selectedPiece = piece
                    self.arr[coords[0]][coords[1]].draw(self.canvas, 'GRAY')
                    self.pieces[coords[0]][coords[1]].draw(self.canvas)
                    self.highlightValidMoves(piece)

    def createGrid(self):
        squareLength = int(self.chessConfig.dimX / self.chessConfig.rows)
        self.arr = [
        [ Square((r,c), squareLength, list(COLOR_LIST.keys())[(r+c+1) % 2])
        for c in range(self.chessConfig.cols) ]
        for r in range(self.chessConfig.rows) ]

    def createPieces(self):
        squareLength = int(self.chessConfig.dimX / self.chessConfig.rows)
        for k in list(PIECE_SETUP_W.keys()):
            for p in PIECE_SETUP_W[k]:
                self.pieces[p[0]][p[1]] = Piece(k, 0, p[0], p[1], squareLength)
        for k in list(PIECE_SETUP_B.keys()):
            for p in PIECE_SETUP_B[k]:
                self.pieces[p[0]][p[1]] = Piece(k, 1, p[0], p[1], squareLength)

    def movePiece(self, coords):
        self.pieces[coords[0]][coords[1]] = self.selectedPiece
        self.pieces[self.selectedPiece.x][self.selectedPiece.y] = 0
        self.selectedPiece.move(coords[0],coords[1])
        self.selectedPiece = 0

    def checkWin(self):
        p0Pieces = []
        p1Pieces = []
        kings = [0,0]
        for row in self.pieces:
            for piece in row:
                if type(piece) is Piece:
                    if piece.team == 0:
                        p0Pieces.append(piece)
                        if piece.type == 'KING':
                            kings[0] = piece
                    else:
                        p1Pieces.append(piece)
                        if piece.type == 'KING':
                            kings[1] = piece
        for k in kings:
            if k.isCheckmate(self.pieces):
                return True
        return False

    def copyBoard(self):
        board = self.pieces
        newBoard = []
        for r in range(len(board[0])):
            col = []
            for c in range(len(board[r])):
                piece = board[r][c]
                if type(piece) is Piece:
                    col.append(Piece(piece.type, piece.team, piece.x, piece.y, piece.length))
                else:
                    col.append(0)
            newBoard.append(col)
        #print(newBoard)
        return newBoard

def getLocFromCoords(squareLength, coords):
    return (math.floor(coords[0] / squareLength), math.floor(coords[1] / squareLength))

def getCoordsFromLoc(squareLength, coords):
    return (coords[0] * squareLength, coords[1] * squareLength)

class Player:
    def __init__(self, type, team):
        self.type = type
        self.team = team
        if self.type != 'USER':
            module = __import__(self.type)
            class_ = getattr(module, self.type)
            self.AI = class_(self.team)

    def getMove(self, board):
        if self.type != 'USER':
            return self.AI.getMove(board)

class Piece:
    def __init__(self, type, team, x, y, length):
        self.type = type
        self.team = team
        self.x = x
        self.y = y
        self.length = length
        path = 'images/' + ('black' if self.team == 1 else 'white')+'/'+ self.type.lower()+'.png'
        loc = getCoordsFromLoc(self.length,(self.x,self.y))
        self.rect = Rectangle(source=path, pos=loc, size=(self.length,self.length))

    def move(self, newX, newY):
        self.x = newX
        self.y = newY
        loc = getCoordsFromLoc(self.length,(self.x,self.y))
        self.rect.pos = loc

        if self.type == "PAWN":
            if self.team == 0 and self.y == 7:
                self.queen()
            elif self.team == 1 and self.y == 0:
                self.queen()

    def queen(self):
        self.type = 'QUEEN'
        path = 'images/' + ('black' if self.team == 1 else 'white')+'/'+ self.type.lower()+'.png'
        loc = getCoordsFromLoc(self.length,(self.x,self.y))
        self.rect = Rectangle(source=path, pos=loc, size=(self.length,self.length))
    def draw(self, canvas):
        canvas.add(COLOR_LIST['WHITE'])
        canvas.add(self.rect)

    def getValidMoves(self, board, deep=True):
        moves = []
        if self.type == 'PAWN':
            facingDir = (1-self.team)*2 - 1
            #print('pawn y '+str(self.y))
            if self.y+facingDir >= 0 and self.y+facingDir < len(board) and type(board[self.x][self.y+facingDir]) is not Piece:
                moves.append((self.x,self.y + facingDir))
                if self.y+(2*facingDir) >= 0 and self.y+(2*facingDir) < len(board) and type(board[self.x][self.y+(2*facingDir)]) is not Piece:
                    if self.team == 0:
                        if self.y == 1:
                            moves.append((self.x,self.y + (2*facingDir)))
                    elif self.y == 6:
                            moves.append((self.x,self.y + (2*facingDir)))
            # diagonal jumping
            if self.y+facingDir >= 0 and self.y+facingDir < len(board):
                if self.x < len(board) -1:
                    p = board[self.x+1][self.y+facingDir]
                    if type(p) is Piece and p.team != self.team:
                        moves.append((self.x+1,self.y + facingDir))
                if self.x > 0:
                    p = board[self.x-1][self.y+facingDir]
                    if type(p) is Piece and p.team != self.team:
                        moves.append((self.x-1,self.y + facingDir))
        elif self.type == "ROOK":
            #move horiz right
            for x in range(self.x+1,len(board)):
                if type(board[x][self.y]) is Piece:
                    if board[x][self.y].team != self.team:
                        moves.append((x,self.y))
                    break
                else:
                    moves.append((x,self.y))
            #move horiz left
            for x in range(self.x-1,-1,-1):
                if type(board[x][self.y]) is Piece:
                    if board[x][self.y].team != self.team:
                        moves.append((x,self.y))
                    break
                else:
                    moves.append((x,self.y))

            #move vert up
            for y in range(self.y+1,len(board)):
                if type(board[self.x][y]) is Piece:
                    if board[self.x][y].team != self.team:
                        moves.append((self.x,y))
                    break
                else:
                    moves.append((self.x,y))
            #move vert down
            for y in range(self.y-1,-1,-1):
                if type(board[self.x][y]) is Piece:
                    if board[self.x][y].team != self.team:
                        moves.append((self.x,y))
                    break
                else:
                    moves.append((self.x,y))
        elif self.type == "KNIGHT":
            for r in range(len(board)):
                for c in range(len(board[r])):
                    if abs(r - self.x) == 2 and abs(c - self.y) == 1 or abs(r - self.x) == 1 and abs(c - self.y) == 2:
                        if type(board[r][c]) is Piece:
                            if board[r][c].team != self.team:
                                moves.append((r,c))
                        else:
                            moves.append((r,c))
        elif self.type == "BISHOP":
            # up right
            for i in range(1,len(board)-self.x):
                if self.y+i >= len(board): break
                if type(board[self.x+i][self.y+i]) is Piece:
                    if board[self.x+i][self.y+i].team != self.team:
                        moves.append((self.x+i,self.y+i))
                    break
                else:
                    moves.append((self.x+i,self.y+i))
            # up left
            for i in range(1,self.x+1):
                if self.y+i >= len(board): break
                if type(board[self.x-i][self.y+i]) is Piece:
                    if board[self.x-i][self.y+i].team != self.team:
                        moves.append((self.x-i,self.y+i))
                    break
                else:
                    moves.append((self.x-i,self.y+i))
            # down right
            for i in range(1,len(board)-self.x):
                if self.y-i < 0: break
                if type(board[self.x+i][self.y-i]) is Piece:
                    if board[self.x+i][self.y-i].team != self.team:
                        moves.append((self.x+i,self.y-i))
                    break
                else:
                    moves.append((self.x+i,self.y-i))
            # down left
            for i in range(1,self.x+1):
                if self.y-i < 0: break
                if type(board[self.x-i][self.y-i]) is Piece:
                    if board[self.x-i][self.y-i].team != self.team:
                        moves.append((self.x-i,self.y-i))
                    break
                else:
                    moves.append((self.x-i,self.y-i))
        elif self.type == "QUEEN":
            # rook type moves
            #move horiz right
            for x in range(self.x+1,len(board)):
                if type(board[x][self.y]) is Piece:
                    if board[x][self.y].team != self.team:
                        moves.append((x,self.y))
                    break
                else:
                    moves.append((x,self.y))
            #move horiz left
            for x in range(self.x-1,-1,-1):
                if type(board[x][self.y]) is Piece:
                    if board[x][self.y].team != self.team:
                        moves.append((x,self.y))
                    break
                else:
                    moves.append((x,self.y))

            #move vert up
            for y in range(self.y+1,len(board)):
                if type(board[self.x][y]) is Piece:
                    if board[self.x][y].team != self.team:
                        moves.append((self.x,y))
                    break
                else:
                    moves.append((self.x,y))
            #move vert down
            for y in range(self.y-1,-1,-1):
                if type(board[self.x][y]) is Piece:
                    if board[self.x][y].team != self.team:
                        moves.append((self.x,y))
                    break
                else:
                    moves.append((self.x,y))
            ################################################
            # bishop type moves
            # up right
            for i in range(1,len(board)-self.x):
                if self.y+i >= len(board): break
                if type(board[self.x+i][self.y+i]) is Piece:
                    if board[self.x+i][self.y+i].team != self.team:
                        moves.append((self.x+i,self.y+i))
                    break
                else:
                    moves.append((self.x+i,self.y+i))
            # up left
            for i in range(1,self.x+1):
                if self.y+i >= len(board): break
                if type(board[self.x-i][self.y+i]) is Piece:
                    if board[self.x-i][self.y+i].team != self.team:
                        moves.append((self.x-i,self.y+i))
                    break
                else:
                    moves.append((self.x-i,self.y+i))
            # down right
            for i in range(1,len(board)-self.x):
                if self.y-i < 0: break
                if type(board[self.x+i][self.y-i]) is Piece:
                    if board[self.x+i][self.y-i].team != self.team:
                        moves.append((self.x+i,self.y-i))
                    break
                else:
                    moves.append((self.x+i,self.y-i))
            # down left
            for i in range(1,self.x+1):
                if self.y-i < 0: break
                if type(board[self.x-i][self.y-i]) is Piece:
                    if board[self.x-i][self.y-i].team != self.team:
                        moves.append((self.x-i,self.y-i))
                    break
                else:
                    moves.append((self.x-i,self.y-i))
        elif self.type == "KING":
            enemyPieces = []
            for row in board:
                for piece in row:
                    if type(piece) is Piece and piece.team != self.team:
                        enemyPieces.append(piece)

            for r in range(len(board)):
                for c in range(len(board[r])):
                    if abs(r - self.x) <= 1 and abs(c - self.y) <= 1 and not (self.x != r and self.y != c):
                        if type(board[r][c]) is Piece:
                            if board[r][c].team != self.team:
                                moves.append((r,c))
                        else:
                            if deep:
                                isCheck = False
                                for ep in enemyPieces:
                                    if (r,c) in ep.getValidMoves(board, False): # prevent moving into check
                                        isCheck = True

                                        break
                                if not isCheck:
                                    moves.append((r,c))
                            else:
                                moves.append((r,c))
        #print(self.type+' has '+str(len(moves))+' moves available')
        if deep:
            for m in moves:
                simulated = self.simulateMove(m, board)
                for r in simulated:
                    for p in r:
                        if type(p) is Piece:
                            if p.team == self.team:
                                if p.inCheck(simulated):
                                    moves.remove(m)


        return moves

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
                if type(piece) is Piece:
                    col.append(Piece(piece.type, piece.team, piece.x, piece.y, piece.length))
                else:
                    col.append(0)
            newBoard.append(col)
        return newBoard

    def getValue(self):
        return PIECE_VALUES[self.type]

    def inCheck(self, board):
        if self.type != "KING":
            return False

        #print("inCHeck?")
        enemyPieces = []
        for row in board:
            for piece in row:
                if type(piece) is Piece and piece.team != self.team:
                    enemyPieces.append(piece)
        print(str(len(enemyPieces))+" enemy pieces")
        for p in enemyPieces:
            if (self.x,self.y) in p.getValidMoves(board, False):
                return True
                print("check")
        return False

    def isCheckmate(self, board):
        if not self.inCheck(board):
            return False

        enemyPieces = []
        for row in board:
            for piece in row:
                if type(piece) is Piece and piece.team != self.team:
                    enemyPieces.append(piece)

        canKingMove = False
        for m in self.getValidMoves(board):
            spotSafe = True
            for ep in enemyPieces:
                if m in ep.getValidMoves(board):
                    spotSafe = False
            if spotSafe:
                return False

    def die(self):
        # self.x = -1
        # self.y = -1
        print(self.type+' has died')
        self.move(-1, -1)

    def __repr__(self):
        return self.type + " "+ str(self.team)

class ChessConfig:
    def __init__(self, rows, cols, dimX, dimY):
        self.rows = rows
        self.cols = cols
        self.dimX = dimX
        self.dimY = dimY
