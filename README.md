## Board game 'Quantik' rules
[Quantik] (https://en.boardgamearena.com/gamepanel?game=quantik) is like a larger and more complex variant of tic tac toe, but still pretty simple and quick to play. The board has *16* fiels in a *4x4* grid. Two player have each *8* tokens in *4* different shapes, two tokens from each shape. Between the two players, tokens are distinguished by color.
Winner is who places a token that produces a row, column or *square* where all four shapes are present (of any color). As square are defined the *4x4* areas resulting from dividing the board with a horizontal and a vertical axis through the middle.
At each turn a player can place any token on a free field, *if* the oponent *did not* already place the same shape in the column, the row or the square of that field.

## AI for quantik
Overall the AI is work in progress, where few ideas were tested and the so far best working kept.
A minimax with alpha beta pruning is the basis for the AI. The explored graph is still too large for reasonble runtimes. 

A sort of *symmetry* is defined to reduce in each step the number of moves to explore: Each free field is assigned a *signature* based on common columns, rows and squares with all fields that are already occupied (by any token). Fields with same signature constitute a symmetry class. Only one representative from each symmetry class is explored (with all possible tokens for the move). This approach is rather rough, since color or shape of tokens is not at all considered. 

Furthermore, to get quick runtimes, 1) minimax is limited to depth of five and 2) the first one or two moves of the AI are done at random (this not too bad, since at the very beginning, all moves seem to be more or less equivalent).

## pygame interface
To test and play the game, *game_app_quantik.py* is a [pygame](https://www.pygame.org) script, when executed opens a window where you can play against the AI.
For that purpose I also tested [processing for python](https://py.processing.org/), however, this turned out to be very slow and unflexible, and also not really simpler than pygame