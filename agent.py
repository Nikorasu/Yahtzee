#!/usr/bin/env python3
from Yahtzee import Game,Turn
import random
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

cats = ['Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes',
        'ThreeKind', 'FourKind', 'FullHouse', 'SmallStraight', 'LargeStraight',
        '\x1b[36mYahtzee\x1b[0m', 'Chance', '\x1b[32mUpperBonus\x1b[0m', '\x1b[36;1mYahtzeeBonus\x1b[0m', '\x1b[1mTotal'] #\x1b[0m

class YahtzeeAgent(nn.Module):
    def __init__(self):
        super(YahtzeeAgent, self).__init__()
        self.fc1 = nn.Linear(35, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 44)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def train_agent(num_episodes):
    game = Game()
    agent = YahtzeeAgent().to(device)
    target_agent = YahtzeeAgent().to(device)
    target_agent.load_state_dict(agent.state_dict())
    optimizer = optim.Adam(agent.parameters(), lr=0.001)
    replay_buffer = deque(maxlen=10000)
    epsilon = 1.0
    epsilon_decay = 0.999  # .999 .995
    epsilon_min = 0.01
    gamma = 0.99
    batch_size = 64
    update_target_every = 256

    for episode in range(num_episodes):
        game.reset_game()
        state = torch.tensor(game.nn_in, dtype=torch.float32, device=device)
        done = False
        episode_reward = 0

        while not done:
            if random.random() < epsilon:
                action = random.randint(0, 43)
            else:
                q_values = agent(state)
                action = torch.argmax(q_values).item()

            reward = game.action(action) #, max_future_reward
            next_state = torch.tensor(game.nn_in, dtype=torch.float32, device=device)

            replay_buffer.append((state, action, reward, next_state)) # + max_future_reward

            if len(replay_buffer) >= batch_size:
                sample = random.sample(replay_buffer, batch_size)
                states, actions, rewards, next_states = zip(*sample)

                states = torch.stack(states).to(device)
                next_states = torch.stack(next_states).to(device)

                q_values = agent(states)
                next_q_values = target_agent(next_states).detach()
                target_q_values = q_values.clone()

                for i in range(batch_size):
                    target_q_values[i][actions[i]] = rewards[i] + gamma * torch.max(next_q_values[i])

                loss = F.mse_loss(q_values, target_q_values)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            state = next_state
            episode_reward += reward

            if reward < 0 or game.rnd_count <= 0:
                done = True

            if episode % update_target_every == 0:
                target_agent.load_state_dict(agent.state_dict())

        epsilon = max(epsilon * epsilon_decay, epsilon_min)
        yellow = '\x1b[33;1m' if episode_reward >= 300 else ''
        bgreen = '\a\x1b[32;1m'
        print(f"Episode: {1+episode: <6} Reward: {yellow}{episode_reward: <6}",end='\x1b[0m')
        print(f"Scored: {'  '.join(f'''{cats[i]}:{bgreen if i==15 and s>=200 else ''}{s}''' for i,s in enumerate(game.scoresheet) if s > 0)}",end='\x1b[0m\n')

# Example usage
train_agent(num_episodes=100000)