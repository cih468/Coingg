import pandas as pd
import numpy as np
import random
from collections import deque

class CustomEnv:
    # A custom Bitcoin trading environment
    def __init__(self, df, initial_balance=1000):
        self.df = df
        # Define action space and state size and other custom parameter
        self.df_total_steps = len(self.df)-1
        self.initial_balance = initial_balance

        # Action space from 0 to 3, 0 is hold, 1 is buy, 2 is sell
        self.action_space = np.array([0, 1, 2])

        # Orders history contains the balance, net_worth, crypto_bought, crypto_sold, crypto_held values for the last lookback_window_size steps
        #self.orders_history = deque(maxlen=self.lookback_window_size)
        
        # Market history contains the OHCL values for the last lookback_window_size prices
        #self.market_history = deque(maxlen=self.lookback_window_size)

        # State size contains Market+Orders history for the last lookback_window_size steps
        #self.state_size = (self.lookback_window_size, 10)

    # Reset the state of the environment to an initial state
    def reset(self):
        self.balance = self.initial_balance
        self.net_worth = self.initial_balance
        self.prev_net_worth = self.initial_balance
        self.crypto_held = 0
        self.crypto_sold = 0
        self.crypto_bought = 0
       
        self.start_step = 0
        self.end_step = self.df_total_steps
            
        self.current_step = self.start_step

        state = 0
        
        state = self._next_observation()
        
        return state

    # Get the data points for the given current_step
    def _next_observation(self):
        #state = round((self.df.loc[self.current_step, 'Close'] - self.df.loc[self.current_step, 'Open'])*100 / self.df.loc[self.current_step, 'Open'],-1)        
        state = 0
        if self.df.loc[self.current_step,'Close'] - self.df.loc[self.current_step,'Open'] > 0 :
            state=1
        return state

    # Execute one time step within the environment
    def step(self, action):
        self.crypto_bought = 0
        self.crypto_sold = 0
        self.current_step += 1

        # Set the current price to a random price between open and close
        current_price = self.df.loc[self.current_step, 'Close']
            
        if action == 0: # Hold
            pass
        
        elif action == 1 and self.balance > self.initial_balance*0.01:
            # Buy with 100% of current balance
            self.crypto_bought = self.balance / current_price
            self.balance -= self.crypto_bought * current_price
            self.crypto_held += self.crypto_bought

        elif action == 2 and self.crypto_held>0:
            # Sell 100% of current crypto held
            self.crypto_sold = self.crypto_held
            self.balance += self.crypto_sold * current_price
            self.crypto_held -= self.crypto_sold

        self.prev_net_worth = self.net_worth
        self.net_worth = self.balance + self.crypto_held * current_price

        # Calculate reward
        reward = self.net_worth - self.prev_net_worth

        if self.net_worth <= self.initial_balance/2:
            done = True
        else:
            done = False

        obs = self._next_observation()
        
        return obs, reward, done

    # render environment
    def render(self):
        print(f'Step: {self.current_step}, Net Worth: {self.net_worth}')