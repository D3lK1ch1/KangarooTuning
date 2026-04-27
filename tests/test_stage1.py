import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment import AcousticEnvironment
from kangaroo_agent import KangarooAgent, Herd
from acoustic_field import AcousticField


class TestStage1:
    def test_1_1_acoustic_gradient_influence(self):
        """
        Test 1.1: Acoustic Gradient Influence
        Goal: Verify acoustic gradient influences kangaroo direction in simulation
        
        Setup:
        - Grid: 50x50
        - Kangaroo: start at (5, 25), stress=0.3, curiosity=0.5
        - Mid-frequency beam: directional toward corridor at (45, 25)
        - Intensity: 0.8
        
        Expected: Kangaroo movement vector has positive x-component toward corridor
        """
        acoustic_env = AcousticEnvironment()
        acoustic_field = AcousticField()
        
        angle = np.arctan2(25 - 25, 45 - 5)
        acoustic_field.set_mid_freq_beam(angle, 0.8, (5, 25))
        acoustic_field.update_fields()
        acoustic_env.update_acoustic_fields(acoustic_field)

        kangaroo = KangarooAgent(5, 25)
        
        initial_x = kangaroo.x
        
        for _ in range(20):
            stimuli = acoustic_env.get_local_acoustics(kangaroo.x, kangaroo.y)
            stimuli = {
                "mid_freq": stimuli["mid_freq"],
                "social_cue": 0,
                "ultrasound": 0,
                "noise": 0,
            }
            movement = kangaroo.calculate_movement_vector(
                stimuli, acoustic_field=acoustic_field
            )
            kangaroo.move(movement[0], movement[1], acoustic_env)
        
        final_x = kangaroo.x
        distance_moved = final_x - initial_x
        
        print(f"\nTest 1.1 Results:")
        print(f"  Initial X: {initial_x}")
        print(f"  Final X: {final_x}")
        print(f"  Distance Moved (X): {distance_moved}")
        
        assert distance_moved > 0, "Kangaroo should move toward corridor (positive X)"
        print(f"  PASS: Kangaroo moved {distance_moved:.2f} units toward corridor")
        
    def test_1_2_ultrasonic_repulsion(self):
        """
        Test 1.2: Ultrasonic Repulsion
        Goal: Verify ultrasonic field near road pushes kangaroo away
        
        Setup:
        - Grid: 50x50, road at x>40
        - Kangaroo: start at (35, 25)
        - Ultrasound intensity at road: 0.9
        
        Expected: Kangaroo moves toward lower x (away from road)
        """
        acoustic_env = AcousticEnvironment()
        acoustic_field = AcousticField()
        
        acoustic_field.set_ultrasound(True, 0.9)
        acoustic_field.ultrasound_origin = (38, 25)
        acoustic_field.update_fields()
        acoustic_env.update_acoustic_fields(acoustic_field)

        kangaroo = KangarooAgent(35, 25)
        
        initial_x = kangaroo.x
        
        for _ in range(20):
            stimuli = acoustic_env.get_local_acoustics(kangaroo.x, kangaroo.y)
            stimuli = {
                "mid_freq": 0,
                "social_cue": 0,
                "ultrasound": stimuli["ultrasound"],
                "noise": 0,
            }
            movement = kangaroo.calculate_movement_vector(
                stimuli, acoustic_field=acoustic_field
            )
            kangaroo.move(movement[0], movement[1], acoustic_env)
        
        final_x = kangaroo.x
        x_change = final_x - initial_x
        
        print(f"\nTest 1.2 Results:")
        print(f"  Initial X: {initial_x}")
        print(f"  Final X: {final_x}")
        print(f"  X Change: {x_change}")
        
        assert x_change < 0, "Kangaroo should move away from road (negative X)"
        print(f"  PASS: Kangaroo moved {abs(x_change):.2f} units away from road")

    def test_stress_response(self):
        """Test that stress increases near road"""
        acoustic_env = AcousticEnvironment()
        
        zone = acoustic_env.get_zone_at(42, 25)
        assert zone == "road"
        
        risk = acoustic_env.get_risk_level(42, 25)
        assert risk > 0.5
        
    def test_herd_behavior(self):
        """Test basic herd behavior"""
        herd = Herd(size=5, start_x=5, start_y=25)
        
        center = herd.get_herd_center()
        assert 3 <= center[0] <= 7
        assert 23 <= center[1] <= 27
        
        dispersion = herd.get_herd_dispersion()
        assert dispersion >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
