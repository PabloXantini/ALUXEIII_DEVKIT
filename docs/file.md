# File Reading Implementation
In this section will be documented the file reading implementation, with the proposal of configure quickly parameters of the robot, workspace and simulation scene.

## Config files

### Model configuration file structure implementation
    model: (name)
    components: {
        motors: [
            { 
                label: (any name) 
                type: (Omni)
                calibration: {
                    action: tuple(float[config.len])
                }
                config: [
                    {
                        label: (any name)
                        properties: { (validator custom per type)
                            pin1
                            pin2
                        }
                    }
                ]
            },
            ...
        ]
        ultrasonics: [
            {
                label: (any name)
                type: (default)
                properties: { (validator custom per type)
                    pin1
                    pin2
                }
            },
            ...
        ]
        compasses: [
            { 
                label: (any name)
                type: (default)
                properties: { (validator custom per type)
                    pin1
                    pin2
                }
            },
            ...
        ]
    }

### Workspaces configuration file structure implementation
    workspace: (any name)
    properties: {
        cam: {
            width: int
            height: int
        }
        masK_dir: str
        masks: [
            "ball",
            "ally_goal",
            "enemy_goal",
        ]
    }

For masks we need to specify a file for each one
#### Mask file structure implementation
    mask: (any name)
    properties: {
        lower_bound: tuple(float[3])
        upper_bound: tuple(float[3])
        filters: [
            {
                type: (filter_type), 
                size: int
                iterations: int
            },
            ...
        ]
    }

Is needed to create a mask recorder that save the filter applied on the image.
Also, it will be stored with a simple filter example (closening, size)
Iterations will be 1 by default.

### Sim Scene configuration file structure implementation
    scene: (any name)
    properties: {
        court: {
            circle: {
                color: tuple(float[3])
                radius: int
                visible: bool
            }
            center_line: {
                color: tuple(float[3])
                visible: bool
            }
            penalty_lines: {
                color: tuple(float[3])
                visible: bool
            }
            limit_lines: {
                color: tuple(float[3])
                visible: bool
            }
            walls: {
                color: tuple(float[3])
            }
        }
    }