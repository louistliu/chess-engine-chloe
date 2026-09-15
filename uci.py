import sys
import chess
from engine.random_move_gen import get_random_move

def main():
    """UCI loop to communicate with a GUI"""
    board = chess.Board()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        words = line.split()
        command = words[0]

        if command == "uci":
            print("id name Chloe", flush=True)
            print("uciok", flush=True)

        elif command == "isready":
            print("readyok", flush=True)

        elif command == "ucinewgame":
            board.reset()

        elif command == "position":
            if words[1] == "startpos":
                board.reset()
                moves_start = 2
            elif words[1] == "fen":
                fen = " ".join(words[2:8])
                board.set_fen(fen)
                moves_start = 8
            
            if len(words) > moves_start and words[moves_start] == "moves":
                for move in words[moves_start + 1:]:
                    board.push_uci(move)

        elif command == "go":
            move = get_random_move(board)
            if move:
                print(f"bestmove {move.uci()}", flush=True)
            else:
                print("bestmove 0000", flush=True)

        elif command == "quit":
            break

if __name__ == "__main__":
    main()