import numpy as np
from stable_baselines3 import PPO
from controller_rl import KangarooTuningEnv, RLController
import config


class Trainer:
    def __init__(self, env=None, save_path="models/ppo_kangaroo"):
        if env is None:
            env = KangarooTuningEnv()
        self.env = env
        self.save_path = save_path
        
        self.model = PPO(
            "MlpPolicy",
            env,
            learning_rate=config.LEARNING_RATE,
            gamma=config.RL_GAMMA,
            verbose=1,
            tensorboard_log="logs/",
        )
        
        self.rl_controller = RLController(model=self.model)
        
    def train(self, total_timesteps=None):
        if total_timesteps is None:
            total_timesteps = config.RL_EPISODES * config.MAX_STEPS_EPISODE
            
        self.model.learn(
            total_timesteps=total_timesteps,
            progress_bar=True,
            save_freq=10000,
        )
        
    def save_model(self, path=None):
        if path is None:
            path = self.save_path
        self.model.save(path)
        print(f"Model saved to {path}")
        
    def load_model(self, path):
        self.model = PPO.load(path)
        self.rl_controller = RLController(model=self.model)
        print(f"Model loaded from {path}")
        
    def evaluate(self, num_episodes=10):
        episode_rewards = []
        episode_lengths = []
        safe_exits = 0
        road_entries = 0
        
        for episode in range(num_episodes):
            state, _ = self.env.reset()
            episode_reward = 0
            terminated = False
            truncated = False
            steps = 0
            
            while not (terminated or truncated):
                action, _ = self.model.predict(state, deterministic=True)
                state, reward, terminated, truncated, info = self.env.step(action)
                episode_reward += reward
                steps += 1
                
                if info.get("herd_center"):
                    zone = self.env.acoustic_env.get_zone_at(
                        info["herd_center"][0], info["herd_center"][1]
                    )
                    if zone == "corridor":
                        safe_exits += 1
                        terminated = True
                    elif zone == "road":
                        road_entries += 1
                        terminated = True
            
            episode_rewards.append(episode_reward)
            episode_lengths.append(steps)
            
        avg_reward = np.mean(episode_rewards)
        avg_length = np.mean(episode_lengths)
        safe_exit_rate = safe_exits / num_episodes
        road_entry_rate = road_entries / num_episodes
        
        return {
            "average_reward": avg_reward,
            "average_length": avg_length,
            "safe_exit_rate": safe_exit_rate,
            "road_entry_rate": road_entry_rate,
        }


def train_baseline():
    print("Training RL controller...")
    trainer = Trainer()
    trainer.train()
    trainer.save_model()
    return trainer


def evaluate_baseline(num_episodes=50):
    trainer = Trainer()
    trainer.load_model("models/ppo_kangaroo")
    results = trainer.evaluate(num_episodes)
    
    print("\n=== Evaluation Results ===")
    print(f"Average Reward: {results['average_reward']:.2f}")
    print(f"Average Episode Length: {results['average_length']:.2f}")
    print(f"Safe Exit Rate: {results['safe_exit_rate']*100:.1f}%")
    print(f"Road Entry Rate: {results['road_entry_rate']*100:.1f}%")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "train":
        train_baseline()
    elif len(sys.argv) > 1 and sys.argv[1] == "eval":
        evaluate_baseline(50)
    else:
        print("Usage: python training.py [train|eval]")
