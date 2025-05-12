# Example Walkthrough

## Initial Setup

**Core_1 (EDF)** contains two components:

1. **Image_Processor**
    - Budget: 2/6
    - Running: Task_5 (WCET=3)

2. **Camera_Sensor**
    - Budget: 5/9
    - Running: Task_1 (WCET=7)

## Timeline Events

| Time | Event | Image_Processor | Camera_Sensor | Core Action |
|------|-------|-----------------|---------------|-------------|
| 0 | Image_Processor starts | budget: 2 → 1 | - | Runs Task_5 (1 unit) |
| 1 | Image_Processor continues | budget: 1 → 0 | - | Runs Task_5 (1 unit) |
| 2 | Image_Processor budget exhausted | Blocked | budget: 5 → 4 | Switches to Camera_Sensor |
| 3-6 | Camera_Sensor execution | - | budget: 4 → 0 | Task_1 paused (4/7 complete) |
| 6 | Image_Processor period reset | New budget: 2 | Blocked | Image_Processor resumes |

## Key Events

- **Time 2**: Image_Processor depletes its 2-unit budget and becomes blocked. Camera_Sensor takes control.
- **Time 6**: Image_Processor's period resets (6/6), receiving fresh budget and preempting current execution.