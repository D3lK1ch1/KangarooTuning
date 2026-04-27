# Changelog

All notable changes to Kangaroo Tuning are recorded here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.3.0] — Architecture Review & Bug Fixes (April 2026)

  **Fixed:**

  - Acoustic sync: `AcousticEnvironment` now syncs from `AcousticField` at the start of
    each step — kangaroos were navigating blind (all-zero sound fields) in every prior run
  - Controller: `apply_action()` was checking `if "key" in action` (always True) instead
    of `if action["key"]` — all action branches ran unconditionally every step
  - Beam direction: hardcoded to `(5, 25)` — now reads live `state["herd_center"]`
  - Beam angle: was applied as a cumulative delta (rotates indefinitely) — now set as
    absolute target angle
  - Visualization: `get_state_image()` multiplied an already-uint8 grid by 255 again —
    every rendered image overflowed to black
  - Visualization: `print_state()` hardcoded step counter as `0` — now receives real step
  - Dead code: `RuleBasedControllerSimple` removed — defined but never imported or used

  **Deferred (structural refactors — low risk, low urgency):**

  - RL action map duplicated across `controller_rl.py` and `simulation_runner.py`
  - `run_demo()` reimplements `SimulationRunner` game loop
  - `SoundEmulator` state fields are set but never read back
  - `hasattr(.model)` controller type detection — fragile attribute sniffing
  - `print_grid()` lives in `main.py` instead of `Visualizer`

  **Test results:**

  - Stage 2: 8/9 passing. `test_2_2` (corridor guidance) now fails — acoustic sync fix
    revealed that stress accumulates past panic threshold before acoustic guidance takes
    effect at current parameter values. Parameter calibration issue, not an implementation bug.
  - Stage 1: stress response PASS, herd behavior PASS, acoustic gradient FAIL,
    ultrasonic repulsion FAIL — same root cause as `test_2_2` (see Known Limitations).
  - Stage 3: RL environment interface PASS. Training tests skipped (no trained model).

## [0.2.0] — Stage 2 Controller (March 2026)

- Stage 2 rule-based controller tests passing: near-road response, corridor guidance,
  stress reduction
- Interactive mode with live beam angle, intensity, and ultrasound toggle controls
- ASCII map renderer with zone and acoustic field overlay

## [0.1.0] — Stage 1 Behavior Model (March 2026)

- 2D grid environment with construction, road, and corridor zones
- Kangaroo agent model: stress, curiosity, herd cohesion, panic threshold, velocity
- 3-band acoustic field: mid-frequency, social cue, ultrasound
- Data comes based on research, hardcoded in config.py
- CLI interface: `status`, `demo`, `interactive`, `test`
- Stage 1 results: stress response PASS, herd behavior PASS
- Stage 1 results: acoustic gradient influence FAIL, ultrasonic repulsion FAIL
