# Test Template - KangarooTuning Simulation

## STAGE 1: Pure Behaviour Model (No AI)

### Test 1.1: Acoustic Gradient Influence
**Goal**: Verify acoustic gradient influences kangaroo direction in simulation

**Test Setup**:
- Grid: 50x50
- Kangaroo: start at (5, 25), stress=0.3, curiosity=0.5
- Mid-frequency beam: directional toward corridor at (45, 25)
- Intensity: 0.8

**Expected**: Kangaroo movement vector has positive x-component toward corridor

**Results**:
| Run | Distance Moved | Direction | Pass/Fail |
|-----|----------------|-----------|-----------|
| 1   |                |           |           |
| 2   |                |           |           |
| 3   |                |           |           |

### Test 1.2: Ultrasonic Repulsion
**Goal**: Verify ultrasonic field near road pushes kangaroo away

**Test Setup**:
- Grid: 50x50, road at x>40
- Kangaroo: start at (35, 25)
- Ultrasound intensity at road: 0.9

**Expected**: Kangaroo moves toward lower x (away from road)

---

## STAGE 2: Rule-Based Controller

### Test 2.1: Near-Road Response
**Conditions**: distance_to_road < 5
**Action**: activate_ultrasound = true
**Expected**: Kangaroo exits road zone within 10 steps

### Test 2.2: Corridor Guidance
**Conditions**: distance_to_corridor > 10
**Action**: beam_direction points to corridor
**Expected**: Kangaroo reduces distance_to_corridor

### Test 2.3: Stress Reduction
**Conditions**: stress > 0.7
**Action**: reduce_intensity
**Expected**: stress decreases within 5 steps

---

## STAGE 3: RL Controller

### Test 3.1: Training Convergence
**Metric**: Reward should increase over 1000 episodes
**Target**: Average reward > baseline (rule-based) by 20%

### Test 3.2: Safe Exit Rate
**Conditions**: 50 random starting positions
**Target**: >80% exit safely, <5% enter road

### Test 3.3: Generalization
**Variables**: Different noise levels, wind directions, herd sizes
**Target**: Performance within 10% of trained environment

---

## Validation Commands

```bash
# Run Stage 1 tests
python -m pytest tests/test_stage1.py -v

# Run Stage 2 tests
python -m pytest tests/test_stage2.py -v

# Run Stage 3 tests
python -m pytest tests/test_stage3.py -v

# Run all tests
python -m pytest tests/ -v --cov=.
```

---

## Key Hypotheses to Validate

| Hypothesis | Test | Evidence Needed |
|------------|------|-----------------|
| Acoustic gradient influences direction | 1.1 | Movement toward sound source |
| Ultrasonic repels from road | 1.2 | Negative x-movement near road |
| RL outperforms rules | 3.2 | 20%+ improvement in exit rate |
