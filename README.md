## Magic Man - NeuroEvolution of Augmenting Topologies (NEAT) Branch


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
Implementing biases to the nodes of the neural nets. This might improve learning.
Playing a game now takes about 0.5 to 1.5 seconds longer. Depending on the improvement this might be worth it.

## Results

The NEAT algorithm so far has perfomed considerably worse than the fixed topology approach.
While the fixed topology neural nets stalled at about 70 points average score the neural nets trained with NEAT stalled at negative 50.

![Score Progress](https://user-images.githubusercontent.com/64082072/94849521-d5129d00-0425-11eb-82ff-94656e5a7f0c.png)

The bots started with full connectivity as described in the reference paper, i.e. every sensor node is connected to every output node.
I suspect that this might be a serious disadvantage because a completely disconnected net performes much better.
If there are no connections between the sensors and the output at all, average score is about 8.

## Speciation 

Speciation works almost perfectly. It is more volatile than the reference papers results but it seems to work as anticipated

![Speciation](https://user-images.githubusercontent.com/64082072/94849529-d774f700-0425-11eb-819e-e07a556ac6bf.png)

The compatibility threshold δ is set to 2.25, C<sub>1</sub> and C<sub>2</sub> are set to 2, and C<sub>3</sub> is set to 0.7
As in the reference paper there are no particular reasons for these values and they are set through trial and error.
