import chess

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}

def evaluate_board(board):
    """Evaluates the board py pieces and their values"""

    score = 0
    for piece_type in PIECE_VALUES:
        white_count = len(board.pieces(piece_type, chess.WHITE))
        black_count = len(board.pieces(piece_type, chess.BLACK))

        score += (white_count - black_count) * PIECE_VALUES[piece_type]
        
    return score