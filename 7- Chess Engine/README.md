# Chess Engine
This is a chess engine written in C++.
![menu_example](/home/chronos/git/CVprojects/7- Chess Engine/meta/menu_example.png) 

## Usage

The source code is provided in the [src](/src) directory.  A compilation script that has been tested on Linux (Centos) that works off the GCC compiler is provided in the [tools](/tools) directory ([compileChess](/tools/compileChess)).  Once compiled and run you should be presented with the menu (pictured above) from which the internal help system can be accessed with *h*.

![game_example](/home/chronos/git/CVprojects/7- Chess Engine/meta/board_example.png) 

## Major Technical Features 

* Move Generation Perft Numbers (thus move generation is known good)
* Alpha-Beta Pruning (granting performance)
* Move Exploration Sorting (Improving performance gains from the alpha beta pruning)
* Transposition Tables based on Zobrist (granting performance by recognising board positions evaluated before)
* Massive general optimisations such as storing piece locations (thus avoiding the need to iterate through the board to find pieces) and preallocation of the move vectors (preventing mass coping during resizing) and many many more!