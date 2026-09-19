import chess
import engine.psqt as psqt

PIECE_PHASE = (0, 0, 1, 1, 2, 4, 0)

def evaluate_board(board):
    """Evaluates the board according to the game phase and the piece square tables."""

    score_mg = 0
    score_eg = 0
    phase = 0

    for piece_type in chess.PIECE_TYPES:
        white_pieces = board.pieces(piece_type, chess.WHITE)
        black_pieces = board.pieces(piece_type, chess.BLACK)

        count = len(white_pieces) + len(black_pieces)
        phase += count * PIECE_PHASE[piece_type]

        mg_base = psqt.PIECES_MG[piece_type]
        eg_base = psqt.PIECES_EG[piece_type]
        mg_table = psqt.MG_LIST[piece_type]
        eg_table = psqt.EG_LIST[piece_type]

        for square in white_pieces:
            score_mg += mg_base + mg_table[chess.square_mirror(square)]
            score_eg += eg_base + eg_table[chess.square_mirror(square)]

        for square in black_pieces:
            score_mg -= mg_base + mg_table[square]
            score_eg -= eg_base + eg_table[square]

    if phase > 24:
        phase = 24

    return (score_mg * phase + score_eg * (24 - phase)) // 24