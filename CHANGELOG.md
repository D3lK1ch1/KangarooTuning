# Changelog

All notable changes to Kangaroo Tuning are recorded here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — Bug Fixes & Cleanup Planned

Full architecture review completed. 14-commit cleanup plan across 6 batches.

**Critical bugs identified:**

- `AcousticEnvironment` and `AcousticField` both hold sound arrays but never sync —
  kangaroos read stale all-zero values, making them acoustically blind
- Controller checks `if "key" in action` (always True) instead of `if action["key"]` —
  all branches run unconditionally every step
- Beam direction computed from hardcoded origin `(5, 25)` instead of live herd position
- Beam angle applied as a cumulative delta instead of an absolute target — spins indefinitely

**Display bugs identified:**

- `get_state_image()` multiplies an already uint8 grid by 255 again — image overflows to black
- `print_state()` hardcodes step number as `0` regardless of actual simulation progress

**Dead code identified:**

- `RuleBasedControllerSimple` defined but never imported or used anywhere

**Structural issues identified:**

- RL action map duplicated in `controller_rl.py` and `simulation_runner.py`
- `run_demo()` in `main.py` re-implements the same game loop as `SimulationRunner`
- State dict constructed three different ways across three files — inconsistent normalization
- `SoundEmulator` tracks state fields that are never read back by anything
- `SimulationRunner` detects controller type via `hasattr(.model)` — fragile attribute sniffing
- `print_grid()` lives in `main.py` instead of `Visualizer`
- `AcousticField.update_fields()` uses a Python nested loop over 2500 cells — numpy-vectorizable

### [0.2.0] — Stage 2 Controller (March 2026)

- Stage 2 rule-based controller tests passing: near-road response, corridor guidance,
  stress reduction
- Interactive mode with live beam angle, intensity, and ultrasound toggle controls
- ASCII map renderer with zone and acoustic field overlay

### [0.1.0] — Stage 1 Behavior Model (March 2026)

- 2D grid environment with construction, road, and corridor zones
- Kangaroo agent model: stress, curiosity, herd cohesion, panic threshold, velocity
- 3-band acoustic field: mid-frequency, social cue, ultrasound
- CLI interface: `status`, `demo`, `interactive`, `test`
- Stage 1 results: stress response PASS, herd behavior PASS
- Stage 1 results: acoustic gradient influence FAIL, ultrasonic repulsion FAIL
