import chess
import time
from engine.evaluate import evaluate_board
from engine.move_order import rank_move
from engine.tt import TranspositionTable, EXACT, BETA_CUT, ALPHA_CUT

node_count = 0
tt = TranspositionTable()

class TimeOutException(Exception):
    """"Custom exception to handle timeouts during search."""

    pass

def get_best_move(board, max_depth=64, wtime=None, btime=None, winc=None, binc=None):
    """Finds the best move at the root of the search tree. Bridges the UCI communication with 
    the search algorithms like negamax below. Does the search at inreasing depth until the time
    allocated for the move is up. Returns the best move and its score."""

    global node_count
    node_count = 1

    if max_depth is None:
        max_depth = 64

    time_limit = None
    if wtime is not None and btime is not None:
        remaining_time = wtime if board.turn == chess.WHITE else btime
        increment = (winc or 0) if board.turn == chess.WHITE else (binc or 0)
        if remaining_time < 100:
            max_depth = 0
        else:
            target_time = (remaining_time / 40) + increment
            time_limit = target_time / 1000 if target_time < (remaining_time - 50) else (remaining_time - 50) / 1000

    if board.is_game_over():
        return None

    best_move = None
    max_score = -float('inf')
    start_time = time.time()
    depth_reached = 0

    moves = list(board.legal_moves)
    moves.sort(key=lambda move: rank_move(board, move), reverse=True)

    for current_depth in range(1, max_depth+1):
        try:
            if best_move in moves:
                moves.remove(best_move)
                moves.insert(0, best_move)
            
            current_best_move = None
            current_max_score = -float('inf')

            alpha = -float('inf')
            beta = float('inf')

            for move in moves:
                board.push(move)
                score = -negamax(board, current_depth - 1, -beta, -alpha, start_time, time_limit)
                board.pop()
                if score > current_max_score:
                    current_max_score = score
                    current_best_move = move
                if current_max_score > alpha:
                    alpha = current_max_score

            best_move = current_best_move
            max_score = current_max_score

            depth_reached = current_depth
            
        except TimeOutException:
            break
    
    return best_move, max_score, depth_reached


def negamax(board, depth, alpha, beta, start_time, time_limit):
    """Negamax function recursively searches moves a certain depth into the search tree and 
    returns the score with the highest evaluation."""

    global node_count
    node_count += 1

    if time_limit is not None and node_count % 1024 == 0:
        if time.time() - start_time > time_limit:
            raise TimeOutException()

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
        return quiescence(board, alpha, beta, start_time, time_limit)

    max_score = -float('inf')
    best_move = None
    alpha_start = alpha

    moves = list(board.legal_moves)
    moves.sort(key=lambda move: 24000 if move == tt_move else rank_move(board, move), reverse=True)

    for move in moves:
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha, start_time, time_limit)
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

def quiescence(board, alpha, beta, start_time, time_limit):
    """Quiescence search keeps searching moves that are only captures, ensuring we end our 
    search whenever the board is "quiet". It returns the score with the highest evaluation."""

    global node_count

    if time_limit is not None and node_count % 1024 == 0:
        if time.time() - start_time > time_limit:
            raise TimeOutException()

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
        node_count += 1

        board.push(move)
        score = -quiescence(board, -beta, -alpha, start_time, time_limit)
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



