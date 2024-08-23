class Board:
    moveStack = []
    mover = None
    fen = ''

    def __init__(self, turn: bool, boardString: str = '---/---/---'):
        self.turn = turn
        if type(turn) is bool:
            Board.mover = turn
        else:
            raise Exception('Turn is not specified.')

        assert type(boardString) is str, f'The board STRING must be a STRING, you gave an {type(boardString)} instead.'

        assert len(boardString) == 11, ('The board string should be 11 characters long, 3 for each row and 2 '
                                        f'separators. Your fen string has {len(boardString)} characters.')

        self.originalFen = boardString.upper()
        out = self.originalFen
        out = out.split('/')
        self.boardArray = []
        for item in range(3):
            for idx in range(3):
                if out[item][idx] == 'X':
                    self.boardArray.append(True)
                elif out[item][idx] == 'O':
                    self.boardArray.append(False)
                elif out[item][idx] == '-':
                    self.boardArray.append(None)
                else:
                    raise ValueError("The supported types are X, O, or -.")
        Board.fen = boardString.upper()
        Board.__updateFen(self)

    def __updateFen(self) -> None:
        out = ''
        for num, item in enumerate(self.boardArray):
            match item:
                case True:
                    out += 'X'
                case False:
                    out += 'O'
                case None:
                    out += '-'
            if (num + 1) % 3 == 0 and (num + 1) != 9:
                out += '/'
        Board.fen = out

    def printBoard(self) -> None:
        out = ''
        for idx, item in enumerate(self.boardArray):
            if item is None:
                out += '-'
            elif item:
                out += 'X'
            elif not item:
                out += 'O'
            if (idx + 1) % 3 == 0 and (idx + 1) != 9:
                out += '\n'

    def printFen(self) -> None:
        Board.__updateFen(self)
        print(Board.fen)

    def clearEntireBoard(self) -> None:
        self.boardArray = [None, None, None,
                           None, None, None,
                           None, None, None]
        Board.mover = True
        Board.__updateFen(self)

    def clearFenBoard(self) -> None:
        Board.mover = self.turn
        out = self.originalFen
        out = out.split('/')
        self.boardArray = []
        for item in range(3):
            for idx in range(3):
                if out[item][idx] == 'X':
                    self.boardArray.append(True)
                elif out[item][idx] == 'O':
                    self.boardArray.append(False)
                elif out[item][idx] == '-':
                    self.boardArray.append(None)
                else:
                    raise ValueError("The supported types are X, O, or -.")
        Board.__updateFen(self)

    def move(self, moveNotation: str) -> None:
        if moveNotation.lower() == 'pass':
            Board.moveStack.append(moveNotation)
            Board.mover = not Board.mover
            return None

        assert Board.terminalState(self) is False, ('Game is already over, you could create a new board or clear this '
                                                    'one using Board.clearBoard().')

        assert len(moveNotation) == 2, (f'The function Board.move() takes in a move notation (e.g. X9, putting X on '
                                        f'the 9th square) and plays the move (if possible). Your input should be'
                                        f' only 2 characters, but you had {len(moveNotation)} character(s).')

        assert int(moveNotation[1]) in range(1, 10), (f'The function Board.move() takes in a move notation (e.g. '
                                                      f'X9, putting X on the 9th square) and plays the'
                                                      f' move (if possible). You entered the command to put '
                                                      f'{moveNotation[0]} on the {moveNotation[1]}(st, nd, rd, '
                                                      f'th) square, but the minimum square is 1 and the maximum '
                                                      f'square is 9. Your input exceeded that range.')

        if moveNotation[0].upper() == 'X':
            transBool = True
        elif moveNotation[0].upper() == 'O':
            transBool = False
        else:
            raise ValueError(f'The function Board.move() takes in move notation (e.g. X9, putting X on the 9th '
                             f'square) and plays the move (if possible). You entered the command to put '
                             f'{moveNotation[0]} '
                             f'on the {moveNotation[1]}(st, nd, rd, th) square, but the first character must be X or O,'
                             f' and nothing else. Your input violated that rule.')
        if Board.mover is True and moveNotation[0].upper() == 'X':
            Board.mover = False
        elif Board.mover is False and moveNotation[0].upper() == 'O':
            Board.mover = True
        else:
            raise Exception('Wrong Turn!')
        if self.boardArray[int(moveNotation[1]) - 1] is None:
            self.boardArray[int(moveNotation[1]) - 1] = transBool
            Board.moveStack.append(moveNotation)
        else:
            raise Exception('That square is already taken.')
        Board.__updateFen(self)

    def terminalState(self) -> bool:
        out = 0
        for item in self.boardArray:
            if item is None:
                out += 1
        if out == 0:
            return True
        for x in range(3):
            if (self.boardArray[x * 3] == self.boardArray[x * 3 + 1] == self.boardArray[x * 3 + 2]) and None is not \
                    self.boardArray[x * 3]:
                return True
        for y in range(3):
            if (self.boardArray[y] == self.boardArray[y + 3] == self.boardArray[y + 6]) and None is not self.boardArray[
                y]:
                return True
        if self.boardArray[0] == self.boardArray[4] == self.boardArray[8] and self.boardArray[0] is not None:
            return True
        if self.boardArray[2] == self.boardArray[4] == self.boardArray[6] and self.boardArray[2] is not None:
            return True
        return False

    def winner(self) -> str | None:
        if Board.terminalState(self):
            for x in range(3):
                if (self.boardArray[x * 3] == self.boardArray[x * 3 + 1] == self.boardArray[x * 3 + 2]) and None is not \
                        self.boardArray[x * 3]:
                    return 'OX'[int(self.boardArray[x * 3])]
            for y in range(3):
                if (self.boardArray[y] == self.boardArray[y + 3] == self.boardArray[y + 6]) and None is not \
                        self.boardArray[y]:
                    return 'OX'[int(self.boardArray[y])]
            if self.boardArray[0] == self.boardArray[4] == self.boardArray[8] and self.boardArray[0] is not None:
                return 'OX'[int(self.boardArray[0])]
            if self.boardArray[2] == self.boardArray[4] == self.boardArray[6] and self.boardArray[2] is not None:
                return 'OX'[int(self.boardArray[2])]
            out = 0
            for item in self.boardArray:
                if item is None:
                    out += 1
            if out == 0:
                return 'Draw'
        else:
            return None

    def legalMoves(self, turn: bool) -> list[str]:
        if not Board.terminalState(self):
            out = []
            xp, yp = 0, 0
            for item in self.boardArray:
                xp += 1
                if item is None:
                    out.append('OX'[int(turn)] + str(xp))
            return out
        else:
            raise Exception('Game already over.')

    def undoMove(self) -> None:
        if len(Board.moveStack) > 0:
            self.boardArray[int(Board.moveStack[-1][1]) - 1] = None
            Board.moveStack.pop(len(Board.moveStack) - 1)
            Board.clearFenBoard(self)
            for possibleMove in Board.moveStack:
                Board.move(self, possibleMove)
                Board.moveStack.pop(-1)
        Board.__updateFen(self)

    def occupied(self, square: int) -> bool:
        if self.boardArray[square - 1] is None:
            return False
        else:
            return True

    def findPiecePositions(self, piece: str) -> list[int] | list[list[str]]:
        assert piece.upper() in ['X', 'O', '-'], "The supported piece types are X, O, or -."
        out = [[], [], []]
        for idx, item in enumerate(self.boardArray):
            match item:
                case True:
                    out[0].append(idx + 1)
                case False:
                    out[1].append(idx + 1)
                case None:
                    out[2].append(idx + 1)
        match piece.upper():
            case 'X':
                return out[0]
            case 'O':
                return out[1]
            case '-':
                return out[2]

    def getRow(self, row: int | str) -> list[str]:
        assert row in [1, 2, 3], "The supported rows are 1, 2, or 3."
        out = []
        match row:
            case 1:
                for item in self.boardArray[:3]:
                    match item:
                        case True:
                            out.append('X')
                        case False:
                            out.append('O')
                        case None:
                            out.append('-')
            case 2:
                for item in self.boardArray[3:6]:
                    match item:
                        case True:
                            out.append('X')
                        case False:
                            out.append('O')
                        case None:
                            out.append('-')
            case 3:
                for item in self.boardArray[6:]:
                    match item:
                        case True:
                            out.append('X')
                        case False:
                            out.append('O')
                        case None:
                            out.append('-')
        return out

    def getColumn(self, column: int | str) -> list[str]:
        assert column in [1, 2, 3], "The supported rows are 1, 2, or 3."
        out = []
        match column:
            case 1:
                for item in [self.boardArray[0], self.boardArray[3], self.boardArray[6]]:
                    match item:
                        case True:
                            out.append('X')
                        case False:
                            out.append('O')
                        case None:
                            out.append('-')
            case 2:
                for item in [self.boardArray[1], self.boardArray[4], self.boardArray[7]]:
                    match item:
                        case True:
                            out.append('X')
                        case False:
                            out.append('O')
                        case None:
                            out.append('-')
            case 3:
                for item in [self.boardArray[2], self.boardArray[5], self.boardArray[8]]:
                    match item:
                        case True:
                            out.append('X')
                        case False:
                            out.append('O')
                        case None:
                            out.append('-')
        return out

    def __minimax(self, board, maximizing_player=True, alpha=float('-inf'), beta=float('inf')) -> tuple[
        float | int, str]:
        if board.terminalState(self):
            match board.winner(self):
                case 'Draw':
                    return 0, None
                case 'X':
                    return 1, None
                case 'O':
                    return -1, None
                case _:
                    raise Exception('Unidentified End State.')

        if maximizing_player:
            best_value = float('-inf')
            best_move = None
            for move in board.legalMoves(self, True):
                board.move(self, move)
                value = board.__minimax(self, board, False, alpha, beta)[0]
                board.undoMove(self)
                if value > best_value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, best_value)
                if alpha >= beta:
                    break
            return best_value, best_move
        else:
            best_value = float('inf')
            best_move = None
            for move in board.legalMoves(self, False):
                board.move(self, move)
                value = board.__minimax(self, board, True, alpha, beta)[0]
                board.undoMove(self)
                if value < best_value:
                    best_value = value
                    best_move = move
                beta = min(beta, best_value)
                if alpha >= beta:
                    break
            return best_value, best_move

    def calculatePosition(self) -> tuple[float | int, str]:
        boardEval = Board.__minimax(self, Board, Board.mover)
        return boardEval

    def __recursiveMinimax(self, board):
        moves = []
        iterable = 0
        while not board.terminalState(self):
            move = board.__minimax(self, board, board.mover)[1]
            moves.append(move)
            Board.move(self, move)
            iterable += 1
        for _ in range(iterable):
            Board.undoMove(self)
        return moves

    def bestContinuation(self) -> list[str]:
        return Board.__recursiveMinimax(self, Board)