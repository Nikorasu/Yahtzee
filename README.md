## Currently a WIP!

The goal of this project is to get a Neural Network to play Yahtzee, possibly through reinforcement learning.

I've already built the Yahtzee game, fully functional and as close to the official rules as I could.
The game is specifically designed with inputs and outputs simplified into lists, so they can be easily implemented into a Neural Network.
But I've also included a "human-playable" version, that can be played in the terminal.

The game provides 35 values for the inputs to the NN, and has 44 actions available that the NN can perform on the game, as it's outputs.
So, 5 dice values, 13 ways that roll might be scored, 1 value for how many rerolls remain, and a list of the current scoresheet of 16 values.
Then, 13 potential scoring actions and 31 different reroll options are available as the outputs of the NN.
