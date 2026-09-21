import chess.polyglot

EXACT = 0
BETA_CUT = 1
ALPHA_CUT = 2

class TranspositionTable:
    def __init__(self):
        self.table = {}

    def lookup(self, board, depth, alpha, beta):
        hash_key = chess.polyglot.zobrist_hash(board)
        entry = self.table.get(hash_key)

        if entry:
            best_move, score, entry_depth, flag = entry
            if entry_depth >= depth:
                if flag == EXACT:
                    return score, best_move
                elif flag == BETA_CUT and score >= beta:
                    return score, best_move
                elif flag == ALPHA_CUT and score <= alpha:
                    return score, best_move
            else:
                return None, best_move

        return None, None
    
    def store(self, board, best_move, score, depth, flag):
        hash_key = chess.polyglot.zobrist_hash(board)
        entry = self.table.get(hash_key)
        if not entry or depth >= entry[2]:
            self.table[hash_key] = (best_move, score, depth, flag)


    def clear(self):
        self.table.clear()