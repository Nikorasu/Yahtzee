#!/usr/bin/env python3
import random
from math import ceil

# A simple list-based terminal Yahtzee game, designed specifically to work with machine learning neural networks.
# The NN will have 35 inputs per turn: the initial dice roll (5 numbers), a list of how that roll might be scored (13)
# how many rerolls are left (1), and a list showing the current game's existing scoresheet including upper bonus, yahtzees, and total score (16).
# The NN's available outputs, possible actions the NN can take, will be 44, the 13 potential scoring choices, & 31 different re-roll choices.
# The game class will automatically manage the finer details of scoring, like tallying yahtzee and upper bonuses (so AI only has to choose 1 action).
# (does nn need to have 13-round countdown? how do I account for variable turn/round length?)

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
                (self.counts[2] > 0 and self.counts[3] > 0 and self.counts[4] > 0 and self.counts[5] > 0)) and
                self.scoresheet[9] == -1 else 0,
            40 if ((self.counts[0] > 0 and self.counts[1] > 0 and self.counts[2] > 0 and self.counts[3] > 0 and self.counts[4] > 0) or
                (self.counts[1] > 0 and self.counts[2] > 0 and self.counts[3] > 0 and self.counts[4] > 0 and self.counts[5] > 0)) and 
                self.scoresheet[10] == -1 else 0,
            50 if any(count == 5 for count in self.counts) and self.scoresheet[11] == -1 else 0,
            sum(self.dice) if self.scoresheet[12] == -1 else 0
        ]

class Game:
    def __init__(self):
        self.rerolls = {
            13: [0], 14: [1], 15: [2], 16: [3], 17: [4],
            18: [0, 1], 19: [0, 2], 20: [0, 3], 21: [0, 4],
            22: [1, 2], 23: [1, 3], 24: [1, 4], 25: [2, 3],
            26: [2, 4], 27: [3, 4], 28: [0, 1, 2], 29: [0, 1, 3],
            30: [0, 1, 4], 31: [0, 2, 3], 32: [0, 2, 4], 33: [0, 3, 4],
            34: [1, 2, 3], 35: [1, 2, 4], 36: [1, 3, 4], 37: [2, 3, 4],
            38: [0, 1, 2, 3], 39: [0, 1, 2, 4], 40: [0, 1, 3, 4],
            41: [0, 2, 3, 4], 42: [1, 2, 3, 4], 43: [0, 1, 2, 3, 4]
        }
        self.reset_game()

    def reset_game(self):
        self.rnd_count = 13 # should round count be an input?
        self.rr_remain = 2  # pretty sure rr_remain may need to be passed to NN
        self.scoresheet = [-1] * 13 + [0] * 3 # 0s are upper & yahtzees bonuses, and total score
        self.turn = Turn(self.scoresheet[:])
        self.nn_in = self.turn.dice + self.turn.score + [self.rr_remain] + [max(0, s) for s in self.scoresheet]

    def action(self, choice):
        # Takes a number from 0 to 43, corresponding to the 13 scoring choices and 31 re-roll choices.
        if (0 <= choice < 13) and self.scoresheet[choice] == -1:
            # Action is a scoring choice
            self.update_scoresheet(choice)
            #reward = self.turn.score[choice] if self.turn.score[choice] > 0 else -1
            #reward = self.turn.score[choice] if choice > 5 or (choice < 6 and any(count > 2 for count in self.turn.counts)) else 0
            reward = self.turn.score[choice] if choice > 5 else ceil(self.turn.score[choice] * self.turn.counts[choice]*.5)
            # add more reward points if yahtzee
            reward += 50 if choice == 11 and any(count == 5 for count in self.turn.counts) else 0
            self.rnd_count -= 1
            if self.rnd_count <=0:
                reward = self.end_game()
                max_future_reward = 0
            else:
                self.turn = Turn(self.scoresheet[:])
                max_future_reward = max(self.turn.score)
            self.rr_remain = 2
        elif choice in self.rerolls and self.rr_remain > 0:
            # Action is a re-roll choice
            self.rr_remain -= 1
            b4roll = max(self.turn.score)
            reroll_indices = self.rerolls[choice]
            self.turn.roll(reroll_indices)
            reward = max(5, max(self.turn.score) - b4roll)
            max_future_reward = max(max(self.turn.score), ceil((self.turn.counts.index(max(self.turn.counts))+1) * max(self.turn.counts) * max(self.turn.counts)*.5))
        else:
            reward = -1
            max_future_reward = max(self.turn.score)
        self.nn_in = self.turn.dice + self.turn.score + [self.rr_remain] + [max(0, s) for s in self.scoresheet]
        return reward, max_future_reward

    def update_scoresheet(self, choice):
        if choice == 11 and self.scoresheet[11] == 50 and any(count == 5 for count in self.turn.counts):
            self.scoresheet[14] += 100
        self.scoresheet[choice] = self.turn.score[choice]
        upper_section_score = sum(self.scoresheet[:6])
        if upper_section_score >= 63:
            self.scoresheet[13] = 35
        self.scoresheet[15] = sum(s for s in self.scoresheet[:15] if s > 0)

    def end_game(self):
        end_score = self.scoresheet[15]
        #end_reward = end_score if end_score > 150 else -50
        end_reward = end_score*2 if end_score > 200 else end_score if end_score > 100 else end_score//2 if end_score > 50 else 0
        # additional reward if all scores indexs(0-10) and 12 are above 0
        #if all(s > 0 for s in self.scoresheet[:11]) and self.scoresheet[12] > 0: end_reward += 100
        self.reset_game()
        return end_reward
