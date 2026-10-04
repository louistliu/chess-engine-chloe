import time
import chess

class TimeOutException(Exception):
    """Custom exception to handle timeouts during search."""

    pass

class TimeManager:
    """Handles the time allocation for the engine. Ensuring the engine never flags."""

    def __init__(self, soft=1.0, hard=1.0):
        self.start_time = None
        self.soft_limit = None
        self.hard_limit = None
        self.skip_search = False

        self.soft_limit_multiplier = soft
        self.hard_limit_multiplier = hard

    def allocate_time(self, board, wtime=None, btime=None, winc=None, binc=None, moves_until_limit=None):
        """Allocates time to the search, based off of the time remaining, increment and
        the amount of moves left until the next time bonus. If the time remaining is too
        low, the search will be skipped and an almost random move will be played."""

        self.start_time = time.time()
        self.soft_limit = None
        self.hard_limit = None
        self.skip_search = False

        if wtime is not None and btime is not None:
            remaining_time = wtime if board.turn == chess.WHITE else btime
            increment = (winc or 0) if board.turn == chess.WHITE else (binc or 0)
            if remaining_time < 75:
                self.skip_search = True
            else:
                divisor = moves_until_limit if moves_until_limit is not None else 20
                target_time = (remaining_time / divisor) + increment / 2
                safe_time = remaining_time - 50
                self.soft_limit = min(target_time * self.soft_limit_multiplier, safe_time) / 1000
                self.hard_limit = min(target_time * self.hard_limit_multiplier, safe_time) / 1000

    def check_early_timeout(self):
        """Checks if soft time limit has been reached. If so, throw an exception to cancel
        the search function in the search loop to search another depth."""

        if self.start_time is not None and self.soft_limit is not None:
            if time.time() - self.start_time > self.soft_limit:
                raise TimeOutException()
        
    def check_timeout(self):
        """Checks if hard time limit has been reached. If so, throw an exception to cancel
        the search function in the search loop."""

        if self.start_time is not None and self.hard_limit is not None:
            if time.time() - self.start_time > self.hard_limit:
                raise TimeOutException()
    
