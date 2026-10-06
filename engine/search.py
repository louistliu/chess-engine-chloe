import chess
from engine.time_management import TimeManager, TimeOutException
from engine.evaluate import evaluate_board
from engine.move_order import rank_move
from engine.tt import TranspositionTable, EXACT, BETA_CUT, ALPHA_CUT

node_count = 0
history_table = [[0 for _ in range(64)] for _ in range(64)]
killer_moves = [[None, None] for _ in range(64)] 
tt = TranspositionTable()
tm = TimeManager(0.3, 1.8)

def get_best_move(board, max_depth=64, wtime=None, btime=None, winc=None, binc=None, moves_until_limit=None):
    """Finds the best move at the root of the search tree. Bridges the UCI communication with 
    the search algorithms like negamax below. Does the search at inreasing depth until the time
    allocated for the move is up. Returns the best move and its score."""

    global node_count, killer_moves, history_table
    node_count = 1

    if max_depth is None:
        max_depth = 64

    if board.is_game_over():
        return None

    moves = list(board.legal_moves)

    best_move = moves[0]
    max_score = -float('inf')
    depth_reached = 0

    tm.allocate_time(board, wtime, btime, winc, binc, moves_until_limit)

    if tm.skip_search:
        return best_move, max_score, 0

    #Sort first moves by MVV-LVA captures.
    moves.sort(key=lambda move: rank_move(board, move), reverse=True)

    #Initialize killer move table with two slots for each new search.
    killer_moves = [[None, None] for _ in range(64)] 

    #Initialize history table for each new search
    history_table = [[0 for _ in range(64)] for _ in range(64)]

    for current_depth in range(1, max_depth+1):
        try:
            prev_best_move = best_move

            if best_move in moves:
                moves.remove(best_move)
                moves.insert(0, best_move)
            
            current_best_move = None
            current_max_score = -float('inf')

            alpha = -float('inf')
            beta = float('inf')

            for move in moves:
                board.push(move)
                score = -negamax(board, current_depth-1, -beta, -alpha, 1)
                board.pop()
                if score > current_max_score:
                    current_max_score = score
                    current_best_move = move
                if current_max_score > alpha:
                    alpha = current_max_score

            best_move = current_best_move
            max_score = current_max_score

            depth_reached = current_depth

            #Forced checkmate is found, hence stop searching deeper depths.
            if max_score > 23000:
                break

            #If the best move stays the same, it is more likely it's the best move, hence
            #we can try to save time here.
            if best_move == prev_best_move:
                tm.check_early_timeout()
            
        except TimeOutException:
            break
    
    return best_move, max_score, depth_reached

def negamax(board, depth, alpha, beta, ply):
    """Negamax function recursively searches moves a certain depth into the search tree and 
    returns the score with the highest evaluation."""

    global node_count, history_table
    node_count += 1

    if node_count & 255 == 0:
        tm.check_timeout()

    #Check claiming draws first, since transposition table does not know anything about either the 3-fold 
    #repetition or the 50-move rule and the engine should prevent it when it thinks it's better.
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
    #Transposition table move goes first, then all captures and then the quiet killer moves.
    moves.sort(key=lambda move: 150000 if move == tt_move else rank_move(board, move, killer_moves[ply], history_table), reverse=True)

    for move in moves:
        board.push(move)
        score = -negamax(board, depth-1, -beta, -alpha, ply+1)
        board.pop()
        if score > max_score:
            max_score = score
            best_move = move
        if score > alpha:
            alpha = max_score
        if score >= beta:
            if not board.is_capture(move):
                #Quiet killer moves get overwritten at a beta-cutoff.
                if killer_moves[ply][0] != move:
                    killer_moves[ply][1] = killer_moves[ply][0]
                    killer_moves[ply][0] = move

                #Quiet moves causing a beta-cutoff are added to the history table.
                history_table[move.from_square][move.to_square] += depth * depth
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

    global node_count

    if node_count & 255 == 0:
        tm.check_timeout()

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
    #Killer moves don't matter here, since quiescence search only evaluates captures.
    captures.sort(key=lambda move: 150000 if move == tt_move else rank_move(board, move), reverse=True)

    for move in captures:
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