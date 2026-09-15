import chess
import random

def get_random_move(board):
    """Returns a random legal move from the current board"""
    legal_moves = list(board.legal_moves)
    return random.choice(legal_moves) if legal_moves else None
