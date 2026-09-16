import chess
from engine.evaluate import evaluate_board

def get_best_move(board, depth=3):
    """Finds the best move at the root of the search tree. Bridges the UCI communication with 
    the search algorithms like negamax below."""

    best_move = None
    max_score = -float('inf')

    for move in board.legal_moves:
        board.push(move)
        score = -negamax(board, depth - 1)
        board.pop()
        if score > max_score:
            max_score = score
            best_move = move
    print(f"info depth {depth} score cp {max_score}")
    return best_move


def negamax(board, depth):
    """Negamax function recursively saerches moves a certain depth into the search tree and 
    returns the score with the highest evaluation."""

    if board.is_checkmate():
        return -24000 - depth
    
    if board.is_game_over():
        return 0
    
    if depth == 0:
        if board.turn == chess.WHITE: 
            return evaluate_board(board)
        else:
            return -evaluate_board(board)

    max_score = -float('inf')
    for move in board.legal_moves:
        board.push(move)
        score = -negamax(board, depth - 1)
        board.pop()
        if score > max_score:
            max_score = score

    return max_score
    
