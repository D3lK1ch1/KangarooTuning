import numpy as np
import config
from acoustic_field import AcousticField


class RuleBasedController:
    def __init__(self):
        self.name = "RuleBased"
        
    def get_action(self, state):
        distance_to_corridor = state["distance_to_corridor"]
        distance_to_road = state["distance_to_road"]
        average_stress = state["average_stress"]
        herd_dispersion = state["herd_dispersion"]
        
        action = {
            "adjust_mid_freq_intensity": 0.0,
            "adjust_beam_direction": 0.0,
            "activate_cue": False,
            "increase_ultrasound": False,
            "decrease_all": False,
        }
        
        if distance_to_road < 5:
            action["increase_ultrasound"] = True
            action["adjust_mid_freq_intensity"] = 0.8
            
        elif distance_to_corridor > 10:
            angle_to_corridor = np.arctan2(
                (config.CORRIDOR_Y_MIN + config.CORRIDOR_Y_MAX) / 2 - 25,
                config.CORRIDOR_X - 5
            )
            action["adjust_beam_direction"] = angle_to_corridor
            action["adjust_mid_freq_intensity"] = 0.8
            
        if average_stress > 0.7:
            action["adjust_mid_freq_intensity"] *= 0.5
            action["decrease_all"] = True
            
        if herd_dispersion > 5:
            action["activate_cue"] = True
            
        return action
    
    def apply_action(self, action, acoustic_field: AcousticField):
        if "adjust_beam_direction" in action:
            current_angle = acoustic_field.beam_angle
            new_angle = current_angle + action["adjust_beam_direction"]
            acoustic_field.set_mid_freq_beam(new_angle, acoustic_field.beam_intensity)
            
        if "adjust_mid_freq_intensity" in action:
            intensity = action["adjust_mid_freq_intensity"]
            acoustic_field.set_mid_freq_beam(
                acoustic_field.beam_angle, 
                intensity,
                acoustic_field.beam_origin
            )
            
        if "activate_cue" in action:
            acoustic_field.set_social_cue(action["activate_cue"], 0.3)
            
        if "increase_ultrasound" in action:
            acoustic_field.set_ultrasound(action["increase_ultrasound"], 0.9)
            
        if "decrease_all" in action and action["decrease_all"]:
            acoustic_field.set_mid_freq_beam(
                acoustic_field.beam_angle,
                acoustic_field.beam_intensity * 0.5
            )
            acoustic_field.set_social_cue(False, 0)
            acoustic_field.set_ultrasound(False, 0)
        
        acoustic_field.update_fields()


class RuleBasedControllerSimple:
    def __init__(self):
        self.name = "RuleBasedSimple"
        
    def get_action(self, state):
        distance_to_corridor = state["distance_to_corridor"]
        distance_to_road = state["distance_to_road"]
        
        if distance_to_road < 5:
            return "increase_ultrasound"
        elif distance_to_corridor > 10:
            return "point_to_corridor"
        else:
            return "maintain"
    
    def apply_action(self, action, acoustic_field: AcousticField):
        if action == "increase_ultrasound":
            acoustic_field.set_ultrasound(True, 0.9)
            
        elif action == "point_to_corridor":
            angle = np.arctan2(10, 40)
            acoustic_field.set_mid_freq_beam(angle, 0.8)
            
        acoustic_field.update_fields()
