# Fourier Robot Descriptions

## Usage

```python
from fourier_robot_descriptions.loaders.pinocchio import load_robot_description
robot = load_robot_description("GR1T2")
```

To directly get the URDF file path:

```python
from fourier_robot_descriptions.fourier_right_hand import URDF_PATH, PACKAGE_PATH
```

## Available Robots

| Name | Description |
|------|-------------|
| GR1T1 | Vanilla GR1T1  |
| GR1T1_fourier_hand | GR1T1 with Fourier hand |
| GR1T2 | Vanilla GR1T2  |
| GR1T2_fourier_hand_capsule_coll | GR1T2 with Fourier hand and capsule collision mesh |
| GR1T2_inspire_hand_capsule_coll | GR1T2 with Inspire hand and capsule collision mesh |
| GR2T1 | Vanilla GR2T1  |
| GR2T1_simple_coll | Vanilla GR2T1 with simple collision mesh | 