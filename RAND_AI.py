import random
import time

import Chess

class RAND_AI:
    def __init__(self, team):
        pass

    def getMove(self, board):
        #print(board)
        while 1:
            x1 = random.randint(0,7)
            y1 = random.randint(0,7)
            while type(board[x1][y1]) is not Chess.Piece:
                x1 = random.randint(0,7)
                y1 = random.randint(0,7)
            moves = board[x1][y1].getValidMoves(board)
            if len(moves) > 0:
                #print('calculating random move')
                # time.sleep(1)
                return [(x1,y1), moves[random.randint(0,len(moves) - 1)]]
