#!/usr/bin/env python3
import random

# A simple list-based terminal Yahtzee game, designed specifically to work with machine learning neural networks.
# The NN will have 35 inputs per turn: the initial dice roll (5 numbers), a list of how that roll might be scored (13)
# how many rerolls are left (1), and a list showing the current game's existing scoresheet including upper bonus, yahtzees, and total score (16).
# The NN's available outputs, possible actions the NN can take, will be 44, the 13 potential scoring choices, & 31 different re-roll choices.
# The game class will automatically manage the finer details of scoring, like tallying yahtzee and upper bonuses (so AI only has to choose 1 action).

class Turn:
    
    def __init__(self, scoresheet):
        self.scoresheet = scoresheet
        self.dice = [0] * 5
        self.roll()
    
    def roll(self, reroll = range(5)):
        for i in reroll:
            self.dice[i] = random.randint(1, 6)
        self.counts = [self.dice.count(s) for s in range(1, 7)]
        self.score = [
            self.counts[0] if self.scoresheet[0] == -1 else 0,     # ones
            self.counts[1] * 2 if self.scoresheet[1] == -1 else 0, # twos
            self.counts[2] * 3 if self.scoresheet[2] == -1 else 0, # threes
            self.counts[3] * 4 if self.scoresheet[3] == -1 else 0, # fours
            self.counts[4] * 5 if self.scoresheet[4] == -1 else 0, # fives
            self.counts[5] * 6 if self.scoresheet[5] == -1 else 0, # sixes
            # three of a kind, four of a kind, full house, small straight, large straight, yahtzee, chance
            sum(self.dice) if any(count >= 3 for count in self.counts) and self.scoresheet[6] == -1 else 0,
            sum(self.dice) if any(count >= 4 for count in self.counts) and self.scoresheet[7] == -1 else 0,
            25 if (3 in self.counts and 2 in self.counts) and self.scoresheet[8] == -1 else 0,
            30 if ((self.counts[0] > 0 and self.counts[1] > 0 and self.counts[2] > 0 and self.counts[3] > 0) or
                        (self.counts[1] > 0 and self.counts[2] > 0 and self.counts[3] > 0 and self.counts[4] > 0) or
                        (self.counts[2] > 0 and self.counts[3] > 0 and self.counts[4] > 0 and self.counts[5] > 0)) and self.scoresheet[9] == -1 else 0,
            40 if ((self.counts[0] > 0 and self.counts[1] > 0 and self.counts[2] > 0 and self.counts[3] > 0 and self.counts[4] > 0) or
                        (self.counts[1] > 0 and self.counts[2] > 0 and self.counts[3] > 0 and self.counts[4] > 0 and self.counts[5] > 0)) and self.scoresheet[10] == -1 else 0,
            50 if any(count == 5 for count in self.counts) and self.scoresheet[11] == -1 else 0,
            sum(self.dice) if self.scoresheet[12] == -1 else 0
        ]

class Game:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.scoresheet = [-1] * 13 + [0] * 3 # 0s are upper & yahtzees bonuses, and total score
        self.rnd_count = 0
        self.rr_remain = 2  # rr_remain may need to be passed to NN
        self.turn = Turn(self.scoresheet[:])

    def action(self, choice):
        # may need to return a reward after actions?
        if 0 <= choice < 13:
            # Action is a scoring choice
            self.score_category(choice)
            self.rr_remain = 2
        elif self.rr_remain > 0:
            self.rr_remain -= 1
            # Action is a re-roll choice
            reroll_indices = self.get_reroll_indices(choice)
            self.turn.roll(reroll_indices)
        else:
            # Action is invalid, resulting in no reward?
            pass

    def score_category(self, category):
        if self.scoresheet[category] == -1:
            self.scoresheet[category] = self.turn.score[category]
            self.update_scoresheet()
            self.rnd_count += 1
            if self.rnd_count >= 13:
                self.end_game()
            else:
                self.turn = Turn(self.scoresheet[:])
        else:
            # Scoring option already used, invalid action
            pass

    def update_scoresheet(self):
        upper_section_score = sum(self.scoresheet[:6])
        if upper_section_score >= 63:
            self.scoresheet[13] = 35
        if self.scoresheet[11] == 50 and any(count == 5 for count in self.turn.counts):
            self.scoresheet[14] += 100
        self.scoresheet[15] = sum(s for s in self.scoresheet[:15] if s > 0)

    def get_reroll_indices(self, action):
        # Map the action index to the corresponding re-roll indices
        reroll_mapping = {
            13: [0], 14: [1], 15: [2], 16: [3], 17: [4],
            18: [0, 1], 19: [0, 2], 20: [0, 3], 21: [0, 4],
            22: [1, 2], 23: [1, 3], 24: [1, 4], 25: [2, 3],
            26: [2, 4], 27: [3, 4], 28: [0, 1, 2], 29: [0, 1, 3],
            30: [0, 1, 4], 31: [0, 2, 3], 32: [0, 2, 4], 33: [0, 3, 4],
            34: [1, 2, 3], 35: [1, 2, 4], 36: [1, 3, 4], 37: [2, 3, 4],
            38: [0, 1, 2, 3], 39: [0, 1, 2, 4], 40: [0, 1, 3, 4],
            41: [0, 2, 3, 4], 42: [1, 2, 3, 4], 43: [0, 1, 2, 3, 4]
        }
        return reroll_mapping[action]

    def end_game(self):
        # Game over, somehow work out how to provide final scores/reward and/or reset the game
        pass


# NOTES & old unused stuff
# ones, twos, threes, fours, fives, sixes, 63bonus(35), three kind, four kind, full house, small straight, large straight, yahtzee, chance, total
#print(f"Ones: {turn.score[0]} Twos: {turn.score[1]} Threes: {turn.score[2]} Fours: {turn.score[3]} Fives: {turn.score[4]} Sixes: {turn.score[5]}")
#print(f"Three of a kind: {turn.score[6]} Four of a kind: {turn.score[7]} Full house: {turn.score[8]} Small straight: {turn.score[9]} Large straight: {turn.score[10]} Yahtzee: { turn.score[11]} Chance: {turn.score[12]}")
''' # for later, list of possible reroll actions AI will have available to choose from, if score options aren't good.
potrolls = [[0], [1], [2], [3], [4], [0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [1, 3], [1, 4],[2, 3], [2, 4], [3, 4],
        [0, 1, 2], [0, 1, 3], [0, 1, 4], [0, 2, 3], [0, 2, 4], [0, 3, 4], [1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4],
        [0, 1, 2, 3], [0, 1, 2, 4], [0, 1, 3, 4], [0, 2, 3, 4], [1, 2, 3, 4], [0, 1, 2, 3, 4]]
'''
