import gymnasium as gym
from stable_baselines3 import PPO

import gym_sailing  # noqa

env = gym.make("Sailboat-v0")
model = PPO("MlpPolicy", env, verbose=1)

# Train the agent
model.learn(total_timesteps=1_000)

# Test the trained model
observation, info = env.reset()
for _ in range(1000):
    action, _ = model.predict(observation)
    observation, reward, terminated, truncated, info = env.step(action)


env.close()
