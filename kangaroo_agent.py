import numpy as np
import config


class KangarooAgent:
    def __init__(self, x, y, agent_id=0):
        self.id = agent_id
        self.x = x
        self.y = y
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        self.stress = config.KANGAROO_INITIAL_STRESS
        self.curiosity = config.KANGAROO_INITIAL_CURIOSITY
        self.herd_cohesion = config.KANGAROO_INITIAL_HERD_COESION
        self.panic_threshold = config.KANGAROO_PANIC_THRESHOLD
        
        self.history = [(x, y)]
        self.stress_history = [self.stress]
        
    def get_position(self):
        return (self.x, self.y)
    
    def get_distance_moved(self):
        if len(self.history) < 2:
            return 0.0
        prev_x, prev_y = self.history[-2]
        return np.sqrt((self.x - prev_x)**2 + (self.y - prev_y)**2)
    
    def get_stress(self):
        return self.stress
    
    def is_panicked(self):
        return self.stress >= self.panic_threshold
    
    def perceive_local_stimuli(self, acoustics, environment):
        local_mid_freq = acoustics.get("mid_freq", 0)
        local_cue = acoustics.get("social_cue", 0)
        local_ultrasound = acoustics.get("ultrasound", 0)
        local_noise = environment.get_construction_noise_at(self.x, self.y)
        
        return {
            "mid_freq": local_mid_freq,
            "social_cue": local_cue,
            "ultrasound": local_ultrasound,
            "noise": local_noise,
        }
    
    def calculate_movement_vector(self, stimuli, herd_center=None, acoustic_field=None):
        guide_pull = np.array([0.0, 0.0])
        cue_pull = np.array([0.0, 0.0])
        ultrasound_push = np.array([0.0, 0.0])
        panic_random = np.array([0.0, 0.0])
        
        if acoustic_field is not None and stimuli["mid_freq"] > 0:
            gradient_x, gradient_y = acoustic_field.get_gradient_at(self.x, self.y)
            guide_pull = np.array([gradient_x, gradient_y]) * stimuli["mid_freq"] * self.curiosity
            
        if stimuli["social_cue"] > 0 and herd_center is not None:
            to_herd = np.array([herd_center[0] - self.x, herd_center[1] - self.y])
            if np.linalg.norm(to_herd) > 0:
                cue_pull = (to_herd / np.linalg.norm(to_herd)) * stimuli["social_cue"] * self.herd_cohesion
                
        if stimuli["ultrasound"] > 0:
            push_strength = stimuli["ultrasound"] * 2.0
            if acoustic_field is not None:
                gradient_x, gradient_y = acoustic_field.get_gradient_at(self.x, self.y, field_type="ultrasound")
                ultrasound_push = -np.array([gradient_x, gradient_y]) * push_strength
        
        if self.is_panicked():
            angle = np.random.uniform(0, 2 * np.pi)
            panic_random = np.array([np.cos(angle), np.sin(angle)]) * self.stress
        
        total_vector = guide_pull + cue_pull + ultrasound_push + panic_random
        
        if np.linalg.norm(total_vector) > config.KANGAROO_MAX_VELOCITY:
            total_vector = total_vector / np.linalg.norm(total_vector) * config.KANGAROO_MAX_VELOCITY
            
        return total_vector
    
    def update_stress(self, stimuli, environment):
        zone = environment.get_zone_at(self.x, self.y)
        risk = environment.get_risk_level(self.x, self.y)
        
        stress_increase = risk * 0.1
        
        if stimuli.get("ultrasound", 0) > 0.5:
            stress_increase += stimuli["ultrasound"] * 0.2
            
        if stimuli.get("noise", 0) > 0.7:
            stress_increase += 0.1
            
        if zone == "corridor":
            stress_increase -= 0.05
            
        self.stress = np.clip(self.stress + stress_increase, 0.0, 1.0)
        self.stress_history.append(self.stress)
    
    def move(self, dx, dy, environment):
        new_x = self.x + dx
        new_y = self.y + dy
        
        if environment.is_valid_position(new_x, new_y):
            friction = environment.get_terrain_friction(new_x, new_y)
            self.x = new_x
            self.y = new_y
            self.velocity_x = dx * friction
            self.velocity_y = dy * friction
            
        self.history.append((self.x, self.y))
    
    def step(self, stimuli, herd_center=None, acoustic_field=None, environment=None):
        if environment is None:
            return
            
        movement = self.calculate_movement_vector(stimuli, herd_center, acoustic_field)
        self.move(movement[0], movement[1], environment)
        self.update_stress(stimuli, environment)
    
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.stress = config.KANGAROO_INITIAL_STRESS
        self.history = [(x, y)]
        self.stress_history = [self.stress]


class Herd:
    def __init__(self, size=config.HERD_SIZE_DEFAULT, start_x=5, start_y=25):
        self.agents = []
        for i in range(size):
            offset_x = np.random.uniform(-3, 3)
            offset_y = np.random.uniform(-3, 3)
            self.agents.append(KangarooAgent(start_x + offset_x, start_y + offset_y, i))
    
    def get_positions(self):
        return [agent.get_position() for agent in self.agents]
    
    def get_herd_center(self):
        if not self.agents:
            return (0, 0)
        positions = self.get_positions()
        center_x = sum(p[0] for p in positions) / len(positions)
        center_y = sum(p[1] for p in positions) / len(positions)
        return (center_x, center_y)
    
    def get_herd_dispersion(self):
        if len(self.agents) < 2:
            return 0.0
        center = self.get_herd_center()
        distances = [np.sqrt((a.x - center[0])**2 + (a.y - center[1])**2) 
                     for a in self.agents]
        return np.mean(distances)
    
    def get_average_stress(self):
        return sum(a.get_stress() for a in self.agents) / len(self.agents)
    
    def step_all(self, acoustic_environment, acoustic_field):
        acoustic_environment.update_acoustic_fields(acoustic_field)
        herd_center = self.get_herd_center()

        for agent in self.agents:
            stimuli = agent.perceive_local_stimuli(
                acoustic_environment.get_local_acoustics(agent.x, agent.y),
                acoustic_environment
            )
            agent.step(stimuli, herd_center, acoustic_field, acoustic_environment)
    
    def reset(self, start_x=5, start_y=25):
        for i, agent in enumerate(self.agents):
            offset_x = np.random.uniform(-3, 3)
            offset_y = np.random.uniform(-3, 3)
            agent.reset(start_x + offset_x, start_y + offset_y)
