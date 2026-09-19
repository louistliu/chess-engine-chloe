import chess
from engine.evaluate import evaluate_board
from engine.move_order import rank_move

node_count = 0

def get_best_move(board, depth=4):
    """Finds the best move at the root of the search tree. Bridges the UCI communication with 
    the search algorithms like negamax below."""

    global node_count
    node_count = 1

    if board.is_game_over():
        return None

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
    
    return best_move, max_score


def negamax(board, depth, alpha, beta):
    """Negamax function recursively searches moves a certain depth into the search tree and 
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
        return quiescence(board, alpha, beta)

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

def quiescence(board, alpha, beta):
    """Quiescence search keeps searching moves that are only captures, ensuring we end our 
    search whenever the board is "quiet". It returns the score with the highest evaluation."""

    if board.turn == chess.WHITE: 
        current_score = evaluate_board(board)
    else:
        current_score = -evaluate_board(board)

    if current_score >= beta:
        return beta

    if current_score > alpha:
        alpha = current_score

    max_score = current_score

    captures = list(board.generate_legal_captures())
    captures.sort(key=lambda move: rank_move(board, move), reverse=True)

    for move in captures:
        global node_count
        node_count += 1

        board.push(move)
        score = -quiescence(board, -beta, -alpha)
        board.pop()

        if score > max_score:
            max_score = score
        if max_score > alpha:
            alpha = max_score
        if max_score >= beta:
            return beta

    return max_score



