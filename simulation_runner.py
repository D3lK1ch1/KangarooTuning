import numpy as np
from environment import AcousticEnvironment
from kangaroo_agent import Herd
from acoustic_field import AcousticField
from controller_rule_based import RuleBasedController
from controller_rl import RLController
import config


class SimulationRunner:
    def __init__(self, controller=None, herd_size=config.HERD_SIZE_DEFAULT):
        self.acoustic_env = AcousticEnvironment()
        self.acoustic_field = AcousticField()
        self.herd = Herd(herd_size)
        
        if controller is None:
            self.controller = RuleBasedController()
        else:
            self.controller = controller
            
        self.step_count = 0
        self.max_steps = config.MAX_STEPS_EPISODE
        self.history = []
        
    def get_state(self):
        herd_center = self.herd.get_herd_center()
        return {
            "herd_center": herd_center,
            "distance_to_corridor": self.acoustic_env.distance_to_corridor(
                herd_center[0], herd_center[1]
            ),
            "distance_to_road": self.acoustic_env.distance_to_road(
                herd_center[0], herd_center[1]
            ),
            "average_stress": self.herd.get_average_stress(),
            "herd_dispersion": self.herd.get_herd_dispersion(),
            "construction_noise_level": self.acoustic_env.construction_noise_level,
        }
    
    def run_step(self):
        state = self.get_state()
        
        if hasattr(self.controller, 'get_action'):
            if hasattr(self.controller, 'model'):
                action = self.controller.get_action(state)
                self._apply_rl_action(action)
            else:
                action = self.controller.get_action(state)
                self.controller.apply_action(action, self.acoustic_field)
        else:
            self.controller.apply_action(state, self.acoustic_field)
            
        self.herd.step_all(self.acoustic_env, self.acoustic_field)
        
        self.step_count += 1
        
        self.history.append({
            "step": self.step_count,
            "state": state.copy(),
            "herd_center": self.herd.get_herd_center(),
            "average_stress": self.herd.get_average_stress(),
            "beam_intensity": self.acoustic_field.beam_intensity,
            "beam_angle": self.acoustic_field.beam_angle,
        })
        
    def _apply_rl_action(self, action):
        action_map = {
            0: "increase_intensity",
            1: "decrease_intensity",
            2: "rotate_beam_left",
            3: "rotate_beam_right",
            4: "toggle_ultrasound",
        }
        
        action_name = action_map.get(action, "increase_intensity")
        
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
    
    def run_episode(self, max_steps=None):
        if max_steps is None:
            max_steps = self.max_steps
            
        self.reset()
        
        for _ in range(max_steps):
            self.run_step()
            
            herd_center = self.herd.get_herd_center()
            zone = self.acoustic_env.get_zone_at(herd_center[0], herd_center[1])
            
            if zone == "corridor":
                return "safe_exit", self.step_count
            elif zone == "road":
                return "road_entry", self.step_count
                
        return "timeout", self.step_count
    
    def reset(self, start_x=5, start_y=25):
        self.step_count = 0
        self.history = []
        self.acoustic_env.reset()
        self.acoustic_field.reset()
        self.herd.reset(start_x, start_y)
        
    def get_results(self):
        if not self.history:
            return {}
            
        final_state = self.history[-1]["state"]
        herd_center = self.herd.get_herd_center()
        
        return {
            "final_step": self.step_count,
            "final_herd_center": herd_center,
            "final_distance_to_corridor": final_state["distance_to_corridor"],
            "final_distance_to_road": final_state["distance_to_road"],
            "final_average_stress": final_state["average_stress"],
            "final_herd_dispersion": final_state["herd_dispersion"],
            "history": self.history,
        }


def run_simulation(controller=None, num_episodes=10, verbose=True):
    results = []
    
    for episode in range(num_episodes):
        runner = SimulationRunner(controller)
        
        start_x = np.random.randint(3, 10)
        start_y = np.random.randint(20, 30)
        runner.reset(start_x, start_y)
        
        outcome, steps = runner.run_episode()
        episode_results = runner.get_results()
        episode_results["outcome"] = outcome
        episode_results["episode"] = episode + 1
        
        results.append(episode_results)
        
        if verbose:
            print(f"Episode {episode+1}: {outcome} in {steps} steps")
            
    safe_exits = sum(1 for r in results if r["outcome"] == "safe_exit")
    road_entries = sum(1 for r in results if r["outcome"] == "road_entry")
    
    if verbose:
        print(f"\n=== Summary ===")
        print(f"Safe Exit Rate: {safe_exits}/{num_episodes} ({safe_exits/num_episodes*100:.1f}%)")
        print(f"Road Entry Rate: {road_entries}/{num_episodes} ({road_entries/num_episodes*100:.1f}%)")
        
    return results
