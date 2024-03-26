#!/usr/bin/env python3
import random

# A bare-bones human-playable version of Yahtzee.

# ⚀ ⚁ ⚂ ⚃ ⚄ ⚅
faces = { 1: '\u2680', 2: '\u2681', 3: '\u2682', 4: '\u2683', 5: '\u2684', 6: '\u2685' }
cats = ['Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes',
        'Three of a kind', 'Four of a kind', 'Full House', 'Small Straight', 'Large Straight',
        'Yahtzee', 'Chance', 'Upper Bonus', 'Yahtzee Bonus', 'Total']

nl='\n' # to bypass f-string limitation

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
        self.reset_game()

    def reset_game(self):
        self.valid = True
        self.rnd_count = 13
        self.rr_remain = 2
        self.scoresheet = [-1] * 13 + [0] * 3 # 0s are upper & yahtzees bonuses, and total score
        self.play()

    def play(self):
        input("Ready? Press Enter!")
        while self.rnd_count > 0:
            if self.rr_remain == 2 and self.valid: self.turn = Turn(self.scoresheet[:])
            print(f"\nScoresheet:\n{'  '.join(f'''{nl if i==6 else ''}{i if i < 13 else nl}-{cats[i]}: {s}''' for i,s in enumerate([s if s >= 0 else '_' for s in self.scoresheet]))}")
            print(f"\nRound - {14-self.rnd_count}")
            print(f'''\nDice:  {'  '.join('abcde'[i]+"-"+faces[d] for i,d in enumerate(self.turn.dice))}\n''')
            print(f"Available:  {'  '.join(f'{i}-{cats[i]}: {s}' for i,s in enumerate(self.turn.score) if s > 0)}")
            print(f"Rerolls remaining:  {self.rr_remain}\n")
            choice = input("Choose a score # option, or which dice (abcde) to reroll: ")
            if choice.isdigit() and (0 <= int(choice) < 13 and self.scoresheet[int(choice)] == -1) or choice == 11:
                #self.scoresheet[int(choice)] = self.turn.score[int(choice)]
                self.update_scoresheet(int(choice))
                self.rr_remain = 2
                self.rnd_count -= 1
            elif all(c in 'abcde' for c in choice) and self.rr_remain > 0:
                self.turn.roll([i for i, c in enumerate('abcde') if c in choice])
                self.rr_remain -= 1
            else:
                print("Invalid choice!")
                self.valid = False
            self.valid = True
        self.end_game()

    def update_scoresheet(self, choice):
        if choice == 11 and self.scoresheet[11] == 50 and any(count == 5 for count in self.turn.counts):
            self.scoresheet[14] += 100
        self.scoresheet[choice] = self.turn.score[choice]
        upper_section_score = sum(self.scoresheet[:6])
        if upper_section_score >= 63:
            self.scoresheet[13] = 35
        self.scoresheet[15] = sum(s for s in self.scoresheet[:15] if s > 0)

    def end_game(self):
        print("\nFinal scores:")
        print(f"{'  '.join(f'''{nl if i==6 else ''}{i if i < 13 else nl}-{cats[i]}: {s}''' for i,s in enumerate([s if s >= 0 else '_' for s in self.scoresheet]))}")

if __name__ == '__main__':
    Game()
