# Changelog

All notable changes to Kangaroo Tuning are recorded here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.3.0] — Architecture Review, Bug Fixes & POC Close-Out (May 2026)

  **Core simulation bug fixed:**

  - Acoustic sync (`kangaroo_agent.py`, `environment.py`): `AcousticEnvironment` holds
    a cached copy of the sound field arrays. `AcousticField` computes the real values.
    `update_acoustic_fields()` — the method that syncs the cache — was never called during
    simulation steps, so kangaroos read all-zero sound fields at all times and moved blind.
    Fix: call `update_acoustic_fields()` at the start of `Herd.step_all()` every step.
    This is a shared-state ownership bug — two objects held the same data and diverged.

  **Controller bugs fixed (`controller_rule_based.py`):**

  - Key-presence vs value check: `if "key" in action` is always True when every key is
    present in the dict. The social cue, ultrasound, and intensity branches ran every step
    regardless of whether the action was actually set. Fixed to check `if action["key"]`.
  - Beam direction hardcoded: angle to corridor was calculated from `(5, 25)` — the
    starting position — even after the herd moved. Fixed to use `state["herd_center"]`.
  - Beam angle additive: `apply_action()` added the angle delta every step, causing the
    beam to spin indefinitely. `get_action()` intended an absolute angle. Fixed to assign,
    not add. Key renamed `set_beam_direction` to make intent explicit.
  - Dead code removed: `RuleBasedControllerSimple` was defined but never imported or used.

  **Runner bug fixed (`simulation_runner.py`):**

  - Controller type detection used `hasattr(controller, 'model')` — any object with a
    `.model` attribute for any reason would be routed to the RL path. Replaced with
    `isinstance(controller, RLController)`.
  - RL action dispatch block (RL_ACTION_MAP lookup + if/elif chain) was placed after both
    branches of the if/else, so it ran for the rule-based controller too. The rule-based
    controller returns a dict; RL_ACTION_MAP expects an int key — TypeError every step.
    Fixed by moving the dispatch block inside the `isinstance` branch.

  **Deduplication (`config.py`, `controller_rl.py`, `simulation_runner.py`):**

  - `RL_ACTION_MAP` was copy-pasted in two files. Defined once in `config.py` and imported
    in both. If a new action is added, there is now one place to update.

  **Display bugs fixed (`visualization.py`):**

  - `get_state_image()` multiplied an already-uint8 grid by 255 again, overflowing every
    pixel value to near-black. Fixed to convert to uint8 once at the final output step.
  - `print_state()` hardcoded the step counter as the integer `0`. Every printout showed
    "Step: 0" regardless of simulation progress. Fixed to receive the real step number.

  **Cleanup (`main.py`):**

  - `SoundEmulator` tracked `mid_freq_active`, `ultrasound_active`, `mid_freq_intensity`,
    `ultrasound_intensity` as instance fields — but `AcousticField` is the real source of
    that state and `SoundEmulator`'s fields were never read back by anything. A developer
    updating `SoundEmulator` thinking it affects the simulation would be wrong. Removed.

  **Deferred (low risk, low urgency — revisit if RL training begins):**

  - `run_demo()` in `main.py` reimplements the `SimulationRunner` game loop manually
  - State dict construction duplicated across `main.py` and `controller_rl.py`
  - `print_grid()` lives in `main.py` instead of `Visualizer`
  - `update_fields()` uses a nested Python loop over 2500 cells — vectorizable with numpy,
    deferred until RL training makes performance a real concern

  **Final test results:**

  - Stage 1 (4/4 PASS): acoustic gradient influence, ultrasonic repulsion, stress response,
    herd behavior — core acoustic mechanics confirmed working
  - Stage 2 (3/4 PASS): near-road response, stress reduction, rule-based baseline pass.
    `test_2_2` (corridor guidance) fails — starting distance of 40 grid units exceeds
    effective beam range at current attenuation settings. Behavioral parameters are not
    field-validated. Documented as a known POC limitation, not a code bug.
  - Stage 3 (2 PASS, 3 SKIP): RL environment interface and RL vs rule comparison pass.
    Training tests skipped — no trained model exists yet.

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
