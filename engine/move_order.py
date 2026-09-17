import chess
from engine.evaluate import PIECE_VALUES

def rank_move(board, move):
    """Ranks moves based off of MVV-LVA. Move ordering helps with pruning."""

    if board.is_capture(move):
        attacker_value = PIECE_VALUES[board.piece_at(move.from_square).piece_type]
        victim = board.piece_at(move.to_square)
        victim_value = PIECE_VALUES[victim.piece_type] if victim else 100

        return (victim_value*10) - attacker_value
    
    return 0