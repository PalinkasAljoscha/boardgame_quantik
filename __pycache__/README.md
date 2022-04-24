## Board game 'Quantik' rules
Quantik is like a larger and more complex variant of tic tac toe. The board has *16* fiels in a *4x4* grid. Two player have each 8 tokens in four different shapes, two tokens from each shape. Between the two players tokens are distinguished by color.
Winner is who places a token which produces a row, column or *square* where all four shapes are present (of any color). As square are defined the *4x4* areas resulting from dividing the board with a horizontal and a vertical axis through the middle.
At each turn a player can place any token on a free field, if the oponent did not already place the same shape in the column, the row or the square of that field.

## AI for quantik
A minimax with alpha beta pruning is the basis for the AI. The explored graph is still too large for reasonble runtimes (serval millions states would be explored). A sort of *symmetry* is defined to reduce in each step the number of moves to explore. Each free field is assigned a *signature* which summarizes how many fields in the row, column and square are already occupied (by any token). Fields with same signature constitute a symmetry class. Only one representative from each symmetry class is explored (with all possible tokens for the move). This approach is rather rough, since color or shape of tokens is not at all considered. However, it serves well. The resulting AI computes fast and plays strong (although I have no benchmark for strength).

Note: For the first three moves in the game, the AI is making a random choice to avoid long computation, the detriment is negligible, since at the first few moves, all moves are more or less equivalent.

## pygame interface
To test and play the game, *game_app_quantik.py* is a [pygame](https://www.pygame.org) script, when executes opens a window where you can play against the AI.
for that purpose I also tested also [processing for python](https://py.processing.org/), however, this turned out to be very slow and unflexible, and also not simpler than pygame