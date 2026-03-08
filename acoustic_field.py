import numpy as np
import config


class AcousticField:
    def __init__(self, width=config.GRID_WIDTH, height=config.GRID_HEIGHT):
        self.width = width
        self.height = height
        
        self.mid_freq_intensity = np.zeros((height, width))
        self.social_cue_intensity = np.zeros((height, width))
        self.ultrasound_intensity = np.zeros((height, width))
        
        self.beam_origin = (5, 25)
        self.beam_angle = 0.0
        self.beam_intensity = 0.0
        
        self.social_cue_origin = (15, 25)
        self.social_cue_active = False
        self.social_cue_intensity_value = 0.0
        
        self.ultrasound_origin = (config.ROAD_X - 2, 25)
        self.ultrasound_active = False
        self.ultrasound_intensity_value = 0.0
        
        self.wind_direction = 0.0
        self.wind_speed = 0.0
    
    def set_mid_freq_beam(self, angle, intensity, origin=None):
        self.beam_angle = angle
        self.beam_intensity = np.clip(intensity, 0.0, 1.0)
        if origin is not None:
            self.beam_origin = origin
    
    def set_social_cue(self, active, intensity=0.3):
        self.social_cue_active = active
        self.social_cue_intensity_value = np.clip(intensity, 0.0, 1.0)
    
    def set_ultrasound(self, active, intensity=0.9):
        self.ultrasound_active = active
        self.ultrasound_intensity_value = np.clip(intensity, 0.0, 1.0)
    
    def set_wind(self, direction, speed):
        self.wind_direction = direction
        self.wind_speed = speed
    
    def calculate_mid_freq_at_point(self, x, y):
        if self.beam_intensity <= 0:
            return 0.0
        
        dx = x - self.beam_origin[0]
        dy = y - self.beam_origin[1]
        distance = np.sqrt(dx**2 + dy**2)
        
        if distance < 0.1:
            return self.beam_intensity
        
        beam_direction = np.array([np.cos(self.beam_angle), np.sin(self.beam_angle)])
        point_direction = np.array([dx, dy])
        
        if np.linalg.norm(point_direction) > 0:
            point_direction = point_direction / np.linalg.norm(point_direction)
        
        alignment = np.dot(beam_direction, point_direction)
        
        if alignment <= 0:
            return 0.0
        
        beam_width_factor = alignment ** 2
        
        attenuation = np.exp(-config.DISTANCE_ATTENUATION_FACTOR * distance)
        
        wind_effect = 1.0
        if self.wind_speed > 0:
            wind_angle = self.wind_direction - self.beam_angle
            wind_effect = 1.0 + config.WIND_DISTORTION_FACTOR * self.wind_speed * np.cos(wind_angle)
        
        intensity = self.beam_intensity * beam_width_factor * attenuation * wind_effect
        return np.clip(intensity, 0.0, 1.0)
    
    def calculate_social_cue_at_point(self, x, y):
        if not self.social_cue_active or self.social_cue_intensity_value <= 0:
            return 0.0
        
        dx = x - self.social_cue_origin[0]
        dy = y - self.social_cue_origin[1]
        distance = np.sqrt(dx**2 + dy**2)
        
        if distance < 0.1:
            return self.social_cue_intensity_value
        
        spread_factor = 0.7
        attenuation = np.exp(-config.DISTANCE_ATTENUATION_FACTOR * spread_factor * distance)
        
        intensity = self.social_cue_intensity_value * attenuation
        return np.clip(intensity, 0.0, 1.0)
    
    def calculate_ultrasound_at_point(self, x, y):
        if not self.ultrasound_active or self.ultrasound_intensity_value <= 0:
            return 0.0
        
        dx = x - self.ultrasound_origin[0]
        dy = y - self.ultrasound_origin[1]
        distance = np.sqrt(dx**2 + dy**2)
        
        if distance < 0.1:
            return self.ultrasound_intensity_value
        
        if distance > 8:
            return 0.0
        
        short_range_attenuation = np.exp(-0.2 * distance)
        
        if dx > 0:
            return 0.0
        
        intensity = self.ultrasound_intensity_value * short_range_attenuation
        return np.clip(intensity, 0.0, 1.0)
    
    def update_fields(self):
        for y in range(self.height):
            for x in range(self.width):
                self.mid_freq_intensity[y, x] = self.calculate_mid_freq_at_point(x, y)
                self.social_cue_intensity[y, x] = self.calculate_social_cue_at_point(x, y)
                self.ultrasound_intensity[y, x] = self.calculate_ultrasound_at_point(x, y)
    
    def get_intensity_at(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return {
                "mid_freq": self.mid_freq_intensity[int(y), int(x)],
                "social_cue": self.social_cue_intensity[int(y), int(x)],
                "ultrasound": self.ultrasound_intensity[int(y), int(x)],
            }
        return {"mid_freq": 0, "social_cue": 0, "ultrasound": 0}
    
    def get_gradient_at(self, x, y, field_type="mid_freq"):
        if field_type == "mid_freq":
            field = self.mid_freq_intensity
        elif field_type == "social_cue":
            field = self.social_cue_intensity
        elif field_type == "ultrasound":
            field = self.ultrasound_intensity
        else:
            return (0, 0)
        
        ix, iy = int(x), int(y)
        
        if ix <= 0 or ix >= self.width - 1 or iy <= 0 or iy >= self.height - 1:
            return (0, 0)
        
        grad_x = field[iy, ix + 1] - field[iy, ix - 1]
        grad_y = field[iy + 1, ix] - field[iy - 1, ix]
        
        return (grad_x, grad_y)
    
    def reset(self):
        self.mid_freq_intensity.fill(0)
        self.social_cue_intensity.fill(0)
        self.ultrasound_intensity.fill(0)
        self.beam_intensity = 0.0
        self.social_cue_active = False
        self.ultrasound_active = False
