import random
import time

import Chess

class RAND_AI:
    def __init__(self, team):
        self.team = team

    def getMove(self, board):
        # print("time to make a choice")
        # time.sleep(1)
        myPieces = []
        for r in board:
            for c in r:
                if type(c) in (Chess.Piece, Chess.King) and c.team == self.team:
                    myPieces.append(c)
        while 1:
            piece = random.choice(myPieces)
            moves = piece.getValidMoves(board)
            if len(moves) > 0:
                return [(piece.x, piece.y), random.choice(moves)]
            # else:
            #     print(str(piece) + " has no valid moves")
                # myPieces.remove(piece)
                # Chess.printBoard(board)
