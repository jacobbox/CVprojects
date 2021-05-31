# Chess Engine
This is a chess engine written in C++.

![menu_example](https://github.com/jacobbox/CVprojects/blob/5dbfeb70926811912f9df80e279c3c093993ee98/7-%20Chess%20Engine/meta/menu_example.png) 

## Usage

The source code is provided in the [src](/src) directory.  A compilation script that has been tested on Linux (Centos) that works off the GCC compiler is provided in the [tools](/tools) directory ([compileChess](/tools/compileChess)).  Once compiled and run you should be presented with the menu (pictured above) from which the internal help system can be accessed with *h*.

![game_example](https://github.com/jacobbox/CVprojects/blob/fd3025564843c6ea0ea47ba1f31324d80c7266aa/7-%20Chess%20Engine/meta/board_example.png) 

## Major Technical Features 

* Move Generation Perft Numbers (thus move generation is known good)
* Alpha-Beta Pruning (granting performance)
* Move Exploration Sorting (Improving performance gains from the alpha beta pruning)
* Transposition Tables based on Zobrist (granting performance by recognising board positions evaluated before)
* Massive general optimisations such as storing piece locations (thus avoiding the need to iterate through the board to find pieces) and preallocation of the move vectors (preventing mass coping during resizing) and many many more!
