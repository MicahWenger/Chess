import Chess

class MW_AI:
    def __init__(self, team):
        self.team = team


    def getBestOffensive(self, team, board):
        # figure out which pieces I have
        myPieces = []
        for r in board:
            for c in r:
                if type(c) in (Chess.Piece, Chess.King) and c.team == team:
                    myPieces.append(c)

        # gather all possible moves I can make
        # myMoves = [[(piece, move) for move in piece.getValidMoves(board)] for piece in myPieces]
        myMoves = []
        for piece in myPieces:
            [myMoves.append((piece, move)) for move in piece.getValidMoves(board)]

        # print(myMoves)
        # picking a default move
        bestMove = myMoves[0][1]
        bestMovePiece = myMoves[0][0]
        bestMoveScore = 0

        # finding the best move for offense
        for moveSet in myMoves:  # a moveset is (piece, move)
            currPiece = moveSet[0]
            currMove = moveSet[1]
            enemyPiece = board[currMove[0]][currMove[1]]
            if type(enemyPiece) in (Chess.Piece, Chess.King):
                if enemyPiece.getValue() >= bestMoveScore and enemyPiece.getValue() >= currPiece.getValue():
                    print("found new best move for " + str(currPiece))
                    bestMove = currMove
                    bestMovePiece = currPiece
                    bestMoveScore = enemyPiece.getValue()


        return [(bestMovePiece.x,bestMovePiece.y), bestMove]

    def getBestDefensive(self, team, board):
        myPieces = []
        myMoves = []
        bestMove = bestMovePiece = bestMoveScore = 0

        for r in board:
            for c in r:
                if type(c) is Chess.Piece and c.team == team:
                    myPieces.append(c)
        for p in myPieces:
            moves = p.getValidMoves(board)
            if len(moves) > 0:
                for m in moves:
                    myMoves.append((p,m))

        # picking a default move
        bestMove = myMoves[0][1]
        bestMovePiece = myMoves[0][0]
        bestMoveScore = 0

        # finding the best move for offense
        for moveSet in myMoves:
            currPiece = moveSet[0]
            m = moveSet[1]
            enemyPiece = board[m[0]][m[1]]
            if type(enemyPiece) is Chess.Piece:
                if enemyPiece.getValue() >= bestMoveScore:
                    # print("found new best move for "+str(currPiece))
                    bestMove = m
                    bestMovePiece = currPiece
                    bestMoveScore = enemyPiece.getValue()


        return [(bestMovePiece.x,bestMovePiece.y), bestMove]

    def getMove(self, board):
        print("getting smart move")
        # myBestOffensiveMove = self.getBestOffensive(self.team, board)
        # myBestMoveScore = board[myBestOffensiveMove[1][0]][myBestOffensiveMove[1][1]].getValue()
        # enemyBestOffensiveMove = self.getBestOffensive(1-self.team, board)
        # enemyBestMoveScore = board[enemyBestOffensiveMove[1][0]][enemyBestOffensiveMove[1][1]].getValue()


        return self.getBestOffensive(self.team, board)
        # return myBestOffensiveMove if myBestMoveScore > enemyBestMoveScore else myBestDefensiveMove
