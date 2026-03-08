import numpy as np
import config


class Environment:
    def __init__(self, grid_width=config.GRID_WIDTH, grid_height=config.GRID_HEIGHT):
        self.width = grid_width
        self.height = grid_height
        self.grid = np.zeros((self.height, self.width, 3))
        self.obstacles = set(config.OBSTACLE_COORDS)
        self.workers = config.WORKER_POSITIONS
        self.wind_direction = 0.0
        self.wind_speed = 0.0
        self.construction_noise_level = 0.5

    def is_in_zone(self, x, y, zone_type):
        if zone_type == "road":
            return x >= config.ROAD_X
        elif zone_type == "corridor":
            return (x >= config.CORRIDOR_X - 5 and 
                    config.CORRIDOR_Y_MIN <= y <= config.CORRIDOR_Y_MAX)
        elif zone_type == "construction":
            return x < config.CONSTRUCTION_ZONE_X_MAX
        elif zone_type == "safe":
            return (x < config.ROAD_X and 
                    config.CORRIDOR_Y_MIN <= y <= config.CORRIDOR_Y_MAX)
        return False

    def get_zone_at(self, x, y):
        if self.is_in_zone(x, y, "road"):
            return "road"
        elif self.is_in_zone(x, y, "corridor"):
            return "corridor"
        elif self.is_in_zone(x, y, "construction"):
            return "construction"
        elif self.is_in_zone(x, y, "safe"):
            return "safe_corridor"
        return "unknown"

    def is_valid_position(self, x, y):
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                (x, y) not in self.obstacles)

    def get_risk_level(self, x, y):
        zone = self.get_zone_at(x, y)
        risk_map = {
            "road": 1.0,
            "construction": 0.3,
            "safe_corridor": 0.1,
            "corridor": 0.05,
        }
        return risk_map.get(zone, 0.5)

    def get_terrain_friction(self, x, y):
        zone = self.get_zone_at(x, y)
        friction_map = {
            "road": 0.8,
            "construction": 1.0,
            "safe_corridor": 0.6,
            "corridor": 0.5,
        }
        return friction_map.get(zone, 0.7)

    def get_construction_noise_at(self, x, y):
        noise = self.construction_noise_level
        for wx, wy in self.workers:
            dist = np.sqrt((x - wx)**2 + (y - wy)**2)
            if dist < 10:
                noise += 0.3 * (1 - dist / 10)
        return min(noise, 1.0)

    def set_wind(self, direction, speed):
        self.wind_direction = direction
        self.wind_speed = speed

    def set_construction_noise(self, level):
        self.construction_noise_level = np.clip(level, 0.0, 1.0)

    def distance_to_corridor(self, x, y):
        corridor_center_x = config.CORRIDOR_X
        corridor_center_y = (config.CORRIDOR_Y_MIN + config.CORRIDOR_Y_MAX) / 2
        return np.sqrt((x - corridor_center_x)**2 + (y - corridor_center_y)**2)

    def distance_to_road(self, x, y):
        return max(0, config.ROAD_X - x)

    def reset(self):
        self.wind_direction = 0.0
        self.wind_speed = 0.0
        self.construction_noise_level = 0.5


class AcousticEnvironment(Environment):
    def __init__(self):
        super().__init__()
        self.mid_freq_field = np.zeros((self.height, self.width))
        self.social_cue_field = np.zeros((self.height, self.width))
        self.ultrasound_field = np.zeros((self.height, self.width))
        
        self.mid_freq_beam_angle = 0.0
        self.mid_freq_beam_intensity = 0.0
        self.mid_freq_beam_origin = (5, 25)
        
        self.social_cue_active = False
        self.ultrasound_active = False
        
    def update_acoustic_fields(self, acoustic_field):
        self.mid_freq_field = acoustic_field.mid_freq_intensity.copy()
        self.social_cue_field = acoustic_field.social_cue_intensity.copy()
        self.ultrasound_field = acoustic_field.ultrasound_intensity.copy()
        
    def get_local_acoustics(self, x, y):
        return {
            "mid_freq": self.mid_freq_field[int(y), int(x)] if self.is_valid_position(x, y) else 0,
            "social_cue": self.social_cue_field[int(y), int(x)] if self.is_valid_position(x, y) else 0,
            "ultrasound": self.ultrasound_field[int(y), int(x)] if self.is_valid_position(x, y) else 0,
        }
    
    def reset_acoustics(self):
        self.mid_freq_field.fill(0)
        self.social_cue_field.fill(0)
        self.ultrasound_field.fill(0)
