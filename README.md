# 🌸 Chess Engine Chloe 🌸

Chloe is a UCI-compatible chess engine written in Python. It utilizes the python-chess library for underlying board representation and move generation, paired with a custom-built, optimized Negamax search algorithm based on Alpha-Beta pruning. 

You can play against Chloe on lichess: [link]

# Features

- Search
  - Negamax with alpha-beta pruning
  - Iterative deepening
  - Quiescence search
  - Transposition table
  - Late move reductions
  - Null move pruning
- Move ordering
  - Transposition table move first
  - MVV-LVA for captures
  - Killer moves (Two slots per ply)
  - Butterfly history heuristic
- Evaluation
  - PeSTO Piece-Square tables
  - Game phase calculation to switch between middlegame and endgame scores
- Time management
  - Allocates time per move from the remaining clock, the increment and moves until time added
  - Soft and hard bound for the allocated time, allowing the engine to use time dynamically.
 
# Setup

