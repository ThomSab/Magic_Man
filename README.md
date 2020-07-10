# Magic Man - NeuroEvolution of Augmenting Topologies (NEAT) Branch

This branch was created in order to implement a far more sophisticated algorithm for evolving NNs.
The planned implementation is based on a [paper](https://www.mitpressjournals.org/doi/abs/10.1162/106365602320169811 "Stanley K., Miikkulainen R. (2002)") by K.O. Stanley and R. Miikkulainen that was published back in 2002 in the MIT Press Journals.
In their paper, K. Stanley and R. Miikulainen outline an algorithm that introduces new features to existing methods.
These new features significantly improve their performance.
The main feature introduced by the authors is the evolution of the topolgy of the neural net in addition to its connectivity.
Beyond that, the authors introduce other innovative mechanisms such as Speciation, starting from minimal structure and an improved method for mating to further improve the performance.

## Motivation and Goals
I implemented the algorithm in the current master branch mostly in order to learn about Neuroevolution.
More specifically - to encounter the most basic problems that have to be solved in order to make a genetic algorithm solve the given task.
Since the current implementation did not achieve much in the sense of maximum fitness, the idea is to turn to more refined approaches in order to achieve better results.
Beyond the results, the motivation is to learn more about Neuroevolution and its practical challenges.

## Challenges
As mentioned in the master branch, the element of chance in the game Wizard will probably remain a problem for the NEAT algorithm.
This concern is appropriate. Mostly because in their paper, K.Stanley and R.Mikkulainen exclusively apply the algorithm to tasks that lack any element of chance.
(XOR gate, Pole Balancing, Double Pole Balancing - with and without velocities)
Training time could be increased significantly by this.

