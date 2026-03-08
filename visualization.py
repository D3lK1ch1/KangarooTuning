import numpy as np
import config


class Visualizer:
    def __init__(self, acoustic_env, acoustic_field, herd):
        self.acoustic_env = acoustic_env
        self.acoustic_field = acoustic_field
        self.herd = herd
        
    def render_grid(self):
        grid = np.zeros((self.acoustic_env.height, self.acoustic_env.width, 3))
        
        for y in range(self.acoustic_env.height):
            for x in range(self.acoustic_env.width):
                zone = self.acoustic_env.get_zone_at(x, y)
                
                if zone == "road":
                    grid[y, x] = [0.3, 0.3, 0.3]
                elif zone == "corridor":
                    grid[y, x] = [0.2, 0.8, 0.2]
                elif zone == "construction":
                    grid[y, x] = [0.6, 0.5, 0.3]
                    
                mid_int = self.acoustic_field.mid_freq_intensity[y, x]
                if mid_int > 0.1:
                    grid[y, x] += [mid_int * 0.3, mid_int * 0.3, 0]
                    
                ultra_int = self.acoustic_field.ultrasound_intensity[y, x]
                if ultra_int > 0.1:
                    grid[y, x] += [ultra_int * 0.5, 0, ultra_int * 0.5]
        
        grid = np.clip(grid, 0, 1)
        return (grid * 255).astype(np.uint8)
    
    def render_agents(self, grid):
        for agent in self.herd.agents:
            x, y = int(agent.x), int(agent.y)
            if 0 <= x < self.acoustic_env.width and 0 <= y < self.acoustic_env.height:
                stress_color = [1.0, 1.0 - agent.stress, 1.0 - agent.stress]
                grid[y, x] = stress_color
        return grid
    
    def get_state_image(self):
        grid = self.render_grid()
        grid = self.render_agents(grid)
        return (grid * 255).astype(np.uint8)
    
    def print_state(self):
        herd_center = self.herd.get_herd_center()
        zone = self.acoustic_env.get_zone_at(herd_center[0], herd_center[1])
        
        print(f"\n=== Simulation State ===")
        print(f"Step: {0}")
        print(f"Herd Center: ({herd_center[0]:.1f}, {herd_center[1]:.1f})")
        print(f"Zone: {zone}")
        print(f"Average Stress: {self.herd.get_average_stress():.2f}")
        print(f"Herd Dispersion: {self.herd.get_herd_dispersion():.2f}")
        print(f"Beam Intensity: {self.acoustic_field.beam_intensity:.2f}")
        print(f"Beam Angle: {np.degrees(self.acoustic_field.beam_angle):.1f}°")
        print(f"Ultrasound Active: {self.acoustic_field.ultrasound_active}")


def create_text_display(acoustic_env, herd, step):
    herd_center = herd.get_herd_center()
    zone = acoustic_env.get_zone_at(herd_center[0], herd_center[1])
    
    lines = [
        f"Step: {step}",
        f"Herd: ({herd_center[0]:.1f}, {herd_center[1]:.1f}) | Zone: {zone}",
        f"Stress: {herd.get_average_stress():.2f} | Dispersion: {herd.get_herd_dispersion():.2f}",
    ]
    
    return "\n".join(lines)
