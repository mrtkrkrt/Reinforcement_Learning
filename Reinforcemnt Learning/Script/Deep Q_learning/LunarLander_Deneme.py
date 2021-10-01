import gym
import numpy as np
import random
import tensorflow as tf
from collections import deque
from keras.layers import Dense
from keras.models import Sequential
from tensorflow.keras.optimizers import Adam

class DQL_Agent():
    
    def __init__(self, env):
        self.env = env
        self.state_size = env.observation_space.shape[0]
        self.action_size = env.action_space.n
        self.epsilon = 1
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9993
        self.gamma = 0.99
        self.learning_rate = 0.0001
        self.memory = deque(maxlen=4000)
        self.model = self.build_model()
        self.target_model = self.build_model()
        
    def build_model(self):
        model = Sequential()
        model.add(Dense(64, input_dim = self.state_size, activation = "relu"))
        model.add(Dense(64, activation = "relu"))
        model.add(Dense(self.action_size, activation="linear"))
        model.compile(loss = "mse", optimizer = Adam(learning_rate=self.learning_rate))
        return model
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        
    def act(self, s):
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.action_size)
        act_ = self.model.predict(s)
        return np.argmax(act_[0])
    
    def replay(self, batch_size):
        
        if len(agent.memory) < batch_size:
            return
        
        mini_batch = random.sample(self.memory, batch_size)
        mini_batch = np.array(mini_batch)
        not_done_indices = np.where(mini_batch[:, 4] == False)
        y = np.copy(mini_batch[:, 2])
        
        if(len(not_done_indices[0]) > 0):
            predict_sprime = self.model.predict(np.vstack(mini_batch[:, 3]))
            predict_sprime_target = self.model.predict(np.vstack(mini_batch[:, 3]))
            
            y[not_done_indices] += np.multiply(self.gamma, predict_sprime_target[not_done_indices, np.argmax(predict_sprime[not_done_indices, :][0], axis=1)][0])
        
        actions = np.array(mini_batch[:, 1], dtype=int)
        y_target = self.model.predict(np.vstack(mini_batch[:, 0]))
        y_target[range(batch_size), actions] = y
        self.model.fit(np.vstack(mini_batch[:, 0]), y_target, epochs=1, verbose=0)
        
#    def replay(self, batch_size):
#        # training
#        if len(self.memory) < batch_size:
#            return
#        minibatch = random.sample(self.memory,batch_size)
#        for state, action, reward, next_state, done in minibatch:
#            if done:
#                target = reward 
#            else:
#                target = reward + self.gamma*np.amax(self.model.predict(next_state)[0])
#            train_target = self.model.predict(state)
#            train_target[0][action] = target
#            self.model.fit(state,train_target, verbose = 0)

    def adaptiveEGreedy(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def targetModelUpdate(self):
        self.target_model.set_weights(self.model.get_weights())


if __name__ == "__main__":
    env = gym.make('LunarLander-v2')

    agent = DQL_Agent(env)
    state_number = env.observation_space.shape[0]
    
    batch_size = 32
    episodes = 10000
    for e in range(episodes):
        
        state = env.reset()
        state = np.reshape(state, [1, state_number])

        total_reward = 0
        for time in range(1000):
            
            # env.render()

            # act
            action = agent.act(state)
            
            # step
            next_state, reward, done, _ = env.step(action)
            next_state = np.reshape(next_state, [1, state_number])

            # remember / storage
            agent.remember(state, action, reward, next_state, done)

            # update state
            state = next_state

            #Perform experience replay if memory length is greater than minibatch length
            agent.replay(batch_size)

            total_reward += reward
            
            if done:
                agent.targetModelUpdate()
                break

        # epsilon decay
        agent.adaptiveEGreedy()

        # Running average of past 100 episodes
        print('Episode: {}, Reward: {}'.format(e,total_reward))  


# %% test
import time
trained_model = agent
state = env.reset()
state = np.reshape(state, [1, env.observation_space.shape[0]])
while True:
    env.render()
    action = trained_model.act(state)
    next_state, reward, done, _ = env.step(action)
    next_state = np.reshape(next_state, [1,env.observation_space.shape[0]])
    state = next_state
#    time.sleep(0.8)
    if done:
        break
print("Done")    