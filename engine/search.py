import chess
from engine.evaluate import evaluate_board
from engine.move_order import rank_move
from engine.tt import TranspositionTable, EXACT, BETA_CUT, ALPHA_CUT

node_count = 0
tt = TranspositionTable()

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

    if board.can_claim_draw():
        return 0

    tt_score, tt_move = tt.lookup(board, depth, alpha, beta)
    if tt_score is not None:
        return tt_score
    
    if board.is_checkmate():
        return -24000 - depth

    if board.is_stalemate():
        return 0
    
    if board.is_insufficient_material():
        return 0
    
    if depth == 0:
        return quiescence(board, alpha, beta)

    max_score = -float('inf')
    best_move = None
    alpha_start = alpha

    moves = list(board.legal_moves)
    moves.sort(key=lambda move: 24000 if move == tt_move else rank_move(board, move), reverse=True)

    for move in moves:
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()
        if score > max_score:
            max_score = score
            best_move = move
        if score > alpha:
            alpha = max_score
        if score >= beta:
            break

    if (max_score <= alpha_start):
        flag = ALPHA_CUT
    elif (max_score >= beta):
        flag = BETA_CUT
    else:
        flag = EXACT

    tt.store(board, best_move, max_score, depth, flag)

    return max_score

def quiescence(board, alpha, beta):
    """Quiescence search keeps searching moves that are only captures, ensuring we end our 
    search whenever the board is "quiet". It returns the score with the highest evaluation."""

    tt_score, tt_move = tt.lookup(board, 0, alpha, beta)
    if tt_score is not None:
        return tt_score

    if board.turn == chess.WHITE: 
        current_score = evaluate_board(board)
    else:
        current_score = -evaluate_board(board)

    if current_score >= beta:
        tt.store(board, None, current_score, 0, BETA_CUT)
        return current_score

    if current_score > alpha:
        alpha = current_score

    max_score = current_score
    best_move = None
    alpha_start = alpha

    captures = list(board.generate_legal_captures())
    captures.sort(key=lambda move: 24000 if move == tt_move else rank_move(board, move), reverse=True)

    for move in captures:
        global node_count
        node_count += 1

        board.push(move)
        score = -quiescence(board, -beta, -alpha)
        board.pop()

        if score > max_score:
            max_score = score
            best_move = move
        if score > alpha:
            alpha = score
        if score >= beta:
            break

    if (max_score <= alpha_start):
        flag = ALPHA_CUT
    elif (max_score >= beta):
        flag = BETA_CUT
    else:
        flag = EXACT

    tt.store(board, best_move, max_score, 0, flag)

    return max_score



