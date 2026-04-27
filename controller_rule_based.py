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
            herd_center = state.get("herd_center", (5, 25))
            angle_to_corridor = np.arctan2(
                (config.CORRIDOR_Y_MIN + config.CORRIDOR_Y_MAX) / 2 - herd_center[1],
                config.CORRIDOR_X - herd_center[0]
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
        if action["adjust_beam_direction"] != 0.0:
            new_angle = action["adjust_beam_direction"]
            acoustic_field.set_mid_freq_beam(new_angle, acoustic_field.beam_intensity)

        if action["adjust_mid_freq_intensity"] != 0.0:
            intensity = action["adjust_mid_freq_intensity"]
            acoustic_field.set_mid_freq_beam(
                acoustic_field.beam_angle,
                intensity,
                acoustic_field.beam_origin
            )

        if action["activate_cue"]:
            acoustic_field.set_social_cue(action["activate_cue"], 0.3)

        if action["increase_ultrasound"]:
            acoustic_field.set_ultrasound(action["increase_ultrasound"], 0.9)
            
        if "decrease_all" in action and action["decrease_all"]:
            acoustic_field.set_mid_freq_beam(
                acoustic_field.beam_angle,
                acoustic_field.beam_intensity * 0.5
            )
            acoustic_field.set_social_cue(False, 0)
            acoustic_field.set_ultrasound(False, 0)
        
        acoustic_field.update_fields()