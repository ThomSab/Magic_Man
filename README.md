# Magic Man

I implemented a game based on the cardgame "Wizard" and want to train bots to play it.
The projects goal is to improve to a point where the bots are as good or better than human players.

## Structure
As of now the bots consist of three neural nets each. Each neural net for a specific action the bots have to take during the game.
The bots then play the game against each other and reproduce based on their average score.
It is also possible to play against the bots directly.

## Challenges

The motivation for this project was to learn about genetic learning algorithms by implementing one from scratch.
Because I had litle experience prior to starting this project a lot of things had to be learned first.
One particular problem I encountered was the factor of luck in the game.
It is not possible to determine how fit any specimen of the population is until it has played a large amount of games.
Other Challenges include finding the optimal topology for the neural nets, optimizing the speed of the algorithm and visualization.

## Results this far

Results from the currently implemented method have been good but do not reach the goal of matching a human player.
While an average human player scores an average score of about 250 in any given game, the bots reach a maximum average score of about 60 before they stall out.

## Prospect

The next step is to implement a NeuroEvolution of Augmenting Topologies (NEAT) algorithm.
I have high expectations for this method, since it is far more sophisticated than the algorithm that I implemented from scratch.

