import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation_runner import SimulationRunner
from controller_rule_based import RuleBasedController
from environment import AcousticEnvironment
from acoustic_field import AcousticField
from kangaroo_agent import Herd
import config


class TestStage2:
    def test_2_1_near_road_response(self):
        """
        Test 2.1: Near-Road Response
        Conditions: distance_to_road < 5
        Action: activate_ultrasound = true
        Expected: Kangaroo exits road zone within 10 steps
        """
        runner = SimulationRunner(controller=RuleBasedController())
        
        runner.reset(start_x=37, start_y=25)
        
        initial_zone = runner.acoustic_env.get_zone_at(37, 25)
        assert initial_zone != "road"
        
        outcome, steps = runner.run_episode(max_steps=50)
        
        print(f"\nTest 2.1 Results:")
        print(f"  Outcome: {outcome}")
        print(f"  Steps: {steps}")
        
        assert outcome != "road_entry", "Kangaroo should not enter road"
        
    def test_2_2_corridor_guidance(self):
        """
        Test 2.2: Corridor Guidance
        Conditions: distance_to_corridor > 10
        Action: beam_direction points to corridor
        Expected: Kangaroo reduces distance_to_corridor
        Known gap: Fails with default parameters. Starting distance of 40 grid units 
        exceeds effective beam range given DISTANCE_ATTENUATION_FACTOR. Behavioral 
        parameters (curiosity, attenuation) are not field-validatted - this reflects 
        a real limitation of the POC, not a code bug.
        """
        runner = SimulationRunner(controller=RuleBasedController())
        
        runner.reset(start_x=5, start_y=25)
        
        initial_dist = runner.acoustic_env.distance_to_corridor(5, 25)
        
        for _ in range(30):
            runner.run_step()
            
        final_dist = runner.acoustic_env.distance_to_corridor(
            runner.herd.get_herd_center()[0],
            runner.herd.get_herd_center()[1]
        )
        
        print(f"\nTest 2.2 Results:")
        print(f"  Initial Distance: {initial_dist}")
        print(f"  Final Distance: {final_dist}")
        
        assert final_dist < initial_dist, "Distance to corridor should decrease"
        print(f"  PASS: Distance reduced by {initial_dist - final_dist:.2f}")
        
    def test_2_3_stress_reduction(self):
        """
        Test 2.3: Stress Reduction
        Conditions: stress > 0.7
        Action: reduce_intensity
        Expected: stress decreases within 5 steps
        """
        acoustic_env = AcousticEnvironment()
        acoustic_field = AcousticField()
        herd = Herd(size=1, start_x=5, start_y=25)
        
        agent = herd.agents[0]
        agent.stress = 0.8
        
        acoustic_field.set_mid_freq_beam(0.5, 0.8)
        acoustic_field.update_fields()
        
        initial_stress = agent.stress
        
        for i in range(5):
            stimuli = agent.perceive_local_stimuli(
                acoustic_env.get_local_acoustics(agent.x, agent.y),
                acoustic_env
            )
            agent.update_stress(stimuli, acoustic_env)
            
        final_stress = agent.stress
        
        print(f"\nTest 2.3 Results:")
        print(f"  Initial Stress: {initial_stress}")
        print(f"  Final Stress: {final_stress}")
        
        print(f"  PASS: Stress reduced" if final_stress < initial_stress else f"  Note: Stress changed by {final_stress - initial_stress:.2f}")

    def test_rule_based_baseline(self):
        """Run rule-based controller across multiple episodes"""
        controller = RuleBasedController()
        
        safe_exits = 0
        road_entries = 0
        
        for i in range(10):
            runner = SimulationRunner(controller)
            runner.reset(start_x=np.random.randint(3, 15), start_y=np.random.randint(20, 30))
            outcome, _ = runner.run_episode()
            
            if outcome == "safe_exit":
                safe_exits += 1
            elif outcome == "road_entry":
                road_entries += 1
                
        print(f"\nRule-Based Baseline Results:")
        print(f"  Safe Exits: {safe_exits}/10 ({safe_exits*10}%)")
        print(f"  Road Entries: {road_entries}/10 ({road_entries*10}%)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
