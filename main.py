#!/usr/bin/env python3
"""
KangarooTuning - Sound-based kangaroo guidance system
CLI Interface for simulation and hardware control
"""

import argparse
import sys
import time
import numpy as np

from environment import AcousticEnvironment
from kangaroo_agent import Herd
from acoustic_field import AcousticField
from controller_rule_based import RuleBasedController
from simulation_runner import SimulationRunner
import config


class SoundEmulator:
    """Software-only sound emulator for simulation mode"""
        
    def emit_mid_freq(self, intensity, angle):
        is_active = intensity > 0
        return f"Mid-freq{'ON' if is_active else 'OFF'} (intensity={intensity:.0%}, angle={np.degrees(angle):.0f}°)"
    
    def emit_ultrasound(self, intensity):
        is_active = intensity > 0
        return f"Ultrasound {'ON' if is_active else 'OFF'} (intensity={intensity:.0%})"
  
    def emit_social_cue(self, intensity):
        return f"Social cue {'ON' if intensity > 0 else 'OFF'} (intensity={intensity:.0%})"
    
    def stop_all(self):
        return "All emitters stopped"


class KangarooTuningCLI:
    def __init__(self):
        self.emulator = SoundEmulator()
        self.runner = None
        self.acoustic_env = AcousticEnvironment()
        self.acoustic_field = AcousticField()
        self.herd = None
        self.controller = RuleBasedController()
        self.step_count = 0
        
    def check_dependencies(self):
        print("=" * 50)
        print("KANGAROO TUNING - System Status")
        print("=" * 50)
        
        deps = []
        try:
            import numpy
            deps.append(("numpy", numpy.__version__, True))
        except ImportError:
            deps.append(("numpy", "NOT INSTALLED", False))
            
        try:
            import matplotlib
            deps.append(("matplotlib", matplotlib.__version__, True))
        except ImportError:
            deps.append(("matplotlib", "NOT INSTALLED", False))
            
        try:
            import pygame
            deps.append(("pygame", pygame.ver, True))
        except ImportError:
            deps.append(("pygame", "NOT INSTALLED", False))
            
        try:
            import stable_baselines3
            deps.append(("stable-baselines3", stable_baselines3.__version__, True))
        except ImportError:
            deps.append(("stable-baselines3", "NOT INSTALLED", False))
            
        try:
            import gymnasium
            deps.append(("gymnasium", gymnasium.__version__, True))
        except ImportError:
            deps.append(("gymnasium", "NOT INSTALLED", False))
        
        print(f"\n{'Package':<25} {'Version':<15} {'Status'}")
        print("-" * 50)
        all_ok = True
        for name, version, ok in deps:
            status = "[OK]" if ok else "[MISSING]"
            print(f"{name:<25} {version:<15} {status}")
            if not ok:
                all_ok = False
                
        print("-" * 50)
        if all_ok:
            print("[OK] All core dependencies installed")
            print("     (pygame is optional - used for graphical display only)")
            print("\nMode: SIMULATION (no hardware connected)")
            return True
        else:
            print("[MISSING] Some dependencies missing. Run: pip install -r requirements.txt")
            return False
            
    def reset_simulation(self, herd_size=5, start_x=5, start_y=25):
        self.acoustic_env = AcousticEnvironment()
        self.acoustic_field = AcousticField()
        self.herd = Herd(herd_size, start_x, start_y)
        self.controller = RuleBasedController()
        self.step_count = 0
        
    def print_grid(self, width=50, height=20):
        """Print ASCII representation of the environment"""
        print("\n" + "=" * 60)
        print("ENVIRONMENT MAP (top-down view)")
        print("=" * 60)
        
        # Zone legend
        print("\n[LEGEND]")
        print("  . = safe zone    # = road    C = construction")
        print("  ~ = corridor     K = kangaroo > = mid-freq beam")
        print("  U = ultrasound   * = herd center")
        
        # Scale down for ASCII
        scale = 2
        h, w = height * scale, width * scale
        
        for y in range(0, h, scale):
            line = ""
            for x in range(0, w, scale):
                rx, ry = x // scale, y // scale
                
                # Check zones
                zone = self.acoustic_env.get_zone_at(rx, ry)
                char = "."
                
                if zone == "road":
                    char = "#"
                elif zone == "corridor":
                    char = "~"
                elif zone == "construction":
                    char = "C"
                    
                # Overlay acoustic fields
                mid = self.acoustic_field.mid_freq_intensity[ry, rx]
                ultra = self.acoustic_field.ultrasound_intensity[ry, rx]
                
                if mid > 0.3:
                    char = ">"
                if ultra > 0.3:
                    char = "U"
                    
                # Overlay kangaroos
                found_kangaroo = False
                for agent in self.herd.agents:
                    if int(agent.x) == rx and int(agent.y) == ry:
                        char = "K"
                        found_kangaroo = True
                        
                # Herd center
                if not found_kangaroo:
                    hc = self.herd.get_herd_center()
                    if int(hc[0]) == rx and int(hc[1]) == ry:
                        char = "*"
                        
                line += char
            print(f"  {line}")
            
        print("=" * 60)
        
    def print_state(self):
        """Print current simulation state"""
        herd_center = self.herd.get_herd_center()
        zone = self.acoustic_env.get_zone_at(herd_center[0], herd_center[1])
        
        print(f"\n--- Step {self.step_count} ---")
        print(f"  Herd position:  ({herd_center[0]:.1f}, {herd_center[1]:.1f})")
        print(f"  Zone:           {zone}")
        print(f"  Avg stress:     {self.herd.get_average_stress():.2f}")
        print(f"  Dispersion:     {self.herd.get_herd_dispersion():.2f}")
        print(f"  Mid-freq beam:  {self.acoustic_field.beam_intensity > 0} (int={self.acoustic_field.beam_intensity:.0%}, angle={np.degrees(self.acoustic_field.beam_angle):.0f}°)")
        print(f"  Ultrasound:     {self.acoustic_field.ultrasound_active} (int={self.acoustic_field.ultrasound_intensity:.0%})")
        
    def run_demo(self, num_steps=50):
        """Run automated demo showing luring behavior"""
        print("\n" + "=" * 60)
        print("DEMO: Luring kangaroos from construction zone")
        print("=" * 60)
        
        self.reset_simulation(herd_size=5, start_x=5, start_y=25)
        
        print("\nInitial setup:")
        print("  - Kangaroos start at construction zone (x=5)")
        print("  - Target: corridor at x=45")
        print("  - Road danger zone: x>40")
        print("  - Using mid-freq attract, ultrasound repel from road")
        
        # Configure acoustic field to guide toward corridor
        self.acoustic_field.set_mid_freq_beam(angle=0.0, intensity=0.8, origin=(25, 25))
        self.acoustic_field.set_ultrasound(True, 0.9)
        self.acoustic_field.ultrasound_origin = (38, 25)
        self.acoustic_field.update_fields()
        
        print(f"\n{self.emulator.emit_mid_freq(0.8, 0.0)}")
        print(f"{self.emulator.emit_ultrasound(0.9)}")
        
        self.print_grid()
        
        success = False
        failure = False
        
        for step in range(num_steps):
            # Step simulation
            herd_center = self.herd.get_herd_center()
            state = {
                "distance_to_corridor": self.acoustic_env.distance_to_corridor(herd_center[0], herd_center[1]),
                "distance_to_road": self.acoustic_env.distance_to_road(herd_center[0], herd_center[1]),
                "average_stress": self.herd.get_average_stress(),
                "herd_dispersion": self.herd.get_herd_dispersion(),
                "construction_noise_level": self.acoustic_env.construction_noise_level,
            }
            
            action = self.controller.get_action(state)
            self.controller.apply_action(action, self.acoustic_field)
            
            self.herd.step_all(self.acoustic_env, self.acoustic_field)
            self.step_count += 1
            
            herd_center = self.herd.get_herd_center()
            zone = self.acoustic_env.get_zone_at(herd_center[0], herd_center[1])
            
            if step % 10 == 0 or step < 3:
                print(f"\nStep {step}: Herd at ({herd_center[0]:.1f}, {herd_center[1]:.1f}) - {zone}")
            
            if zone == "corridor":
                success = True
                break
            if zone == "road":
                failure = True
                break
                
        print("\n" + "=" * 60)
        if success:
            print("[SUCCESS] Herd reached safe corridor!")
            print(f"  Steps taken: {self.step_count}")
        elif failure:
            print("[FAILURE] Herd entered road zone!")
        else:
            print("[-] TIMEOUT: Herd did not reach corridor in time")
        print("=" * 60)
        
    def run_interactive(self):
        """Run interactive mode with real-time control"""
        print("\n" + "=" * 60)
        print("INTERACTIVE MODE")
        print("=" * 60)
        print("Commands:")
        print("  status              - Show current state")
        print("  map                 - Show environment map")
        print("  step [N]            - Run N simulation steps (default 1)")
        print("  reset               - Reset simulation")
        print("  beam angle DEG      - Set beam angle (degrees)")
        print("  beam intensity 0-1  - Set beam intensity")
        print("  ultrasound on/off   - Toggle ultrasound")
        print("  social on/off       - Toggle social cue")
        print("  demo                - Run demo scenario")
        print("  help                - Show this help")
        print("  exit                - Exit interactive mode")
        print("=" * 60)
        
        self.reset_simulation()
        
        # Initial state
        print(f"\n{self.emulator.emit_mid_freq(0.5, 0.0)}")
        self.acoustic_field.set_mid_freq_beam(angle=0.0, intensity=0.5, origin=(25, 25))
        self.acoustic_field.update_fields()
        
        self.print_state()
        
        while True:
            try:
                cmd = input("\n> ").strip().lower()
                if not cmd:
                    continue
                    
                parts = cmd.split()
                action = parts[0]
                
                if action == "exit" or action == "quit":
                    print("Exiting interactive mode.")
                    break
                    
                elif action == "help":
                    print("\nCommands:")
                    print("  status              - Show current state")
                    print("  map                 - Show environment map")  
                    print("  step [N]            - Run N simulation steps")
                    print("  reset               - Reset simulation")
                    print("  beam angle DEG      - Set beam angle")
                    print("  beam intensity 0-1  - Set beam intensity")
                    print("  ultrasound on/off   - Toggle ultrasound")
                    print("  social on/off       - Toggle social cue")
                    print("  demo                - Run demo scenario")
                    print("  exit                - Exit")
                    
                elif action == "status":
                    self.print_state()
                    
                elif action == "map":
                    self.print_grid()
                    
                elif action == "step":
                    n = int(parts[1]) if len(parts) > 1 else 1
                    for _ in range(n):
                        self.herd.step_all(self.acoustic_env, self.acoustic_field)
                        self.step_count += 1
                    self.print_state()
                    
                elif action == "reset":
                    self.reset_simulation()
                    self.acoustic_field.set_mid_freq_beam(angle=0.0, intensity=0.5, origin=(25, 25))
                    self.acoustic_field.update_fields()
                    print(f"\n{self.emulator.emit_mid_freq(0.5, 0.0)}")
                    print("Simulation reset.")
                    self.print_state()
                    
                elif action == "beam" and len(parts) >= 3:
                    if parts[1] == "angle":
                        angle = np.radians(float(parts[2]))
                        self.acoustic_field.set_mid_freq_beam(angle, self.acoustic_field.beam_intensity)
                        self.acoustic_field.update_fields()
                        print(f"Beam angle set to {parts[2]}°")
                    elif parts[1] == "intensity":
                        intensity = float(parts[2])
                        self.acoustic_field.set_mid_freq_beam(self.acoustic_field.beam_angle, intensity)
                        self.acoustic_field.update_fields()
                        print(f"Beam intensity set to {intensity:.0%}")
                        
                elif action == "ultrasound" and len(parts) >= 2:
                    if parts[1] == "on":
                        self.acoustic_field.set_ultrasound(True, 0.9)
                        self.acoustic_field.update_fields()
                        print(self.emulator.emit_ultrasound(0.9))
                    elif parts[1] == "off":
                        self.acoustic_field.set_ultrasound(False)
                        self.acoustic_field.update_fields()
                        print(self.emulator.emit_ultrasound(0))
                        
                elif action == "social" and len(parts) >= 2:
                    if parts[1] == "on":
                        self.acoustic_field.set_social_cue(True, 0.5)
                        self.acoustic_field.update_fields()
                        print(self.emulator.emit_social_cue(0.5))
                    elif parts[1] == "off":
                        self.acoustic_field.set_social_cue(False)
                        self.acoustic_field.update_fields()
                        print(self.emulator.emit_social_cue(0))
                        
                elif action == "demo":
                    self.run_demo()
                    # Reset after demo
                    self.reset_simulation()
                    self.acoustic_field.set_mid_freq_beam(angle=0.0, intensity=0.5, origin=(25, 25))
                    self.acoustic_field.update_fields()
                    
                else:
                    print(f"Unknown command: {cmd}")
                    print("Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="KangarooTuning - Sound-based kangaroo guidance system"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=["status", "demo", "interactive", "test"],
        help="Command to run"
    )
    parser.add_argument(
        "--steps", "-n",
        type=int,
        default=50,
        help="Number of steps for demo"
    )
    
    args = parser.parse_args()
    
    cli = KangarooTuningCLI()
    
    if args.command == "status":
        cli.check_dependencies()
        
    elif args.command == "demo":
        cli.check_dependencies()
        print()
        cli.run_demo(args.steps)
        
    elif args.command == "interactive":
        cli.check_dependencies()
        print()
        cli.run_interactive()
        
    elif args.command == "test":
        cli.check_dependencies()
        print("\nRunning pytest tests...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])


if __name__ == "__main__":
    main()
