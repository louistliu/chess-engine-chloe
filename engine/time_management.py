import time
import chess

class TimeOutException(Exception):
    """Custom exception to handle timeouts during search."""

    pass

class TimeManager:
    """Handles the time allocation for the engine. Ensuring the engine never flags."""

    def __init__(self):
        self.start_time = None
        self.time_limit = None
        self.skip_search = False

    def allocate_time(self, board, wtime=None, btime=None, winc=None, binc=None, moves_until_limit=None):
        """Allocates time to the search, based off of the time remaining, increment and
        the amount of moves left until the next time bonus. If the time remaining is too
        low, the search will be skipped and an almost random move will be played."""

        self.start_time = time.time()
        self.skip_search = False
        self.time_limit = None

        if wtime is not None and btime is not None:
            remaining_time = wtime if board.turn == chess.WHITE else btime
            increment = (winc or 0) if board.turn == chess.WHITE else (binc or 0)
            if remaining_time < 150:
                self.skip_search = True
            else:
                divisor = moves_until_limit if moves_until_limit is not None else 40
                target_time = (remaining_time / divisor) + increment
                self.time_limit = target_time / 1000 if target_time < (remaining_time - 100) else (remaining_time - 100) / 1000



    def check_timeout(self):
        """Checks if time limit has been reached. If so, throw an exception to cancel
        the search function in the search loop."""

        if self.start_time is not None and self.time_limit is not None:
            if time.time() - self.start_time > self.time_limit:
                raise TimeOutException()
    
