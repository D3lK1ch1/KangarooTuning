import numpy as np
import gymnasium as gym
from gymnasium import spaces
import config
from environment import AcousticEnvironment
from kangaroo_agent import Herd
from acoustic_field import AcousticField
from controller_rule_based import RuleBasedController


class KangarooTuningEnv(gym.Env):
    metadata = {"render_modes": ["human"]}
    
    def __init__(self, render_mode=None, herd_size=config.HERD_SIZE_DEFAULT):
        super().__init__()
        
        self.herd_size = herd_size
        self.render_mode = render_mode
        
        self.observation_space = spaces.Box(
            low=0, high=50, shape=(config.RL_STATE_DIM,), dtype=np.float32
        )
        
        self.action_space = spaces.Discrete(config.RL_ACTION_DIM)
        
        self.acoustic_env = AcousticEnvironment()
        self.acoustic_field = AcousticField()
        self.herd = Herd(herd_size)
        self.controller = RuleBasedController()
        
        self.current_step = 0
        self.max_steps = config.MAX_STEPS_EPISODE
        
    def _get_state(self):
        herd_center = self.herd.get_herd_center()
        
        distance_to_corridor = self.acoustic_env.distance_to_corridor(
            herd_center[0], herd_center[1]
        )
        distance_to_road = self.acoustic_env.distance_to_road(
            herd_center[0], herd_center[1]
        )
        average_stress = self.herd.get_average_stress()
        herd_dispersion = self.herd.get_herd_dispersion()
        construction_noise = self.acoustic_env.construction_noise_level
        
        return np.array([
            distance_to_corridor / 50.0,
            distance_to_road / 50.0,
            average_stress,
            herd_dispersion / 10.0,
            construction_noise,
        ], dtype=np.float32)
    
    def _calculate_reward(self, previous_state):
        herd_center = self.herd.get_herd_center()
        
        prev_dist_to_corridor = previous_state[0] * 50.0
        curr_dist_to_corridor = self.acoustic_env.distance_to_corridor(
            herd_center[0], herd_center[1]
        )
        
        reward = 0.0
        
        if curr_dist_to_corridor < prev_dist_to_corridor:
            reward += config.CORRIDOR_PROXIMITY_REWARD
        
        zone = self.acoustic_env.get_zone_at(herd_center[0], herd_center[1])
        if zone == "corridor":
            reward += config.SAFE_EXIT_REWARD
            return reward, True
            
        if zone == "road":
            reward += config.ROAD_ENTRY_PENALTY
            return reward, True
            
        avg_stress = self.herd.get_average_stress()
        if avg_stress > config.KANGAROO_PANIC_THRESHOLD:
            reward += config.STRESS_PANIC_PENALTY
            
        herd_dispersion = self.herd.get_herd_dispersion()
        if herd_dispersion > 8:
            reward += config.HERD_FRAGMENT_PENALTY
            
        return reward, False
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        self.acoustic_env.reset()
        self.acoustic_field.reset()
        
        start_x = np.random.randint(3, 10)
        start_y = np.random.randint(20, 30)
        self.herd.reset(start_x, start_y)
        
        self.current_step = 0
        
        state = self._get_state()
        info = {}
        
        return state, info
    
    def step(self, action):
        self.current_step += 1
        
        previous_state = self._get_state()
        
        action_name = config.RL_ACTION_MAP.get(action, "increase_intensity")
        
        if action_name == "increase_intensity":
            new_intensity = min(1.0, self.acoustic_field.beam_intensity + 0.1)
            self.acoustic_field.set_mid_freq_beam(
                self.acoustic_field.beam_angle, new_intensity
            )
        elif action_name == "decrease_intensity":
            new_intensity = max(0.0, self.acoustic_field.beam_intensity - 0.1)
            self.acoustic_field.set_mid_freq_beam(
                self.acoustic_field.beam_angle, new_intensity
            )
        elif action_name == "rotate_beam_left":
            new_angle = self.acoustic_field.beam_angle - 0.1
            self.acoustic_field.set_mid_freq_beam(
                new_angle, self.acoustic_field.beam_intensity
            )
        elif action_name == "rotate_beam_right":
            new_angle = self.acoustic_field.beam_angle + 0.1
            self.acoustic_field.set_mid_freq_beam(
                new_angle, self.acoustic_field.beam_intensity
            )
        elif action_name == "toggle_ultrasound":
            new_state = not self.acoustic_field.ultrasound_active
            self.acoustic_field.set_ultrasound(new_state, 0.9)
        
        self.acoustic_field.update_fields()
        
        self.herd.step_all(self.acoustic_env, self.acoustic_field)
        
        state = self._get_state()
        reward, terminated = self._calculate_reward(previous_state)
        
        truncated = self.current_step >= self.max_steps
        
        info = {
            "herd_center": self.herd.get_herd_center(),
            "average_stress": self.herd.get_average_stress(),
            "herd_dispersion": self.herd.get_herd_dispersion(),
        }
        
        return state, reward, terminated, truncated, info
    
    def render(self):
        pass
    
    def close(self):
        pass


class RLController:
    def __init__(self, model=None):
        self.name = "RLController"
        self.model = model
        self.env = None
        
    def set_env(self, env):
        self.env = env
        
    def get_action(self, state):
        if self.model is None:
            return np.random.randint(0, config.RL_ACTION_DIM)
        action, _ = self.model.predict(state, deterministic=True)
        return action
    
    def train(self, total_timesteps=config.RL_EPISODES * config.MAX_STEPS_EPISODE):
        if self.model is None:
            print("No model to train. Use load_model to load a pretrained model.")
            return
            
        self.model.learn(total_timesteps=total_timesteps, progress_bar=True)
        
    def save(self, path):
        if self.model is not None:
            self.model.save(path)
            
    def load(self, path):
        from stable_baselines3 import PPO
        self.model = PPO.load(path)
