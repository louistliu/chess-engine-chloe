import chess

class ChessEngine:
    def __init__(self):
        """Initializes a new chess board."""
        self.board = chess.Board()

    def get_legal_moves(self):
        """Returns a list of all legal moves in the current position."""
        return list(self.board.legal_moves)

    def make_move(self, move):
        """Makes a move on the board."""
        self.board.push(move)
    
    def undo_move(self):
        """Removes the last move from the board."""
        self.board.pop()

    def is_game_over(self):
        """Checks if the game has ended due to checkmate, stalemate, or draw."""
        return self.board.is_game_over()

    def reset_board(self):
        """Resets the board to the initial position."""
        self.board.reset()

    def __str__(self):
        """Returns a string representation of the board."""
        return str(self.board)