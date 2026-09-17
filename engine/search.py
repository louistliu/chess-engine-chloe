import chess
from engine.evaluate import evaluate_board
from engine.move_order import rank_move

node_count = 0

def get_best_move(board, depth=4):
    """Finds the best move at the root of the search tree. Bridges the UCI communication with 
    the search algorithms like negamax below."""

    global node_count
    node_count += 1

    best_move = None
    max_score = -float('inf')

    alpha = -float('inf')
    beta = float('inf')

    moves = list(board.legal_moves)
    moves.sort(key=lambda move: rank_move(board, move), reverse=True)

    for move in moves:
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()
        if score > max_score:
            max_score = score
            best_move = move
        if max_score > alpha:
            alpha = max_score
    
    print(f"info depth {depth} score cp {max_score} nodes {node_count}")
    return best_move


def negamax(board, depth, alpha, beta):
    """Negamax function recursively saerches moves a certain depth into the search tree and 
    returns the score with the highest evaluation."""

    global node_count
    node_count += 1
    
    if board.is_checkmate():
        return -24000 - depth

    if board.can_claim_draw():
        return 0
    
    if board.is_game_over():
        return 0
    
    if depth == 0:
        if board.turn == chess.WHITE: 
            return evaluate_board(board)
        else:
            return -evaluate_board(board)

    max_score = -float('inf')

    moves = list(board.legal_moves)
    moves.sort(key=lambda move: rank_move(board, move), reverse=True)

    for move in moves:
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()
        if score > max_score:
            max_score = score
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
        

    return max_score

