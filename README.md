# Currently a WIP!

The goal of this project is to get a Neural Network to play Yahtzee, possibly through reinforcement learning.
I've always wanted to learn how to apply a neural network to a game! This is just a project for my curiosity.

Already built the Yahtzee game, fully functional and as close to the official rules as I could. Really curious how high a NN might score!
The game is specifically designed with inputs and outputs simplified into lists, so they can be easily implemented into a Neural Network.
But I've also included a "human-playable" version, that can be played in the terminal.

The game provides 35 values for the inputs to the NN, and has 44 actions available that the NN can perform on the game, as it's outputs.
So, 5 dice values, 13 ways that roll might be scored, 1 value for how many rerolls remain, and a list of the current scoresheet of 16 values.
Then, 13 potential scoring actions and 31 different reroll options are available as the outputs of the NN.

After coding the game, and trying a few basic NN designs as I understood them from tutorials, I was getting nowhere.
So I tried asking Claude.ai, and after a couple tries, it seems to have come up with an agent that kinda works!
However, I am not experienced enough with reinforcement learning, to know how to tweak things for better results,
and the AI is currently only able to give me general guidance on how to go further.
I've made several tweaks to my reward system, and various agent settings, and managed to get the NN to score
around 150-200 sometimes, but beyond that it doesn't seem to be progressing.

If anyone out there knows how to improve this, I could really use some help at this point.
