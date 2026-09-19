import chess
from engine.psqt import PIECES_MG

def rank_move(board, move):
    """Ranks moves based off of MVV-LVA. Move ordering helps with pruning."""

    if board.is_capture(move):
        attacker_value = PIECES_MG[board.piece_at(move.from_square).piece_type]
        victim = board.piece_at(move.to_square)
        victim_value = PIECES_MG[victim.piece_type] if victim else PIECES_MG[chess.PAWN]

        return (victim_value*10) - attacker_value
    
    return 0