# Requirements to do implement
- Motor calibration for 4WD and 3WD, via file reading
- PID implementation on robot
- UDP Communication Backend and simulation implementation
- Improve simulation architecture (physics, match rules, etc...)
- Change enviroment via file reading (include name on manifest)
- Scene atributes via file reading (include name on manifest)
- UI Observability
- Suscribe robot to game to avoid passing as argument

- ### Modularize run system, example (run simulation, run robot, show cameras, process test (ui, logger, etc...)) [Mostly Done]
    - Run sandbox (--sandbox)
        - prepare match
        - do run sanbox method
        - (--debug) enable debug (cameras)
        #### Command: alux.py --sandbox [--debug]
    - Run robot
        - (--debug) enable debug (cameras)
        #### Command: alux.py [--debug]
    command
    - Run test (--test)
        - process test (tracker)
        - (--sandbox) do run sandbox method
        - (--debug) enable debug (cameras)
        #### Command: alux.py --test [--sandbox] [--debug]

    - Only missing show the camera when run test with --debug (real)