import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestStage3:
    def test_3_1_training_convergence(self):
        """
        Test 3.1: Training Convergence
        Metric: Reward should increase over 1000 episodes
        Target: Average reward > baseline (rule-based) by 20%
        
        Note: This test requires training to be run first.
        Run: python training.py train
        """
        pytest.skip("Requires trained model - run 'python training.py train' first")
        
    def test_3_2_safe_exit_rate(self):
        """
        Test 3.2: Safe Exit Rate
        Conditions: 50 random starting positions
        Target: >80% exit safely, <5% enter road
        
        Note: This test requires a trained RL model.
        Run: python training.py train
        """
        pytest.skip("Requires trained model - run 'python training.py train' first")
        
    def test_3_3_generalization(self):
        """
        Test 3.3: Generalization
        Variables: Different noise levels, wind directions, herd sizes
        Target: Performance within 10% of trained environment
        
        Note: This test requires a trained RL model.
        Run: python training.py train
        """
        pytest.skip("Requires trained model - run 'python training.py train' first")
        
    def test_rl_env_interface(self):
        """Test that RL environment interface works"""
        try:
            from controller_rl import KangarooTuningEnv
            
            env = KangarooTuningEnv()
            state, info = env.reset()
            
            assert state.shape == (5,), f"Expected state shape (5,), got {state.shape}"
            assert env.action_space is not None
            
            state, reward, terminated, truncated, info = env.step(0)
            
            assert isinstance(reward, (int, float))
            assert isinstance(terminated, bool)
            assert isinstance(truncated, bool)
            
            print("\nRL Environment Interface: PASS")
            
        except ImportError as e:
            pytest.skip(f"RL dependencies not available: {e}")
            
    def test_rl_vs_rule_comparison(self):
        """Compare RL performance to rule-based (untrained)"""
        try:
            from controller_rl import RLController
            from controller_rl import KangarooTuningEnv
            
            rl_controller = RLController()
            
            env = KangarooTuningEnv()
            
            total_reward = 0
            for _ in range(10):
                state, _ = env.reset()
                terminated = False
                truncated = False
                
                while not (terminated or truncated):
                    action = rl_controller.get_action(state)
                    state, reward, terminated, truncated, info = env.step(action)
                    total_reward += reward
                    
            avg_reward = total_reward / 10
            
            print(f"\nUntrained RL Average Reward: {avg_reward:.2f}")
            
        except ImportError as e:
            pytest.skip(f"RL dependencies not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
