# Integrated In-Tune Hearing Guide for Animals
Chief user problem specific example: Construction boxing in kangaroos, needing to guide them to an open corridor not from the main road where workers come in and out and responsible for many kangaroo deaths.

Potential solution: A  hardware system tuning into kangaroo's hearing frequency to guide animals into open corridors, to avoid the main road where workers come in and out.

Proof of Concept: Using a simulation model to test demo setup on luring kangaroos from construction zone with setup by using mid-frequency attraction (if possible) and ultrasound repel (more possible) from road.

## Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

### Simulation Mode

python main.py status
- check system status and verify software

python main.py demo 
- automated demo of luring behavior

python main.py interactive
- For a more interactive experience

python main.py test
- For the test templates

---


### Real Mode (Hardware Integration) - Planned

Hardware integration requires additional setup. To enable when ready, if simulation results are good and in need of more tweaking:

1. **Connect Hardware** - Configure in `config.py`:
   ```python
   # config.py
   REAL_MODE = True
   GPIO_PINS = {
       'mid_freq_emitter': 18,    # 8-16kHz directional speaker
       'ultrasound_emitter': 23, # 25kHz+ repeller
       'pir_sensor': 24,         # Motion detection
   }
   ```

2. **Create hardware interface** (create `real_hardware.py`):
   ```python
   # real_hardware.py - Template for GPIO control
   import RPi.GPIO as GPIO
   
   class HardwareInterface:
       def __init__(self, pins):
           GPIO.setmode(GPIO.BCM)
           for name, pin in pins.items():
               GPIO.setup(pin, GPIO.OUT if 'emitter' in name else GPIO.IN)
       
       def read_sensors(self):
           # Read PIR/thermal sensors
           pass
       
       def emit_sound(self, acoustic_field):
           # Control speakers based on acoustic_field state
           pass
   ```

4. **Safety Checklist**:
   - [ ] Test speakers at low volume first
   - [ ] Monitor animal behavior continuously
   - [ ] Stop immediately if distress signs observed
   - [ ] Comply with local wildlife regulations
   - [ ] Obtain necessary permits

---

## Features
* Two sensors, around the construction place. One at the center heard at a large range around for lost kangaroos, and the other near the corridor meant for kangaroos to pass through.

* The center sensor is a passive receiver, and the other one is a transmitter, which is tuned into the kangaroo's hearing frequency to guide them to the corridor.

* The center sensor lures the kangaroos to the center of the construction place at first, for the other sensor guides the kangaroos to the corridor.

## Configurations
* Python? Works well with a lot of hardware systems
* Hardware types: Microcontroller, Transmitter, Receiver, Sensor, Actuator (Searching for potential setups close to problem-solution)
* Sensor Layer - PIR, Thermal cameras, LiDAR, CV
* Guidance layer - Directional sound emitters etc
* Control layer - Feedback loop behaviour monitoring, reinforcement path shaping

## Research
### Questions
* What are the frequencies that kangaroos can hear to attract vs. repel -Eastern grey kangaroo amplification btwn 1 - 18kHZ, sensitivity btwn 2 - 3.5kHz. Can hear above 20kHz but sensitivity >18kHz greatly reduced. Foot thump signal frequency below 7kHz, directed at predator and increasing vigiance levels amongst kangaros to take flight. Artificial deterrents lose efficacy over time because animals become habituated. Have yet to find sound that attracts kangaroos, when natural sounds for interactions, fights and flights away, but not towards. 
* Can sound guide movement reliably in open environments? - Outdoors have natural elements and dispersing quickly with background noises. ... They use a construction site, meaning a lot of background noise. Can ultrasound be separated from that?
* What has already been tried for the kangaroo problem? - Roo Guard and Shu Roo - mixed opinion but statistics aren't showing their effectiveness against repelling away kangaroos. Whistlers to whistle ultrasonically to clear animals out of the way. Roobadge, for cars to prevent collisions with kangaroos, a few are tentatively hopeful but admit none of the ventures have worked over the years.
* How kangaroos respond to directional sound cues - see above
* Ethical and legal restrictions

For auditory detterant, audible to target species at best hearing frequency, meaningful such as an alarm signal, generate flight response and sufficient time btwn playing auditory stimulus and target species response. Sufficient intensity.

If auditory does not work, visually. Virtual fencing, but works at dawn, dusk and night. What about day?

## Progress Summary
Working on testing the concept, as a simulation before any full AI or hardware investment with detailed kangaroo model about stress, curiosity, herd cohesion, panic threshold using mid-frequency guide, social cue and ultrasonic to guide kangarros to the corridor.

Potential gaps mentioned in research would be unproven attraction sound, tested that if acoustic gradient influence doesn't work, then the concept is flawed. Habituation is not modeled, and still working on ethical / legality for this project. How outdoor dispersion may affect this project.

According to tests, the acoustic gradient influence for attraction and ultrasonic repulsion failed even though repulsion should technically be possible considering there is research to back up. Will further read up and check on code or else re-evaluate. 

Needing to test whether herd reaches to the corridor in construction zone in time?

Contributions and feedback are always welcome for this proof of concept.