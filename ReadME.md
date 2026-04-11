# KangarooTuning

A sound-based wildlife guidance simulation for redirecting kangaroos away from construction zones and toward safe corridors — before investing in hardware.

> **Status:** Proof-of-concept simulation. Stage 1 (behavior model) partially
> passing. Stage 2 (rule-based controller) passing. Stage 3 (RL) not yet trained.

---

## Description

Construction sites near wildlife corridors cause kangaroo fatalities when animals wander onto active roads. This project models a hardware-free-first approach:
tune directional sound emitters to the kangaroo's hearing range to guide herds toward a safe exit corridor, away from the road.

The simulation tests whether acoustic gradient influence is even plausible before any hardware investment is made.

---

## Current Features

- **2D grid simulation** — 50×50 environment with construction zone, road boundary,
  safe corridor, obstacles, and worker noise sources
- **Kangaroo behavioral model** — per-agent stress, curiosity, herd cohesion, panic
  threshold, and velocity
- **3-band acoustic field** — mid-frequency guide (2–10 kHz), social cue (500 Hz–2 kHz),
  ultrasonic repeller (>20 kHz) with distance attenuation and wind distortion
- **Rule-based controller** — hard-coded guidance strategy as a baseline
- **RL environment scaffold** — Gymnasium-compatible environment for PPO training
  (untrained)
- **CLI interface** — `status`, `demo`, `interactive`, `test` modes
- **ASCII map renderer** — real-time top-down environment view in terminal
- **Test suite** — Stage 1–3 pytest tests with documented expected outcomes

---

## Built With

| Library | Purpose |
|---|---|
| Python 3.x | Core language |
| numpy | Grid math, vector calculations |
| matplotlib | Plotting (optional) |
| pygame | Graphical display (optional) |
| stable-baselines3 | PPO reinforcement learning |
| gymnasium | Custom RL environment |

---

## Getting Started

### Prerequisites

Python 3.8+ recommended.

```bash
pip install -r requirements.txt
```

pygame and stable-baselines3 are optional — the core simulation runs without them.

### Installation

```bash
git clone <repo-url>
cd KangarooTuning
pip install -r requirements.txt
```

Verify setup:

```bash
python main.py status
```

---

## Usage

```bash
# Check dependencies and system status
python main.py status

# Watch an automated demo of the guidance attempt
python main.py demo

# Control the simulation interactively (beam angle, intensity, ultrasound toggle)
python main.py interactive

# Run the full pytest test suite
python main.py test
```

### Interactive Commands

| Command | Description |
|---|---|
| `status` | Show herd position, stress, zone |
| `map` | Print ASCII environment map |
| `step [N]` | Advance simulation N steps |
| `beam angle DEG` | Set mid-freq beam angle |
| `beam intensity 0-1` | Set mid-freq intensity |
| `ultrasound on/off` | Toggle ultrasonic repeller |
| `social on/off` | Toggle social cue emitter |
| `reset` | Reset to initial state |
| `demo` | Run automated demo |
| `exit` | Quit |

---

## Roadmap

- [ ] **Fix acoustic response bug** — kangaroos not responding to sound stimuli
  (root cause: `AcousticEnvironment` not syncing from `AcousticField`)
- [ ] **Stage 1 passing** — acoustic gradient influence and ultrasonic repulsion tests
- [ ] **RL training** — train PPO controller, target >80% safe exit rate
- [ ] **Sensitivity analysis** — test curiosity, herd cohesion, gradient strength
- [ ] **Baseline comparison** — random walk vs acoustic-guided to prove influence is real
- [ ] **Monte Carlo runs** — multiple seeds, statistical validation
- [ ] **Hardware prototype** — Raspberry Pi + directional speaker + PIR sensor
- [ ] **Field testing** — requires wildlife permit and ethics clearance

### Hardware Integration (Planned)

When simulation results are validated, hardware setup requires:

1. **Connect Hardware** — configure in `config.py`:
   ```python
   REAL_MODE = True
   GPIO_PINS = {
       'mid_freq_emitter': 18,    # 8–16 kHz directional speaker
       'ultrasound_emitter': 23,  # 25 kHz+ repeller
       'pir_sensor': 24,          # Motion detection
   }
   ```

2. **Create hardware interface** (create `real_hardware.py`):
   ```python
   import RPi.GPIO as GPIO

   class HardwareInterface:
       def __init__(self, pins):
           GPIO.setmode(GPIO.BCM)
           for name, pin in pins.items():
               GPIO.setup(pin, GPIO.OUT if 'emitter' in name else GPIO.IN)

       def read_sensors(self):
           pass  # Read PIR/thermal sensors

       def emit_sound(self, acoustic_field):
           pass  # Control speakers based on acoustic_field state
   ```

3. **Safety checklist**:
   - [ ] Test speakers at low volume first
   - [ ] Monitor animal behavior continuously
   - [ ] Stop immediately if distress signs observed
   - [ ] Comply with local wildlife regulations
   - [ ] Obtain necessary permits

---

## Research Notes

- Eastern grey kangaroo amplification: 1–18 kHz, peak sensitivity 2–3.5 kHz
- Can hear above 20 kHz but sensitivity drops sharply above 18 kHz
- Foot thump frequency below 7 kHz — signals predator threat, increases herd vigilance
- No confirmed attraction sound found — natural vocalizations are for interactions, fights, or flight, not approach
- Existing deterrents (Roo Guard, Shu Roo, Roobadge) show mixed or no proven results
- Habituation is a known risk — animals adapt to repeated artificial stimuli over time
- Outdoor sound dispersion and construction background noise are unresolved challenges

---

## License

TBD

---